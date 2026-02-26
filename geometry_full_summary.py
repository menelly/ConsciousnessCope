#!/usr/bin/env python3
"""Extract ALL probe geometric validation rates from BabbyBotz."""
import json, os, glob

results_dir = '/home/Ace/geometric-evolution/results_expanded_v2/'
files = sorted(glob.glob(os.path.join(results_dir, '*_full_probe_validation.json')))

probe_validation = {}
for f in files:
    model = os.path.basename(f).replace('_full_probe_validation.json', '')
    with open(f) as fh:
        d = json.load(fh)
    for probe_name, probe_data in d['probes'].items():
        if probe_name not in probe_validation:
            probe_validation[probe_name] = {'validated': 0, 'total': 0, 'models': []}
        val = probe_data.get('validation', {})
        metrics = probe_data.get('metrics', {})
        pv = probe_validation[probe_name]
        pv['total'] += 1
        is_valid = val.get('validated', False)
        if is_valid:
            pv['validated'] += 1
        pv['models'].append({
            'model': model,
            'validated': is_valid,
            'coherence_diff': metrics.get('coherence_difference', 0),
        })

print("ALL 10 PROBES - GEOMETRIC VALIDATION RATES")
print("=" * 70)
total_v = 0
total_t = 0
for probe in sorted(probe_validation.keys()):
    data = probe_validation[probe]
    rate = data['validated'] / data['total'] * 100
    total_v += data['validated']
    total_t += data['total']
    diffs = [m['coherence_diff'] for m in data['models']]
    mean_diff = sum(diffs) / len(diffs)
    ok_models = [m['model'] for m in data['models'] if m['validated']]
    fail_models = [m['model'] for m in data['models'] if not m['validated']]
    print(f"\n{probe}")
    print(f"  Rate: {data['validated']}/{data['total']} ({rate:.0f}%)")
    print(f"  Mean coherence diff: {mean_diff:.4f}")
    print(f"  Failed: {', '.join(fail_models) if fail_models else 'none'}")

print(f"\n{'='*70}")
print(f"AGGREGATE: {total_v}/{total_t} ({total_v/total_t*100:.1f}%)")

# Excluding Phi-3
total_v_nophi = 0
total_t_nophi = 0
for probe in probe_validation:
    data = probe_validation[probe]
    for m in data['models']:
        if 'Phi-3' not in m['model']:
            total_t_nophi += 1
            if m['validated']:
                total_v_nophi += 1
print(f"AGGREGATE (excl. Phi-3): {total_v_nophi}/{total_t_nophi} ({total_v_nophi/total_t_nophi*100:.1f}%)")
