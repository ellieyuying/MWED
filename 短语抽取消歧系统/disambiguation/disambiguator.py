#!/usr/bin/env python3
"""
EVP 多义短语消歧模块
==================================
职责：对已抽取的多义短语命中，用 LLM 判定学习者意图的义项。

设计：核心 API 与抽取模块解耦——接受通用实例，不依赖 MatchHit 类。
  disambiguate(instances, dry_run=False) -> List[Optional[dict]]
    instances: [{'phrase':..., 'target':句子, 'context':上下文, 'senses':[义项...]}]
    返回: 每条 {'sense': int|'not_applied', 'confidence':..., 'reason':...} 或 None
另附便捷适配器（衔接抽取模块的 MatchHit）：
  disambiguate_hits(hits, dry_run=False) -> List[Optional[dict]]  # 与 hits 等长，单义位 None

配置（环境变量）：
  DASHSCOPE_API_KEY   必填（dry_run 除外）
  DASHSCOPE_API_BASE  默认 dashscope compatible-mode
  DISAMBIG_MODEL      默认 qwen3.6-flash

依赖：openai（惰性导入，仅真实调用时需要）
"""

import os
import json
import time
from typing import List, Dict, Optional

# ── 配置（环境变量）────────────────────────────────────────────────
API_KEY    = os.environ.get('DASHSCOPE_API_KEY', '')
API_BASE   = os.environ.get('DASHSCOPE_API_BASE',
                            'https://dashscope.aliyuncs.com/compatible-mode/v1')
MODEL      = os.environ.get('DISAMBIG_MODEL', 'qwen3.6-flash')
BATCH_SIZE = int(os.environ.get('DISAMBIG_BATCH', '6'))   # 单次 API 最多几条
SLEEP_SEC  = float(os.environ.get('DISAMBIG_SLEEP', '0.5'))
MAX_RETRY  = int(os.environ.get('DISAMBIG_RETRY', '3'))


_CLIENT = None


def _ensure_openai():
    """惰性创建 openai 客户端（新版 SDK >=1.0，client-based）。"""
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    if not API_KEY:
        raise RuntimeError('未设置 DASHSCOPE_API_KEY 环境变量，无法调用消歧 API')
    from openai import OpenAI
    _CLIENT = OpenAI(api_key=API_KEY, base_url=API_BASE)
    return _CLIENT


SYSTEM_PROMPT = """\
You are a word sense disambiguation expert specializing in English learner writing.

Given a sentence written by a language learner and a target phrase with multiple senses,
identify which sense the learner intended.

Rules:
- Consider the full context of the sentence, not just keyword overlap.
- Learner sentences may be grammatically imperfect — focus on intended meaning.
- If two senses seem equally plausible, pick the more common usage for learners.
- Use "not_applied" for sense if EITHER of the following is true:
    (a) The phrase is used with a meaning not covered by any of the listed dictionary senses.
    (b) The learner has clearly misused the phrase such that no listed sense applies.
- Reply ONLY with a JSON object on a single line. No explanation outside the JSON.

Output format (normal case):
{"sense": <integer>, "confidence": "high" | "medium" | "low", "reason": "<one sentence>"}

Output format (not applicable):
{"sense": "not_applied", "confidence": "high" | "medium" | "low", "reason": "<one sentence>"}\
"""


def _build_sense_block(senses: List[Dict]) -> str:
    lines = []
    for s in senses:
        defn   = str(s.get('释义', '') or '').strip()
        ex_raw = str(s.get('词典例句', '') or '').strip().split('\n')[0].strip()
        ex_str = f'\n     Example: {ex_raw[:80]}' if ex_raw else ''
        lines.append(f'  [{s.get("释义序号", "?")}] {defn}{ex_str}')
    return '\n'.join(lines)


def _build_batch_prompt(batch: List[Dict]) -> str:
    """batch 中每个元素：{phrase, context, target, senses}"""
    items = []
    for i, inst in enumerate(batch, 1):
        sense_block = _build_sense_block(inst['senses'])
        items.append(
            f'--- Item {i} ---\n'
            f'Phrase: "{inst["phrase"]}"\n'
            f'Context: {inst.get("context", inst["target"])}\n'
            f'Target sentence: {inst["target"]}\n'
            f'Senses:\n{sense_block}'
        )
    return (
        '\n\n'.join(items) + '\n\n'
        'For each item above, reply with ONE JSON object per line (no array brackets), in order:\n'
        '{"item": 1, "sense": <int or "not_applied">, "confidence": "high|medium|low", "reason": "<one sentence>"}\n'
        '{"item": 2, ...}\n'
        'Output ONLY these JSON lines, nothing else.'
    )


