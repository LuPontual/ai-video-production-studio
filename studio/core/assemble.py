#!/usr/bin/env python3
"""Assemble a film from a production spec (shots with in/out, act, composites) into 16:9 and 9:16 masters.

For each shot it uses, in order: clips/shot_NN_9x16.mp4 (native vertical) | clips/shot_NN.mp4 (16:9; cropped for 9:16)
| a generated slate (animatic placeholder). Then: trim -> scale/crop -> per-act LUT -> brand labels -> concat
-> burned brand captions -> audio mix (voice ducking music, 2-pass loudness) -> mux -> QA.

Usage:
  python3 studio/core/assemble.py SPEC.json --clips DIR --out DIR --aspect 16x9|9x16 [--voice VO.wav] [--music M.wav]
         [--srt captions.srt] [--endcard PNG] [--luts config/luts] [--fonts brands/lullia/fonts] [--tag animatic]
Without --srt, captions are planned from the spec's speech lines (syllable timing).
"""
import argparse
import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio_mix  # noqa: E402
import captions  # noqa: E402

GRADE = {"I": "cold", "II": "night", "III": "warm", "IV": "golden"}
SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}


def ff(*args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-2000:])


def slate(shot, W, H, path, font_dir):
    """Animatic placeholder: shot number, timecode, framing and action on the act's tone (clearly marked as placeholder)."""
    tone = {"I": "#1c2630", "II": "#14161f", "III": "#2a2219", "IV": "#2e2416", "V": "#0F1419"}[shot["act"]]
    body = "\n".join(textwrap.wrap(shot["action"], 46 if H > W else 70))
    head = f"PLANO {shot['n']:02d} · {shot['in']:.1f}–{shot['out']:.1f} s · ATO {shot['act']}"
    sub = f"{shot.get('framing', '')} · {shot.get('lens', '')} · {shot.get('camera', '')}"
    s = min(W, H) / 1080
    subprocess.run(["convert", "-size", f"{W}x{H}", f"xc:{tone}",
                    "-font", str(Path(font_dir) / "Jost-Regular.ttf"), "-fill", "#DCC08A", "-pointsize", str(int(30 * s)), "-gravity", "northwest",
                    "-annotate", f"+{int(80*s)}+{int(H*0.18)}", head,
                    "-fill", "#9B9B93", "-pointsize", str(int(26 * s)), "-annotate", f"+{int(80*s)}+{int(H*0.18 + 52*s)}", sub,
                    "-font", str(Path(font_dir) / "BodoniModa-Regular.ttf"), "-fill", "#EFEAE0", "-pointsize", str(int(44 * s)),
                    "-annotate", f"+{int(80*s)}+{int(H*0.18 + 130*s)}", body,
                    "-font", str(Path(font_dir) / "Jost-Light.ttf"), "-fill", "#9B9B93", "-pointsize", str(int(22 * s)), "-gravity", "southwest",
                    "-annotate", f"+{int(80*s)}+{int(80*s)}", "ANIMATIC · PLACEHOLDER (sem imagem gerada)", str(path)], check=True)


def label_filter(text, W, H, font_dir, dur):
    s = min(W, H) / 1080
    t = text.replace(":", r"\:").replace("'", r"\'")
    y = int(H * (0.12 if H > W else 0.09))
    return (f"drawtext=fontfile='{Path(font_dir) / 'Jost-Regular.ttf'}':text='{t}':fontcolor=0xDCC08A:fontsize={int(24*s)}:"
            f"x={int(W*0.07)}:y={y}:alpha='if(lt(t,0.3),t/0.3,if(gt(t,{dur-0.3}),({dur}-t)/0.3,1))'")


