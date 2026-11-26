#!/usr/bin/env python3
"""Technical scorecard for a generated still (keyframe / character test). Uses ImageMagick + numpy (system).

python3 studio/core/image_qa.py IMAGE --look cold|night|warm|golden [--out report.json]

Measured (objective): resolution, sharpness (Laplacian std on luma), clipped shadows/highlights, mean saturation,
midtone temperature (blue-minus-red) vs the act's intended look, overall exposure. Creative criteria (realism, anatomy,
likeness, cinematic credibility) stay human-scored in the same report template.
"""
import argparse
import json
import subprocess
import numpy as np

LOOK_TEMP = {"cold": (2.0, 40.0), "night": (-40.0, 40.0), "warm": (-40.0, 2.0), "golden": (-60.0, -2.0)}  # (min,max) of B-R in midtones


def load(path, width=1280):
    raw = subprocess.run(["convert", path, "-resize", f"{width}x>", "-depth", "8", "ppm:-"], capture_output=True, check=True).stdout
    parts = raw.split(maxsplit=4)
    w, h = int(parts[1]), int(parts[2])
    return np.frombuffer(parts[4][: w * h * 3], dtype=np.uint8).reshape(h, w, 3).astype(np.float32)


def size(path):
    w, h = subprocess.run(["identify", "-format", "%w %h", path + "[0]"], capture_output=True, text=True, check=True).stdout.split()
    return int(w), int(h)


def analyze(path, look):
    W, H = size(path)
    img = load(path)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    lap = (-4 * y[1:-1, 1:-1] + y[:-2, 1:-1] + y[2:, 1:-1] + y[1:-1, :-2] + y[1:-1, 2:])
    mx, mn = img.max(-1), img.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    mid = (y > 60) & (y < 190)
    temp = float((b[mid] - r[mid]).mean()) if mid.any() else 0.0
    m = {"width": W, "height": H, "sharpness_lap_std": round(float(lap.std()), 2),
         "clip_shadows_pct": round(float((y <= 2).mean() * 100), 2), "clip_highlights_pct": round(float((y >= 253).mean() * 100), 2),
         "mean_luma": round(float(y.mean()), 1), "mean_saturation": round(float(sat.mean()), 3), "midtone_b_minus_r": round(temp, 1)}
    lo, hi = LOOK_TEMP[look]
    checks = [
        ("resolution_long_side_>=1920", max(W, H) >= 1920),
        ("sharpness_not_soft (lap std >= 6)", m["sharpness_lap_std"] >= 6),
        ("highlights_not_clipped (<= 1.5%)", m["clip_highlights_pct"] <= 1.5),
        ("shadows_not_crushed (<= 8%)", m["clip_shadows_pct"] <= 8),
        ("saturation_restrained (<= 0.45)", m["mean_saturation"] <= 0.45),
        (f"temperature_matches_{look} ({lo}..{hi})", lo <= temp <= hi),
    ]
    return m, [{"check": c, "pass": bool(ok)} for c, ok in checks]


CREATIVE = ["1 Pele e olhos fotorrealistas", "2 Anatomia sem artefatos", "3 Luz motivada conforme keyframe", "4 Ótica crível (85 mm, bokeh)",
            "5 Fidelidade ao briefing da personagem", "6 Cor dentro da paleta da cena", "7 Sem texto/logos", "8 Composição utilizável e recorte 9:16",
            "9 Teste cego: still de comercial de alto padrão"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("image"); ap.add_argument("--look", required=True, choices=LOOK_TEMP); ap.add_argument("--out")
    a = ap.parse_args()
    m, checks = analyze(a.image, a.look)
    rep = {"image": a.image, "look": a.look, "metrics": m, "technical": checks, "technical_pass": all(c["pass"] for c in checks),
           "creative_scores_1to5": {c: None for c in CREATIVE},
           "decision_rule": "APROVA se técnico = pass, critérios 1–5 >= 4 e nenhum < 3"}
    out = json.dumps(rep, indent=2, ensure_ascii=False)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
    print(out)