def _call_api(user_content: str) -> Optional[str]:
    client = _ensure_openai()
    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL, max_tokens=800, temperature=0.0,
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user',   'content': user_content},
                ],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f'    [API 错误] 第 {attempt} 次: {e}')
            if attempt < MAX_RETRY:
                time.sleep(2 ** attempt)
    return None


def _parse_batch_response(raw: Optional[str], batch_size: int) -> List[Optional[Dict]]:
    results = [None] * batch_size
    if not raw:
        return results
    for line in raw.splitlines():
        line = line.strip()
        if not line or not line.startswith('{'):
            continue
        try:
            obj = json.loads(line)
            idx = int(obj.get('item', 0)) - 1
            if 0 <= idx < batch_size:
                results[idx] = obj
        except (json.JSONDecodeError, ValueError):
            pass
    return results


# ══════════════════════════════════════════════════════════════════
# 公开 API
# ══════════════════════════════════════════════════════════════════
def disambiguate(instances: List[Dict], dry_run: bool = False) -> List[Optional[Dict]]:
    """
    对多义实例批量消歧。返回与 instances 等长的结果列表。
    instances 每项：{'phrase':str, 'target':句子, 'context':上下文(可选), 'senses':[义项dict]}
      义项 dict 需含 '释义序号'/'释义'（可选 '词典例句'）。
    结果每项：{'sense': int|'not_applied', 'confidence':str, 'reason':str} 或 None（失败）。
    dry_run=True 时不调用 API，返回占位结果（sense=1）。
    """
    results: List[Optional[Dict]] = [None] * len(instances)
    if not instances:
        return results
    n_batches = (len(instances) + BATCH_SIZE - 1) // BATCH_SIZE
    for bi in range(n_batches):
        batch = instances[bi * BATCH_SIZE:(bi + 1) * BATCH_SIZE]
        prompt = _build_batch_prompt(batch)
        if dry_run:
            parsed = [{'sense': 1, 'confidence': 'low', 'reason': '[dry-run]'}] * len(batch)
        else:
            parsed = _parse_batch_response(_call_api(prompt), len(batch))
            time.sleep(SLEEP_SEC)
        for j, out in enumerate(parsed):
            results[bi * BATCH_SIZE + j] = out
    return results


def disambiguate_hits(hits, dry_run: bool = False) -> List[Optional[Dict]]:
    """
    便捷适配器：衔接抽取模块的 MatchHit 列表。
    hits 每项须有 .pattern.is_ambiguous / .pattern.phrase_id /
    .pattern.senses / .sentence / .context。
    返回与 hits 等长：单义命中位置为 None，多义命中位置为消歧结果。
    """
    results: List[Optional[Dict]] = [None] * len(hits)
    ambig_idx = [i for i, h in enumerate(hits) if getattr(h.pattern, 'is_ambiguous', False)]
    if not ambig_idx:
        return results
    instances = [{
        'phrase':  hits[i].pattern.phrase_id,
        'target':  hits[i].sentence,
        'context': getattr(hits[i], 'context', hits[i].sentence),
        'senses':  hits[i].pattern.senses,
    } for i in ambig_idx]
    print(f'  多义短语命中 {len(instances)} 条，批量消歧中...')
    outs = disambiguate(instances, dry_run=dry_run)
    for i, out in zip(ambig_idx, outs):
        results[i] = out
    return results


if __name__ == '__main__':
    # 自测（dry-run，不需 API）
    demo = [{
        'phrase': 'store up sth',
        'target': 'I store up money for the future.',
        'context': 'I store up money for the future.',
        'senses': [
            {'释义序号': 1, '释义': 'to keep something and not use it now'},
            {'释义序号': 2, '释义': 'to remember things'},
        ],
    }]
    print('dry-run 结果:', disambiguate(demo, dry_run=True))
