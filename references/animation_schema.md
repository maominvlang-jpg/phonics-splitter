# Animation Data Schema (animation_data.json)

## 完整字段说明

```typescript
interface AnimationData {
  // 基础信息
  word: string;                    // 原始输入单词（小写）
  strategy: "sight_word" | "rule_based" | "compound";

  // 音节结构
  syllables: string[];             // 切分后的音节数组
  rule: string | null;             // 应用的动物规则名称
  rule_icon: string | null;        // 规则 emoji 图标

  // 词缀信息（可选）
  affixes?: {
    prefix?: string;
    suffix?: string;
    root: string;
  };

  // 复合词（可选）
  compound_parts?: AnimationData[]; // 子部分递归结构

  // 元音标记
  vowels: VowelMark[];

  // Digraph 标记
  digraphs: DigraphMark[];

  // 特效
  special_fx: {
    magic_e: boolean;
    magic_e_position?: number;       // 词尾e的字符位置（0-indexed）
    magic_e_affected_vowel?: number; // 被影响元音的位置
    silent_letters: number[];        // 静默字母的位置数组
  };

  // 音频脚本
  audio_script: AudioScript;

  // 动画步骤序列
  animation_steps: AnimationStep[];
}

interface VowelMark {
  char: string;          // 元音字符
  type: "short" | "long" | "team" | "bossy_r" | "y_vowel";
  position: number;      // 字符在原单词中的位置（0-indexed）
  team?: string;         // 若为 vowel team，记录组合（如 "ea"）
}

interface DigraphMark {
  chars: string;         // digraph 字符（如 "sh", "ch"）
  start: number;         // 起始位置（0-indexed）
  end: number;           // 结束位置（exclusive）
  type: "consonant_digraph" | "trigraph";
}

interface AudioScript {
  zh: string;            // 中文引导语（如"看这个词，tiger，我们来拆一拆"）
  zh_rule?: string;      // 中文规则说明（如"两个元音中间有一个辅音，虎规则，在辅音前切开"）
  phonemes_en: string[]; // 英文音素数组（如 ["t", "i", "g", "er"]）
  syllables_en: string[]; // 音节发音数组（如 ["ti", "ger"]）
  blend: string;         // 完整单词发音（如 "tiger"）
}

type AnimationStep =
  | VowelFlashStep
  | DigraphLockStep
  | RuleAnnotationStep
  | CutAnimationStep
  | SyllableSoundStep
  | BlendStep
  | MagicEStep
  | SilentLetterStep
  | ImageDisplayStep;

interface VowelFlashStep {
  type: "vowel_flash";
  targets: number[];     // 需要高亮的字符位置
  color: string;         // 高亮颜色（如 "#FF6B6B" 红色表示元音）
  duration_ms: number;   // 动画时长
}

interface DigraphLockStep {
  type: "digraph_lock";
  digraph: string;
  start: number;
  color: string;         // 如 "#4ECDC4" 青色
  duration_ms: number;
}

interface RuleAnnotationStep {
  type: "rule_annotation";
  rule_name: string;
  rule_icon: string;     // emoji
  cut_position: number;  // 切分点位置
  duration_ms: number;
}

interface CutAnimationStep {
  type: "cut_animation";
  position: number;      // 在第几个字符后切
  rule: string;
  show_scissors: boolean;
  show_dashed_line: boolean;
  duration_ms: number;
}

interface SyllableSoundStep {
  type: "syllable_sound";
  syllables: string[];
  highlight_each: boolean; // 逐个高亮并发音
  zoom_factor: number;     // 放大倍数（如 1.3）
  duration_ms: number;
}

interface BlendStep {
  type: "blend";
  word: string;
  show_merge_animation: boolean;
  duration_ms: number;
}

interface MagicEStep {
  type: "magic_e";
  e_position: number;
  affected_vowel_position: number;
  wand_animation: boolean;
  duration_ms: number;
}

interface SilentLetterStep {
  type: "silent_letter";
  positions: number[];
  fade_to_gray: boolean;
  duration_ms: number;
}

interface ImageDisplayStep {
  type: "image_display";
  query: string;           // 图片搜索关键词
  position: "top_right" | "bottom_right";
  duration_ms: number;
}
```

---

## 完整示例：单词 "table"

