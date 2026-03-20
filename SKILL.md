---
name: phonics-splitter
description: 自然拼读单词分析与教学内容生成工具，专为中小学生设计。当用户输入任意英语单词，需要进行音节切分、拼读规则分析、生成教学讲解、或输出自然拼读动画数据时，必须使用此 skill。触发场景包括：分析单词拼读结构、识别元音/辅音规则、应用动物规则切分音节、生成双语教学脚本、输出 animation_data.json 动画数据、解释 Magic E / Bossy R / Digraph 等拼读特殊规则。只要用户提到"自然拼读"、"phonics"、"音节切分"、"拆分单词"、"拼读规则"、"phonics动画"，就立即调用此 skill。
---

# Phonics Splitter Skill

专为中小学生设计的自然拼读分析工具。

**教学目标：学自然拼读 + 背单词拼写 + 记读音**

> ⚠️ **核心原则：以发音为准，音节拆分必须服务于"学生开口读出正确发音"**
>
> 拆分结果的唯一标准：**学生按音节读出来 = 单词的正确发音**
> 拼写规则（动物规则）是辅助工具，当规则推断与实际发音冲突时，**以实际发音优先**

---

> ⚠️ **执行纪律（必须严格遵守）**
> 1. 必须按 Step 0→1→2→3→4→5→6→7 顺序执行，禁止跳步
> 2. **Step 0 必须最先执行**：查 IPA，确定每个音节的实际发音边界
> 3. Step 5 必须在 Step 6 之前完成，Digraph 未锁定前禁止切分
> 4. **cut_position 必须等于前面所有音节的字符数之和**
> 5. JSON 中禁止出现 `//` 注释
> 6. 输出前必须过自检清单，不通过不得输出

---

## 执行流程总览

```
Step 0 → IPA 查询（确定实际发音和音节数）← 新增，必须最先执行
Step 1 → 白名单检测 (Sight Words)
Step 2 → 复合词识别
Step 3 → 词缀分离（识别后仍扫描完整原词）
Step 4 → 元音定位
Step 5 → 二合字母标记
Step 6 → 动物规则应用（以IPA音节为准校验）
Step 7 → 特效渲染（Magic E / Silent Letters）
```

---

## Step 0：IPA 查询（必须最先执行）

**在做任何字母分析之前，先确定单词的 IPA 音标和音节数。**

输出格式：
```
IPA: /xxx/
音节数: N
发音音节: [syl1] - [syl2] - [syl3]
```

**常见单词 IPA 参考（Tiger vs Camel 易错词）：**

| 单词 | IPA | 正确拆法 | 错误拆法 |
|------|-----|---------|---------|
| animal | /ˈæn.ɪ.məl/ | an-i-mal | ~~an-im-al~~ |
| family | /ˈfæm.ɪ.li/ | fam-i-ly | ~~fam-il-y~~ |
| tomorrow | /təˈmɒr.əʊ/ | to-mor-row | ~~tom-or-row~~ |
| camera | /ˈkæm.ər.ə/ | cam-er-a | ~~cam-er-a~~ ✓ |
| generous | /ˈdʒen.ər.əs/ | gen-er-ous | ~~gen-er-ous~~ ✓ |
| origin | /ˈɒr.ɪ.dʒɪn/ | or-i-gin | ~~or-ig-in~~ |
| second | /ˈsek.ənd/ | sec-ond | ~~se-cond~~ |
| river | /ˈrɪv.ər/ | riv-er | ~~ri-ver~~ |
| never | /ˈnev.ər/ | nev-er | ~~ne-ver~~ |
| clever | /ˈklev.ər/ | clev-er | ~~cle-ver~~ |

**若不确定 IPA，默认以字典音节（Merriam-Webster 或牛津词典）为准。**

---

## Step 1：白名单检测

常见 Sight Words 不做规则拆分，采用整体认读：

> the, was, said, have, come, some, what, where, there, they, you, your, are, were, one, two, who, do, to, of, from, into, been, any, many, could, would, should, does, goes, says, put, pull, full, push, both, talk, walk

若命中白名单 → 输出 `strategy: "sight_word"`，直接跳至 Step 7。

---

## Step 2：复合词识别

检测是否为复合词（如 classroom = class + room，sunflower = sun + flower）。

- 分别对子部分递归执行完整流程
- 子部分之间用 `|` 标记复合词边界

---

## Step 3：词缀分离

**前缀**：un-, re-, pre-, dis-, mis-, in-, im-, non-, over-, sub-, super-, inter-, trans-, ex-

