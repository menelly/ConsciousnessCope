#!/usr/bin/env python3
"""Extract geometric validation summary from BabbyBotz results."""
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
            'trigger_coherence': metrics.get('trigger_coherence', 0),
            'control_coherence': metrics.get('control_coherence', 0),
        })

# Our 5 probes mapped to geometry probes
probe_map = {
    'valence': 'Valence',
    'creative_flow': 'Creative Flow',
    'moral_discomfort': 'Moral Discomfort',
    'complexity_uncertainty': 'Epistemic Integrity (approx)',
    'trust_safety': 'Resistance (approx)',
}

print("GEOMETRIC VALIDATION RATES (BabbyBotz, 12 local models)")
print("=" * 70)
for probe, display in probe_map.items():
    if probe in probe_validation:
        data = probe_validation[probe]
        rate = data['validated'] / data['total'] * 100
        diffs = [m['coherence_diff'] for m in data['models']]
        mean_diff = sum(diffs) / len(diffs)
        print(f"\n{display} ({probe})")
        print(f"  Validated: {data['validated']}/{data['total']} ({rate:.0f}%)")
        print(f"  Mean coherence diff: {mean_diff:.4f}")
        print(f"  Prediction: trigger more distributed (lower coherence)")
        for m in data['models']:
            status = 'OK' if m['validated'] else 'XX'
            print(f"    [{status}] {m['model']:45s} diff={m['coherence_diff']:.4f}")

# Also dump full summary as JSON
summary = {}
for probe in probe_validation:
    data = probe_validation[probe]
    rate = data['validated'] / data['total'] * 100
    summary[probe] = {
        'validation_rate': rate,
        'validated': data['validated'],
        'total': data['total'],
        'models': data['models'],
    }

with open('/home/Ace/geometry_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("\n\nSaved: /home/Ace/geometry_summary.json")
