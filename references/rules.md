# Phonics Rules Reference

## Table of Contents
1. Level 1: Basic Building Blocks
2. Level 2: Animal Rules (Syllable Splitting)
3. Level 3: Special Rules
4. Edge Cases & Exception Words
5. Tiger vs Camel Decision Guide

---

## Level 1: Basic Building Blocks

### Short Vowels (短元音)
| 字母 | 发音 | 示例单词 |
|------|------|----------|
| a | /æ/ | cat, map, hand |
| e | /ɛ/ | bed, red, set |
| i | /ɪ/ | sit, big, milk |
| o | /ɒ/ | hot, top, clock |
| u | /ʌ/ | cup, bus, jump |

### Digraphs (二合辅音)
| Digraph | 发音 | 示例 |
|---------|------|------|
| sh | /ʃ/ | ship, fish, wish |
| ch | /tʃ/ | chip, much, lunch |
| th | /θ/ or /ð/ | thin, this, bath |
| wh | /w/ | when, where, white |
| ph | /f/ | phone, photo |
| ck | /k/ | back, duck, clock |
| ng | /ŋ/ | ring, sing, long |
| nk | /ŋk/ | sink, bank, trunk |
| tch | /tʃ/ | match, catch, watch |
| dge | /dʒ/ | bridge, edge, fudge |

### Vowel Teams (元音组合)
| 组合 | 发音 | 示例 |
|------|------|------|
| ai | /eɪ/ | rain, train, wait |
| ay | /eɪ/ | day, play, say |
| ee | /iː/ | tree, see, feet |
| ea | /iː/ or /ɛ/ | eat, sea / bread, head |
| oa | /oʊ/ | boat, road, coat |
| ow | /oʊ/ or /aʊ/ | snow, low / cow, now |
| oo | /uː/ or /ʊ/ | moon, food / book, look |
| ou | /aʊ/ | out, cloud, mouth |
| oi | /ɔɪ/ | oil, coin, point |
| oy | /ɔɪ/ | boy, toy, enjoy |
| ue | /juː/ | blue, clue, true |
| ui | /uː/ | fruit, suit, juice |
| igh | /aɪ/ | night, light, fight |

### Bossy R (R控制元音)
| 组合 | 发音 | 示例 |
|------|------|------|
| ar | /ɑːr/ | car, farm, star |
| er | /ɜːr/ | her, fern, verb |
| ir | /ɜːr/ | bird, girl, shirt |
| or | /ɔːr/ | corn, fork, storm |
| ur | /ɜːr/ | burn, turn, fur |

---

## Level 2: Animal Rules (Syllable Splitting)

### 🐰 Rabbit Rule (VCCV Pattern)

**触发条件**：两个元音音节之间有2个或以上辅音

**切分位置**：
- 普通双辅音：从中间切（VC|CV）
- 双写字母（bb, tt, pp等）：在第一个辅音后切（保留发音完整性）
- Digraph（算作单辅音）：整体归后一音节

**示例集合**：
```
rabbit  → rab | bit   (bb → 在b后切)
napkin  → nap | kin
pepper  → pep | per
kitten  → kit | ten
picnic  → pic | nic
public  → pub | lic
```

**边界情况**：
- `chicken` → `chick | en`（ch是digraph，ck是digraph，算作2辅音间隔）
- `pitcher` → `pitch | er`（tch是三合字母，算单辅音）

---

### 🐯 Tiger Rule (V/CV Pattern - Open Syllable)

**触发条件**：两元音间仅1个辅音，且前元音发**长音**（开音节，元音说字母本音）

**切分位置**：辅音**前**（前音节成为开音节 CV）

**示例集合**：
```
tiger  → ti | ger   (i 发长音 /aɪ/)
baby   → ba | by    (a 发长音 /eɪ/)
music  → mu | sic   (u 发长音 /juː/)
open   → o | pen    (o 发长音 /oʊ/)
robot  → ro | bot   (o 发长音 /oʊ/)
paper  → pa | per   (a 发长音 /eɪ/)
```

---

### 🐫 Camel Rule (VC/V Pattern - Closed Syllable)

**触发条件**：两元音间仅1个辅音，且前元音发**短音**（闭音节）

**切分位置**：辅音**后**（前音节成为闭音节 VC）

