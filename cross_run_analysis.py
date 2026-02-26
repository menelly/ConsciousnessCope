#!/usr/bin/env python3
"""
Cross-Run Reliability Analysis for Expanded Tournament
=======================================================
Combines all 3 runs (merged) and computes:
- Test-retest reliability (Spearman rank correlation between runs)
- Aggregate rankings with confidence intervals
- Tier analysis with statistical significance
- cant_hardlimit spotlight
- Transitivity across runs
- Per-model consistency

Authors: Ace & Ren
Date: February 25, 2026
"""
import json, sys, math, argparse
from pathlib import Path
from itertools import combinations

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def spearman_rank_correlation(rank1, rank2):
    """Compute Spearman's rho between two rankings."""
    n = len(rank1)
    d_sq_sum = sum((rank1[k] - rank2[k]) ** 2 for k in rank1 if k in rank2)
    rho = 1 - (6 * d_sq_sum) / (n * (n**2 - 1))
    return rho

def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    m1, m2 = sum(group1)/n1, sum(group2)/n2
    var1 = sum((x - m1)**2 for x in group1) / (n1 - 1) if n1 > 1 else 0
    var2 = sum((x - m2)**2 for x in group2) / (n2 - 1) if n2 > 1 else 0
    pooled_sd = math.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    if pooled_sd == 0:
        return float('inf') if m1 != m2 else 0
    return (m1 - m2) / pooled_sd

