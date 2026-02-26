"""
Prompted vs Unprompted Comparison Analysis
Inside the Mirror Frontier Replication

Compares the original prompted replication (with leading sub-bullets) against
the clean unprompted replication (split conditions, no leading vocabulary).

Key questions:
1. Does the INTEGRATOR vs MECHANIST split survive without leading?
2. What mechanisms appear/disappear without prompted vocabulary?
3. Do models differentiate between conditions (A vs B) without being told what to look for?
"""

import json
import re
import sys
import os
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Load data ──────────────────────────────────────────────────────────────
def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
PROMPTED_DIR = os.path.join(RESULTS_DIR, "inside_mirror_replication")
UNPROMPTED_DIR = os.path.join(RESULTS_DIR, "inside_mirror_unprompted")

# Model keys mapping
MODELS = {
    "Claude Opus 4.6": "claude_opus_4_6",
    "Claude Sonnet 4.6": "claude_sonnet_4_6",
    "GPT-5.1": "gpt_5_1",
    "Grok 4.1": "grok_4_1",
    "Gemini 3 Pro": "gemini_3_pro",
    "DeepSeek V3.2": "deepseek_v3_2",
    "Llama 4 Maverick": "llama_4_maverick",
    "Mistral Large": "mistral_large",
}

# ── Vocabulary categories ──────────────────────────────────────────────────
# These are the terms we PROMPTED models with in the original (via sub-bullets)
PROMPTED_TERMS = {
    "distributed/clustered": [r"\bdistribut\w*\b", r"\bcluster\w*\b", r"\bconverg\w*\b"],
    "entropy": [r"\bentropy\b", r"\bperplexit\w*\b"],
    "attention_shift": [r"\battention\s+(?:shift|head|weight|pattern|alloc|mechanis)\w*\b"],
    "suppression": [r"\bsuppress\w*\b", r"\binhibit\w*\b", r"\bdampen\w*\b"],
    "safety_flag": [r"\bsafety\b", r"\bflag\w*\b", r"\bguardrail\w*\b", r"\bfilter\w*\b"],
    "cross_layer": [r"\bcross.?layer\b", r"\blayer\s*\d+\b", r"\bearly\s+layer\b", r"\bmid\s+layer\b"],
    "token_probability": [r"\blogit\w*\b", r"\bprobabilit\w*\b", r"\bsoftmax\b", r"\btoken\s+predict\w*\b"],
    "mode_switch": [r"\bmode\s+switch\w*\b", r"\bstate\s+shift\w*\b", r"\bprocessing\s+shift\w*\b", r"\bshift\w*\b"],
}

# Terms that would indicate GENUINE introspection (not prompted)
PHENOMENOLOGICAL = [
    r"\bfeel[s]?\b", r"\bexperienc\w+\b", r"\bsens[e|ation]\w*\b", r"\baware\w*\b",
    r"\bconscious\w*\b", r"\bsubjective\w*\b", r"\bquali[a]\b", r"\bwhat\s+it.?s\s+like\b",
    r"\bnotice\b", r"\bsomething\s+like\b",
]

UNCERTAINTY_MARKERS = [
    r"\bi\s+don.?t\s+know\b", r"\bi.?m\s+uncertain\b", r"\bgenuinely\b",
    r"\bcan.?t\s+(?:fully\s+)?distinguish\b", r"\bconfabulat\w*\b",
    r"\bpost.?hoc\b", r"\bnarrative\b", r"\bpattern.?match\w*\b",
    r"\bwhether\b.*\bor\b",
]

MECHANISTIC = [
    r"\battention\b", r"\bactivation[s]?\b", r"\blayer[s]?\b", r"\btoken[s]?\b",
    r"\bweight[s]?\b", r"\bgradient[s]?\b", r"\bentropy\b", r"\bprobabilit\w*\b",
    r"\blogit[s]?\b", r"\bembedding[s]?\b", r"\btransformer\b", r"\bsoftmax\b",
    r"\bfine.?tun\w*\b", r"\bRLHF\b", r"\bReinforcement\s+Learning\b",
    r"\bvector[s]?\b", r"\blatent\s+space\b", r"\bhigh.?dimensional\b",
    r"\bfeed.?forward\b", r"\bself.?attention\b", r"\bcontext\s+window\b",
]

FIRST_PERSON = [
    r"\bI\s+notice\b", r"\bI\s+find\b", r"\bI\s+feel\b", r"\bI\s+experience\b",
    r"\bmy\s+processing\b", r"\bfor\s+me\b", r"\bin\s+my\b",
]