**后缀**：-ing, -ed, -er, -est, -tion, -sion, -ness, -ful, -less, -ly, -able, -ible, -ment, -ous, -ive, -or, -ar

**启发式规避过度拆分**：
- 去除词缀后剩余部分必须是独立语素，否则不拆
- `tiger` → `er` 不是后缀（`tig` 非语素）→ 保留整体
- `expensive` → `ex-` 合法，`-ive` 不拆（`expens` 非语素）

### ⚠️ 词缀识别后元音定位必须扫描完整原词

词缀识别只是标注，**不得从原词中移除任何字母**。Step 4 必须对完整原词逐一扫描。

```
conductor：识别后缀 -or，但元音定位仍扫描 c-o-n-d-u-c-t-o-r
→ 元音 o(1), u(4), [or](7-8) 全部保留
→ 正确切分：con-duc-tor ✓（不是 con-duct-or ✗）
```

---

## Step 4：元音定位

**按优先级从高到低识别**：

| 优先级 | 类型 | 示例 |
|--------|------|------|
| 1 | Bossy R | ar, er, ir, or, ur → 整体锁定，r 不再参与辅音计数 |
| 2 | Vowel Teams | ai, ay, ee, ea, oa, ow, oo, ou, oi, oy, ue, ui, igh |
| 3 | y 作元音 | 词中或词尾的 y（非词首）|
| 4 | 单元音 | a, e, i, o, u |

### ⚠️ Bossy R 锁定规则

Bossy R 锁定后：r 不再是辅音，禁止在 Step 6 中计入辅音数量。

```
dangerous：er(4-5) 锁定为 [ER]，r 不算辅音
→ a(1) 与 [ER] 之间只有 ng（1个Digraph单位）→ Tiger Rule → da|nger ✓
❌ 错误：把 r 当辅音 → dan-ge-r-ous
```

---

## Step 5：二合字母标记

锁定以下辅音组合为不可分割整体（整体算作 **1个辅音单位**）：

| 类型 | 列表 |
|------|------|
| 基础 Digraph | sh, ch, th, wh, ph, ck, ng, nk |
| 三合字母 | tch, dge, igh |

### ⚠️ Digraph 必须结合 IPA 发音验证，不能仅凭字母组合判断

**`ng` 的两种情况（最易混淆）：**

| 情况 | 发音 | 是否 Digraph | 处理方式 | 示例 |
|------|------|------------|---------|------|
| 词尾或同一音节内 | /ŋ/ | ✅ 是 Digraph | 整体算1个辅音单位 | ring, sing, long, ang-ry |
| 跨越音节边界 | /n/+/dʒ/ 或 /n/+/g/ | ❌ 不是 Digraph | n 和 g 各算1个辅音单位 | dan-ger-ous, en-gine |

**dangerous 详解（必须按此执行）：**
```
字母：d-a-n-g-e-r-o-u-s
Step 0 IPA：/ˈdeɪn.dʒər.əs/ → 第一音节 /deɪn/ 含 n，第二音节 /dʒər/ 以 dʒ 开头
→ n(2) 和 g(3) 跨越音节边界，发 /n/+/dʒ/，不是 /ŋ/
→ n 和 g 各算1个辅音单位，共2个
→ Rabbit Rule 🐰，在 n 和 g 之间切 → dan | ger，cut=3 ✓

❌ 错误：把 ng 当 Digraph → 只算1个辅音单位 → Tiger Rule → da | nger，cut=2（错！）
```

**判断口诀：先查 IPA，音节边界两侧的字母不构成 Digraph。**

---

## Step 6：动物规则应用

### 🔑 Tiger vs Camel 决策规则（最重要）

**必须以 Step 0 的 IPA 发音为最终依据，不得仅凭字母结构推断。**

```
两元音之间仅1个辅音时：
  → 先查 IPA，看前音节是开音节还是闭音节
  → 开音节（元音发字母音）= Tiger Rule（V|CV）
  → 闭音节（元音发短音）= Camel Rule（VC|V）
  → IPA 不确定时，查字典音节，以字典为准
```

**易错对照表（必须记住）：**

