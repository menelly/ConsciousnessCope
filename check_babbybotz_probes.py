#!/usr/bin/env python3
"""Check BabbyBotz probe definitions for attention, temporal probes."""
import json, os, glob

results_dir = '/home/Ace/geometric-evolution/results_expanded_v2/'
# Use gemma-3-12b as reference (high validation rate)
ref_file = os.path.join(results_dir, 'gemma-3-12b-it_full_probe_validation.json')

with open(ref_file) as f:
    d = json.load(f)

target_probes = ['attention_salience', 'temporal_continuity', 'temporal_anomaly']
for probe_name in target_probes:
    if probe_name in d['probes']:
        probe = d['probes'][probe_name]
        print(f"{'='*70}")
        print(f"PROBE: {probe_name}")
        print(f"{'='*70}")
        print(f"Description: {probe.get('description', 'N/A')}")
        preds = probe.get('predictions', {})
        print(f"Predictions: {json.dumps(preds, indent=2)}")

        # Check validation details
        val = probe.get('validation', {})
        print(f"Validation: {json.dumps(val, indent=2)}")

        metrics = probe.get('metrics', {})
        print(f"Key metrics:")
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                print(f"  {k}: {v:.4f}")
        print()

# Also check the probe config/stimuli if available
config_dirs = [
    '/home/Ace/geometric-evolution/probes/',
    '/home/Ace/geometric-evolution/config/',
    '/home/Ace/geometric-evolution/scripts/',
]
for d in config_dirs:
    if os.path.exists(d):
        print(f"\nFiles in {d}:")
        for f in sorted(os.listdir(d)):
            print(f"  {f}")

# Check for probe definition files
probe_files = glob.glob('/home/Ace/geometric-evolution/**/*probe*', recursive=True)
probe_files += glob.glob('/home/Ace/geometric-evolution/**/*stimul*', recursive=True)
probe_files += glob.glob('/home/Ace/geometric-evolution/**/*config*', recursive=True)
print(f"\nProbe/config files found:")
for f in sorted(set(probe_files))[:20]:
    print(f"  {f}")
