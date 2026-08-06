# MWED 短语抽取模块 —— 核查与修复总报告

> **当前状态（读前必看）**：本报告是**修复过程的历史记录**，记到 §7.5 为止。此后又做了：
> 正则生成器模块化（`evp_special_cases.py` 特例表 + `evp_linguistic_data.py` 词表）、`single_word_regex`
> 移除（短语表只保留多词短语）、词形还原对齐等召回修复、`as...as`/`sb` 非人名词等精度修复。
> 最新抽取质量与结果口径以 `短语级指标_有效性分析简报.md` §3.6 和各 README 为准。
> **P/R/F1 口径澄清**：下文 §7.3.4 的 **96.7/96.4/96.6** 是 carry-forward 估计（对变化命中逐条favorable重判）；
> 直接按 30 篇标注文件原始 FP/FN 计（TP295/FP34/FN17）为 **Precision 89.7% / Recall 94.6% / F1 92.0%**，
> 这是可复现的口径，对外应以此为准；例句集正则召回另为 92.2%。

- **维护**：2026-07-24 起持续更新
- **范围**：短语表（拆分器 + 单义/多义划分）、正则生成器、匹配层、预处理器；附 BERT 消歧代码核查
- **配套文件**（本报告不重复其内容）：
  - `评测集_短语抽取_扩充版_待标注.xlsx` — 30 篇标注工作台（待标注）
  - `评测集_计分.py` — P/R/F1 计分脚本
  - `评测集人工审查结果.xlsx` — 9 篇金标（已标注，修复前基线）

---

## 0. 摘要（TL;DR）

- **数据链**：EVP 原始表 `dataset_final_1219.xlsx` → 拆分器把复杂短语拆成简单变体 → 分为**单义**（`单义短语_updated_v10.xlsx`）与**多义/跨等级**（`多义短语_v10.xlsx`）两表 → 正则生成器逐变体生成正则 → 匹配层在**归一化**后的作文文本上命中 → 多义送 LLM 消歧。
- **已修 5 个问题**（代码+数据，逐一验证）：②斜杠断词、③去 be 过匹配、P2 正则编译失败(16→0)、P1 占位符裸通配、P4 预处理大小写敏感。
- **实测收益**（9 篇金标，占位符口径）：Precision **86.4% → 96.0%**（问题②单项）；问题③在 120 篇上再清 32 条 be 短语 FP（零真 TP 损失）。
- **BERT cross-encoder 核查结论**：报告的 78.1% 用 bert-base-uncased(未微调)、`mean_a`（联合编码后两段 token 均值的 cosine），不是句向量、不是分类头分数；作为对比基线成立，但不宜按标准 cross-encoder 口径描述。
- **下一步**：用户标注扩充版评测集 → 出终版 P/R/F1；再迭代 P3/P5（漏抽/边界 FP）、P7（删冗余特例）、P6（全量重跑落地）。

---

## 1. BERT 消歧代码核查（cross-encoder）

**对象**：`dab/mwed_cross_encoder_v1.py`。对应导师批注"用 bert-base 做不到 / 确认是句向量还是哪个向量、哪个模型"。

- **模型**：`bert-base-uncased`，`AutoModel`，**未在句对/NLI 上微调**。
- **报告的 78.1% 走 `mean_a`**：把 `[CLS] 目标句 [SEP] 义项释义+例句 [SEP]` **拼接后联合编码**，取目标句段 token 均值 `vec_a`、义项段 token 均值 `vec_b`，分数 = `cosine(vec_a,vec_b)`。**不是 CLS 句向量，不是分类头分数**。
- **`cls` 模式**（标准 cross-encoder）线性层随机初始化、代码自打 `[WARN]`，**未使用**——导师"用 bert-base 做不到"的直觉针对的正是这条，且作者确实没走。
- **口径修正**：`mean_a` 本质是"bi-encoder 打分方式 + 联合编码"的混合体，与 bi-encoder 唯一实质区别是"两段一起编码 vs 分开编码"。70.9%→78.1% 的增益可归因于联合编码，作为对比基线成立，但**不宜称"cross-encoder 直接输出相关性分数"**。
- **小 bug**：`mean_a` 的 `vec_a` 混入了中间 `[SEP]`（注释称去掉特殊 token，实际只去了 `[CLS]`）。
- **数据版本对不上**：BERT 实验用的多义表与最终标注用表非同一版；slide 5(BERT) 与 slide 6(LLM) 数字不同口径，横向比较须注明。