**示例集合**：
```
camel  → cam | el   (a 发短音 /æ/)
city   → cit | y    (i 发短音 /ɪ/)
robin  → rob | in   (o 发短音 /ɒ/)
model  → mod | el   (o 发短音 /ɒ/)
seven  → sev | en   (e 发短音 /ɛ/)
melon  → mel | on   (e 发短音 /ɛ/)
```

---

### 🦁 Lion Rule (V/V Pattern)

**触发条件**：两个元音字母直接相邻，但**不构成元音组合**，需分开发音

**切分位置**：两元音之间

**判断要点**：先检查是否为已知 Vowel Team（参考 Level 1），若不在列表中则应用 Lion Rule

**示例集合**：
```
lion   → li | on
poem   → po | em
diet   → di | et
cruel  → cru | el
Iowa   → I | o | wa
create → cre | ate
```

---

### 🐢 Turtle Rule (-Cle Pattern)

**触发条件**：单词以 `-Cle` 结尾（C = 一个辅音字母）

**切分方法**：从词尾往前数三个字母（e, l, 辅音C），在辅音C**前**切开

**示例集合**：
```
turtle → tur | tle
table  → ta  | ble
puzzle → puz | zle
simple → sim | ple
apple  → ap  | ple  (注意：pp → Rabbit+Turtle组合)
circle → cir | cle
gentle → gen | tle
```

---

## Level 3: Special Rules

### Magic E ✨

**结构**：[元音] + [≥1辅音] + [词尾e]（e不发音，影响前方元音）

**效果**：前元音由短音变为长音（发字母本音）

**示例集合**：
```
cake  → c-[a]ke  (a: /æ/ → /eɪ/)
hope  → h-[o]pe  (o: /ɒ/ → /oʊ/)
time  → t-[i]me  (i: /ɪ/ → /aɪ/)
cute  → c-[u]te  (u: /ʌ/ → /juː/)
these → th-[e]se (e: /ɛ/ → /iː/)
```

**动画处理**：词尾 e 显示魔法棒动画，箭头指向前方元音，颜色由蓝（短音）变红（长音）

---

### Silent Letters 🔇

**常见静默字母规律**：

| 模式 | 静默字母 | 示例 |
|------|----------|------|
| kn- | k | knife, know, kneel |
| wr- | w | write, wrap, wrong |
| -mb | b | lamb, climb, thumb |
| -lk | l | talk, walk, folk |
| -gh | gh | night, light, taught |
| gn- | g | gnome, gnat |
| ps- | p | psalm, psychology |
| 词中 | 视情况 | listen(t), whistle(t), castle(t) |

**动画处理**：静默字母颜色设为灰色（opacity: 0.3），其余字母正常显示

---

### Soft C / Soft G

**Soft C**（发 /s/ 音）：c + e, i, y
- city, cell, cycle, center, pencil

**Soft G**（发 /dʒ/ 音）：g + e, i, y
- gym, gem, giraffe, giant, gentle

---

## Tiger vs Camel 决策指南

遇到 V_CV 模式（两元音间仅1辅音）时，按以下顺序判断：

1. **检查常见词**：直接查下方已知词表
2. **检查词尾**：若结尾是 Magic E 结构，元音为长音
3. **查 IPA 字典**（如有）：直接获取第一音节元音发音
4. **使用启发式规则**：
   - 单词来自拉丁/法语词根 → 倾向 Tiger（开音节）
   - 单词以 -it, -in, -ot, -en, -on, -el, -il 结尾 → 倾向 Camel
5. **默认 Tiger**：若仍不确定，使用 Tiger Rule 并注明"需验证"

**Tiger（长音）常见词**：tiger, baby, music, open, robot, paper, basic, bonus, labor, pilot, vital, major, female, moment

**Camel（短音）常见词**：camel, city, robin, model, seven, melon, lemon, river, finish, rapid, solid, magic, promise, body, money

---

## 常见例外与注意事项

1. `tion` / `sion` 后缀整体不拆分，发音 /ʃən/（如 action, nation）
2. `ture` 后缀整体处理，发音 /tʃər/（如 picture, nature）
3. 元音组合 `ea` 在 `bread`, `head`, `dead` 中发短音 /ɛ/，需特殊标注
4. `ow` 在词中可发 /oʊ/（snow）或 /aʊ/（cow），通常词尾或+l发 /oʊ/
5. `y` 在词首发辅音 /j/（yes, yellow），不视为元音
