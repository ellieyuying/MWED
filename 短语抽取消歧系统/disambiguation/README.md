# disambiguation —— EVP 多义短语消歧模块（独立封装）

对**已抽取**的多义短语命中，用 LLM（Qwen）判定学习者意图的义项。**只做消歧，不做抽取**。

## 结构
```
disambiguation/
  disambiguator.py   # prompt / API 调用 / 批量消歧 + 公开 API
  __init__.py / README.md
```

## 配置（环境变量，勿硬编码 key）
```bash
export DASHSCOPE_API_KEY=<your-key>          # 必填（dry-run 除外）
export DASHSCOPE_API_BASE=...                # 可选，默认 dashscope compatible-mode
export DISAMBIG_MODEL=qwen3.6-flash          # 可选
```
依赖：`pip install openai`（惰性导入，仅真实调用时需要）。

## 公开 API

### 通用（与抽取解耦）
```python
from disambiguator import disambiguate
instances = [{
    'phrase': 'store up sth',
    'target': 'I store up money for the future.',
    'context': '<前句> I store up money for the future. <后句>',
    'senses': [{'释义序号':1,'释义':'keep and not use'},
               {'释义序号':2,'释义':'remember things'}],
}]
out = disambiguate(instances)          # [{'sense':1,'confidence':'high','reason':...}]
out = disambiguate(instances, dry_run=True)   # 不调 API，占位结果
```

### 衔接抽取模块（流水线）
```python
from extractor import extract              # phrase_extraction 包
from disambiguator import disambiguate_hits

results = extract(essay_paths, unambig_regex_xlsx, ambig_xlsx)
for answer, hits in results:
    sense_results = disambiguate_hits(hits)   # 与 hits 等长；单义位 None，多义位消歧结果
    for hit, sr in zip(hits, sense_results):
        if sr:  # 多义命中
            print(hit.pattern.phrase_id, '→ sense', sr['sense'], sr['confidence'])
```

## 与抽取模块的边界
- **抽取**（phrase_extraction）判"短语在某句是否出现" → 输出 hits；
- **消歧**（本模块）只对 hits 中 `多义=是` 的命中判"哪个义项"；
- 两者评测口径分开：抽取评 P/R/F1，消歧评义项准确率（另有 BERT/LLM 选型对比，见 `dab/`）。

## 消歧质量
消歧方案与选型详见项目 `dab/`（BERT bi/cross-encoder vs LLM 对比）与总报告。本模块封装的是 annotator 现用的 **LLM（Qwen3.6-flash）批量消歧**逻辑（prompt/解析与原实现逐字符一致，已回归验证）。
