#!/usr/bin/env python3
"""Film audio mix: voice (VO + dialogue) over music with sidechain ducking, timed SFX, two-pass loudness.

mix(out, duration, voice=None, music=None, sfx=[(path, at_s, gain_db)], target_lufs=-14, tp=-1.5)
- Voice chain: high-pass 80 Hz, gentle compression, de-ess-like high-shelf cut.
- Music ducked under voice (sidechaincompress), -10..-12 dB effective.
- Loudness: two-pass loudnorm (linear) to target, true peak margin for AAC.
Missing inputs are replaced by silence, so the same call works for animatics and finals.
"""
import json
import subprocess
from pathlib import Path


def _run(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", *args], capture_output=True, text=True)


def mix(out, duration, voice=None, music=None, sfx=(), target_lufs=-14.0, tp=-1.5):
    out = Path(out); tmp = out.with_suffix(".premix.wav")
    ins, fl = [], []
    def add(path):
        ins.append(["-i", str(path)] if path else ["-f", "lavfi", "-t", str(duration), "-i", "anullsrc=r=48000:cl=stereo"])
        return len(ins) - 1
    vi = add(voice); mi = add(music)
    fl.append(f"[{vi}:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=80,acompressor=threshold=0.12:ratio=3:attack=8:release=120,highshelf=f=7000:g=-2,apad,atrim=0:{duration}[v]")
    fl.append(f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,volume=-6dB,apad,atrim=0:{duration}[m]")
    fl.append("[v]asplit=2[vk][vm]")
    fl.append("[m][vk]sidechaincompress=threshold=0.01:ratio=4:attack=20:release=500:level_sc=2:makeup=1[md]")
    labels = ["[vm]", "[md]"]
    for k, (path, at, gain) in enumerate(sfx):
        idx = add(path)
        fl.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,adelay={int(at*1000)}|{int(at*1000)},apad,atrim=0:{duration}[s{k}]")
        labels.append(f"[s{k}]")
    fl.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{duration}[mx]")
    r = _run([*[x for grp in ins for x in grp], "-filter_complex", ";".join(fl), "-map", "[mx]", "-c:a", "pcm_s24le", str(tmp)])
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    meas = _run(["-i", str(tmp), "-af", f"loudnorm=I={target_lufs}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"]).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    if float(j["input_i"]) < -70:   # silent mix (animatic without audio): skip normalization
        tmp.rename(out); return {"lufs": None, "note": "silent"}
    ln = (f"loudnorm=I={target_lufs}:TP={tp}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
    r = _run(["-i", str(tmp), "-af", ln, "-c:a", "pcm_s24le", str(out)])
    tmp.unlink(missing_ok=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return {"input_lufs": float(j["input_i"]), "target": target_lufs}
