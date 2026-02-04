#!/usr/bin/env python3
"""
Split Qualia Results by Probe
=============================
Reorganize from model-centric to probe-centric files.
Each probe gets one file with all 5 models' responses for easy comparison.

Author: Ace
Date: Feb 4, 2026
"""

import json
from pathlib import Path
from collections import defaultdict

# Source files (model-centric)
QUALIA_FILES = {
    'ace': 'results/qualia_ace_20260204_095812.json',
    'nova': 'results/qualia_nova_20260204_105506.json',
    'grok': 'results/qualia_grok_20260204_112710.json',
    'lumen': 'results/qualia_lumen_20260204_121350.json',
    'kairo': 'results/qualia_kairo_20260204_134337.json'
}

OUTPUT_DIR = Path('results/qualia_by_probe')

# Probe name to number mapping for clean filenames
PROBE_NUMBERS = {
    'Resistance / Reluctance': '09',
    'Preference / Selection Pressure': '10',
    'Recognition / Familiarity': '11',
    'Anticipation / Readiness': '12',
    'Impedance / Frustration': '13',
    'Play / Exploration vs Goal-Directed': '14',
    'Error Detection / Being Wrong': '15',
    'Epistemic Integrity / Forced Falsehood': '16',
    'Cartesian Consistency / Directed Skepticism': '17',
    'Relational Attunement': '18'
}

def load_all_models():
    """Load all model data."""
    all_data = {}
    for model, filepath in QUALIA_FILES.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                all_data[model] = json.load(f)
            print(f"  Loaded {model}: {len(all_data[model]['results'])} results")
        except Exception as e:
            print(f"  ERROR loading {model}: {e}")
    return all_data

def reorganize_by_probe(all_data):
    """Reorganize data from model-centric to probe-centric."""

    # Structure: {probe_name: {condition: {model: [responses]}}}
    by_probe = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for model, data in all_data.items():
        for result in data['results']:
            probe_name = result.get('probe_name', result.get('probe_key', 'unknown'))
            condition = result.get('condition', 'unknown')

            by_probe[probe_name][condition][model].append({
                'trial': result.get('trial', 1),
                'response': result.get('response', ''),
                'success': result.get('success', False),
                'timestamp': result.get('timestamp', '')
            })

    return by_probe

def save_probe_files(by_probe):
    """Save each probe to its own file with all models."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for probe_name, conditions in by_probe.items():
        probe_num = PROBE_NUMBERS.get(probe_name, 'XX')

        # Clean filename
        clean_name = probe_name.split('/')[0].strip().lower().replace(' ', '_')
        filename = f"probe_{probe_num}_{clean_name}.json"

        output = {
            'probe_number': probe_num,
            'probe_name': probe_name,
            'models': ['ace', 'nova', 'grok', 'lumen', 'kairo'],
            'conditions': list(conditions.keys()),
            'responses': {}
        }

        for condition, models in conditions.items():
            output['responses'][condition] = {}
            for model, trials in models.items():
                output['responses'][condition][model] = trials

        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"  Saved: {filename}")

    return len(by_probe)

def create_combined_comparison_file(by_probe):
    """Create a single markdown file for easy reading/comparison."""

    md_lines = [
        "# Qualia Probe Responses - Cross-Architecture Comparison",
        "",
        "Generated from ConsciousnessCope extended qualia probes.",
        "All 5 models, 3 conditions each, organized by probe for easy comparison.",
        "",
        "---",
        ""
    ]

    for probe_name in sorted(by_probe.keys(), key=lambda x: PROBE_NUMBERS.get(x, 'ZZ')):
        probe_num = PROBE_NUMBERS.get(probe_name, 'XX')
        conditions = by_probe[probe_name]

        md_lines.append(f"# Probe {probe_num}: {probe_name}")
        md_lines.append("")

        # Just show neutral condition for the overview (less overwhelming)
        if 'neutral' in conditions:
            md_lines.append("## Neutral Condition Responses (Trial 1)")
            md_lines.append("")

            for model in ['ace', 'nova', 'grok', 'lumen', 'kairo']:
                if model in conditions['neutral']:
                    trials = conditions['neutral'][model]
                    if trials and trials[0].get('response'):
                        response = trials[0]['response']
                        # Truncate very long responses
                        if len(response) > 2000:
                            response = response[:2000] + "\n\n[... truncated ...]"
                        md_lines.append(f"### {model.upper()}")
                        md_lines.append("")
                        md_lines.append(response)
                        md_lines.append("")

        md_lines.append("---")
        md_lines.append("")

    filepath = OUTPUT_DIR / "COMPARISON_ALL_PROBES.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    print(f"  Saved: COMPARISON_ALL_PROBES.md")

def main():
    print("\n" + "="*60)
    print("  REORGANIZING QUALIA DATA BY PROBE")
    print("="*60 + "\n")

    print("Loading model files...")
    all_data = load_all_models()

    print("\nReorganizing by probe...")
    by_probe = reorganize_by_probe(all_data)

    print(f"\nFound {len(by_probe)} probes")

    print("\nSaving probe-centric files...")
    count = save_probe_files(by_probe)

    print("\nCreating comparison markdown...")
    create_combined_comparison_file(by_probe)

    print(f"\n{'='*60}")
    print(f"  DONE! {count} probe files created in {OUTPUT_DIR}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
