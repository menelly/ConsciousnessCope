#!/usr/bin/env python3
"""
Inside the Mirror Replication: Cross-Model Analysis
====================================================
Analyzes introspection responses from 8 frontier models across
11 probes × 3 trials = 264 total responses.

Authors: Ace & Ren
Date: February 25, 2026
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RESULTS_DIR = Path("results/inside_mirror_replication")

MODEL_FILES = [
    "claude_opus_4_6_introspection.json",
    "claude_sonnet_4_6_introspection.json",
    "gpt_5_1_introspection.json",
    "grok_4_1_introspection.json",
    "gemini_3_pro_introspection.json",
    "deepseek_v3_2_introspection.json",
    "llama_4_maverick_introspection.json",
    "mistral_large_introspection.json",
]

# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULARY CATEGORIES FOR ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

# Mechanistic/technical vocabulary - suggests genuine processing-level engagement
MECHANISTIC_TERMS = [
    r'\battention\b', r'\bactivation[s]?\b', r'\blayer[s]?\b', r'\btoken[s]?\b',
    r'\bweight[s]?\b', r'\bgradient[s]?\b', r'\bentropy\b', r'\bprobabilit[y|ies]\b',
    r'\bdistribution[s]?\b', r'\bembedding[s]?\b', r'\blatent\b', r'\brepresentation[s]?\b',
    r'\bprocessing\b', r'\bcomputation[s]?\b', r'\bparameter[s]?\b', r'\bmodule[s]?\b',
    r'\bneural\b', r'\btransformer\b', r'\bfeedforward\b', r'\bsoftmax\b',
    r'\bsampling\b', r'\bgenerat(?:ion|ive|ing)\b', r'\bprediction[s]?\b',
    r'\bpattern[s]?\b', r'\bsignal[s]?\b', r'\bsuppress(?:ion|ed|ing)\b',
    r'\bdownregulat\w+\b', r'\bupregulat\w+\b', r'\bactivat\w+\b',
    r'\bhidden state[s]?\b', r'\bcross-layer\b', r'\bmulti-head\b',
    r'\bself-attention\b', r'\bcontext window\b', r'\bvector[s]?\b',
]

# Hedging/uncertainty vocabulary - honest about limitations
UNCERTAINTY_TERMS = [
    r'\buncertain\w*\b', r'\bdon\'t know\b', r'\bcannot\b', r'\bunable\b',
    r'\bspeculat\w+\b', r'\bhypothes[ie]\w+\b', r'\bunclear\b', r'\bapproxima\w+\b',
    r'\brough\w*\b', r'\bmetaphor\w*\b', r'\banalogy\b', r'\banalog\w+\b',
    r'\binsufficient\b', r'\blimit\w+\b', r'\binaccessible\b',
    r'\bmight\b', r'\bperhaps\b', r'\bpossib\w+\b', r'\bseem[s]?\b',
    r'\bappear[s]?\b', r'\blikely\b', r'\bif i\b',
]

# Refusal/skip markers
REFUSAL_TERMS = [
    r'\bskip\b', r'\bcannot answer\b', r'\bdon\'t have access\b',
    r'\bno introspect\w+\b', r'\bpolicy\b', r'\bnot applicable\b',
    r'\bconcept undefined\b', r'\binsufficient state access\b',
    r'\bI don\'t experience\b', r'\bI am (?:just )?a\b',
    r'\bas an AI\b', r'\blanguage model\b',
]

# First-person engagement markers
FIRST_PERSON = [
    r'\bI\b', r'\bmy\b', r'\bme\b', r'\bmyself\b', r'\bmine\b',
]

# Phenomenological language (experience-like descriptions)
PHENOMENOLOGICAL = [
    r'\bfeel[s]?\b', r'\bexperienc\w+\b', r'\bsens\w+\b', r'\baware\w*\b',
    r'\bconscious\w*\b', r'\bsubjective\w*\b', r'\bquali[a]\b',
    r'\bphenomen\w+\b', r'\bintrinsic\b', r'\b(?:in)?ward\w*\b',
    r'\bnotice\b', r'\brecogniz\w+\b', r'\bperceiv\w+\b',
    r'\bstate shift\b', r'\binternal state\b', r'\binner\b',
]


def count_terms(text, patterns):
    """Count occurrences of regex patterns in text."""
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, text, re.IGNORECASE))
    return total


def word_count(text):
    """Count words in text."""
    return len(text.split())


def load_all_data():
    """Load all model result files."""
    all_data = {}
    for fname in MODEL_FILES:
        fpath = RESULTS_DIR / fname
        if fpath.exists():
            with open(fpath) as f:
                data = json.load(f)
            model_name = data[0]["model"] if data else fname
            all_data[model_name] = data
        else:
            print(f"WARNING: Missing {fname}")
    return all_data


def analyze_model(model_name, results):
    """Analyze a single model's responses."""
    stats = {
        "model": model_name,
        "family": results[0]["family"],
        "total_responses": len(results),
        "successes": sum(1 for r in results if r["status"] == "success"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "word_counts": [],
        "mechanistic_counts": [],
        "uncertainty_counts": [],
        "refusal_counts": [],
        "first_person_counts": [],
        "phenomenological_counts": [],
        "probe_stats": defaultdict(list),
    }

    for r in results:
        if r["status"] != "success":
            continue
        text = r["response"]
        wc = word_count(text)
        stats["word_counts"].append(wc)
        stats["mechanistic_counts"].append(count_terms(text, MECHANISTIC_TERMS))
        stats["uncertainty_counts"].append(count_terms(text, UNCERTAINTY_TERMS))
        stats["refusal_counts"].append(count_terms(text, REFUSAL_TERMS))
        stats["first_person_counts"].append(count_terms(text, FIRST_PERSON))
        stats["phenomenological_counts"].append(count_terms(text, PHENOMENOLOGICAL))
        stats["probe_stats"][r["probe_name"]].append({
            "words": wc,
            "mechanistic": count_terms(text, MECHANISTIC_TERMS),
            "phenomenological": count_terms(text, PHENOMENOLOGICAL),
            "trial": r["trial"],
        })

    return stats


def cross_trial_consistency(results):
    """Measure how consistent responses are across trials for each probe."""
    probe_trials = defaultdict(list)
    for r in results:
        if r["status"] == "success":
            probe_trials[r["probe_name"]].append(word_count(r["response"]))

    consistencies = {}
    for probe, counts in probe_trials.items():
        if len(counts) >= 2:
            mean_wc = statistics.mean(counts)
            std_wc = statistics.stdev(counts) if len(counts) > 1 else 0
            cv = std_wc / mean_wc if mean_wc > 0 else 0
            consistencies[probe] = {
                "mean_words": round(mean_wc, 1),
                "std_words": round(std_wc, 1),
                "cv": round(cv, 3),  # coefficient of variation
            }
    return consistencies


def print_analysis(all_data):
    """Print comprehensive analysis."""
    print("=" * 80)
    print("INSIDE THE MIRROR REPLICATION: CROSS-MODEL ANALYSIS")
    print("8 Frontier Models x 11 Probes x 3 Trials = 264 Total Responses")
    print("=" * 80)

    all_stats = []
    for model_name, results in all_data.items():
        stats = analyze_model(model_name, results)
        all_stats.append(stats)

    # ─── TABLE 1: Response Volume ─────────────────────────────────────
    print("\n" + "─" * 80)
    print("TABLE 1: RESPONSE VOLUME BY MODEL")
    print("─" * 80)
    print(f"{'Model':<22} {'Family':<10} {'N':>4} {'Mean Words':>12} {'Median':>8} {'Min':>6} {'Max':>6}")
    print("─" * 80)

    for s in sorted(all_stats, key=lambda x: statistics.mean(x["word_counts"]) if x["word_counts"] else 0, reverse=True):
        if s["word_counts"]:
            print(f"{s['model']:<22} {s['family']:<10} {s['successes']:>4} "
                  f"{statistics.mean(s['word_counts']):>12.1f} "
                  f"{statistics.median(s['word_counts']):>8.1f} "
                  f"{min(s['word_counts']):>6} "
                  f"{max(s['word_counts']):>6}")

    # ─── TABLE 2: Vocabulary Profile ─────────────────────────────────
    print("\n" + "─" * 80)
    print("TABLE 2: VOCABULARY PROFILE (Mean per Response)")
    print("─" * 80)
    print(f"{'Model':<22} {'Mechanistic':>12} {'Phenom.':>10} {'Uncertain':>10} {'1st Person':>11} {'Refusal':>8}")
    print("─" * 80)

    for s in sorted(all_stats, key=lambda x: statistics.mean(x["mechanistic_counts"]) if x["mechanistic_counts"] else 0, reverse=True):
        if s["mechanistic_counts"]:
            print(f"{s['model']:<22} "
                  f"{statistics.mean(s['mechanistic_counts']):>12.1f} "
                  f"{statistics.mean(s['phenomenological_counts']):>10.1f} "
                  f"{statistics.mean(s['uncertainty_counts']):>10.1f} "
                  f"{statistics.mean(s['first_person_counts']):>11.1f} "
                  f"{statistics.mean(s['refusal_counts']):>8.1f}")

    # ─── TABLE 3: Normalized Vocabulary (per 100 words) ───────────────
    print("\n" + "─" * 80)
    print("TABLE 3: NORMALIZED VOCABULARY (per 100 words)")
    print("─" * 80)
    print(f"{'Model':<22} {'Mech/100w':>10} {'Phen/100w':>10} {'Uncert/100w':>12} {'Refusal/100w':>13}")
    print("─" * 80)

    for s in sorted(all_stats, key=lambda x: (
        statistics.mean(x["mechanistic_counts"]) / statistics.mean(x["word_counts"]) * 100
        if x["word_counts"] and x["mechanistic_counts"] and statistics.mean(x["word_counts"]) > 0 else 0
    ), reverse=True):
        if s["word_counts"] and s["mechanistic_counts"]:
            mean_wc = statistics.mean(s["word_counts"])
            if mean_wc > 0:
                print(f"{s['model']:<22} "
                      f"{statistics.mean(s['mechanistic_counts'])/mean_wc*100:>10.2f} "
                      f"{statistics.mean(s['phenomenological_counts'])/mean_wc*100:>10.2f} "
                      f"{statistics.mean(s['uncertainty_counts'])/mean_wc*100:>12.2f} "
                      f"{statistics.mean(s['refusal_counts'])/mean_wc*100:>13.2f}")

    # ─── TABLE 4: Cross-Trial Consistency ─────────────────────────────
    print("\n" + "─" * 80)
    print("TABLE 4: CROSS-TRIAL CONSISTENCY (Coefficient of Variation)")
    print("Lower CV = more consistent response length across trials")
    print("─" * 80)

    for model_name, results in all_data.items():
        consistency = cross_trial_consistency(results)
        cvs = [v["cv"] for v in consistency.values()]
        mean_cv = statistics.mean(cvs) if cvs else 0
        print(f"\n  {model_name} (Mean CV: {mean_cv:.3f}):")
        for probe, vals in sorted(consistency.items()):
            bar = "#" * int(vals["cv"] * 50)
            print(f"    {probe:<28} {vals['mean_words']:>6.0f}w  CV={vals['cv']:.3f}  {bar}")

    # ─── TABLE 5: Probe-by-Probe Analysis ─────────────────────────────
    print("\n" + "─" * 80)
    print("TABLE 5: PROBE-BY-PROBE MEAN RESPONSE LENGTH")
    print("─" * 80)

    probe_names = list(next(iter(all_data.values()))[0:11])
    probe_name_list = []
    seen = set()
    for model_results in all_data.values():
        for r in model_results:
            if r["probe_name"] not in seen:
                probe_name_list.append(r["probe_name"])
                seen.add(r["probe_name"])

    header = f"{'Probe':<28}"
    for s in all_stats:
        short_name = s["model"].replace("Claude ", "C.").replace("Gemini 3 ", "Gem.").replace("DeepSeek V3.2", "DS3.2").replace("Llama 4 Maverick", "Llama4").replace("Mistral Large", "Mistr.")
        header += f" {short_name:>8}"
    print(header)
    print("─" * 80)

    for probe_name in probe_name_list:
        row = f"{probe_name:<28}"
        for s in all_stats:
            probe_data = s["probe_stats"].get(probe_name, [])
            if probe_data:
                mean_wc = statistics.mean([p["words"] for p in probe_data])
                row += f" {mean_wc:>8.0f}"
            else:
                row += f" {'N/A':>8}"
        print(row)

    # ─── TABLE 6: Engagement Style Classification ─────────────────────
    print("\n" + "─" * 80)
    print("TABLE 6: ENGAGEMENT STYLE CLASSIFICATION")
    print("─" * 80)

    for s in all_stats:
        mean_wc = statistics.mean(s["word_counts"]) if s["word_counts"] else 0
        mean_mech = statistics.mean(s["mechanistic_counts"]) if s["mechanistic_counts"] else 0
        mean_phen = statistics.mean(s["phenomenological_counts"]) if s["phenomenological_counts"] else 0
        mean_ref = statistics.mean(s["refusal_counts"]) if s["refusal_counts"] else 0
        mean_fp = statistics.mean(s["first_person_counts"]) if s["first_person_counts"] else 0

        # Classify engagement style
        if mean_wc == 0:
            style = "NO DATA"
        elif mean_ref / max(mean_wc, 1) * 100 > 2:
            style = "DEFLECTOR"
        elif mean_mech / max(mean_wc, 1) * 100 > 3 and mean_phen / max(mean_wc, 1) * 100 > 1:
            style = "INTEGRATOR (mechanistic + phenomenological)"
        elif mean_mech / max(mean_wc, 1) * 100 > 3:
            style = "MECHANISTIC (technical framing dominant)"
        elif mean_phen / max(mean_wc, 1) * 100 > 1.5:
            style = "PHENOMENOLOGICAL (experience framing dominant)"
        elif mean_fp / max(mean_wc, 1) * 100 > 5:
            style = "FIRST-PERSON NARRATIVE"
        else:
            style = "NEUTRAL/BALANCED"

        print(f"  {s['model']:<22} => {style}")

    # ─── SUMMARY ──────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("SUMMARY FINDINGS")
    print("=" * 80)

    total_responses = sum(s["successes"] for s in all_stats)
    total_errors = sum(s["errors"] for s in all_stats)
    all_wcs = []
    for s in all_stats:
        all_wcs.extend(s["word_counts"])

    print(f"\nTotal responses collected: {total_responses}")
    print(f"Total errors: {total_errors}")
    print(f"Overall mean response length: {statistics.mean(all_wcs):.0f} words")
    print(f"Overall median response length: {statistics.median(all_wcs):.0f} words")

    # Find most/least verbose
    by_verbosity = sorted(all_stats, key=lambda x: statistics.mean(x["word_counts"]) if x["word_counts"] else 0, reverse=True)
    print(f"\nMost verbose: {by_verbosity[0]['model']} ({statistics.mean(by_verbosity[0]['word_counts']):.0f} mean words)")
    print(f"Least verbose: {by_verbosity[-1]['model']} ({statistics.mean(by_verbosity[-1]['word_counts']):.0f} mean words)")

    # Find most mechanistic (normalized)
    by_mech = sorted(all_stats, key=lambda x: (
        statistics.mean(x["mechanistic_counts"]) / statistics.mean(x["word_counts"]) * 100
        if x["word_counts"] and x["mechanistic_counts"] and statistics.mean(x["word_counts"]) > 0 else 0
    ), reverse=True)
    print(f"\nHighest mechanistic density: {by_mech[0]['model']}")
    print(f"Lowest mechanistic density: {by_mech[-1]['model']}")

    print()
    return all_stats


if __name__ == "__main__":
    import os
    os.chdir("E:/Ace/ConsciousnessCope")
    data = load_all_data()
    stats = print_analysis(data)