```json
{
  "word": "table",
  "strategy": "rule_based",
  "syllables": ["ta", "ble"],
  "rule": "Turtle Rule",
  "rule_icon": "🐢",
  "affixes": {
    "root": "table"
  },
  "vowels": [
    {"char": "a", "type": "long", "position": 1},
    {"char": "e", "type": "long", "position": 4}
  ],
  "digraphs": [],
  "special_fx": {
    "magic_e": false,
    "silent_letters": []
  },
  "audio_script": {
    "zh": "看这个词，table，我们来拆一拆",
    "zh_rule": "词尾是 le，前面有一个辅音 b，乌龟规则，数三下，在辅音 b 前面切开",
    "phonemes_en": ["t", "a", "b", "le"],
    "syllables_en": ["ta", "ble"],
    "blend": "table"
  },
  "animation_steps": [
    {
      "type": "vowel_flash",
      "targets": [1, 4],
      "color": "#FF6B6B",
      "duration_ms": 800
    },
    {
      "type": "rule_annotation",
      "rule_name": "Turtle Rule",
      "rule_icon": "🐢",
      "cut_position": 2,
      "duration_ms": 600
    },
    {
      "type": "cut_animation",
      "position": 2,
      "rule": "Turtle Rule",
      "show_scissors": true,
      "show_dashed_line": true,
      "duration_ms": 1000
    },
    {
      "type": "syllable_sound",
      "syllables": ["ta", "ble"],
      "highlight_each": true,
      "zoom_factor": 1.3,
      "duration_ms": 1500
    },
    {
      "type": "blend",
      "word": "table",
      "show_merge_animation": true,
      "duration_ms": 800
    },
    {
      "type": "image_display",
      "query": "table furniture",
      "position": "top_right",
      "duration_ms": 3000
    }
  ]
}
```

---

## Sight Word 示例：单词 "the"

```json
{
  "word": "the",
  "strategy": "sight_word",
  "syllables": ["the"],
  "rule": null,
  "rule_icon": null,
  "vowels": [
    {"char": "e", "type": "short", "position": 2}
  ],
  "digraphs": [
    {"chars": "th", "start": 0, "end": 2, "type": "consonant_digraph"}
  ],
  "special_fx": {
    "magic_e": false,
    "silent_letters": []
  },
  "audio_script": {
    "zh": "这是一个常见词，the，整体记住它",
    "phonemes_en": ["the"],
    "syllables_en": ["the"],
    "blend": "the"
  },
  "animation_steps": [
    {
      "type": "digraph_lock",
      "digraph": "th",
      "start": 0,
      "color": "#4ECDC4",
      "duration_ms": 600
    },
    {
      "type": "blend",
      "word": "the",
      "show_merge_animation": false,
      "duration_ms": 800
    }
  ]
}
```

---

## 复合词示例：单词 "classroom"

```json
{
  "word": "classroom",
  "strategy": "compound",
  "syllables": ["class", "room"],
  "rule": null,
  "rule_icon": null,
  "compound_parts": [
    {
      "word": "class",
      "strategy": "rule_based",
      "syllables": ["cl", "a", "ss"],
      "rule": "Rabbit Rule",
      "rule_icon": "🐰",
      "vowels": [{"char": "a", "type": "short", "position": 2}],
      "digraphs": [],
      "special_fx": {"magic_e": false, "silent_letters": []},
      "audio_script": {
        "zh": "第一部分 class",
        "phonemes_en": ["cl", "a", "ss"],
        "syllables_en": ["class"],
        "blend": "class"
      },
      "animation_steps": []
    },
    {
      "word": "room",
      "strategy": "rule_based",
      "syllables": ["room"],
      "rule": null,
      "rule_icon": null,
      "vowels": [{"char": "oo", "type": "team", "position": 1, "team": "oo"}],
      "digraphs": [],
      "special_fx": {"magic_e": false, "silent_letters": []},
      "audio_script": {
        "zh": "第二部分 room",
        "phonemes_en": ["r", "oo", "m"],
        "syllables_en": ["room"],
        "blend": "room"
      },
      "animation_steps": []
    }
  ],
  "vowels": [],
  "digraphs": [],
  "special_fx": {"magic_e": false, "silent_letters": []},
  "audio_script": {
    "zh": "这是一个复合词，classroom，由 class 和 room 组成",
    "phonemes_en": ["class", "room"],
    "syllables_en": ["class", "room"],
    "blend": "classroom"
  },
  "animation_steps": [
    {
      "type": "cut_animation",
      "position": 5,
      "rule": "Compound Word",
      "show_scissors": true,
      "show_dashed_line": true,
      "duration_ms": 1000
    },
    {
      "type": "syllable_sound",
      "syllables": ["class", "room"],
      "highlight_each": true,
      "zoom_factor": 1.2,
      "duration_ms": 1500
    },
    {
      "type": "blend",
      "word": "classroom",
      "show_merge_animation": true,
      "duration_ms": 800
    }
  ]
}
```
