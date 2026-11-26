#!/usr/bin/env python3
"""Validate the V4.3 production spec and build prompts, budget and the production bible.

Usage: python3 build.py            (writes prompts/, PROMPTS.md, BIBLE.md, budget.json; exits 1 on validation errors)
Inputs: spec.json (single source of truth) + ../tools/vo_timing.py (speech duration estimate).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from vo_timing import est  # noqa: E402

S = json.loads((HERE / "spec.json").read_text(encoding="utf-8"))
F, ST, CH, SETS, SH, M = S["film"], S["style"], S["characters"], S["sets"], S["shots"], S["models"]
errors, warnings = [], []

# ---------- validation ----------
t = 0.0
for s in SH:
    if abs(s["in"] - t) > 1e-6:
        errors.append(f"shot {s['n']}: starts at {s['in']} but previous ended at {t}")
    if s["out"] <= s["in"]:
        errors.append(f"shot {s['n']}: non-positive duration")
    t = s["out"]
    if s.get("set") and s["set"] not in SETS:
        errors.append(f"shot {s['n']}: unknown set {s['set']}")
    for c in s.get("chars", []):
        if c not in CH:
            errors.append(f"shot {s['n']}: unknown character {c}")
    for c, w in s.get("wardrobe", {}).items():
        if w not in CH[c]["wardrobe"]:
            errors.append(f"shot {s['n']}: {c} has no wardrobe {w}")
    if s["act"] not in ST["acts"]:
        errors.append(f"shot {s['n']}: unknown act")
    if s.get("gen") and (s["out"] - s["in"]) > 6.0:
        errors.append(f"shot {s['n']}: {s['out']-s['in']:.1f}s exceeds a 6s generation")
if abs(t - F["duration_s"]) > 1e-6:
    errors.append(f"timeline ends at {t}, film is {F['duration_s']}")

# speech: estimated windows, overlaps and film end
speech = []
for s in SH:
    a = s.get("audio", {})
    for key in ("line", "vo"):
        if key in a:
            e = est(a[key]["text"], "dlg" if key == "line" else "vo")
            speech.append({"shot": s["n"], "kind": key, "text": a[key]["text"], "start": a[key]["at"],
                           "end_nom": round(a[key]["at"] + e["nom"], 2), "end_max": round(a[key]["at"] + e["max"], 2)})
speech.sort(key=lambda x: x["start"])
for i, sp in enumerate(speech):
    nxt = speech[i + 1]["start"] if i + 1 < len(speech) else F["duration_s"]
    if sp["end_nom"] > nxt:
        errors.append(f"speech '{sp['text'][:30]}…' (nominal end {sp['end_nom']}s) overlaps next at {nxt}s")
    elif sp["end_max"] > nxt:
        warnings.append(f"speech '{sp['text'][:30]}…' could overrun to {sp['end_max']}s with a slow narrator (next at {nxt}s): trim the following shot")
spoken_words = sum(est(sp["text"], "vo")["words"] for sp in speech)

# wardrobe continuity per day block
day = {1: "A", 2: "A", 3: "A", 7: "A", 8: "B", 9: "B", 10: "A", 11: "A", 14: "B", 15: "B", 16: "A", 17: "A", 18: "A", 21: "A"}
for s in SH:
    w = s.get("wardrobe", {}).get("helena")
    if w and s["n"] in day and day[s["n"]] != w:
        errors.append(f"shot {s['n']}: Helena wardrobe {w} breaks continuity (expected {day[s['n']]})")

# ---------- prompts ----------
def char_text(c, s):
    w = s.get("wardrobe", {}).get(c) or next(iter(CH[c]["wardrobe"]))
    return f"{CH[c]['name']}: {CH[c]['description']}, wearing {CH[c]['wardrobe'][w]}"

out_dir = HERE / "prompts"
out_dir.mkdir(exist_ok=True)
prompts = []
for s in SH:
    if not s.get("gen"):
        continue
    act = ST["acts"][s["act"]]
    refs = [f"{c}_sheet" for c in s["chars"] if c in ("helena", "augusto", "ana")][:2] + [f"set_{s['set']}"]
    def wtxt(c):
        w = s.get("wardrobe", {}).get(c)
        return f"{CH[c]['short']}" + (f" wearing {CH[c]['wardrobe'][w]}" if w else "")
    image_prompt = ". ".join([
        ST["compact_prefix"],
        f"{s['framing'].capitalize()}, {s['lens']} lens",
        SETS[s['set']]['description'].split(',')[0].capitalize(),
        *[wtxt(c) for c in s["chars"]],
        s["action"],
        f"Light: {s['light']}",
        "16:9, subject inside central 9:16 safe area" if s["vertical"] == "crop" else "16:9",
        ST["compact_avoid"],
    ])
    image_prompt = ". ".join(x.strip().rstrip(".") for x in image_prompt.split(". ") if x.strip()) + "."
    if len(image_prompt) > 950:
        errors.append(f"shot {s['n']}: keyframe prompt {len(image_prompt)} chars > 950 (Gen-4 Image limit 1000)")
    _unused_long_prompt = ". ".join([
        ST["global_prefix"],
        f"{s['framing'].capitalize()}, {s['lens']} lens, camera {s['camera']}",
        f"Setting: {SETS[s['set']]['description']}",
        *[char_text(c, s) for c in s["chars"]],
        f"Action: {s['action']}",
        f"Lighting: {s['light']}; overall look: {act['look']}",
        "Aspect ratio 16:9, keep the main subject inside the central vertical 9:16 safe area" if s["vertical"] == "crop" else "Aspect ratio 16:9 (a separate 9:16 composition will be generated)",
    ]) + "."
    video_prompt = (f"Cinematic, realistic motion. Camera: {s['move']}. {s['action']} "
                    f"Natural human micro-movements, no exaggerated gestures, no lip movement unless speaking is specified, "
                    f"keep lighting and wardrobe identical to the first frame. {act['look']}.")
    m = M[s["gen"]["model"]]
    p = {"shot": s["n"], "timecode": f"{s['in']:.1f}–{s['out']:.1f}", "act": s["act"], "edit_duration_s": round(s["out"] - s["in"], 2),
         "keyframe": {"model": "gen4_image_1080p", "model_id": M["gen4_image_1080p"]["id"], "aspect_ratio": "16:9", "resolution": "1080p",
                      "references": refs, "prompt": image_prompt, "negative": ST["global_negative"]},
         "video": {"model": s["gen"]["model"], "model_id": m["id"], "params": {**m["params"], "duration": s["gen"]["duration"], "aspect_ratio": "16:9"},
                   "first_frame": f"keyframe_{s['n']:02d}_approved.png", "prompt": video_prompt, "negative_prompt": ST["global_negative"]},
         "composite": s.get("composite", []), "vertical": s["vertical"]}
    if s["vertical"] == "own_9x16":
        p["vertical_variant"] = {"aspect_ratio": "9:16", "note": "recompose for vertical: subject centered, more headroom, same lighting"}
    (out_dir / f"shot_{s['n']:02d}.json").write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")
    prompts.append(p)

# reference assets (character sheets + set plates) — generated once, reused as references
ref_assets = []
for c in ("helena", "augusto", "ana"):
    for view in CH[c]["reference_sheet"]:
        ref_assets.append({"id": f"{c}_sheet_{view.replace(' ', '_')}", "prompt": ". ".join([
            ST["global_prefix"], f"Character reference, {view} view, head and shoulders, neutral dark charcoal background, soft 45 degree key light",
            char_text(c, {"wardrobe": {c: 'B' if 'wardrobe B' in view else 'A'}})]) + "."})
for k, v in SETS.items():
    if any(s.get("set") == k for s in SH):
        ref_assets.append({"id": f"set_{k}", "prompt": f"{ST['global_prefix']}. Empty set plate, no people, 24mm wide establishing view. {v['description']}."})
(HERE / "prompts" / "reference_assets.json").write_text(json.dumps(ref_assets, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------- budget (verified quotes) ----------
img_c = M["gen4_image_1080p"]["credits"]
n_ref = len(ref_assets)
n_key = len(prompts) + sum(1 for p in prompts if p["vertical"] == "own_9x16")
images = (n_ref + n_key) * 2 * img_c
video = sum(M[p["video"]["model"]]["credits_6s"] * next(s for s in SH if s["n"] == p["shot"])["gen"]["attempts"] * (2 if p["vertical"] == "own_9x16" else 1) for p in prompts)
# vertical strategy comparison: cropping 9:16 from a 1080p 16:9 master leaves 608 px of real width (soft).
vid_cost = lambda p: M[p["video"]["model"]]["credits_6s"] * next(s for s in SH if s["n"] == p["shot"])["gen"]["attempts"]
img_both = (n_ref + 2 * len(prompts)) * 2 * img_c
vertical_strategies = {
    "crop_from_1080p_master": {"credits": images + video, "vertical_quality": "LOW for 'crop' shots: 608 px real width upscaled to 1080"},
    "native_16x9_and_9x16_all_shots": {"credits": img_both + 2 * sum(vid_cost(p) for p in prompts), "vertical_quality": "full 1080x1920"},
    "native_9x16_only_then_16x9_later": {"credits": (n_ref + len(prompts)) * 2 * img_c + sum(vid_cost(p) for p in prompts), "vertical_quality": "full; 16:9 deferred to a second budget"},
}
budget = {"vertical_strategies": vertical_strategies, "assumptions": {"image_attempts": 2, "video_attempts_per_shot": "per spec (3)", "image_credits": img_c,
                          "veo31_standard_6s": M["veo31_standard"]["credits_6s"], "veo31_fast_6s": M["veo31_fast"]["credits_6s"], "source": "Figma Weave connector quotes, 2026-11-26"},
          "reference_assets": n_ref, "keyframes": n_key, "image_credits": images, "video_credits": video, "total_credits": images + video,
          "helena_single_image_test_max_credits": 2 * img_c}
(HERE / "budget.json").write_text(json.dumps(budget, indent=2), encoding="utf-8")

# ---------- documents ----------
md = [f"# Prompts de produção — {F['id']}", "", "Gerado por `build.py` a partir de `spec.json`. Não editar à mão.", ""]
for p in prompts:
    md += [f"## Plano {p['shot']:02d} · {p['timecode']} s · Ato {p['act']}", "", f"**Keyframe** ({p['keyframe']['model']}, refs: {', '.join(p['keyframe']['references'])})", "",
           "```text", p["keyframe"]["prompt"], "```", "", f"**Vídeo** ({p['video']['model']}, {p['video']['params']['duration']})", "", "```text", p["video"]["prompt"], "```", ""]
    if p["composite"]:
        md += ["**Pós-produção:** " + "; ".join(p["composite"]), ""]
(HERE / "PROMPTS.md").write_text("\n".join(md), encoding="utf-8")

bible = [f"# Bíblia de produção — {F['title_working']}", "", f"Duração {F['duration_s']} s · {F['fps']} fps · master {F['master']} · palavras faladas: {spoken_words}", "",
         "## Personagens", "", "| Personagem | Papel | Descrição | Figurinos |", "|---|---|---|---|"]
bible += [f"| {c['name']} | {c['role']} | {c['description']} | " + " / ".join(f"{k}: {v}" for k, v in c['wardrobe'].items()) + " |" for c in CH.values()]
bible += ["", "## Cenários", "", "| Cenário | Descrição | Planos |", "|---|---|---|"]
bible += [f"| {k} | {v['description']} | " + ", ".join(str(s['n']) for s in SH if s.get('set') == k) + " |" for k, v in SETS.items()]
bible += ["", "## Decupagem", "", "| # | Tempo | Ato | Plano | Lente / câmera | Ação | Som / fala | Geração |", "|---|---|---|---|---|---|---|---|"]
for s in SH:
    a = s.get("audio", {})
    snd = "; ".join(filter(None, [a.get("sfx"), a.get("music"), (f"“{a['line']['text']}”" if 'line' in a else None), (f"VO: “{a['vo']['text']}”" if 'vo' in a else None)]))
    g = f"{s['gen']['model']} ×{s['gen']['attempts']}" if s.get("gen") else "local"
    bible.append(f"| {s['n']} | {s['in']:.1f}–{s['out']:.1f} | {s['act']} | {s['framing']} | {s.get('lens','')} · {s.get('camera','')} | {s['action']} | {snd} | {g} |")
bible += ["", "## Fala (estimativa por sílabas)", "", "| Plano | Tipo | Início | Fim nominal | Fim máx. | Texto |", "|---|---|---|---|---|---|"]
bible += [f"| {sp['shot']} | {sp['kind']} | {sp['start']} | {sp['end_nom']} | {sp['end_max']} | {sp['text']} |" for sp in speech]
bible += ["", "## Orçamento (cotações verificadas do conector)", "", "```json", json.dumps(budget, indent=2), "```", "",
          "## Validação", "", f"Erros: {len(errors)} · Avisos: {len(warnings)}"] + [f"- ⚠ {w}" for w in warnings] + [f"- ✗ {e}" for e in errors]
(HERE / "BIBLE.md").write_text("\n".join(bible), encoding="utf-8")

print(json.dumps({"errors": errors, "warnings": warnings, "shots": len(SH), "generated_shots": len(prompts), "spoken_words": spoken_words,
                  "budget": {k: budget[k] for k in ("reference_assets", "keyframes", "image_credits", "video_credits", "total_credits")}, "vertical_strategies": {k: v["credits"] for k, v in vertical_strategies.items()}}, indent=2, ensure_ascii=False))
sys.exit(1 if errors else 0)