def build_segment(shot, aspect, clips, work, luts, fonts, endcard):
    W, H = SIZES[aspect]
    dur = round(shot["out"] - shot["in"], 3)
    seg = work / f"seg_{shot['n']:02d}.mp4"
    native = Path(clips) / f"shot_{shot['n']:02d}_{aspect}.mp4"
    master = Path(clips) / f"shot_{shot['n']:02d}.mp4"
    vf, inp, kind = [], None, "clip"
    if shot.get("local") and endcard:
        inp, kind = ["-loop", "1", "-i", endcard], "endcard"
        vf.append(f"scale={W}:{H},fade=t=in:st=0:d=0.6")
    elif native.exists():
        inp = ["-i", native]; vf.append(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}")
    elif master.exists():
        inp = ["-i", master]
        vf.append(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}" if aspect == "16x9" else f"crop=ih*9/16:ih,scale={W}:{H}")
    else:
        png = work / f"slate_{shot['n']:02d}.png"; slate(shot, W, H, png, fonts)
        inp, kind = ["-loop", "1", "-i", png], "slate"
    if kind == "clip":
        vf.append("tpad=stop_mode=clone:stop_duration=10")  # hold last frame if the clip is shorter than the shot
    if kind == "clip" and shot["act"] in GRADE:
        vf.append(f"lut3d=file='{Path(luts) / (GRADE[shot['act']] + '.cube')}':interp=tetrahedral")
    for item in shot.get("composite", []):
        if item.startswith("label:"):
            vf.append(label_filter(item.split(":", 1)[1].strip(), W, H, fonts, dur))
    vf += ["fps=24", "format=yuv420p"]
    ff(*inp, "-t", dur, "-vf", ",".join(vf), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-r", "24", seg)
    return seg, kind


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--clips", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--aspect", choices=SIZES, default="16x9"); ap.add_argument("--voice"); ap.add_argument("--music"); ap.add_argument("--srt")
    ap.add_argument("--endcard"); ap.add_argument("--luts", default=str(ROOT / "config/luts")); ap.add_argument("--fonts", default=str(ROOT / "brands/lullia/fonts"))
    ap.add_argument("--tag", default="cut")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    W, H = SIZES[a.aspect]
    out = Path(a.out); work = out / f"work_{a.aspect}"; work.mkdir(parents=True, exist_ok=True)
    segs, kinds = [], {}
    for s in spec["shots"]:
        seg, kind = build_segment(s, a.aspect, a.clips, work, a.luts, a.fonts, a.endcard)
        segs.append(seg); kinds[s["n"]] = kind
    lst = work / "concat.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in segs))
    silent = work / "video.mp4"; ff("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", silent)
    # captions
    srt = Path(a.srt) if a.srt else work / "captions_planned.srt"
    if not a.srt:
        lines = []
        for s in spec["shots"]:
            for k in ("line", "vo"):
                if k in s.get("audio", {}):
                    lines.append({"text": s["audio"][k]["text"], "at": s["audio"][k]["at"]})
        captions.planned_srt(lines, srt)
    end_t = next((s["in"] for s in spec["shots"] if s.get("local")), None)
    if end_t is not None:   # clip cues at the end card: on-screen CTA already shows the same words
        kept = [(x, min(y, end_t), t) for x, y, t in captions.read_srt(srt) if x < end_t - 0.3]
        clipped = work / "captions_burn.srt"
        clipped.write_text("\n".join(f"{i+1}\n{captions.fmt_srt(x)} --> {captions.fmt_srt(y)}\n{t}\n" for i, (x, y, t) in enumerate(kept)), encoding="utf-8")
    else:
        clipped = srt
    ass = work / "captions.ass"; captions.srt_to_ass(clipped, ass, W, H)
    burned = work / "video_captioned.mp4"
    ff("-i", silent, "-vf", captions.burn_filter(ass, a.fonts), "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", burned)
    # audio
    dur = spec["film"]["duration_s"]
    mixwav = work / "mix.wav"; info = audio_mix.mix(mixwav, dur, voice=a.voice, music=a.music)
    final = out / f"{spec['film']['id']}_{a.tag}_{a.aspect}.mp4"
    ff("-i", burned, "-i", mixwav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", 48000, "-t", dur, "-movflags", "+faststart", final)
    preset = "horizontal_1080" if a.aspect == "16x9" else "vertical_1080"
    qa = subprocess.run([sys.executable, str(ROOT / "studio/core/qa.py"), final, "--preset", preset, "--srt", srt, "--expected-duration", str(dur),
                         "--fps", "24", "--out", out / f"qa_{a.tag}_{a.aspect}.json"], capture_output=True, text=True)
    print(json.dumps({"output": str(final), "segments": kinds, "audio": info, "qa": "pass" if qa.returncode == 0 else "fail"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
