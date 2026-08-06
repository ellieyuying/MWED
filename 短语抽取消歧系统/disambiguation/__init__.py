"""EVP 多义短语消歧模块（独立封装版）。

    from disambiguator import disambiguate, disambiguate_hits

只做消歧（LLM 判义项），不做抽取。与抽取模块 phrase_extraction 通过
MatchHit / 通用实例衔接成流水线。API key 走环境变量 DASHSCOPE_API_KEY。
"""
from disambiguator import (
    disambiguate, disambiguate_hits,
    SYSTEM_PROMPT, MODEL, API_BASE,
)

__all__ = ['disambiguate', 'disambiguate_hits', 'SYSTEM_PROMPT', 'MODEL', 'API_BASE']
