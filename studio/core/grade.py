#!/usr/bin/env python3
"""Per-act color grades as 3D LUTs (.cube), generated deterministically (stdlib only), applied with FFmpeg lut3d.

Looks (V4.3 color script):
  cold   — Act I pressure: steel blue, desaturated, lifted-free blacks toward nero, ~4:1 contrast
  night  — Act II clarity: cool shadows, warm brass highlights (split-tone), low key
  warm   — Act III LULLIA: warm natural, bone highlights, gentle contrast
  golden — Act IV decision: amber/brass highlights, preserved nero blacks
Usage:
  python3 studio/core/grade.py write-luts OUT_DIR
  python3 studio/core/grade.py apply IN.mp4 OUT.mp4 --look cold [--luts-dir DIR]
"""
import argparse
import subprocess
from pathlib import Path

NERO = (15 / 255, 20 / 255, 25 / 255)
LOOKS = {
    #        sat   contrast  shadow tint (rgb add)       highlight tint (rgb mul)   black point
    "cold":   (0.66, 1.08, (-0.005, 0.000, 0.012), (0.97, 0.99, 1.03), 0.020),
    "night":  (0.78, 1.12, (-0.006, 0.000, 0.014), (1.04, 1.00, 0.93), 0.022),
    "warm":   (0.94, 1.04, (0.006, 0.003, -0.004), (1.025, 1.00, 0.96), 0.015),
    "golden": (0.96, 1.10, (0.006, 0.002, -0.006), (1.05, 1.00, 0.92), 0.018),
}


def _clamp(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def transform(r, g, b, look):
    sat, con, sh, hi, bp = LOOKS[look]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    r, g, b = (y + (c - y) * sat for c in (r, g, b))                      # saturation
    r, g, b = ((c - 0.5) * con + 0.5 for c in (r, g, b))                  # contrast around mid grey
    w = _clamp(1 - y * 1.6)                                               # shadow weight
    h = _clamp((y - 0.45) / 0.55)                                         # highlight weight
    r, g, b = (c + w * d for c, d in zip((r, g, b), sh))                  # shadow tint
    r, g, b = (c * (1 - h + h * m) for c, m in zip((r, g, b), hi))        # highlight tint
    r, g, b = (n + (c - bp) * (1 - n) / (1 - bp) if c > bp else n * c / bp for c, n in zip((r, g, b), NERO))  # blacks to nero
    return tuple(_clamp(c) for c in (r, g, b))


def write_lut(path, look, size=33):
    lines = [f'TITLE "LULLIA {look}"', f"LUT_3D_SIZE {size}"]
    for bi in range(size):
        for gi in range(size):
            for ri in range(size):
                lines.append("%.6f %.6f %.6f" % transform(ri / (size - 1), gi / (size - 1), bi / (size - 1), look))
    Path(path).write_text("\n".join(lines) + "\n")


def lut_filter(look, luts_dir):
    return f"lut3d=file='{Path(luts_dir) / (look + '.cube')}':interp=tetrahedral"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write-luts"); w.add_argument("out_dir")
    a = sub.add_parser("apply"); a.add_argument("src"); a.add_argument("dst"); a.add_argument("--look", required=True, choices=LOOKS)
    a.add_argument("--luts-dir", default="config/luts")
    x = ap.parse_args()
    if x.cmd == "write-luts":
        Path(x.out_dir).mkdir(parents=True, exist_ok=True)
        for k in LOOKS:
            write_lut(Path(x.out_dir) / f"{k}.cube", k)
        print("wrote", ", ".join(f"{k}.cube" for k in LOOKS))
    else:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", x.src, "-vf", lut_filter(x.look, x.luts_dir), x.dst], check=True)


if __name__ == "__main__":
    main()
