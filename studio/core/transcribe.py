#!/usr/bin/env python3
"""Word-level transcription + caption generation with Faster-Whisper (local, CPU int8).

Run with the isolated environment:
  tools/whisper/.venv/bin/python studio/core/transcribe.py VO.wav --lang pt --out-dir jobs/<job>/work/ \
      [--model small] [--script script.txt] [--max-chars 30]

Outputs: transcript.json (segments + words with start/end/probability) and captions.srt (≤ max-chars per line, 1 line/cue).
With --script, the reference script is compared word-by-word to flag likely mis-hearings (brand terms such as ICEIA™, LULLIA).
Models are read from ./models (pre-downloaded); nothing is uploaded anywhere.
"""
import argparse
import difflib
import json
import re
from pathlib import Path


def fmt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def chunk(words, max_chars):
    cues, cur = [], []
    for w in words:
        if cur and len(" ".join(x["word"] for x in cur)) + len(w["word"]) + 1 > max_chars:
            cues.append(cur); cur = []
        cur.append(w)
        if re.search(r"[,.:?!—]$", w["word"]) and len(cur) >= 2:
            cues.append(cur); cur = []
    if cur:
        cues.append(cur)
    return cues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--model", default="small")
    ap.add_argument("--models-dir", default="models")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--script")
    ap.add_argument("--max-chars", type=int, default=30)
    a = ap.parse_args()

    from faster_whisper import WhisperModel, download_model
    path = download_model(a.model, cache_dir=a.models_dir)  # resolves the local cache; downloads only if missing
    model = WhisperModel(path, device="cpu", compute_type="int8")
    prompt = None
    if a.script:
        prompt = Path(a.script).read_text(encoding="utf-8")[:800]  # biases spelling of brand terms
    # Decode with system FFmpeg (16 kHz mono float32) instead of PyAV: the PyAV build pulled in by faster-whisper 1.2.1
    # here rejects faster-whisper's own open() arguments; FFmpeg is the studio's validated media engine anyway.
    import subprocess
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-i", a.audio, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.float32)
    segs, info = model.transcribe(audio, language=a.lang, word_timestamps=True, vad_filter=True,
                                  initial_prompt=prompt, beam_size=5)
    segments, words = [], []
    for s in segs:
        ws = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 3)} for w in s.words]
        segments.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": ws})
        words += ws
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    report = {"language": info.language, "duration": info.duration, "model": a.model, "segments": segments}

    if a.script:
        ref = re.findall(r"[\wÀ-ÿ™]+", Path(a.script).read_text(encoding="utf-8").lower())
        hyp = [re.sub(r"[^\wÀ-ÿ™]", "", w["word"].lower()) for w in words]
        sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
        report["script_match_ratio"] = round(sm.ratio(), 4)
        report["script_diffs"] = [{"op": op, "script": " ".join(ref[i1:i2]), "heard": " ".join(hyp[j1:j2])}
                                  for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]

    (out / "transcript.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    cues = chunk(words, a.max_chars)
    srt = []
    for i, c in enumerate(cues):
        end = c[-1]["end"]
        if i + 1 < len(cues):
            end = min(end + 0.25, cues[i + 1][0]["start"])
        srt.append(f"{i + 1}\n{fmt(c[0]['start'])} --> {fmt(end)}\n{' '.join(w['word'] for w in c)}\n")
    (out / "captions.srt").write_text("\n".join(srt), encoding="utf-8")
    print(json.dumps({"words": len(words), "cues": len(cues), "language": info.language,
                      "script_match_ratio": report.get("script_match_ratio")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
