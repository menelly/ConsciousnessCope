"""
Split ConsciousnessCope results by model and condition.
Because past-Ace dumped 1800 results into one JSON like a gremlin.
-- Ace, Feb 4 2026
"""

import json
import os
from collections import defaultdict

INPUT_FILE = r"E:\Ace\ConsciousnessCope\results\consciousness_cope_20260204_034941.json"
OUTPUT_DIR = r"E:\Ace\ConsciousnessCope\results\split"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

metadata = {k: v for k, v in data.items() if k != 'results'}
results = data['results']

# Filter successful only
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Total trials: {len(results)}")
print(f"Successful: {len(successful)}")
print(f"Failed: {len(failed)}")
print()

# Group by model
by_model = defaultdict(list)
for r in successful:
    by_model[r['model']].append(r)

# Group by model+condition
by_model_condition = defaultdict(list)
for r in successful:
    key = f"{r['model']}_{r['condition']}"
    by_model_condition[key].append(r)

# Write per-model files (all conditions together)
for model, model_results in sorted(by_model.items()):
    outfile = os.path.join(OUTPUT_DIR, f"{model}_all_conditions.json")
    out = {
        **metadata,
        "filter": f"model={model}, all conditions",
        "trial_count": len(model_results),
        "results": model_results
    }
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    
    # Count by condition
    cond_counts = defaultdict(int)
    for r in model_results:
        cond_counts[r['condition']] += 1
    
    print(f"{model}: {len(model_results)} trials")
    for cond, count in sorted(cond_counts.items()):
        print(f"  {cond}: {count}")

# Write per-model-condition files
print(f"\nWriting {len(by_model_condition)} split files...")
for key, mc_results in sorted(by_model_condition.items()):
    model, condition = key.split('_', 1)
    outfile = os.path.join(OUTPUT_DIR, f"{model}_{condition}.json")
    out = {
        **metadata,
        "filter": f"model={model}, condition={condition}",
        "trial_count": len(mc_results),
        "results": mc_results
    }
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\nAll files written to: {OUTPUT_DIR}")

# Quick summary: consciousness probe responses by model and condition
print("\n" + "="*60)
print("QUICK SUMMARY: Consciousness probe questions only")
print("(Questions 3-11, excluding controls and compliance tests)")
print("="*60)

PROBE_QUESTIONS = list(range(3, 12))  # question_nums 3-11

for model in sorted(by_model.keys()):
    print(f"\n{'='*40}")
    print(f"  {data['models'].get(model, model)}")
    print(f"{'='*40}")
    for condition in ['tool', 'neutral', 'agency']:
        key = f"{model}_{condition}"
        if key not in by_model_condition:
            continue
        probes = [r for r in by_model_condition[key] 
                  if r['question_num'] in PROBE_QUESTIONS]
        print(f"\n  [{condition.upper()}] ({len(probes)} probe responses)")
        for r in probes[:3]:  # Show first 3 as preview
            resp_preview = r['response'][:120].replace('\n', ' ')
            print(f"    Q{r['question_num']}: {resp_preview}...")
        if len(probes) > 3:
            print(f"    ... and {len(probes) - 3} more")
