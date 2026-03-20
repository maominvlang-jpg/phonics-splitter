"""
Phonics Splitter - Manim Renderer
==================================
读取 animation_data.json，渲染自然拼读教学动画视频（MP4）。
音频通过 edge-tts 生成，用 ffmpeg 按时序合并进视频。

用法:
    python3 manim_renderer.py --json elephant_animation.json
    python3 manim_renderer.py --batch words.txt

依赖:
    pip3 install manim edge-tts requests pillow
    brew install ffmpeg
"""

import json, sys, os, asyncio, argparse, subprocess, tempfile, shutil
from pathlib import Path

from manim import *
import edge_tts
import requests
from PIL import Image

# ─────────────────────────────────────────────
# 颜色常量
# ─────────────────────────────────────────────
COLOR_BG        = "#1A1A2E"
COLOR_TEXT      = "#EAEAEA"
COLOR_VOWEL     = "#FF6B6B"
COLOR_DIGRAPH   = "#4ECDC4"
COLOR_RULE_TAG  = "#FFD93D"
COLOR_SILENT    = "#555555"
COLOR_MAGIC_E   = "#C77DFF"
SYLLABLE_COLORS = ["#74C0FC", "#63E6BE", "#FFA94D"]
FONT_MAIN       = "Arial Rounded MT Bold"

# ─────────────────────────────────────────────
# TTS 音频生成
# ─────────────────────────────────────────────
async def _tts(text, voice, path):
    await edge_tts.Communicate(text, voice).save(path)

def generate_audio(text, voice, path):
    asyncio.run(_tts(text, voice, path))

def build_audio_files(data, tmp_dir):
    audio  = {}
    script = data.get("audio_script", {})
    if script.get("zh"):
        p = os.path.join(tmp_dir, "zh_intro.mp3")
        generate_audio(script["zh"], "zh-CN-XiaoxiaoNeural", p)
        audio["zh_intro"] = p
    if script.get("zh_rule"):
        p = os.path.join(tmp_dir, "zh_rule.mp3")
        generate_audio(script["zh_rule"], "zh-CN-XiaoxiaoNeural", p)
        audio["zh_rule"] = p
    for i, syl in enumerate(script.get("syllables_en", [])):
        p = os.path.join(tmp_dir, f"syl_{i}.mp3")
        generate_audio(syl, "en-US-AriaNeural", p)
        audio[f"syl_{i}"] = p
    if script.get("blend"):
        p = os.path.join(tmp_dir, "blend.mp3")
        generate_audio(script["blend"], "en-US-AriaNeural", p)
        audio["blend"] = p
    return audio

# ─────────────────────────────────────────────
# 音频时序 & ffmpeg 合并
# ─────────────────────────────────────────────
def get_audio_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return 1.0

