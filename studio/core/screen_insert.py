#!/usr/bin/env python3
"""Screen replacement: warp a real UI capture (image or video) onto a four-corner quad of a locked-off plate.

insert(plate, screen, quad, out)  quad = [(x0,y0) top-left, (x1,y1) top-right, (x2,y2) bottom-left, (x3,y3) bottom-right]
in plate pixel coordinates. The capture is padded with a transparent border so pixels outside the quad stay
transparent after the perspective warp; a slight blur and brightness match keep it photographic.
For moving shots, export per-frame corner tracks and use the same filter with sendcmd (not needed for locked-off shot 9).
"""
import subprocess


def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    return int(out[0]), int(out[1])


def insert(plate, screen, quad, out, brightness=-0.04, blur=0.6, still_seconds=None, overscan=2):
    W, H = probe_size(plate)
    cx = sum(x for x, _ in quad) / 4; cy = sum(y for _, y in quad) / 4
    k = 1 + overscan / max(1.0, min(abs(quad[1][0] - quad[0][0]), abs(quad[2][1] - quad[0][1])) / 2)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = [(round(cx + (x - cx) * k, 1), round(cy + (y - cy) * k, 1)) for x, y in quad]
    pre = ["-loop", "1"] if screen.lower().endswith((".png", ".jpg", ".jpeg")) else []
    fc = (f"[1:v]format=rgba,pad=iw+4:ih+4:2:2:color=black@0,scale={W}:{H},"
          f"perspective={x0}:{y0}:{x1}:{y1}:{x2}:{y2}:{x3}:{y3}:sense=destination:interpolation=cubic,"
          f"eq=brightness={brightness},gblur=sigma={blur}[scr];"
          f"[0:v][scr]overlay=0:0:shortest=1:format=auto,format=yuv420p[v]")
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", plate, *pre, "-i", screen, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
            "-c:v", "libx264", "-crf", "16", "-preset", "medium"]
    if still_seconds:
        args += ["-t", str(still_seconds)]
    subprocess.run(args + [out], check=True)
