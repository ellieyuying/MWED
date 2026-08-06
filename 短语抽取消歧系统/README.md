# 短语抽取消歧系统

EVP 学习者作文的**短语自动抽取 + 多义消歧**系统。两个独立可检验模块 + 串联流水线 + 结果与分析。

## 目录结构
```
短语抽取消歧系统/
  phrase_extraction/        ← 模块①：短语抽取（无 LLM 依赖）
    extractor.py              解析→归一化→匹配→抽取结果 + extract() API + CLI
    evp_regex_generator.py    短语→正则（phrase_to_regex）
    evp_special_cases.py      特例规则表 + decade 合并规则
    evp_linguistic_data.py    语言学数据表（屈折/代词/缩写 + 词形还原/匹配用词表）
    test_regex_recall.py      正则在例句集上的召回率测试
    data/  单义短语_v12_regex.xlsx  多义短语_v10.xlsx  单义短语_updated_v12.xlsx
    README.md

  disambiguation/           ← 模块②：多义消歧（LLM，key 走环境变量）
    disambiguator.py          disambiguate() / disambiguate_hits() API
    README.md

  run_pipeline.py           ← 流水线：抽取 + 消歧一次跑完（支持 --reuse-disambig）
  compute_phrase_indices.py ← 短语级 CEFR 复杂度指标（sense-aware）+ 与写作分相关
  word_vs_phrase_regression.py ← 词级 vs 短语级 层次回归
  结果_v12/                 ← 结果（v12 词表，全 2474 篇 answer）
    sentences.xlsx            句子表（每句一行）
    hit_detail.xlsx           抽取+消歧结果（短语/变体/CEFR/义项/置信度/理由）
    phrase_indices_v12.csv    每篇作文的 16 个短语级复杂度指标
    phrase_corr_v12.csv       16 指标与写作分的相关（sense-aware / 固定级 / 旧 v6 三口径）
    word_indices_v12.csv      每篇的词级指标（层次回归的词级基线）
```

## 快速开始

### 只抽取（无需 API）
```bash
cd phrase_extraction
python extractor.py --essays-dir <XML目录> --out-sentences s.xlsx --out-hits h.xlsx
```

### 抽取 + 消歧（完整流水线，消歧需 API key）
```bash
export DASHSCOPE_API_KEY=<your-key>
export DISAMBIG_MODEL=qwen3.6-flash          # 可选，默认即此
python run_pipeline.py --essays-dir <XML目录> --out-dir 结果_v12
# 复用已有义项标注（仅新命中调 LLM）：--reuse-disambig 旧hit_detail.xlsx
# 免 API 试跑：--dry-run
```

## 当前结果（结果_v12/）
- 2474 篇 answer，23881 命中；多义命中 3286，已 LLM（qwen3.6-flash）消歧。
- 抽取质量（30 篇分层标注集，逐句 phrase-occurrence 口径）：**Precision 89.7% / Recall 94.6% / F1 92.0%**。
- 正则在 EVP 例句集上的召回：**92.2%**（词典 88.9% / 学习者 88.5%，见 `phrase_extraction/test_regex_recall.py`）。

## 验证与文档
- 核查/修复/评测记录见 `核查说明/MWED短语抽取_核查与修复总报告.md`；指标有效性见 `核查说明/短语级指标_有效性分析简报.md`。
- 词表条目经人工核对，正则列由生成器产出；改生成器后可重生成正则列（见 `phrase_extraction/README.md`）。

## 安全
- API key 一律走环境变量 `DASHSCOPE_API_KEY`，代码无硬编码。