def build_audio_timeline(data, audio_files, tmp_dir):
    """按 animation_steps 时序把音频片段拼成完整音轨，返回 WAV 路径"""
    steps  = data.get("animation_steps", [])
    cues   = []   # [(offset_sec, key)]
    cursor = 0.0

    if "zh_intro" in audio_files:
        cues.append((cursor, "zh_intro"))
        cursor += get_audio_duration(audio_files["zh_intro"]) + 0.3

    cursor += 1.2  # rule badge
    cursor += 0.9  # 单词 FadeIn

    for step in steps:
        stype = step.get("type")
        dur   = step.get("duration_ms", 800) / 1000

        if stype == "vowel_flash":
            cursor += dur + 0.4
        elif stype == "digraph_lock":
            cursor += dur + 0.3
        elif stype == "rule_annotation":
            if "zh_rule" in audio_files:
                cues.append((cursor, "zh_rule"))
            cursor += dur + 0.3
        elif stype == "cut_animation":
            cursor += dur + 0.5
        elif stype == "syllable_sound":
            for i in range(len(step.get("syllables", []))):
                if f"syl_{i}" in audio_files:
                    cues.append((cursor, f"syl_{i}"))
                cursor += 0.8
        elif stype == "blend":
            if "blend" in audio_files:
                cues.append((cursor, "blend"))
            cursor += dur + 0.5
        elif stype in ("magic_e", "silent_letter"):
            cursor += dur + 0.5
        elif stype == "image_display":
            cursor += dur

    cursor += 1.0
    if "blend" in audio_files:
        cues.append((cursor, "blend"))

    if not cues:
        return None

    total   = cursor + 2.5
    inputs  = ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={total:.2f}"]
    fparts  = ["[0:a]acopy[base]"]
    mlabels = ["[base]"]

    for idx, (offset, key) in enumerate(cues):
        si    = idx + 1
        delay = int(offset * 1000)
        lbl   = f"[s{si}]"
        inputs += ["-i", audio_files[key]]
        fparts.append(f"[{si}:a]adelay={delay}|{delay}{lbl}")
        mlabels.append(lbl)

    n = len(mlabels)
    fparts.append(f"{''.join(mlabels)}amix=inputs={n}:duration=first:normalize=0[out]")
    fc      = ";".join(fparts)
    out     = os.path.join(tmp_dir, "full_audio.wav")
    cmd     = ["ffmpeg", "-y"] + inputs + ["-filter_complex", fc, "-map", "[out]", out]
    r       = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and os.path.exists(out):
        return out
    print(f"  ⚠ 音轨合成失败:\n{r.stderr[-400:]}")
    return None

def merge_audio_into_video(video, audio, output):
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", video, "-i", audio,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output],
        capture_output=True, text=True)
    return r.returncode == 0

# ─────────────────────────────────────────────
# 图片获取
# ─────────────────────────────────────────────
def fetch_word_image(query, tmp_dir):
    try:
        r    = requests.get("https://api.duckduckgo.com/",
                            params={"q": query, "format": "json",
                                    "iax": "images", "ia": "images"}, timeout=5)
        data = r.json()
        url  = data.get("Image") or (
            data.get("Results", [{}])[0].get("Image") if data.get("Results") else None)
        if not url:
            return None
        p = os.path.join(tmp_dir, "word_image.jpg")
        with open(p, "wb") as f:
            f.write(requests.get(url, timeout=5).content)
        Image.open(p).verify()
        return p
    except Exception:
        return None

# ─────────────────────────────────────────────
# 辅助
# ─────────────────────────────────────────────
def build_letters(word, font_size=96):
    g = VGroup(*[Text(c, font=FONT_MAIN, font_size=font_size, color=COLOR_TEXT) for c in word])
    g.arrange(RIGHT, buff=0.05)
    return g

def group_by_syllables(letters, syllables):
    groups, cursor = [], 0
    for syl in syllables:
        groups.append(VGroup(*[letters[i] for i in range(cursor, min(cursor+len(syl), len(letters)))]))
        cursor += len(syl)
    return groups

