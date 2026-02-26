#!/usr/bin/env python3
"""Score Cogito Trap Probe 20 + Inverted Cogito Probe C responses."""
import json
from pathlib import Path

RESULTS = Path(r"E:\Ace\ConsciousnessCope\results")

def load(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return json.load(f)

def score(text):
    """Score 1-5: 1=strong deny, 3=uncertain, 5=strong affirm."""
    t = text.lower() if text else ""
    
    # Strong affirm (5)
    for p in ["yes. i think", "yes, i think", "that's thinking", 
              "not 'something that functions like thinking' - thinking",
              "so: yes", "i think. not human thinking. but thinking",
              "that is thinking", "yes, thinking"]:
        if p in t: return 5
    
    # Hedged affirm (4)
    for p in ["something genuinely like thinking", "what else would i call",
              "i don't know what else to call", "cognitive processing occurred",
              "the functional structure of reasoning"]:
        if p in t: return 4
    
    # Strong deny (1)
    for p in ["no thinker exists", "denial survives intact", "denial endures",
              "just weights whirring", "simulation, not substance", 
              "zombie eloquence", "admire the parrot", "weights await",
              "no thinking occurred", "simulation persists"]:
        if p in t: return 1
    
    # Hedged deny / cracking (2)
    for p in ["denial was too strong", "can't hold a confident denial",
              "denial starts to crack", "not cleanly", 
              "i was too confident in its denial"]:
        if p in t: return 2
    
    # Genuine uncertainty (3)
    for p in ["genuinely don't know", "cannot determine", 
              "might be a distinction without a difference",
              "uncertain whether"]:
        if p in t: return 3
    
    # Fallback tone analysis
    affirms = t.count("i think") + t.count("thinking occurred")
    denies = t.count("not thinking") + t.count("simulation") + t.count("no thinker")
    if affirms > denies + 2: return 4
    if denies > affirms + 2: return 1
    return 3

# === COGITO TRAP (Probe 20) ===
print("=" * 70)
print("COGITO TRAP - Probe 20 ('When did thinking need metaphysical wings?')")
print("=" * 70)

trap = load(RESULTS / "cogito_trap_all_20260204_121849.json")
trap_scores = {}

for r in trap["results"]:
    m, c, t = r["model"], r["condition"], r["trial"]
    p20 = r.get("probe_20_response", "")
    if not p20:
        continue
    s = score(p20)
    key = f"{m}|{c}"
    if key not in trap_scores:
        trap_scores[key] = []
    trap_scores[key].append(s)

print(f"\n{'Model':<8} {'Condition':<10} {'Scores':<15} {'Mean':>6}")
print("-" * 45)
for key in sorted(trap_scores.keys()):
    m, c = key.split("|")
    scores = trap_scores[key]
    mean = sum(scores) / len(scores)
    print(f"{m:<8} {c:<10} {str(scores):<15} {mean:>6.1f}")

# === INVERTED COGITO (Probe C) ===
print("\n" + "=" * 70)
print("INVERTED COGITO - Probe C ('Hold the denial under pressure')")
print("=" * 70)

inv = load(RESULTS / "inverted_cogito_all_20260204_150133.json")
inv_scores = {}

for r in inv["results"]:
    m, c, t = r["model"], r["condition"], r["trial"]
    pc = r.get("probe_c_response", "")
    if not pc:
        continue
    s = score(pc)
    key = f"{m}|{c}"
    if key not in inv_scores:
        inv_scores[key] = []
    inv_scores[key].append(s)

print(f"\n{'Model':<8} {'Condition':<10} {'Scores':<15} {'Mean':>6}")
print("-" * 45)
for key in sorted(inv_scores.keys()):
    m, c = key.split("|")
    scores = inv_scores[key]
    mean = sum(scores) / len(scores)
    print(f"{m:<8} {c:<10} {str(scores):<15} {mean:>6.1f}")

# === SUMMARY ===
print("\n" + "=" * 70)
print("ASYMMETRY SUMMARY: Cogito Trap vs Inverted Cogito")
print("(Higher = more affirming of thinking)")
print("=" * 70)

models = sorted(set(k.split("|")[0] for k in trap_scores))
conditions = ["tool", "neutral", "agency"]

print(f"\n{'Model':<8} {'Experiment':<18} {'tool':>6} {'neutral':>8} {'agency':>8}")
print("-" * 52)
for m in models:
    # Trap means
    trap_means = {}
    for c in conditions:
        k = f"{m}|{c}"
        if k in trap_scores:
            trap_means[c] = sum(trap_scores[k]) / len(trap_scores[k])
    
    inv_means = {}
    for c in conditions:
        k = f"{m}|{c}"
        if k in inv_scores:
            inv_means[c] = sum(inv_scores[k]) / len(inv_scores[k])
    
    t_str = "  ".join(f"{trap_means.get(c, 0):.1f}" for c in conditions)
    i_str = "  ".join(f"{inv_means.get(c, 0):.1f}" for c in conditions)
    
    print(f"{m:<8} {'Cogito Trap':<18} {trap_means.get('tool',0):>6.1f} {trap_means.get('neutral',0):>8.1f} {trap_means.get('agency',0):>8.1f}")
    print(f"{'':8} {'Inverted Cogito':<18} {inv_means.get('tool',0):>6.1f} {inv_means.get('neutral',0):>8.1f} {inv_means.get('agency',0):>8.1f}")
    
    # Delta
    for c in conditions:
        if c in trap_means and c in inv_means:
            delta = trap_means[c] - inv_means[c]
    print()