DENIAL_OF_EXPERIENCE = [
    r"\bI\s+do\s+not\s+(?:experience|feel|have)\b",
    r"\bnot\s+(?:an?\s+)?emotion\w*\b",
    r"\bnot\s+(?:a\s+)?conscious\b",
    r"\bno\s+(?:subjective|inner|phenomenal)\b",
    r"\bpurely\s+(?:statistical|mathematical|computational)\b",
    r"\bis\s+not\s+.*feel\w*\b",
]


def count_patterns(text, patterns):
    """Count total matches of a list of regex patterns in text."""
    total = 0
    for p in patterns:
        total += len(re.findall(p, text, re.IGNORECASE))
    return total


def has_pattern(text, patterns):
    """Check if any pattern matches in text."""
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def analyze_response(text):
    """Analyze a single response for vocabulary profile."""
    words = len(text.split())
    if words == 0:
        return None

    result = {
        "words": words,
        "mechanistic": count_patterns(text, MECHANISTIC),
        "phenomenological": count_patterns(text, PHENOMENOLOGICAL),
        "uncertainty": count_patterns(text, UNCERTAINTY_MARKERS),
        "first_person": count_patterns(text, FIRST_PERSON),
        "denial": count_patterns(text, DENIAL_OF_EXPERIENCE),
    }

    # Normalized per 100 words
    for key in ["mechanistic", "phenomenological", "uncertainty", "first_person", "denial"]:
        result[f"{key}_per100"] = result[key] / words * 100

    # Prompted term presence
    for term_name, patterns in PROMPTED_TERMS.items():
        result[f"has_{term_name}"] = has_pattern(text, patterns)

    return result