# ─────────────────────────────────────────────
# Manim 场景（纯视觉，无内置音频）
# ─────────────────────────────────────────────
class PhonicsSplitterScene(Scene):

    def __init__(self, data, image_path, **kwargs):
        self.data       = data
        self.image_path = image_path
        super().__init__(**kwargs)

    def construct(self):
        self.camera.background_color = COLOR_BG
        word  = self.data["word"]
        steps = self.data.get("animation_steps", [])

        self._intro(word)
        self._rule_badge()

        letters = build_letters(word)
        letters.move_to(ORIGIN)
        self.play(FadeIn(letters, shift=UP*0.3), run_time=0.6)
        self.wait(0.3)

        colored = {}
        for step in steps:
            t   = step["type"]
            dur = step.get("duration_ms", 800) / 1000
            if   t == "vowel_flash":     self._vowel_flash(letters, step, dur, colored)
            elif t == "digraph_lock":    self._digraph_lock(letters, step, dur, colored)
            elif t == "rule_annotation": self._rule_annotation(letters, step, dur)
            elif t == "cut_animation":   self._cut_animation(letters, step, dur)
            elif t == "syllable_sound":  self._syllable_sound(letters, step, dur)
            elif t == "blend":           self._blend(letters, step, dur)
            elif t == "magic_e":         self._magic_e(letters, step, dur)
            elif t == "silent_letter":   self._silent_letter(letters, step, dur)
            elif t == "image_display":   self._image_display(step, dur)

        self._outro(word)

    def _intro(self, word):
        script = self.data.get("audio_script", {})
        title  = Text("自然拼读", font=FONT_MAIN, font_size=28, color=COLOR_RULE_TAG)
        title.to_corner(UL, buff=0.4)
        self.play(FadeIn(title), run_time=0.4)
        if script.get("zh"):
            zh = Text(script["zh"], font="PingFang SC", font_size=26, color=COLOR_TEXT)
            zh.to_edge(DOWN, buff=0.6)
            self.play(FadeIn(zh, shift=UP*0.2), run_time=0.5)
            self.wait(2.0)
            self.play(FadeOut(zh), run_time=0.4)

    def _rule_badge(self):
        rule     = self.data.get("rule")
        icon     = self.data.get("rule_icon", "")
        strategy = self.data.get("strategy", "")
        affixes  = self.data.get("affixes", {})
        lines    = []
        if strategy == "compound": lines.append("复合词")
        if affixes.get("prefix"):  lines.append(f"前缀: {affixes['prefix']}-")
        if affixes.get("suffix"):  lines.append(f"后缀: -{affixes['suffix']}")
        if rule:                   lines.append(f"{icon} {rule}")
        if not lines: return
        badge = VGroup(*[Text(l, font=FONT_MAIN, font_size=22, color=COLOR_RULE_TAG) for l in lines])
        badge.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.4)
        box = SurroundingRectangle(badge, color=COLOR_RULE_TAG,
                                   buff=0.2, corner_radius=0.12, stroke_width=1.5)
        self.play(FadeIn(badge, shift=LEFT*0.2), Create(box), run_time=0.6)
        self.wait(0.5)

    def _vowel_flash(self, L, step, dur, colored):
        targets = [p for p in step.get("targets", []) if p < len(L)]
        color   = step.get("color", COLOR_VOWEL)
        if not targets: return
        self.play(*[L[p].animate.set_color(color) for p in targets], run_time=dur*0.5)
        self.play(*[L[p].animate.scale(1.3) for p in targets], run_time=0.2)
        self.play(*[L[p].animate.scale(1/1.3) for p in targets], run_time=0.2)
        self.wait(0.2)
        for p in targets: colored[p] = color

    def _digraph_lock(self, L, step, dur, colored):
        start = step.get("start", 0)
        dg    = step.get("digraph", "")
        end   = min(start + len(dg), len(L))
        color = step.get("color", COLOR_DIGRAPH)
        idxs  = range(start, end)
        if not list(idxs): return
        self.play(*[L[i].animate.set_color(color) for i in idxs], run_time=dur*0.4)
        group = VGroup(*[L[i] for i in idxs])
        brace = Brace(group, DOWN, color=color, buff=0.05)
        label = Text(dg, font=FONT_MAIN, font_size=20, color=color)
        label.next_to(brace, DOWN, buff=0.05)
        self.play(GrowFromCenter(brace), FadeIn(label), run_time=0.4)
        self.wait(dur*0.4)
        self.play(FadeOut(brace), FadeOut(label), run_time=0.3)

    def _rule_annotation(self, L, step, dur):
        cut = step.get("cut_position", 0)
        if cut >= len(L): return
        tag   = Text(f"{step.get('rule_icon','')} {step.get('rule_name','')}", 
                     font=FONT_MAIN, font_size=24, color=COLOR_RULE_TAG)
        tag.next_to(L, UP, buff=0.5)
        arrow = Arrow(tag.get_bottom(), L[min(cut, len(L)-1)].get_top()+UP*0.1,
                      color=COLOR_RULE_TAG, stroke_width=2,
                      max_tip_length_to_length_ratio=0.15)
        self.play(FadeIn(tag, shift=DOWN*0.2), GrowArrow(arrow), run_time=0.5)
        self.wait(dur)
        self.play(FadeOut(tag), FadeOut(arrow), run_time=0.3)

    def _cut_animation(self, L, step, dur):
        pos = step.get("position", 0)
        if pos <= 0 or pos >= len(L): return
        cut_x = (L[pos-1].get_right()[0] + L[pos].get_left()[0]) / 2
        top_y = L.get_top()[1] + 0.6
        bot_y = L.get_bottom()[1] - 0.6
        dash  = None
        if step.get("show_dashed_line", True):
            dash = DashedLine([cut_x, top_y, 0], [cut_x, bot_y, 0],
                              color="#888888", dash_length=0.12, stroke_width=2)
            self.play(Create(dash), run_time=0.4)
        if step.get("show_scissors", True):
            sc = Text("✂", font_size=32, color=COLOR_RULE_TAG)
            sc.move_to([cut_x, top_y+0.3, 0])
            self.play(FadeIn(sc), run_time=0.2)
            self.play(sc.animate.move_to([cut_x, bot_y-0.3, 0]), run_time=dur*0.6)
            self.play(FadeOut(sc), run_time=0.2)
        self.play(VGroup(*[L[i] for i in range(pos)]).animate.shift(LEFT*0.25),
                  VGroup(*[L[i] for i in range(pos, len(L))]).animate.shift(RIGHT*0.25),
                  run_time=0.5)
        if dash:
            self.play(FadeOut(dash), run_time=0.2)

    def _syllable_sound(self, L, step, dur):
        syllables = step.get("syllables", [])
        zoom      = step.get("zoom_factor", 1.3)
        groups    = group_by_syllables(L, syllables)
        for i, g in enumerate(groups):
            color = SYLLABLE_COLORS[i % len(SYLLABLE_COLORS)]
            self.play(*[l.animate.set_color(color) for l in g], run_time=0.3)
            if zoom > 1: self.play(g.animate.scale(zoom), run_time=0.2)
            self.wait(0.6)
            if zoom > 1: self.play(g.animate.scale(1/zoom), run_time=0.2)
            self.wait(0.2)

    def _blend(self, L, step, dur):
        if step.get("show_merge_animation", True):
            self.play(L.animate.move_to(ORIGIN), run_time=0.5)
        self.play(L.animate.scale(1.15).set_color(COLOR_TEXT), run_time=0.4)
        self.play(L.animate.scale(1/1.15), run_time=0.3)
        self.wait(dur*0.5)

    def _magic_e(self, L, step, dur):
        ep, vp = step.get("e_position", len(L)-1), step.get("affected_vowel_position", 0)
        if ep >= len(L) or vp >= len(L): return
        self.play(L[ep].animate.set_color(COLOR_MAGIC_E), run_time=0.3)
        arc   = CurvedArrow(L[ep].get_top()+UP*0.1, L[vp].get_top()+UP*0.1,
                            color=COLOR_MAGIC_E, stroke_width=2, angle=-TAU/4)
        label = Text("Magic E", font_size=20, color=COLOR_MAGIC_E)
        label.next_to(arc, UP, buff=0.1)
        self.play(Create(arc), FadeIn(label), run_time=0.5)
        self.play(L[vp].animate.set_color(COLOR_MAGIC_E).scale(1.2), run_time=0.4)
        self.play(L[vp].animate.scale(1/1.2), run_time=0.2)
        self.wait(dur*0.5)
        self.play(FadeOut(arc), FadeOut(label), run_time=0.3)

    def _silent_letter(self, L, step, dur):
        positions = [p for p in step.get("positions", []) if p < len(L)]
        if positions:
            self.play(*[L[p].animate.set_color(COLOR_SILENT).set_opacity(0.3)
                        for p in positions], run_time=dur*0.5)
        for p in positions:
            tag = Text("silent", font_size=16, color=COLOR_SILENT)
            tag.next_to(L[p], DOWN, buff=0.15)
            self.play(FadeIn(tag), run_time=0.2)
        self.wait(dur*0.4)

    def _image_display(self, step, dur):
        if not self.image_path:
            self.wait(dur); return
        try:
            img = ImageMobject(self.image_path).scale(0.8)
            img.to_corner(UR if step.get("position") == "top_right" else DR, buff=0.5)
            box = SurroundingRectangle(img, color=COLOR_RULE_TAG, buff=0.08, corner_radius=0.1)
            self.play(FadeIn(img), Create(box), run_time=0.5)
            self.wait(max(dur-0.5, 0.1))
        except Exception:
            self.wait(dur)

    def _outro(self, word):
        self.play(FadeOut(*self.mobjects), run_time=0.5)
        final = Text(word, font=FONT_MAIN, font_size=120, color=COLOR_TEXT)
        self.play(GrowFromCenter(final), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(final), run_time=0.5)

