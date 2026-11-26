#!/usr/bin/env python3
"""Estimate PT-BR voice-over/dialogue duration by syllable count (heuristic) for timeline planning.
Calm commercial narration: ~4.2-5.0 syllables/s (nominal 4.6). Dialogue: ~4.6-5.6 (nominal 5.0).
Adds a breath per sentence break. Real durations are re-measured from the recorded VO with Whisper."""
import re, json, sys
V = "aeiouáéíóúâêôãõàü"
def syl(w):
    w = w.lower().replace("™", "")
    if re.fullmatch(r"[\d.]+", w): return 3
    w = re.sub(r"(qu|gu)(?=[eiéí])", "q", w)
    g = re.findall(rf"[{V}]+", w)
    n = 0
    for grp in g:  # split hiatus-like groups crudely: falling diphthongs count 1, others 2
        n += 1 if len(grp) == 1 or re.fullmatch(r"[aeoáéóâêôãõ][iu]|[ãõ][eo]|[iu][aeo]", grp) else len(grp) - 1 if len(grp) > 2 else 1
    return max(1, n)
def est(text, kind):
    words = re.findall(r"[\wÀ-ÿ™.]+", text)
    s = sum(syl(w) for w in words)
    breaks = len(re.findall(r"[.,:?!—]", text))
    lo_r, nom_r, hi_r = (4.2, 4.6, 5.0) if kind == "vo" else (4.6, 5.0, 5.6)
    b = 0.18 * breaks
    return {"words": len(words), "syl": s, "min": round(s / hi_r + b, 2), "nom": round(s / nom_r + b, 2), "max": round(s / lo_r + b, 2)}
if __name__ == "__main__":
    lines = json.load(open(sys.argv[1]))
    tot = {"min": 0, "nom": 0, "max": 0, "words": 0}
    for L in lines:
        e = est(L["text"], L["kind"]); L.update(e)
        for k in tot: tot[k] += e[k]
        print(f'{L["id"]:5} {L["kind"]:4} {e["words"]:3}w {e["syl"]:3}s  {e["min"]:5.2f}–{e["max"]:5.2f}s (nom {e["nom"]:5.2f})  {L["text"]}')
    print(f'TOTAL speech: {tot["words"]} words · {tot["min"]:.1f}–{tot["max"]:.1f}s (nominal {tot["nom"]:.1f}s)')
