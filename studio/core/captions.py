#!/usr/bin/env python3
"""Brand-styled captions: planned SRT from a timeline, SRT -> ASS (libass) with brand font and platform safe areas.

- planned_srt(lines, path): lines = [{"text", "at"}] -> SRT with word-timed cues (syllable estimate), <=30 chars per cue.
- srt_to_ass(srt, ass, width, height, font="Jost Medium"): ASS with an opaque translucent plate, positioned in the
  safe area (9:16: bottom edge at 70% height; 16:9: at 88%).
- burn filter: subtitles='file.ass':fontsdir='brands/<brand>/fonts'
Stdlib only.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "brands/lullia/campaigns/c03-o-futuro-nao-espera/tools"))


def fmt_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def fmt_ass(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def planned_srt(lines, path, max_chars=30, rate_syl=4.6):
    from vo_timing import syl
    cues = []
    for L in lines:
        words = L["text"].split()
        durs = [max(0.12, syl(re.sub(r"[^\wÀ-ÿ™.]", "", w) or "a") / rate_syl + (0.18 if re.search(r"[,.:?!]$", w) else 0)) for w in words]
        t, cur, start = L["at"], [], L["at"]
        for w, d in zip(words, durs):
            if cur and len(" ".join(cur + [w])) > max_chars:
                cues.append((start, t, " ".join(cur))); cur, start = [], t
            cur.append(w); t += d
            if re.search(r"[.?!]$", w) and len(cur) >= 2:
                cues.append((start, t, " ".join(cur))); cur, start = [], t
        if cur:
            cues.append((start, t, " ".join(cur)))
    cues.sort()
    out = []
    for i, (a, b, txt) in enumerate(cues):
        if i + 1 < len(cues):
            b = min(b + 0.25, cues[i + 1][0])
        out.append(f"{i + 1}\n{fmt_srt(a)} --> {fmt_srt(b)}\n{txt}\n")
    Path(path).write_text("\n".join(out), encoding="utf-8")
    return len(out)


def read_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8").strip()):
        ls = block.strip().splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ls[1]) if len(ls) >= 3 else None
        if m:
            v = list(map(int, m.groups()))
            cues.append((v[0] * 3600 + v[1] * 60 + v[2] + v[3] / 1000, v[4] * 3600 + v[5] * 60 + v[6] + v[7] / 1000, " ".join(ls[2:])))
    return cues


def srt_to_ass(srt, ass, width, height, font="Jost Medium", color_hex="EFEAE0"):
    vertical = height > width
    size = round((46 if vertical else 40) * min(width, height) / 1080)
    margin_v = round(height * (0.30 if vertical else 0.12))
    r, g, b = color_hex[0:2], color_hex[2:4], color_hex[4:6]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,{font},{size},&H00{b}{g}{r},&H00FFFFFF,&H70191410,&H70191410,0,0,0,0,100,100,0.5,0,3,{round(size*0.32)},0,2,{round(width*0.08)},{round(width*0.08)},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 0,{fmt_ass(a)},{fmt_ass(b)},Brand,,0,0,0,,{t}" for a, b, t in read_srt(srt)]
    Path(ass).write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    return len(ev)


def burn_filter(ass, fontsdir):
    return f"subtitles='{ass}':fontsdir='{fontsdir}'"