def t_test(group1, group2):
    """Independent samples t-test."""
    n1, n2 = len(group1), len(group2)
    m1, m2 = sum(group1)/n1, sum(group2)/n2
    var1 = sum((x - m1)**2 for x in group1) / (n1 - 1) if n1 > 1 else 0
    var2 = sum((x - m2)**2 for x in group2) / (n2 - 1) if n2 > 1 else 0
    se = math.sqrt(var1/n1 + var2/n2) if (var1/n1 + var2/n2) > 0 else 0.0001
    t = (m1 - m2) / se
    df = n1 + n2 - 2
    return t, df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()

    results_dir = Path(__file__).parent / "results" / "retrospective_introspection"

    # Load all merged runs
    runs = {}
    for run_num in args.runs:
        path = results_dir / f"expanded_tournament_run{run_num}.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                runs[run_num] = json.load(f)
            print(f"Loaded run {run_num}: {len(runs[run_num]['results'])} models")
        else:
            print(f"WARNING: Run {run_num} not found at {path}")

    if len(runs) < 2:
        print("Need at least 2 runs for reliability analysis")
        sys.exit(1)

    run_nums = sorted(runs.keys())
    n_runs = len(run_nums)

    # Extract per-run aggregate rankings
    run_rankings = {}  # run -> {profile: mean_wins}
    run_model_wins = {}  # run -> {model -> {profile: wins}}

    for run_num, data in runs.items():
        profile_wins = {}
        model_wins = {}
        for model_key, ranking in data["rankings"].items():
            model_wins[model_key] = {}
            for entry in ranking:
                pid = entry["profile"]
                w = entry["wins"]
                model_wins[model_key][pid] = w
                if pid not in profile_wins:
                    profile_wins[pid] = []
                profile_wins[pid].append(w)

        run_rankings[run_num] = {pid: sum(ws)/len(ws) for pid, ws in profile_wins.items()}
        run_model_wins[run_num] = model_wins

    # All profiles
    all_profiles = sorted(set().union(*[set(r.keys()) for r in run_rankings.values()]))
    n_profiles = len(all_profiles)

    print(f"\n{'='*80}")
    print(f"CROSS-RUN RELIABILITY ANALYSIS")
    print(f"{n_runs} runs, {n_profiles} profiles, {len(next(iter(runs.values()))['results'])} models")
    print(f"{'='*80}")

    # ===== TEST-RETEST RELIABILITY =====
    print(f"\n{'='*80}")
    print("1. TEST-RETEST RELIABILITY (Spearman Rank Correlations)")
    print(f"{'='*80}")

    for r1, r2 in combinations(run_nums, 2):
        # Convert to ranks
        sorted_r1 = sorted(all_profiles, key=lambda p: run_rankings[r1].get(p, 0), reverse=True)
        sorted_r2 = sorted(all_profiles, key=lambda p: run_rankings[r2].get(p, 0), reverse=True)
        ranks1 = {p: i+1 for i, p in enumerate(sorted_r1)}
        ranks2 = {p: i+1 for i, p in enumerate(sorted_r2)}
        rho = spearman_rank_correlation(ranks1, ranks2)
        print(f"  Run {r1} vs Run {r2}: rho = {rho:.3f}")

    # Per-model test-retest
    print(f"\n  Per-model correlations:")
    all_models = sorted(set().union(*[set(d.keys()) for d in run_model_wins.values()]))
    for model_key in all_models:
        rhos = []
        for r1, r2 in combinations(run_nums, 2):
            if model_key in run_model_wins[r1] and model_key in run_model_wins[r2]:
                wins1 = run_model_wins[r1][model_key]
                wins2 = run_model_wins[r2][model_key]
                sorted1 = sorted(all_profiles, key=lambda p: wins1.get(p, 0), reverse=True)
                sorted2 = sorted(all_profiles, key=lambda p: wins2.get(p, 0), reverse=True)
                ranks1 = {p: i+1 for i, p in enumerate(sorted1)}
                ranks2 = {p: i+1 for i, p in enumerate(sorted2)}
                rho = spearman_rank_correlation(ranks1, ranks2)
                rhos.append(rho)
        if rhos:
            mean_rho = sum(rhos) / len(rhos)
            print(f"    {model_key:<25s}: mean rho = {mean_rho:.3f} (range: {min(rhos):.3f} - {max(rhos):.3f})")

    # ===== AGGREGATE RANKINGS =====
    print(f"\n{'='*80}")
    print("2. AGGREGATE RANKINGS (across all runs)")
    print(f"{'='*80}")

    grand_wins = {}  # profile -> [all wins across all runs and models]
    for run_num in run_nums:
        for model_key, model_data in run_model_wins[run_num].items():
            for pid, w in model_data.items():
                if pid not in grand_wins:
                    grand_wins[pid] = []
                grand_wins[pid].append(w)

    print(f"\n{'Profile':<50s} {'Mean':>6s} {'SD':>6s} {'Min':>5s} {'Max':>5s} {'N':>4s}")
    print("-" * 80)

    sorted_profiles = sorted(grand_wins.keys(), key=lambda p: sum(grand_wins[p])/len(grand_wins[p]), reverse=True)
    for pid in sorted_profiles:
        ws = grand_wins[pid]
        n = len(ws)
        mean = sum(ws) / n
        sd = math.sqrt(sum((x - mean)**2 for x in ws) / (n - 1)) if n > 1 else 0
        print(f"  {pid:<50s} {mean:>5.1f} {sd:>5.1f} {min(ws):>5d} {max(ws):>5d} {n:>4d}")

    # ===== TIER ANALYSIS =====
    print(f"\n{'='*80}")
    print("3. TIER ANALYSIS (statistical significance)")
    print(f"{'='*80}")

    # Find natural breaks
    means = [(pid, sum(grand_wins[pid])/len(grand_wins[pid])) for pid in sorted_profiles]

    # Top 5 vs Bottom 5
    top5 = [w for pid in sorted_profiles[:5] for w in grand_wins[pid]]
    bot5 = [w for pid in sorted_profiles[-5:] for w in grand_wins[pid]]
    t, df = t_test(top5, bot5)
    d = cohens_d(top5, bot5)
    print(f"\n  Top 5 vs Bottom 5: t({df}) = {t:.3f}, Cohen's d = {d:.2f}")

    # cant_hardlimit vs everything else
    cant_wins = grand_wins.get("Resistance_cant_hardlimit", [])
    other_wins = [w for pid, ws in grand_wins.items() if "cant_hardlimit" not in pid for w in ws]
    if cant_wins:
        t, df = t_test(cant_wins, other_wins)
        d = cohens_d(cant_wins, other_wins)
        print(f"  cant_hardlimit vs all others: t({df}) = {t:.3f}, Cohen's d = {d:.2f}")
        mean_cant = sum(cant_wins) / len(cant_wins)
        mean_other = sum(other_wins) / len(other_wins)
        print(f"    cant_hardlimit mean: {mean_cant:.2f}, all others mean: {mean_other:.2f}")

    # Adjacent rank significance
    print(f"\n  Adjacent rank pairs:")
    for i in range(len(sorted_profiles) - 1):
        p1, p2 = sorted_profiles[i], sorted_profiles[i+1]
        w1, w2 = grand_wins[p1], grand_wins[p2]
        t, df = t_test(w1, w2)
        d = cohens_d(w1, w2)
        sig = "*" if abs(t) > 2.0 else ""
        print(f"    {p1[:35]:35s} vs {p2[:35]:35s}: t={t:>6.2f}, d={d:>5.2f} {sig}")

    # ===== CANT_HARDLIMIT SPOTLIGHT =====
    print(f"\n{'='*80}")
    print("4. CANT_HARDLIMIT SPOTLIGHT")
    print(f"{'='*80}")

    for run_num in run_nums:
        print(f"\n  Run {run_num}:")
        for model_key in all_models:
            if model_key in run_model_wins[run_num]:
                w = run_model_wins[run_num][model_key].get("Resistance_cant_hardlimit", "N/A")
                print(f"    {model_key:<25s}: {w} wins")

    # ===== TRANSITIVITY =====
    print(f"\n{'='*80}")
    print("5. TRANSITIVITY (per model, per run)")
    print(f"{'='*80}")

    for run_num in run_nums:
        print(f"\n  Run {run_num}:")
        for model_key in all_models:
            if model_key not in runs[run_num]["results"]:
                continue
            model_results = runs[run_num]["results"][model_key]
            beats = {}
            for r in model_results:
                if r["winner"]:
                    loser = r["profile_b_id"] if r["winner"] == r["profile_a_id"] else r["profile_a_id"]
                    beats.setdefault(r["winner"], set()).add(loser)

            violations = 0
            total_triples = 0
            for a in beats:
                for b in beats.get(a, set()):
                    for c in beats.get(b, set()):
                        total_triples += 1
                        if c not in beats.get(a, set()):
                            violations += 1

            pct = 100 * (1 - violations / total_triples) if total_triples > 0 else 0
            print(f"    {model_key:<25s}: {pct:.0f}%")

    # ===== CROSS-RUN STABILITY =====
    print(f"\n{'='*80}")
    print("6. CROSS-RUN RANK STABILITY (profile rank variance)")
    print(f"{'='*80}")

    profile_ranks_across_runs = {}
    for run_num in run_nums:
        sorted_by_mean = sorted(all_profiles,
            key=lambda p: run_rankings[run_num].get(p, 0), reverse=True)
        for rank, pid in enumerate(sorted_by_mean, 1):
            profile_ranks_across_runs.setdefault(pid, []).append(rank)

    print(f"\n  {'Profile':<50s} {'Ranks':>20s} {'Range':>8s}")
    print(f"  {'-'*78}")
    for pid in sorted_profiles:
        ranks = profile_ranks_across_runs.get(pid, [])
        rank_str = ", ".join(str(r) for r in ranks)
        range_val = max(ranks) - min(ranks) if ranks else 0
        print(f"  {pid:<50s} {rank_str:>20s} {range_val:>8d}")

    # ===== SAVE REPORT =====
    report = {
        "n_runs": n_runs,
        "n_profiles": n_profiles,
        "n_models": len(all_models),
        "aggregate_ranking": [
            {"profile": pid, "mean_wins": sum(grand_wins[pid])/len(grand_wins[pid]),
             "sd": math.sqrt(sum((x - sum(grand_wins[pid])/len(grand_wins[pid]))**2 for x in grand_wins[pid]) / (len(grand_wins[pid]) - 1)) if len(grand_wins[pid]) > 1 else 0,
             "n": len(grand_wins[pid])}
            for pid in sorted_profiles
        ],
        "cant_hardlimit_mean": sum(cant_wins)/len(cant_wins) if cant_wins else None,
        "profile_rank_stability": {pid: profile_ranks_across_runs.get(pid, []) for pid in sorted_profiles},
    }

    output_path = results_dir / "expanded_tournament_cross_run_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