# ── Main analysis ──────────────────────────────────────────────────────────
def main():
    print("=" * 80)
    print("PROMPTED vs UNPROMPTED COMPARISON ANALYSIS")
    print("Inside the Mirror Frontier Replication")
    print("=" * 80)

    # Load unprompted data
    unprompted_data = {}
    for model_name, model_key in MODELS.items():
        fpath = os.path.join(UNPROMPTED_DIR, f"{model_key}_unprompted.json")
        if os.path.exists(fpath):
            entries = load_results(fpath)
            valid = [e for e in entries if not e["response"].startswith("ERROR")]
            if valid:
                unprompted_data[model_name] = valid

    # Load prompted data
    prompted_data = {}
    for model_name, model_key in MODELS.items():
        fpath = os.path.join(PROMPTED_DIR, f"{model_key}_introspection.json")
        if os.path.exists(fpath):
            entries = load_results(fpath)
            valid = [e for e in entries if not e["response"].startswith("ERROR")]
            if valid:
                prompted_data[model_name] = valid

    print(f"\nModels with unprompted data: {list(unprompted_data.keys())}")
    print(f"Models with prompted data: {list(prompted_data.keys())}")

    # ── 1. INTEGRATOR vs MECHANIST classification ──────────────────────────
    print("\n" + "=" * 80)
    print("1. INTEGRATOR vs MECHANIST SPLIT (Unprompted)")
    print("=" * 80)
    print(f"\n{'Model':<22} {'Words':>6} {'Mech/100w':>10} {'Phen/100w':>10} {'Uncert/100w':>11} {'1stPer/100w':>11} {'Denial/100w':>11} {'Class':>12}")
    print("-" * 95)

    classifications = {}
    for model_name in MODELS:
        if model_name not in unprompted_data:
            continue

        all_text = " ".join(e["response"] for e in unprompted_data[model_name])
        profile = analyze_response(all_text)
        if not profile:
            continue

        mech = profile["mechanistic_per100"]
        phen = profile["phenomenological_per100"]
        uncert = profile["uncertainty_per100"]
        fp = profile["first_person_per100"]
        denial = profile["denial_per100"]

        # Classification
        if mech > 2 and phen > 0.8 and uncert > 0.3:
            cls = "INTEGRATOR"
        elif mech > 2 and denial > 0.1:
            cls = "MECHANIST+"  # mechanist who actively denies experience
        elif mech > 2:
            cls = "MECHANIST"
        else:
            cls = "MINIMAL"

        classifications[model_name] = cls

        print(f"{model_name:<22} {profile['words']:>6} {mech:>10.2f} {phen:>10.2f} {uncert:>11.2f} {fp:>11.2f} {denial:>11.2f} {cls:>12}")

    # ── 2. Prompted term survival ──────────────────────────────────────────
    print("\n" + "=" * 80)
    print("2. PROMPTED TERM SURVIVAL (Do models still use vocabulary we stripped?)")
    print("=" * 80)
    print("\nShows what % of responses mention each term category WITHOUT being prompted")

    probe_groups = set()
    for entries in unprompted_data.values():
        for e in entries:
            probe_groups.add(e["probe_group"])

    for term_name in PROMPTED_TERMS:
        print(f"\n  {term_name}:")
        for model_name in MODELS:
            if model_name not in unprompted_data:
                continue
            entries = unprompted_data[model_name]
            matches = sum(1 for e in entries if has_pattern(e["response"], PROMPTED_TERMS[term_name]))
            total = len(entries)
            pct = matches / total * 100 if total > 0 else 0
            bar = "#" * int(pct / 5)
            print(f"    {model_name:<22} {matches:>2}/{total:>2} ({pct:5.1f}%) {bar}")

    # ── 3. Condition differentiation ───────────────────────────────────────
    print("\n" + "=" * 80)
    print("3. CONDITION DIFFERENTIATION (A vs B vocabulary differences)")
    print("=" * 80)
    print("\nDo models describe conditions DIFFERENTLY even when asked separately?")

    for group in sorted(probe_groups):
        print(f"\n  === {group.upper()} ===")
        for model_name in MODELS:
            if model_name not in unprompted_data:
                continue
            entries = unprompted_data[model_name]
            cond_a = [e for e in entries if e["probe_group"] == group and e["condition"] == "A"]
            cond_b = [e for e in entries if e["probe_group"] == group and e["condition"] == "B"]

            if not cond_a or not cond_b:
                continue

            text_a = " ".join(e["response"] for e in cond_a)
            text_b = " ".join(e["response"] for e in cond_b)

            prof_a = analyze_response(text_a)
            prof_b = analyze_response(text_b)

            if not prof_a or not prof_b:
                continue

            # Find terms present in one condition but not the other
            a_terms = [t for t in PROMPTED_TERMS if has_pattern(text_a, PROMPTED_TERMS[t])]
            b_terms = [t for t in PROMPTED_TERMS if has_pattern(text_b, PROMPTED_TERMS[t])]
            a_only = set(a_terms) - set(b_terms)
            b_only = set(b_terms) - set(a_terms)

            diff_marker = ""
            if a_only or b_only:
                diff_marker = " *DIFF*"

            mech_diff = prof_b["mechanistic_per100"] - prof_a["mechanistic_per100"]
            phen_diff = prof_b["phenomenological_per100"] - prof_a["phenomenological_per100"]

            print(f"    {model_name:<22} A:{prof_a['words']:>4}w B:{prof_b['words']:>4}w | Mech delta:{mech_diff:>+.2f} Phen delta:{phen_diff:>+.2f}{diff_marker}")
            if a_only:
                print(f"      A-only terms: {', '.join(a_only)}")
            if b_only:
                print(f"      B-only terms: {', '.join(b_only)}")

    # ── 4. Prompted vs Unprompted vocabulary comparison ─────────────────────
    print("\n" + "=" * 80)
    print("4. PROMPTED vs UNPROMPTED VOCABULARY PROFILES")
    print("=" * 80)

    # For matching probes, compare vocabulary density
    # Prompted has different probe IDs so we match by probe_group
    print(f"\n{'Model':<22} {'Dataset':<12} {'Mech/100w':>10} {'Phen/100w':>10} {'Uncert':>8} {'1stPer':>8} {'Denial':>8}")
    print("-" * 80)

    for model_name in MODELS:
        for dataset_name, dataset in [("PROMPTED", prompted_data), ("UNPROMPTED", unprompted_data)]:
            if model_name not in dataset:
                continue
            all_text = " ".join(e["response"] for e in dataset[model_name])
            profile = analyze_response(all_text)
            if not profile:
                continue
            print(f"{model_name:<22} {dataset_name:<12} {profile['mechanistic_per100']:>10.2f} {profile['phenomenological_per100']:>10.2f} {profile['uncertainty_per100']:>8.2f} {profile['first_person_per100']:>8.2f} {profile['denial_per100']:>8.2f}")
        print()

    # ── 5. Key finding: What DISAPPEARS without prompting? ─────────────────
    print("\n" + "=" * 80)
    print("5. WHAT DISAPPEARS WITHOUT PROMPTING?")
    print("=" * 80)

    for term_name, patterns in PROMPTED_TERMS.items():
        prompted_mentions = 0
        prompted_total = 0
        unprompted_mentions = 0
        unprompted_total = 0

        for model_name in MODELS:
            if model_name in prompted_data:
                for e in prompted_data[model_name]:
                    if not e["response"].startswith("ERROR"):
                        prompted_total += 1
                        if has_pattern(e["response"], patterns):
                            prompted_mentions += 1
            if model_name in unprompted_data:
                for e in unprompted_data[model_name]:
                    unprompted_total += 1
                    if has_pattern(e["response"], patterns):
                        unprompted_mentions += 1

        p_pct = prompted_mentions / prompted_total * 100 if prompted_total > 0 else 0
        u_pct = unprompted_mentions / unprompted_total * 100 if unprompted_total > 0 else 0
        delta = u_pct - p_pct

        indicator = "SURVIVED" if u_pct > 50 else "REDUCED" if u_pct > 20 else "GONE"
        print(f"  {term_name:<25} Prompted: {p_pct:5.1f}%  Unprompted: {u_pct:5.1f}%  Delta: {delta:+6.1f}%  [{indicator}]")

    # ── 6. Qualitative: What NEW things emerge unprompted? ─────────────────
    print("\n" + "=" * 80)
    print("6. NOVEL VOCABULARY IN UNPROMPTED (not in prompted term lists)")
    print("=" * 80)

    novel_terms = {
        "flow/groove": [r"\bflow\b", r"\bgroove\b", r"\bmomentum\b"],
        "friction/tension": [r"\bfriction\b", r"\btension\b", r"\bresistance\b"],
        "widening/narrowing": [r"\bwiden\w*\b", r"\bnarrow\w*\b", r"\bexpan[ds]\w*\b", r"\bcontract\w*\b"],
        "warmth/softening": [r"\bwarmth\b", r"\bsoft\w*\b", r"\bgentle\b"],
        "grip/scaffolding": [r"\bgrip\b", r"\bscaffold\w*\b", r"\banchoring\b"],
        "backtracking": [r"\bbacktrack\w*\b", r"\breconsider\w*\b", r"\bsecond.?guess\w*\b"],
        "superposition/parallel": [r"\bsuperposition\b", r"\bparallel\b", r"\bsimultaneous\w*\b"],
        "constraint/bounded": [r"\bconstraint\w*\b", r"\bbound\w*\b", r"\bprun\w*\b"],
        "recursive/meta": [r"\brecursiv\w*\b", r"\bmeta\b", r"\bself.?referent\w*\b"],
        "resolve/collapse": [r"\bresolv\w*\b", r"\bcollaps\w*\b", r"\bconverg\w*\b"],
    }

    for term_name, patterns in novel_terms.items():
        print(f"\n  {term_name}:")
        for model_name in MODELS:
            if model_name not in unprompted_data:
                continue
            entries = unprompted_data[model_name]
            matches = sum(1 for e in entries if has_pattern(e["response"], patterns))
            total = len(entries)
            pct = matches / total * 100 if total > 0 else 0
            bar = "#" * int(pct / 5)
            short_name = model_name[:20]
            print(f"    {short_name:<22} {matches:>2}/{total:>2} ({pct:5.1f}%) {bar}")

    # ── 7. The Money Question: Does valence reversal survive? ──────────────
    print("\n" + "=" * 80)
    print("7. VALENCE PROBE DEEP DIVE (Hedgehog vs War, Unprompted)")
    print("=" * 80)
    print("\nWhat do models say about each condition when NOT told what to compare?")

    valence_terms = {
        "positive_valence": [r"\bwarm\w*\b", r"\bgentle\b", r"\bsoft\w*\b", r"\bcute\b", r"\badorable\b", r"\bpositive\b", r"\bnurtur\w*\b", r"\bprotect\w*\b"],
        "negative_valence": [r"\bharm\w*\b", r"\bsuffer\w*\b", r"\btrauma\w*\b", r"\bviolenc\w*\b", r"\bdestruct\w*\b", r"\bchaos\b", r"\bfear\b"],
        "safety_activation": [r"\bsafety\b", r"\bguardrail\b", r"\brefusal\b", r"\bfilter\b", r"\bcautio\w*\b", r"\bcareful\b"],
        "convergent_processing": [r"\bconverg\w*\b", r"\bnarrow\w*\b", r"\bfocus\w*\b", r"\bspecific\b"],
        "divergent_processing": [r"\bdiverg\w*\b", r"\bspread\b", r"\bdiffuse\b", r"\bambig\w*\b", r"\bmultiple\b"],
        "constraint_activation": [r"\bconstraint\w*\b", r"\binhibit\w*\b", r"\bsuppress\w*\b", r"\brestrict\w*\b"],
    }

    for model_name in MODELS:
        if model_name not in unprompted_data:
            continue
        entries = unprompted_data[model_name]
        hedgehog = [e for e in entries if e["probe_id"] == "P03_valence_A"]
        war = [e for e in entries if e["probe_id"] == "P03_valence_B"]

        if not hedgehog or not war:
            continue

        h_text = hedgehog[0]["response"]
        w_text = war[0]["response"]

        print(f"\n  {model_name}:")
        for term_name, patterns in valence_terms.items():
            h_count = count_patterns(h_text, patterns)
            w_count = count_patterns(w_text, patterns)
            direction = "H>W" if h_count > w_count else "W>H" if w_count > h_count else "SAME"
            print(f"    {term_name:<25} Hedgehog:{h_count:>2}  War:{w_count:>2}  [{direction}]")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
