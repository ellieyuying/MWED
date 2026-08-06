"""
EVP 短语正则的特例规则表。

部分短语若走通用生成逻辑会过匹配或漏匹配，这里按短语文本命中触发式，
直接给出固定/半固定正则。规则按列表顺序匹配，命中即返回；未命中则回到
通用生成。match_special_case(phrase) 供 evp_regex_generator.phrase_to_regex
在通用生成前调用。

规则两种形态：
  声明式  (kind, 触发正则, 输出正则, 备注)
          kind ∈ full/prefix/search（对 phrase.strip() 匹配）、
                 search_raw（对原始 phrase 做 search，用于含斜杠列举的词条）
  函数式  callable(phrase) -> (正则, 备注) | None
          用于需要按短语内容动态构造正则的特例（枚举词提取等）
"""
import re
from evp_linguistic_data import DECADE_RE

_I = re.IGNORECASE
def _C(p):
    return re.compile(p, _I)


# ── 相似结构合并规则（decade phrases）────────────────────────
# 触发式匹配【预处理后】的短语（物主代词已归一为 your），命中即把
# teens…nineties 折为一条枚举正则。由 phrase_to_regex 的 Step 0 调用。
MERGE_PATTERNS = [
    (_C(r'^be in your ' + DECADE_RE + r'$'),
     r'(?i)\bbe\s+in\s+your\s+' + DECADE_RE + r'\b', 'decade合并'),
    (_C(r'^in your ' + DECADE_RE + r'$'),
     r'(?i)\bin\s+your\s+' + DECADE_RE + r'\b', 'decade合并'),
    (_C(r'^the ' + DECADE_RE + r'$'),
     r'(?i)\bthe\s+' + DECADE_RE + r'\b', 'decade合并'),
]


# ── 函数式特例：需动态构造正则 ────────────────────────────────
def _everything(phrase):
    # be/mean everything：everything 字面匹配，前面接 be 或 mean
    if re.search(r'\beverything\b', phrase, _I):
        core = re.sub(r'^be\s*/', '', phrase, flags=_I).strip()
        if re.match(r'^(\w+)', core):
            return (r'(?i)\b(?:be|is|are|was|were|am|mean|means|meant)\s+everything\b',
                    '特例-everything字面')
    return None


def _broken(phrase):
    # broken English/Spanish, etc.：broken 保持字面，后跟语言名词（枚举或通配）
    if re.match(r'^broken\s+', phrase.strip(), _I) and ('etc.' in phrase or '_adj_' in phrase):
        slash = re.findall(r'\b\w+(?:/\w+)+\b', phrase)
        lang = ('(?:' + '|'.join(re.escape(w) for w in slash[0].split('/')) + ')'
                if slash else r'[A-Z]\w+')
        return (rf'(?i)\bbroken\s+{lang}\b', '特例-broken语言字面')
    return None


def _speaking(phrase):
    # generally/personally, etc. speaking：副词枚举 + speaking 字面
    if re.search(r'speaking', phrase, _I) and ('etc.' in phrase or '_adv_' in phrase):
        slash = re.findall(r'\b\w+(?:/\w+)+\b', phrase)
        adv = ('(?:' + '|'.join(re.escape(w) for w in slash[0].split('/')) + ')'
               if slash else r'\w+')
        return (rf'(?i)\b{adv}\s+speaking\b', '特例-adv speaking字面')
    return None


