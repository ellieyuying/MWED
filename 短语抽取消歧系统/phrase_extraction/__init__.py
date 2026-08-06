"""EVP 短语抽取模块（独立封装版）。

公开 API：
    from phrase_extraction import extract, load_patterns, FixedPreprocessor
    results = extract(essay_paths, unambig_regex_xlsx, ambig_xlsx)

只做抽取（解析→归一化→正则匹配→抽取结果），不含 LLM 消歧。
"""
from extractor import (
    extract, load_patterns, match_answer, parse_clc_xml,
    FixedPreprocessor, Answer, PhrasePattern, MatchHit,
    write_sentences, write_hits,
)

__all__ = [
    'extract', 'load_patterns', 'match_answer', 'parse_clc_xml',
    'FixedPreprocessor', 'Answer', 'PhrasePattern', 'MatchHit',
    'write_sentences', 'write_hits',
]
