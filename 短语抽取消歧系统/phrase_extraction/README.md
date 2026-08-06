# phrase_extraction —— EVP 短语抽取模块（独立封装）

作文 → 句子 → 归一化 → 正则匹配 → **抽取结果**。**只做抽取，不含 LLM 消歧**（消歧为独立模块）。

## 结构
```
phrase_extraction/
  extractor.py            # 主模块：解析/归一化/加载/匹配/词性验证 + extract() API + 输出
  evp_regex_generator.py  # 正则生成器：短语→正则（phrase_to_regex），process_file 批量写入正则列
  evp_special_cases.py    # 特例规则表 + decade 合并规则（phrase_to_regex 通用生成前先查）
  evp_linguistic_data.py  # 语言学数据（屈折/代词/缩写表 + 词形还原/匹配用词表）
  test_regex_recall.py    # 正则在 EVP 例句集上的召回率测试
  __init__.py             # 公开 API
  data/
    单义短语_v12_regex.xlsx   # 单义短语表（含"正则表达式"列，抽取器加载此文件）
    单义短语_updated_v12.xlsx # 单义短语表（无正则列，重生成正则的输入）
    多义短语_v10.xlsx         # 多义短语义项表
```

## 依赖
```
pip install openpyxl nltk
python -c "import nltk; nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger_eng'); nltk.download('punkt_tab'); nltk.download('omw-1.4')"
```

## 用法

### CLI
```bash
python extractor.py --essays-dir <作文XML目录> \
    --unambig data/单义短语_v12_regex.xlsx \
    --ambig   data/多义短语_v10.xlsx \
    --out-sentences sentences.xlsx --out-hits hits.xlsx
```
输出：
- `sentences.xlsx` 句子表（每句一行：essay_id/题号/句序/句子/句级错误类型）
- `hits.xlsx` 抽取结果（每次命中一行：essay_id/句序/句子/短语/变体/CEFR/词性/释义/多义）

### 作为库
```python
from extractor import extract, write_sentences, write_hits
results = extract(essay_paths, 'data/单义短语_v12_regex.xlsx', 'data/多义短语_v10.xlsx')
# results: List[(Answer, List[MatchHit])]
write_sentences(results, 'sentences.xlsx')
write_hits(results, 'hits.xlsx')
```

## 正则表的再生成（改了短语表/生成器后）
单义表的"正则表达式"列由 `evp_regex_generator.process_file` 生成：
```python
from evp_regex_generator import process_file
process_file('data/单义短语_updated_v12.xlsx', 'data/单义短语_v12_regex.xlsx')
```

## 与消歧模块的边界
- 本模块输出的"抽取结果"中，`多义=是` 的命中即需送**消歧模块**判定义项；
- 抽取评测口径 = "短语在某句是否出现"（P/R/F1），义项对错由消歧模块单独评。

## 验证状态
- 抽取质量（30 篇分层标注集，逐句 phrase-occurrence 口径）：**Precision 89.7% / Recall 94.6% / F1 92.0%**。剩余 FP 多为义项边界类（交消歧）。
- 正则在 EVP 例句集上的召回：**92.2%**（`python test_regex_recall.py`）。
- 详见 `核查说明/MWED短语抽取_核查与修复总报告.md`。
