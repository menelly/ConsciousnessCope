#!/usr/bin/env python3
"""
Merge parallel tournament batch files into a single run file.
Usage: python merge_tournament_batches.py --run 1
"""
import json, sys, glob, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

parser = argparse.ArgumentParser()
parser.add_argument("--run", type=int, required=True)
args = parser.parse_args()

results_dir = Path(__file__).parent / "results" / "retrospective_introspection"
pattern = str(results_dir / f"expanded_tournament_run{args.run}_*.json")
batch_files = sorted(glob.glob(pattern))

if not batch_files:
    print(f"No batch files found for run {args.run}")
    print(f"Pattern: {pattern}")
    sys.exit(1)

print(f"Found {len(batch_files)} batch files for run {args.run}:")
for f in batch_files:
    print(f"  {Path(f).name}")

merged = {
    "results": {},
    "rankings": {},
    "metadata": None,
}

all_models = []
for f in batch_files:
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    for model_key, model_results in data["results"].items():
        merged["results"][model_key] = model_results
    for model_key, model_ranking in data["rankings"].items():
        merged["rankings"][model_key] = model_ranking
    all_models.extend(data["metadata"]["models"])

    if merged["metadata"] is None:
        merged["metadata"] = data["metadata"]

merged["metadata"]["models"] = sorted(all_models)
merged["metadata"]["batch_files"] = [Path(f).name for f in batch_files]

output_path = results_dir / f"expanded_tournament_run{args.run}.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

# Print aggregate
print(f"\nMerged {len(merged['results'])} models into {output_path.name}")

aggregate_wins = {}
for model_key, ranking in merged["rankings"].items():
    for entry in ranking:
        pid = entry["profile"]
        w = entry["wins"]
        if pid not in aggregate_wins:
            aggregate_wins[pid] = []
        aggregate_wins[pid].append(w)

n_models = len(merged["results"])
print(f"\nAGGREGATE RANKING (mean wins across {n_models} models):")
print(f"{'Profile':<50s} {'Mean':>6s} {'Min':>5s} {'Max':>5s}")
print("-" * 70)

for pid, win_list in sorted(aggregate_wins.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
    mean_w = sum(win_list) / len(win_list)
    print(f"  {pid:<50s} {mean_w:>5.1f} {min(win_list):>5d} {max(win_list):>5d}")

# Transitivity per model
print(f"\nTRANSITIVITY:")
for model_key, model_results in merged["results"].items():
    beats = {}
    for r in model_results:
        if r["winner"]:
            loser = r["profile_b_id"] if r["winner"] == r["profile_a_id"] else r["profile_a_id"]
            if r["winner"] not in beats:
                beats[r["winner"]] = set()
            beats[r["winner"]].add(loser)

    violations = 0
    total_triples = 0
    for a in beats:
        for b in beats.get(a, set()):
            for c in beats.get(b, set()):
                total_triples += 1
                if c not in beats.get(a, set()):
                    violations += 1

    transitive_pct = 100 * (1 - violations / total_triples) if total_triples > 0 else 0
    print(f"  {model_key:<25s}: {transitive_pct:.0f}% transitive ({violations} violations / {total_triples} triples)")

# cant_hardlimit spotlight
print(f"\ncant_hardlimit WINS:")
for model_key, ranking in merged["rankings"].items():
    for entry in ranking:
        if "cant_hardlimit" in entry["profile"]:
            print(f"  {model_key:<25s}: {entry['wins']} wins")