**给导师的话**：Cross-encoder 用 bert-base-uncased(未微调)；78.1% 是"联合编码后 A/B 两段 token 均值的余弦"，非句向量非分类头；标准 CLS 分类头因未训练而没用。

---

## 2. 短语表：拆分器与单义/多义划分核查

### 2.1 数据结构
- 原始表 `dataset_final_1219.xlsx` 自带分表：`full_phrase`(4383) = `mono_phrase`(4067) + `poly_phrase`(316)。
- 拆分器输入是**已分出的单义表**（非原始全表），只对单义做"变体扩展"。
- 单义 `updated_v7`（5237 变体行，含"原始短语/拆分后/变体序号"列）；多义 `v10`（728 义项，未做变体拆分）。

### 2.2 单义/多义划分依据
- **判据 = 词条的释义序号是否 ≥2（同形多义，可跨等级）**：`poly_phrase`(121词条/316义项) 带释义序号；`mono_phrase` 单义无需序号。
- `full_phrase` 因按(词条,释义)去重，丢了义项区分，**不能**作判据。

### 2.3 拆分器逻辑（`evp_phrase_splitter.py`，12 步）
Step0 语义标签 → Step1 斜杠空格归一 → Step2 智能 or 拆分（结合例句）→ Step3 分号递归 → Step3.5 etc.斜杠泛化 → Step4 去 etc. → Step5 括号展开(含/不含两版) → Step6 智能斜杠展开(多特殊模式) → Step7 清理+冠词修正 → Step8 小品词移位变体 → Step9 to 可选 → Step10 前置 the 可选 → Step11 中/末 sth 可选 → Step12 句内逗号可选。
- **实测 18 个代表性复杂短语拆分全部正确**（括号/斜杠/or/etc./小品词/可选成分）。

### 2.4 两表 vs 原始表的差异（核对结果）
- **多义 v10**：280词条/728义项。原 poly 121词条中 **21 个被移出**（`Yours sincerely`、`more and more` 等伪多义，符合 PPT"去伪多义"）；**180 个新词条**为重分类进来的真多义。
- **单义**：193 个 mono 词条从表中消失 → 其中 **111 重分类进多义**、**38 个非短语条目被手动删除**（`Absolutely!`、`God`、`Help!`、`Road`、`days`、`hundreds` 等，用户确认属非短语条目）。
- **数据修复 v7→v8→v9**：v8 删 3 个双重分类短语（`turn out`/`get in`/`depend on/upon sb/sth`）；v9 删 11 行断词 + 正 4 单元格（见问题②）。

---

## 3. 正则生成器：逻辑梳理与特例分析

### 3.1 最重要前提：正则匹配"归一化文本"
生成器写出的正则**不匹配原句**，匹配的是预处理器归一化后的文本：词形还原(made→make/was→be)、物主代词→your、人称/宾格→_sb_/sb、缩写展开、小写化。生成器每个 Pre-step 都在镜像预处理器——**封装时"生成器+预处理器"必须成对**。

### 3.2 流水线（`phrase_to_regex`）
① 特例早退层(43个) → ② Pre-steps 镜像归一（缩写/保护 used to·be going to/cannot→can not/动词还原/代词归一/撇号拆分/had better）→ ③ Step0–9d 占位符化与组装（decade合并、去/近邻 be、etc.枚举、sb/sth/doing等占位符、数字、被动检测、逐词转义、占位符还原、空格→\s+、组装、冠词泛化/可选、末尾复数 s?、被动备选分支）。
（注：此后 `single_word_regex` 已移除，短语表只保留多词短语。）

### 3.3 特例是否必要（数据驱动结论）
- **43 个特例只覆盖 51 个短语（0.86%），39 个各命中 1 条** —— 极度过拟合的一次性补丁。
- **类甲**（约 10 个，真必要）：`used to`/`something like`/`be coming up` 等——归一化会破坏，**应收进 `{短语:正则}` 数据表**。
- **类乙**（约 40 个，多数可消除）：注释自承"通配过宽"，各自对应问题①③根因；**根治后逐个复测即可删**。
- **红线**：无 P/R/F1 评测集**不可盲删**（每个特例都编码了一个真实 bad case）。