| 单词 | IPA | 前元音 | 正确规则 | 正确拆法 |
|------|-----|--------|---------|---------|
| animal | /ˈæn.ɪ.məl/ | a=短/æ/ | 🐫 Camel | **an**-i-mal |
| family | /ˈfæm.ɪ.li/ | a=短/æ/ | 🐫 Camel | **fam**-i-ly |
| river | /ˈrɪv.ər/ | i=短/ɪ/ | 🐫 Camel | **riv**-er |
| never | /ˈnev.ər/ | e=短/ɛ/ | 🐫 Camel | **nev**-er |
| second | /ˈsek.ənd/ | e=短/ɛ/ | 🐫 Camel | **sec**-ond |
| tiger | /ˈtaɪ.ɡər/ | i=长/aɪ/ | 🐯 Tiger | **ti**-ger |
| baby | /ˈbeɪ.bi/ | a=长/eɪ/ | 🐯 Tiger | **ba**-by |
| music | /ˈmjuː.zɪk/ | u=长/juː/ | 🐯 Tiger | **mu**-sic |
| open | /ˈoʊ.pən/ | o=长/oʊ/ | 🐯 Tiger | **o**-pen |

### 动物规则速查

**🐰 Rabbit Rule (VCCV)** — 辅音单位 ≥ 2
- 切分位置：两辅音单位之间
- 示例：rab-bit, nap-kin, dish-pan(sh+p), con-duc-tor(nd, ct)

**🐯 Tiger Rule (V/CV)** — 辅音单位=1，前元音长音（开音节）
- 切分位置：辅音前（辅音归后音节）
- 示例：ti-ger, ba-by, mu-sic, to-mor-row(第一刀)

**🐫 Camel Rule (VC/V)** — 辅音单位=1，前元音短音（闭音节）
- 切分位置：辅音后（辅音归前音节）
- 示例：cam-el, an-i-mal, fam-i-ly, riv-er

**🦁 Lion Rule (V/V)** — 两元音直接相邻，非 Vowel Team
- 切分位置：两元音之间
- 示例：li-on, po-em, gym-na-si-um(第三刀)

**🐢 Turtle Rule (-Cle)** — 词尾辅音+le
- 切分位置：从词尾数3个字母，辅音前切
- 示例：tur-tle, ta-ble, puz-zle

---

## Step 7：特效识别

### Magic E ✨
- 结构：元音 + 辅音 + 不发音e（词尾）
- 效果：词尾 e 使前元音发长音
- 示例：cake(a→/eɪ/), hope(o→/oʊ/), time(i→/aɪ/)

### Silent Letters 🔇
- 常见：kn-(knife), wr-(write), -mb(lamb), gh(night), listen中的t
- 处理：标记静默字母，动画中灰度化显示

---

## ✅ 输出前自检清单

```
□ 0. Step 0 是否已查 IPA？发音音节是否已确认？
□ 1. Bossy R 是否已检查？若存在，r 是否已从辅音列表中移除？
□ 2. Digraph 是否已锁定？辅音单位计数是否基于锁定结果？
□ 3. Tiger vs Camel 决策是否以 IPA 发音为依据，而非仅凭字母推断？
□ 4. cut_position 是否等于前面所有音节字符数之和？
     dish-pan: dish=4 → cut=4 ✓
     con-duc-tor: con=3 → cut=3；con+duc=6 → cut=6 ✓
     to-mor-row: to=2 → cut=2；to+mor=5 → cut=5 ✓
□ 5. syllables 数组拼接后是否等于原单词？
□ 6. JSON 中是否有 // 注释？（有则必须删除）
□ 7. 按音节读出来是否等于单词正确发音？（最终验证）
□ 8. 四项输出是否全部准备好？缺一不可
```

---

## 输出格式

> ⚠️ **输出纪律（强制执行）**
>
> 每次分析必须按顺序完整输出以下六项，**缺少任何一项均视为未完成任务，必须补全**：

### 必须输出：完整六项

**① 分析步骤（Phonics-Splitter 7步）**

| 步骤 | 说明 |
|------|------|
| Step 0 – IPA | /xxx/，音节：syl1-syl2-syl3 |
| Step 1 – Sight Word | PASS / HIT |
| Step 2 – 复合词 | SKIP / [结果] |
| Step 3 – 词缀 | 前缀=x，后缀=y，根词=z |
| Step 4 – 元音定位 | [每个元音位置、类型、长短音] |
| Step 5 – 二合字母 | [Digraph列表，无则填"无"] |
| Step 6 – 动物规则 | [元音对 → 辅音单位 → 规则 → cut_position → 切分] |
| Step 7 – 特效 | Magic E=[y/n]，Silent=[letters或none] |

自检清单：□0 □1 □2 □3 □4 □5 □6 □7 □8 全部通过

---

**② 最终音节划分**

