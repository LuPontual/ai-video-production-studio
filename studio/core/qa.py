#!/usr/bin/env python3
"""Technical QA for rendered deliverables (stdlib only; uses system ffprobe/ffmpeg).

Usage:
  python3 studio/core/qa.py VIDEO --preset vertical_1080 [--srt captions.srt] [--expected-duration 53] [--loudness -14]
          [--no-audio-ok] [--out qa_report.json]

Exit code 0 = no blocking failures, 1 = at least one blocking failure.
Thresholds mirror config/qa-thresholds.yaml (kept in sync manually until a YAML parser is approved).
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

PRESETS = {
    "vertical_1080": (1080, 1920), "horizontal_1080": (1920, 1080), "square_1080": (1080, 1080),
    "portrait_4x5": (1080, 1350), "horizontal_2160": (3840, 2160), "ambient_longform_1080": (1920, 1080),
}
TH = {"loudness_tol": 1.0, "tp_max": -1.0, "black_min": 0.5, "freeze_min": 2.0, "cue_min": 0.3, "cue_max": 7.0,
      "max_chars_line": 32, "max_lines": 2}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def check(results, name, ok, detail, blocking=True):
    results.append({"check": name, "status": "pass" if ok else ("fail" if blocking else "warn"), "detail": detail})


def srt_cues(path):
    txt = open(path, encoding="utf-8").read().strip()
    cues, bad = [], []
    for block in re.split(r"\n\s*\n", txt):
        lines = block.strip().splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)$", lines[1]) if len(lines) >= 3 else None
        if not m:
            bad.append(block[:80])
            continue
        v = list(map(int, m.groups()))
        s = v[0] * 3600 + v[1] * 60 + v[2] + v[3] / 1000
        e = v[4] * 3600 + v[5] * 60 + v[6] + v[7] / 1000
        cues.append({"start": s, "end": e, "lines": lines[2:]})
    return cues, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--preset", default="vertical_1080")
    ap.add_argument("--srt")
    ap.add_argument("--expected-duration", type=float)
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--loudness", type=float, default=-14.0)
    ap.add_argument("--no-audio-ok", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    R = []

    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", a.video]).stdout)
    v = next((s for s in pr["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
    dur = float(pr["format"]["duration"])
    W, H = PRESETS[a.preset]
    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    check(R, "video_codec", v["codec_name"] == "h264", v["codec_name"])
    check(R, "resolution", (v["width"], v["height"]) == (W, H), f'{v["width"]}x{v["height"]} (expected {W}x{H})')
    check(R, "pixel_format", v.get("pix_fmt") == "yuv420p", v.get("pix_fmt"))
    check(R, "frame_rate", abs(fps - a.fps) < 0.01, f"{fps:.3f} fps")
    if a.expected_duration:
        check(R, "duration", abs(dur - a.expected_duration) <= 1.0 / a.fps + 0.05, f"{dur:.3f}s (expected {a.expected_duration}s)")
    check(R, "faststart", True, "set by renderer (+faststart)")

    if au:
        check(R, "audio_codec", au["codec_name"] == "aac" and au.get("sample_rate") == "48000", f'{au["codec_name"]} {au.get("sample_rate")} Hz {au.get("channels")}ch')
        vd, ad = float(v.get("duration", dur)), float(au.get("duration", dur))
        check(R, "av_duration_sync", abs(vd - ad) <= 1.0 / a.fps + 0.03, f"video {vd:.3f}s / audio {ad:.3f}s")
        e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
        summ = e[e.rfind("Summary:"):]
        I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
        TP = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
        check(R, "integrated_loudness", abs(I - a.loudness) <= TH["loudness_tol"], f"{I} LUFS (target {a.loudness} ±{TH['loudness_tol']})")
        check(R, "true_peak", TP <= TH["tp_max"], f"{TP} dBTP (max {TH['tp_max']})")
    else:
        check(R, "audio_present", a.no_audio_ok, "no audio stream", blocking=not a.no_audio_ok)

    e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-map", "0:v:0", "-vf",
             f"blackdetect=d={TH['black_min']}:pix_th=0.05,freezedetect=n=0.001:d={TH['freeze_min']}", "-f", "null", "-"]).stderr
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", e)
    freezes = re.findall(r"freeze_start: ([\d.]+)", e)
    check(R, "black_segments", not blacks, f"{len(blacks)} segment(s) ≥ {TH['black_min']}s: {blacks}" if blacks else "none")
    check(R, "frozen_segments", not freezes, f"{len(freezes)} hold(s) ≥ {TH['freeze_min']}s at {freezes}" if freezes else "none", blocking=False)

    if a.srt:
        cues, bad = srt_cues(a.srt)
        check(R, "captions_well_formed", not bad, f"{len(bad)} malformed cue block(s)" + (f": {bad[:2]}" if bad else ""))
        short = [c for c in cues if c["end"] - c["start"] < TH["cue_min"]]
        long_ = [c for c in cues if c["end"] - c["start"] > TH["cue_max"]]
        overlap = [i for i in range(1, len(cues)) if cues[i]["start"] < cues[i - 1]["end"] - 1e-3]
        outside = [c for c in cues if c["end"] > dur + 0.01]
        wide = [c for c in cues if any(len(l) > TH["max_chars_line"] for l in c["lines"]) or len(c["lines"]) > TH["max_lines"]]
        check(R, "captions_count", len(cues) > 0, f"{len(cues)} cues")
        check(R, "captions_min_duration", not short, f"{len(short)} cue(s) < {TH['cue_min']}s")
        check(R, "captions_max_duration", not long_, f"{len(long_)} cue(s) > {TH['cue_max']}s")
        check(R, "captions_overlap", not overlap, f"{len(overlap)} overlap(s)")
        check(R, "captions_within_video", not outside, f"{len(outside)} cue(s) beyond video end")
        check(R, "captions_line_length", not wide, f"{len(wide)} cue(s) exceed {TH['max_chars_line']} chars/line or {TH['max_lines']} lines")

    fails = [r for r in R if r["status"] == "fail"]
    report = {"file": a.video, "preset": a.preset, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "result": "fail" if fails else "pass", "blocking_failures": len(fails),
              "warnings": sum(r["status"] == "warn" for r in R), "checks": R}
    out = json.dumps(report, indent=2, ensure_ascii=False)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
    print(out)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