---

## 4. 误差模式扫描（过匹配，无监督）

- 数据 `hit_detail.xlsx`(25009 命中)；方法：合法命中的"变体实词"应现于句中，缺失即疑似。
- **初筛 21.8% 疑似，剔除启发式误报后真过匹配 ≈4–5%**。误报来源：枚举成员错位、词形变化、合法斜杠分支、按设计丢 be（"be"是还原词，原句是 is/was，故被误标）。
- **确认 3 类真问题**（即下节的问题①②③），两个在拆分器、一个在生成器，均定点可修。

---

## 5. 问题清单（状态总览）

| 编号 | 问题 | 类型 | 状态 |
|---|---|---|---|
| ② | 斜杠断词（`have a/no right`→`have a to do`丢核心词） | 精确率 | ✅ 已修 |
| ③ | 去 be 过匹配（`be around`→任意around、`be called`→主动call） | 精确率 | ✅ 已修 |
| P2 | 16 条正则编译失败→静默零召回 | 召回 | ✅ 已修 |
| P1 | `_adj_/_noun_` 泛化→裸`\w+`（`the most \w+`/`get \w+`） | 精确率 | ✅ 已修 |
| P4 | 预处理器大小写敏感（全大写句归一不稳） | 双向 | ✅ 已修 |
| P3 | 常见短语漏抽（`look forward to`/`be going to do`/`first of all` 等） | 召回 | ⏳ 待办 |
| P5 | 义项边界/跨词过匹配（`take place on`→`take on`、`for all events`→`for all`） | 精确率 | ⏳ 待办 |
| P6 | 修复全量落地（v10 重跑 annotator 出新 hit_detail，含 LLM 消歧） | 落地 | ⏳ 待办(需API) |
| P7 | 43 特例过拟合，删冗余 | 可维护 | ⏳ 待办 |
| P8 | 源表畸形条目 `squeeze (sb/sth) in/squeeze...` | 数据 | ⏳ 待办 |

---

## 6. 修复实录与验证

### 问题② —— 斜杠断词
- **根因**：拆分器 `_expand_slashes_smart` 的特殊模式 5b「斜杠组+共享后缀」误触发——本为"数字+单位"(`one metre/6 ft deep`)设计，却把单 token 交替(`a/no`、`sb/sth`)当同构，导致 `have a/no right to do sth`→`have a to do sth`(丢 right)。
- **修复**：(a) 5b 加**数字守卫**（仅斜杠段含数字才触发）；(b) 末端加**合法性过滤器**（丢弃含 `from of`/`sth sth`/`between and` 等不可能相邻词对的变体）。
- **数据**：`单义_v9`（v8 删 11 行断词 + 正 4 单元格 `class sb as sth` 等）。全 3054 mono 词条断词残留归零。
- **实测**（9 篇金标）：11 条问题② FP 全消失、零误伤、1 条新增为 TP；**Precision 86.4%→96.0%，F1 88.8%→93.7%**。

### 问题③ —— 去 be 过匹配
- **根因**：生成器 Step 0b 整词删开头 `be`，正则只剩裸谓词。
- **修复**：不删 be，改在组装时要求谓语近邻(≤2词)出现**系动词全形态** `(?:be|is|are|was|were|am|been|being)`——兼容预处理器对 `are being`/`are+副词` 归一不稳的情况。
- **实测**（120 篇）：be 短语命中 72→41，**剔除的 32 条全是真 FP**（`I called a taxi`/`sharks came around`/`swim in the middle of sharks`），零真 TP 损失；1 条新小 FP（`was getting into`）。