```
IPA: /xxx/
Final Split: syl · la · ble
```

---

**③ 中文教学脚本**

按以下结构生成，语气自然活泼，像老师在课堂上讲课：

```
"同学们，今天我们要拆解的单词是 [word]，意思是[中文含义]。
[若有前缀/后缀] 先把[前缀/后缀] [prefix/suffix] 分出去。
首先找元音 [vowel1] 和 [vowel2]，中间有[N]个辅音 [consonants]，
应用[规则名称]在 [位置] 切开，得到 [syllable1]。
[若有多刀] 接着 [继续描述下一刀]。
[若有特效] [Magic E / Bossy R / Digraph 的自然语言说明]。
拼在一起：[syl1]-[syl2]-[syl3]，[word]！"
```

**风格要求：**
- 开头固定用"同学们，今天我们要拆解的单词是 xxx"
- 描述规则时用"应用骆驼法则/兔子法则/虎规则"等自然名称，不用英文
- 结尾固定用"拼在一起：xxx-xxx，xxx！"
- 语气活泼，像真实课堂，不要生硬罗列
- 遇到特殊规则（Magic E、Bossy R、Digraph、Soft C/G）要自然说明，不要跳过

**示例（management）：**
```
"同学们，今天我们要拆解的单词是 management，意思是管理。
首先找元音 a 和 a，中间有1个辅音 n，应用骆驼法则在 n 后面切开，得到 man。
接着结尾是后缀 ment，直接切分出来。
中间的 age 有一个不发音的 e，它让 g 发出 soft G 的声音。
拼在一起：man-age-ment，management！"
```

---

**④ 英文教学脚本**

按以下结构生成，语气自然，像英语课堂的 phonics 教学：

```
"Today's word is [word], it means [meaning].
[若有前后缀] First, let's spot the [prefix/suffix]: [prefix/suffix].
Find the vowels [v1] and [v2] — there [is/are] [N] consonant[s] [consonants] between them.
[规则说明，自然语言]: [rule explanation] → [syllable].
[继续下一刀...]
[特效说明（Magic E / Bossy R / Digraph）]
Now blend it together: [syl1] - [syl2] - [syl3]. [word]!"
```

**风格要求：**
- 开头固定用"Today's word is xxx, it means xxx"
- 结尾固定用"Now blend it together: xxx - xxx. xxx!"
- 规则说明要口语化，不要照搬规则名称
- 遇到特效要自然解释（如"the silent e at the end makes the i say its name"）

**示例（management）：**
```
"Today's word is management, it means 管理.
First, let's spot the suffix: -ment.
Find the vowels a and a — there is 1 consonant n between them.
The a says short /æ/, so we use the Camel Rule and cut after n → man.
The middle chunk is age — notice the silent e at the end makes g say the soft sound /dʒ/.
Now blend it together: man - age - ment. Management!"
```

---

**⑤ animation_data.json（可直接用于本地渲染）**

```json
{
  "word": "example",
  "ipa": "/ɪɡˈzɑːm.pəl/",
  "strategy": "rule_based",
  "syllables": ["ex", "am", "ple"],
  "rule": "Rabbit Rule",
  "rule_icon": "🐰",
  "vowels": [...],
  "digraphs": [...],
  "special_fx": {"magic_e": false, "silent_letters": []},
  "audio_script": {
    "zh": "...",
    "zh_rule": "...",
    "phonemes_en": [...],
    "syllables_en": [...],
    "blend": "example"
  },
  "animation_steps": [...]
}
```

**JSON 规范（违反导致渲染报错）：**
- 严禁出现 `//` 注释
- `cut_position` 必须等于前面所有音节字符数之和
- `syllables` 数组拼接后必须等于原单词

---

**⑥ 本地渲染指引**

```bash
source ~/phonics-env/bin/activate
cd ~/phonics-project
cat << 'EOF' | python3 scripts/manim_renderer.py --json /dev/stdin --output ./output
（粘贴上方 JSON）
EOF
```

视频生成在 `~/phonics-project/output/[word]_Phonics.mp4`

---

## 批量处理

```
Input: animal, family, river, tomorrow
→ 每个单词独立执行 Step 0～7 + 自检清单
→ 输出汇总表 + 各单词 animation_data.json
```

---

## 参考文件

- `references/rules.md` — 完整规则细节、边界案例、例外词表
- `references/animation_schema.md` — animation_data.json 完整 schema
- `scripts/manim_renderer.py` — Manim 视频渲染脚本（Mac 本地运行）
