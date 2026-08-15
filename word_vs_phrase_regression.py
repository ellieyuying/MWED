#!/usr/bin/env python3
"""
词级 vs 短语级 CEFR 指标 —— 层次回归（看短语指标的增量价值）
=============================================================
词级指标：用 cefr-lexical-sophistication 的 target_level.data（词→最低CEFR级，
          论文 "Min" 模式，无需 BERT WSD），对每篇作文算内容词的等级分布指标。
短语级指标：读 compute_phrase_indices 产出的 phrase_indices_v12.csv。
层次回归：Model1(词块) → Model2(词+短语块)，报 ΔR² + F 检验。

注：Min 模式是论文自带模式之一，不含义项消歧；作为 BERT-free 的词级基线，
    用于评估"短语级指标在词级之上是否有增量解释力"。
"""
import sys, os, csv, pickle
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.stats import f as fdist

sys.path.insert(0, str(Path(__file__).parent / 'phrase_extraction'))
import extractor as EX
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer

DICT = r"D:\projects\cefr-lexical-sophistication\dict\target_level.data"
LEVEL_SCORE = {'A1':1,'A2':2,'B1':3,'B2':4,'C1':5,'C2':6}
_lem = WordNetLemmatizer(); _tok = TreebankWordTokenizer()

def _wn(tag):
    return {'N':'n','V':'v','J':'a','R':'r'}.get(tag[:1])

import re as _re
def classify_genre(paragraphs):
    """按作文内容判体裁（对齐 FCE 作文集类型与主题调查的启发式）。"""
    full = '\n'.join(paragraphs)
    tl = full.lower(); head = full[:400].lower()
    if ('dear' in head or 'yours faithfully' in tl or 'yours sincerely' in tl
            or 'best wishes' in tl or 'yours truly' in tl):
        return '书信'
    if (head.strip().startswith('report') or ('introduction' in head and 'conclusion' in tl)
            or _re.search(r'\bto:\b|\bsubject:\b', head)):
        return '报告'
    if _re.search(r'\bonce\b|\bsuddenly\b|that day|last (summer|year|week|night)|when i was',
                  head) and ' i ' in head:
        return '记叙'
    return '议论·文章'

def word_indices_for_essay(paragraphs, level_dict):
    """内容词 → min 级；返回词级指标 dict 或 None。"""
    levels = []
    for para in paragraphs:
        toks = _tok.tokenize(para.lower())
        for w, t in pos_tag(toks):
            wn = _wn(t)
            if wn is None:            # 只要内容词(名/动/形/副)
                continue
            lemma = _lem.lemmatize(w, wn)
            e = level_dict.get(lemma) or level_dict.get(w)
            if e and e.get('min') in LEVEL_SCORE:
                levels.append(e['min'])
    tot = len(levels)
    if tot < 5:
        return None
    c = Counter(levels); n = lambda k: c.get(k,0); r = lambda x: x/tot
    nA=n('A1')+n('A2'); nB=n('B1')+n('B2'); nC=n('C1')+n('C2')
    sc=[LEVEL_SCORE[x] for x in levels]
    return {
        'W_ratio_A1': r(n('A1')), 'W_ratio_A': r(nA), 'W_ratio_B': r(nB), 'W_ratio_C': r(nC),
        'W_ratio_AboveB1': r(nB+nC), 'W_mean_score': float(np.mean(sc)), 'W_n': tot,
    }

def load_phrase_csv(path):
    out={}
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            out[row['essay_id']] = row
    return out

def ols_r2(X, y):
    """加截距最小二乘, 返回 R²。"""
    X1 = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    pred = X1 @ beta
    ss_res = np.sum((y-pred)**2); ss_tot = np.sum((y-np.mean(y))**2)
    return 1 - ss_res/ss_tot

def main():
    print('加载词级词典 ...')
    level_dict = pickle.load(open(DICT,'rb'))
    print('解析作文 + 算词级指标 ...')
    ESSAY = r"D:\projects\MWED\fce-released-dataset\fce-released-dataset\clean_data"
    word_idx = {}; scores = {}; genre = {}
    import glob
    for xml in glob.glob(os.path.join(ESSAY,'**','*.xml'), recursive=True):
        try: answers = EX.parse_clc_xml(xml)
        except: continue
        for a in answers:
            wi = word_indices_for_essay(a.paragraphs, level_dict)
            if wi and a.total_score:
                word_idx[a.essay_id] = wi; scores[a.essay_id] = float(a.total_score)
                genre[a.essay_id] = classify_genre(a.paragraphs)
    print(f'  词级有效作文: {len(word_idx)}')

    ph = load_phrase_csv(str(Path(__file__).parent / '结果_v12' / 'phrase_indices_v12.csv'))
    common = [e for e in word_idx if e in ph and scores.get(e,0)>0]
    print(f'  词级∩短语级∩已评分: {len(common)}')

    y = np.array([scores[e] for e in common])
    # 词块预测子(低共线): 词均分 + A1比例
    Wcols = ['W_mean_score','W_ratio_A1']
    Xw = np.array([[word_idx[e][c] for c in Wcols] for e in common])
    # 短语块预测子: 短语均分 + A1比例 + 短语动词比例
    Pcols = ['PH_mean_score','PH_ratio_A1','PH_pv_ratio']
    Xp = np.array([[float(ph[e][c]) for c in Pcols] for e in common])

    def hier(sub_idx, label):
        yy = y[sub_idx]; Xww = Xw[sub_idx]; Xpp = Xp[sub_idx]
        if len(yy) < 30 or np.std(yy) == 0:
            print(f'  [{label}] n={len(yy)} 太小，跳过'); return
        r2w = ols_r2(Xww, yy); r2wp = ols_r2(np.column_stack([Xww, Xpp]), yy)
        d = r2wp - r2w; nn=len(yy); ka=Xpp.shape[1]; kf=Xww.shape[1]+Xpp.shape[1]
        F = (d/ka)/((1-r2wp)/(nn-kf-1)); pp = 1 - fdist.cdf(F, ka, nn-kf-1)
        sig = 'sig' if pp < .05 else 'ns'
        print(f'  [{label:22}] n={nn:4d} | R²词={r2w:.4f}  R²词+短语={r2wp:.4f}  '
              f'ΔR²={d:+.4f}  p={pp:.4g} {sig}  (仅短语R²={ols_r2(Xpp,yy):.4f})')

    print('\n============ 层次回归：总体 + 分体裁(按内容判定) ============')
    print(f'词块={Wcols} | 短语块={Pcols}\n')
    idx_all = np.arange(len(common))
    hier(idx_all, '总体')
    # 分体裁(内容启发式，对齐 FCE 作文集调查)
    gs = [genre[c] for c in common]
    from collections import Counter as _C
    print('  体裁分布:', dict(_C(gs)), '\n')
    for g in ['书信','议论·文章','记叙','报告']:
        sub = np.array([i for i,gg in enumerate(gs) if gg==g])
        if len(sub): hier(sub, g)

    # 存词级指标 csv
    wpath = str(Path(__file__).parent / '结果_v12' / 'word_indices_v12.csv')
    with open(wpath,'w',newline='',encoding='utf-8-sig') as f:
        cols=['essay_id','total_score']+list(word_idx[common[0]].keys())
        w=csv.writer(f); w.writerow(cols)
        for e in common: w.writerow([e,scores[e]]+[word_idx[e][c] for c in word_idx[e]])
    print(f'\n[保存] 词级指标 → {wpath}')

if __name__ == '__main__':
    main()