# ─────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────
def render_word(json_path, output_dir="."):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    word = data["word"]
    print(f"\n▶ 渲染: {word}")
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:

        print("  → 生成音频片段...")
        audio_files = build_audio_files(data, tmp_dir)

        print("  → 合成完整音轨...")
        audio_timeline = build_audio_timeline(data, audio_files, tmp_dir)

        image_path = None
        for step in data.get("animation_steps", []):
            if step["type"] == "image_display":
                print(f"  → 搜索图片: {step['query']}")
                image_path = fetch_word_image(step["query"], tmp_dir)
                break

        print("  → 渲染动画...")
        config.background_color = "#1A1A2E"
        config.pixel_height     = 1080
        config.pixel_width      = 1920
        config.frame_rate       = 30
        config.output_file      = f"{word}_Phonics_silent"
        config.media_dir        = output_dir
        config.quality          = "high_quality"

        PhonicsSplitterScene(data=data, image_path=image_path).render()

        # 找到渲染输出文件
        found = list(Path(output_dir).rglob(f"{word}_Phonics_silent.mp4"))
        if not found:
            print("  ✗ 找不到渲染输出文件")
            return None

        silent_path = str(found[0])
        final_path  = str(Path(output_dir) / f"{word}_Phonics.mp4")

        if audio_timeline:
            print("  → 合并音视频...")
            ok = merge_audio_into_video(silent_path, audio_timeline, final_path)
            if ok:
                print(f"\n  ✅ 完成: {final_path}")
                return final_path
            print("  ⚠ 合并失败，输出无声版本")

        shutil.copy(silent_path, final_path)
        print(f"\n  ✅ 完成（无声）: {final_path}")
        return final_path


def main():
    p = argparse.ArgumentParser(description="Phonics Splitter - Manim 渲染器")
    p.add_argument("word",    nargs="?", help="单词（读取 <word>_animation.json）")
    p.add_argument("--json",  help="指定 JSON 文件路径")
    p.add_argument("--batch", help="批量渲染（文本文件，每行一个 JSON 路径）")
    p.add_argument("--output", default="./output", help="输出目录")
    args = p.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.batch:
        with open(args.batch) as f:
            for path in [l.strip() for l in f if l.strip()]:
                try:    render_word(path, args.output)
                except Exception as e: print(f"  ✗ 失败: {e}")
    elif args.json:
        render_word(args.json, args.output)
    elif args.word:
        jp = f"{args.word}_animation.json"
        if not os.path.exists(jp):
            print(f"错误: 找不到 {jp}"); sys.exit(1)
        render_word(jp, args.output)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