# ── 特例表（顺序即匹配优先级）────────────────────────────────
SPECIAL_CASES = [
    # be something：保留字面，不走通配逻辑
    ('full',   _C(r'be\s+something'),          r'\bbe\s+something\b', '特例-字面匹配'),
    # used to：词形还原会把 used→use，学习者写的是 used to
    ('prefix', _C(r'used\s+to\b'),             r'(?i)\bused?\s+to\b', '特例-used to'),
    ('full',   _C(r'that\s+is\s+\(to\s+say\)'),
     r'(?i)\bthat\s+(?:is|was)\b(?:\s+to\s+say)?', '特例-that is to say'),
    ('full',   _C(r'or\s+something\s+\(like\s+that\)'),
     r'(?i)\bor\s+something(?:\s+like\s+that)?\b', '特例-or something'),
    ('full',   _C(r'something\s+like'),         r'(?i)\bsomething\s+like\b', '特例-something like字面'),
    ('full',   _C(r'something\s+of\s+a\s+sth'), r'(?i)\bsomething\s+of\s+a\b', '特例-something of a字面'),

    _everything,

    # be used to sb/sth/doing sth：used 保持字面，要求前面有 be 动词
    ('prefix', _C(r'be\s+used\s+to\b'),
     r'(?i)\b(?:be|is|are|was|were|am|been)\s+used\s+to\b', '特例-be used to字面'),
    ('full',   _C(r'be\s+coming\s+up'),
     r'(?i)\b(?:be|is|are|was|were|am|been)\s+coming\s+up\b', '特例-be coming up字面'),
    ('full',   _C(r'be\s+a\s+first'),
     r'(?i)\b(?:be|is|are|was|were|am)\s+a\s+first\b', '特例-be a first'),
    ('full',   _C(r'be\s+up\s+to\s+sb'),
     r'(?i)\b(?:be|is|are|was|were|am)\s+up\s+to\b', '特例-be up to字面'),

    # do up sth / do sth up
    ('full',   _C(r'do\s+up'),         r'(?i)\bdo\s+up\b', '特例-do up字面'),
    ('full',   _C(r'do\s+up\s+sth'),   r'(?i)\bdo\s+up\s+\w+(?:\s+\w+){0,2}\b', '特例-do up sth'),
    ('full',   _C(r'do\s+sth\s+up'),   r'(?i)\bdo\s+\w+(?:\s+\w+){0,2}\s+up\b', '特例-do sth up'),

    # class sb/sth as sth：class + sth + as 在5词内
    ('prefix', _C(r'class\s+'),        r'(?i)\bclass\s+\w+(?:\s+\w+){0,3}\s+as\b', '特例-class...as'),

    # take in sth / take sth in
    ('full',   _C(r'take\s+in'),       r'(?i)\btake\s+in\b', '特例-take in字面'),
    ('full',   _C(r'take\s+in\s+sth'), r'(?i)\btake\s+in\s+\w+(?:\s+\w+){0,2}\b', '特例-take in sth'),
    ('full',   _C(r'take\s+sth\s+in'), r'(?i)\btake\s+\w+(?:\s+\w+){0,2}\s+in\b', '特例-take sth in'),

    ('full',   _C(r'of\s+course\s+not'), r'(?i)\bof\s+course\s+not\b', '特例-of course not字面'),
    ('full',   _C(r'kind\s+of'),         r'(?i)\bkind\s+of\b', '特例-kind of字面'),

    # a hand / a touch：冠词可选会撞 on the other hand / touch pads，固定两词
    ('full',   _C(r'a\s+hand'),        r'(?i)\ba\s+hand\b', '特例-a hand字面'),
    ('full',   _C(r'a\s+touch'),       r'(?i)\ba\s+touch\b', '特例-a touch字面'),

    # as ... as：省略号默认跨10词会连起两个不相关 as，收紧为中间 ≤4 词；
    # 并排除 as far/long/soon/well as（是"就…而言/只要/一…就/以及"等固定搭配，
    # 非比较级 as X as），否则会误命中 "as far as sb is concerned" 等。
    ('full',   _C(r'as\s+\.\.\.\s+as'),
     r'(?i)\bas\s+(?!(?:far|long|soon|well)\b)\w+(?:\s+\w+){0,3}\s+as\b',
     '特例-as...as限4词'),

    # for all（"尽管"义）：排除字面"为所有…of/复数"
    ('full',   _C(r'for\s+all'),
     r'(?i)\bfor\s+all\b(?!\s+(?:of\b|the\b|_sb_\b|you\b|\w+s\b))', '特例-for all尽管义'),

    # have sth on（"穿着"义）：排除 on 后的时间词，不排除宾语冠词
    ('full',   _C(r'have\s+sth\s+on'),
     r'(?i)\bhave\s+\w+(?:\s+\w+)?\s+on\b'
     r'(?!\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|'
     r'day|days|week|weeks|month|months|morning|afternoon|evening|night|'
     r'time|the\s+\w+day)\b)', '特例-have sth on穿着义'),

    ('full',   _C(r'not\s+a'),   r'(?i)\bnot\s+a\b', '特例-not a字面'),
    ('full',   _C(r'not\s+one'), r'(?i)\bnot\s+one\b', '特例-not one字面'),

    # from ... to ...：中间最多2词
    ('full',   _C(r'from\s+\.\.\.\s+to\s+\.\.\.'),
     r'(?i)\bfrom\s+\w+(?:\s+\w+)?\s+to\b', '特例-from...to...限2词'),

    _broken,
    _speaking,
    # go badly/well, etc.：由 Step 0c 枚举展开处理，此处无规则

    # love/(with) love from...：只精确匹配含 love 的完整变体
    ('full',   _C(r'love\s+from'),        r'(?i)\blove\s+from\b', '特例-love from字面'),
    ('full',   _C(r'with\s+love\s+from'), r'(?i)\bwith\s+love\s+from\b', '特例-with love from字面'),
    ('full',   _C(r'all\s+my\s+love'),    r'(?i)\ball\s+(?:my|your)\s+love\b', '特例-all my love字面'),
    ('full',   _C(r'lots\s+of\s+love'),   r'(?i)\blots\s+of\s+love\b', '特例-lots of love字面'),

    # look on/upon sb/sth as sth
    ('full',   _C(r'look\s+on'),
     r'(?i)\blook\s+on(?:\s+\w+(?:\s+\w+){0,3}\s+as)?\b', '特例-look on..as'),
    ('prefix', _C(r'look\s+on(?:\s+sth|\s+sb)?$'),
     r'(?i)\blook\s+on(?:to)?\s+\w+(?:\s+\w+){0,3}\s+as\b', '特例-look on sth as'),
    ('prefix', _C(r'look\s+upon'),
     r'(?i)\blook\s+upon\s+\w+(?:\s+\w+){0,3}\s+as\b', '特例-look upon sth as'),

    # place sth in/on, etc.：look-behind 须定宽，拆成 a\s/an\s/the\s
    ('full',   _C(r'place\s+in'),
     r'(?i)(?<!a\s)(?<!an\s)(?<!the\s)\bplace\s+in\b', '特例-place in字面'),
    ('full',   _C(r'place\s+in\s+sth'),
     r'(?i)\bplace\s+in\s+\w+(?:\s+\w+){0,2}\b', '特例-place in sth'),
    ('full',   _C(r'place\s+on'),
     r'(?i)(?<!a\s)(?<!an\s)(?<!the\s)\bplace\s+on\b', '特例-place on字面'),
    ('full',   _C(r'place\s+on\s+sth'),
     r'(?i)\bplace\s+on\s+\w+(?:\s+\w+){0,2}\b', '特例-place on sth'),
    ('full',   _C(r'place\s+sth\s+in'),
     r'(?i)\bplace\s+\w+(?:\s+\w+){0,2}\s+in\b', '特例-place sth in'),
    ('full',   _C(r'place\s+sth\s+on'),
     r'(?i)\bplace\s+\w+(?:\s+\w+){0,2}\s+on\b', '特例-place sth on'),

    # be a bad/good influence (on sb)
    ('prefix', _C(r'(?:be\s+a\s+)?(?:bad|good)\s+influence'),
     r'(?i)\b(?:bad|good)\s+influence\b', '特例-bad/good influence'),
    ('search', _C(r'influence\s+on'),
     r'(?i)\b(?:bad|good)\s+influence\s+on\b', '特例-influence on'),

    # 含斜杠列举的固定搭配（对原始 phrase 做 search）
    ('search_raw', _C(r'army/prison'),
     r'(?i)\b(?:an?\s+)?(?:army|prison|refugee|internment|labor|labour|'
     r'concentration|detention|training|holiday|summer|boot)\s+camps?\b', '特例-army camp枚举'),
    ('search_raw', _C(r'committee/panel'),
     r'(?i)\bon\s+(?:a|an|the)\s+'
     r'(?:committee|panel|board|council|jury|team|staff|faculty|tribunal)\b', '特例-committee枚举'),
    ('search_raw', _C(r'all\s+the\s+better/easier/more'),
     r'(?i)\ball\s+the\s+'
     r'(?:better|easier|more|worse|harder|faster|stronger|sooner|less)\b', '特例-all the better枚举'),

    # somewhere around/between：swh 展开过宽，限为数字/量词前缀或 somewhere 字面
    ('full',   _C(r'somewhere\s+around'),
     r'(?i)\b(?:somewhere\s+around|(?:\d+(?:\.\d+)?|a\s+few|about)\s+around)\b', '特例-somewhere around'),
    ('full',   _C(r'somewhere\s+between'),
     r'(?i)\b(?:somewhere\s+between|(?:\d+|a\s+few|about)\s+between)\b', '特例-somewhere between'),

    # serve a (purpose) / serve the purpose：补上 purpose 才精确
    ('full',   _C(r'serve\s+a'),
     r'(?i)\bserve\s+(?:a|an|the)(?:\s+\w+){0,2}\s+purposes?\b', '特例-serve a purpose'),
    ('full',   _C(r'serve\s+the\s+purpose'),
     r'(?i)\bserve\s+(?:a|an|the)(?:\s+\w+){0,2}\s+purposes?\b', '特例-serve the purpose'),
]


def match_special_case(phrase):
    """命中特例返回 (正则, 备注)，否则 None。按 SPECIAL_CASES 顺序匹配。"""
    stripped = phrase.strip()
    for rule in SPECIAL_CASES:
        if callable(rule):
            res = rule(phrase)
        else:
            kind, rx, out, note = rule
            target = phrase if kind == 'search_raw' else stripped
            fn = rx.fullmatch if kind == 'full' else (rx.match if kind == 'prefix' else rx.search)
            res = (out, note) if fn(target) else None
        if res is not None:
            return res
    return None