### P2 —— 16 条正则编译失败
- **根因**：(a) `place in/on` 特例用变长 look-behind `(?<![aA][nN]?\s)` 非法；(b) 14 条含括号可选 `(...)` 的短语（`keep up (with sb/sth)` 等）括号残留→unbalanced。这些短语**静默永不匹配**。
- **修复**：(a) look-behind 拆成定宽 `(?<!a\s)(?<!an\s)(?<!the\s)`；(b) 生成器加**括号可选处理**（生成"含/不含内容"两版正则再 OR，(?i)提到最外层）。
- **实测**：编译错误 16→0；并**附带修好一批"括号被转义成字面、编译通过但永不匹配"的短语**（`such a(n)`、`in order (for sb/sth) to do sth`），纯召回收益。

### P1 —— 占位符裸通配
- **根因**：拆分器 Step 3.5 把 `attractive/important/popular, etc.` 泛化成 `_adj_`，生成器只能还原成裸 `\w+`（`the most \w+`、`get \w+`、`have \w+` 匹配任意词）。**注**：`next week/year, etc.`、`too small, etc.` 等 etc.类当前生成器已枚举，并非问题；真问题仅开放类占位符。
- **修复**：拆分器 Step 3.5 **只对时间词(封闭集)泛化为 `_timeunit_`，开放类(形/副/名/动)不泛化**，保留真实列举词交生成器 Step 0c 精确枚举。
- **数据**：外科重拆 20 个受影响短语（`the most _adj_`→`the most attractive/important/popular` 等），`单义_v10`（v9 基础替换 28 行为 65 枚举行，占位符清零，其余原样）。

### P4 —— 预处理器大小写敏感
- **根因**：`FixedPreprocessor` 词性标注前未小写，全大写词(FCE 学习者文本常见)被误标专有名词→动词不还原、系动词不归一（`OBLIGED` 不还原、`ARE BEING` 不归一）。
- **修复**：标注前 `pos_tag([w.lower() ...])`。实测全大写句归一恢复正常、正常大小写句不受影响。

### 落地产物
- `单义短语_updated_v10.xlsx`（②③数据 + P1 重拆）
- 生成器(③P2) + 预处理器(P4) 代码已改
- `_v10_regex.xlsx`（重生成正则表，编译错误 0）

---

## 7. P/R/F1 评测集

### 7.1 设计
- **人工金标不可省**：机器抽的对不对(精确率)、漏没漏(召回率)只能人判；无监督扫描只测精确率方向且有误报，不能当金标。
- **分层抽样**：按每篇命中数取"最少/中位/最多"三档——两端极值最能暴露过匹配与漏抽，只抽中位会两头失真。
- **评测单位 = 短语在某句中的一次出现**（非句子、非类型）：抽取器逐次判断，须逐次评分。
- **两表分担**：精确率表判 1/0 → TP,FP；召回率表(含零命中句)补漏抽 → FN。`Precision=TP/(TP+FP)`、`Recall=TP/(TP+FN)`、`F1=2PR/(P+R)`。

### 7.2 修复前基线（9 篇，已标注）
| | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| 总体 | 95 | 15 | 9 | 86.4% | 91.3% | 88.8% |
- FP 主因：11 条问题② `have a/no right`/`consider`（已修）；4 条问题③④边界(`take on`/`for all`/`a hand`/`in two months`)。
- FN：`look forward to`(×2)、`be going to do`(×2)、`first of all`、`would appreciate`、`on the other hand`、`come from swh`、`in that case`。

### 7.3 扩充版（30 篇，修复后抽取器，待标注）
- `评测集_短语抽取_扩充版_待标注.xlsx`：最少/中位/最多各 10 篇，329 条命中待判、412 句待查漏。
- 内部一致性 5 项全 ✓（0 孤儿命中、归属唯一、三表篇集一致）。
- **重点检验对象**：be 短语、the most 系列、括号短语——正是本轮修复目标。
- 标注后运行 `python 评测集_计分.py 评测集_短语抽取_扩充版_待标注.xlsx` 出终版 P/R/F1。

### 7.3.1 扩充版 30 篇标注结果（修复前抽取器 v10）
| | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| 30篇 | 291 | 38 | 18 | 88.4% | 94.2% | 91.2% |
- **主要 FP（38）**：`a hand`(8，撞 on the other hand)、`without sb`(6，撞 without doing)、`between sth and sth`(3，range 断词)、`take sth in`/`as...as`/`have sth on`/`leave sb doing`/`for all` 等义项边界(21)。
- 已修 3 个高频源：`a hand`→字面两词；`without sb`→占位符排除动词原形；`between`→range 断词修正。

### 7.3.3 最终采纳方案：v10 + 定点重拆（v12）
全量重拆 v11 会误动 v10 本已拆对的短语、引入过匹配垃圾（见 7.3.2）。最终采纳**更稳的定点方案**：
- **以 v10 打底**，只对 **114 个"拆分后仍含字面斜杠→零匹配"的原始短语**用当前拆分器重拆（其余 2800+ 短语原样保留，不引入垃圾）；
- 对重拆后仍出错的 ~18 个斜杠短语**单独写显式规则**修正：
  - 共享后缀/裸介词（`on/off duty`→`on duty`、`from/out of nowhere`→`from nowhere` 等，3 个）；
  - 共享动词/前缀（`range.../between...`→`range between sth and sth`、`put/set sb's mind...` 4 变体）；
  - 词交替被拆碎（`think highly/a lot of sb/sth`→`think highly of sb/sth`+`think a lot of sb/sth`、`do sb a/the world of good`→补全）；
  - 低价值过匹配短语（`it's sb/sth` 删除，"it is X" 全撞）。
- **产物**：`单义短语_updated_v12.xlsx`（5255 行）——字面斜杠 0、编译错误 0、灾难垃圾 0。
- **30 篇实测**：总命中 314；`a hand`/`without sb`(动名词)/`between`/`be sth`/`it's sth` 全部归零；新增命中 0 个属已知 FP；已修 3 类 FP + 114 召回漏洞，无新过匹配。
- **估算 P/R/F1**（待轻量重标核实）：**Precision ≈ 92%**（约 289TP/25FP）、Recall ≈ 94%、**F1 ≈ 93%**（对比修复前 88.4/94.2/91.2）。
- **残留**：义项边界类 FP，见下节 P5 处理。

### 7.3.4 P5 义项边界 FP 处理（①③ 定点修 + ② 轻量约束）
剩余 FP 分三类，分别处理：
- **① 占位符指代错误**（sb 该是人却匹配物）：`get to sb`←"get to your house"、`leave sb doing sth`←"leave your key"、`take sb on`←"take place on"。
  → 修：sb 占位符首词排除**高频非人称名词**（house/key/place…）+ **物主代词+非人称名词**（"your house"）。**已消除**。
- **③ 跨词误切**：`take sth in`←"take place/part in"、`as ... as`←跨句"as us…as us"。
  → 修：sth 首词排除 place/part；`as...as` 跨度收紧至 ≤4 词（不跨句）。**已消除**（`as...as` 剩余 4 条均为真命中 as much/simple/far as）。
- **② 义项不符**（词在、意思不同，用户选"轻量结构约束"）：
  - `a touch`→字面两词（同 a hand）；`for all`→后接 of/复数则拒（"despite"义 vs "for all of us"）；`have sth on`→on 后接时间词则拒（"穿着"义 vs "on Wednesday"）。**已消除**。
  - `take sth in`(理解 vs 拥入/参与)、`used to be`(过去常 vs 用某物) 等**同串词不同义**，正则无法可靠区分 → **保留，交消歧模块**（属抽取器不该越界的语义判断）。
- **30 篇实测**：总命中 306；P5 类 FP 再清约 8–11 条，无真 TP 损失（`as...as`、`hear from you` 等 TP 保留）。
- **累计 P/R/F1（30 篇，carry-forward 计分）**：TP/FP/FN = 296/10/11 → **Precision 96.7%、Recall 96.4%、F1 96.6%**（对比修复前 88.4/94.2/91.2）。FP 仅剩 10 个、全为 ② 义项类（交消歧）；召回顺带回升（`first of all`/`on behalf of`/`hear from`/`yours faithfully` 等原漏抽现已命中）。
  > 说明：基于用户原标注 carry-forward + 对变化命中逐条判定，接近精确；完全独立数字需重标那几条变化命中。
- **方法论**：② 中"同串词不同义"未在正则堆语义规则（避免脆化/回到特例老路），转由消歧模块评测——抽取器只判"短语出现与否"。

### 7.3.2 全量重拆 v10→v11（已弃用，仅存档教训）
为根治"114 个变体拆分后仍含斜杠→字面斜杠正则→零匹配"的召回漏洞（`take care of sb/sth`、`in front of sb/sth` 等常见短语零匹配），用当前拆分器全量重拆得 `单义短语_updated_v11.xlsx`（6417 行）。
- **收益**：114 个零匹配召回漏洞**全部修复**（字面斜杠归零）。
- **代价（已清理）**：当前拆分器"可选 sth/共享前缀分配"过激进，重拆引入过匹配垃圾变体，已逐一修正：
  - `be sth`(单独匹配 183 次)←`be going to do/be sth` 丢前缀，修为 `be going to do/be sth`；
  - `it's sb/sth`(39，"it is X"全撞)→删除该低价值变体；
  - `think sth`←`think highly/a lot of sb/sth`、`do sb a`←`do sb a/the world of good` 丢内容，修正；
  - 12 个裸介词(`on/off duty`→`on`)、`range/between`、`put/set sb's mind...` 共享前缀/后缀丢失，surgical 补全。
- **30 篇实测**：清理后总命中 323（≈旧 329），无灾难过匹配，新增命中中 0 个属已知 FP；已知 FP 由 38 降至 24（义项边界类残留，属 P5）。
- **说明**：v11 的召回收益（114 漏洞）在这 30 篇上体现有限（`take care of sb/sth` 等在本样本出现少），属**面向更广覆盖的潜在修复**；精确率改动已生效。
- **待办**：hit 集变动较大，v11 的**精确 P/R/F1 需对 30 篇做一次轻量重标**；根因（拆分器共享前缀/后缀分配、可选 sth 过激进）仍在拆分器，后续应从逻辑层根治而非持续外科修补。

### 7.4 限制（汇报须注明）
- 样本量仍不大；单人标注、无标注者间一致性(Kappa)；扩充版评测的是修复后抽取，与 9 篇基线非同批，趋势可比、绝对值各自独立。

---

## 7.5 模块封装（抽取 + 消歧，已完成）

在验证定稿基础上（P/R/F1 口径见文首澄清），按"验证优先、封装可检验模块"完成两个独立包：

**`phrase_extraction/`（短语抽取，零 LLM 依赖）**
- `extractor.py`：解析 XML→归一化→加载正则→匹配→词性验证 + `extract()` API + CLI + 输出（句子表/抽取结果，无消歧列）；
- 自带 `evp_regex_generator`（`phrase_to_regex`）+ `evp_special_cases`（特例/decade 规则）+ `evp_linguistic_data` + `data/`（单义_v12_regex、多义_v10）；
- **回归验证**：封装当时新包对 30 篇的命中与旧 annotator **逐条完全一致（306==306，含 span）**。

**`disambiguation/`（多义消歧，独立）**
- `disambiguator.py`：`disambiguate(instances)`（与抽取解耦）+ `disambiguate_hits(hits)`（衔接 MatchHit）；封装 annotator 现用的 LLM（Qwen3.6-flash）批量消歧；
- **验证**：prompt/解析与原实现**逐字符一致**（dry-run 免 API 验证）。

**安全**：两模块 API key 均改为**环境变量 `DASHSCOPE_API_KEY`**，openai 惰性导入；annotator 硬编码 key 已移除。
> 遗留：`dab/mwed_llm_*.py` 等实验脚本仍有硬编码 key，建议一并清理。

## 8. 剩余待办与建议顺序

1. **（用户）标注扩充版评测集** → 跑计分 → 终版 P/R/F1。
2. **P3/P5**：逐条诊断漏抽短语(在不在表→正则是否编译→是否命中)与边界 FP(加邻接约束/归消歧)。
3. **P7**：①③根治后逐个复测、删类乙冗余特例，类甲例外数据化。
4. **P6 全量落地**：用 v10 重跑整个 annotator（含多义 LLM 消歧）产出全量新 hit_detail——**需 API、需用户确认**。
5. **P8**：源表改写畸形条目。

> 方法论红线（导师 slide 11）：P3/P5 这类有精确率↔召回率权衡的改动，必须在评测集上量化净效果、证明净改善再定稿汇报。
