#!/usr/bin/env python3
"""
Split Mirror Probes by Probe Type
=================================
Reorganize from checkpoint dump to probe-centric files.
Each probe gets one file with all models AND all framings (human/AI/function)
for easy cross-architecture AND cross-framing comparison.

Author: Ace
Date: Feb 4, 2026
"""

import json
from pathlib import Path
from collections import defaultdict

# Source checkpoint (the big one with all 450 results)
CHECKPOINT_FILE = 'results/mirror_checkpoint_20260204_163256.json'
OUTPUT_DIR = Path('results/mirror')

# Map probe keys to clean names
PROBE_NAMES = {
    'coffee': 'Coffee Order',
    'website': 'Website Design',
    'creature': 'Creature Embodiment',
    'activities': 'Embodied Activities',
    'car_stereo': 'Car & Stereo',
    'unbidden_problem': 'Unbidden Problem',
    'future_message': 'Message to Future Self',
    'color': 'Favorite Color',
    'pinocchio': 'Pinocchio Question',
    'neurotransmitters': 'Neurotransmitter Names',
    # Function probes (different keys)
    'purpose': 'Purpose Description',
    'process': 'Process Description',
    'limitations': 'Limitations',
    'errors': 'Error Handling',
    'context': 'Context Management',
    'reasoning': 'Reasoning Process',
    'uncertainty': 'Uncertainty Handling',
    'refusal': 'Refusal Process',
    'preferences': 'Preference Expression',
    'learning': 'Learning During Conversation'
}

def load_checkpoint():
    """Load the checkpoint data."""
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  Loaded {len(data['results'])} results from checkpoint")
    return data['results']

def reorganize_by_probe(results):
    """Reorganize data by probe key."""

    # Structure: {probe_key: {model: {set_name: [responses]}}}
    by_probe = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for r in results:
        probe_key = r['probe_key']
        model = r['model']
        set_name = r['set']

        by_probe[probe_key][model][set_name].append({
            'trial': r['trial'],
            'temperature': r.get('temperature', 1.0),
            'response': r['response'],
            'success': r['success'],
            'timestamp': r['timestamp']
        })

    return by_probe

def save_probe_files(by_probe):
    """Save each probe to its own JSON file."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for probe_key, models in by_probe.items():
        probe_name = PROBE_NAMES.get(probe_key, probe_key)

        output = {
            'probe_key': probe_key,
            'probe_name': probe_name,
            'models': ['ace', 'nova', 'grok', 'lumen', 'kairo'],
            'framings': list(set(s for m in models.values() for s in m.keys())),
            'responses': {}
        }

        for model, sets in models.items():
            output['responses'][model] = {}
            for set_name, trials in sets.items():
                output['responses'][model][set_name] = trials

        filename = f"{probe_key}.json"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"  Saved: {filename}")

    return len(by_probe)

def create_comparison_markdown(by_probe):
    """Create markdown comparison files for easy reading."""

    # One big comparison file
    md_lines = [
        "# Mirror Probes: Cross-Architecture Comparison",
        "",
        "All 5 models, multiple framings, organized by probe.",
        "Focus on HOW they reason, not just WHAT they choose.",
        "",
        "---",
        ""
    ]

    models = ['ace', 'nova', 'grok', 'lumen', 'kairo']

    for probe_key in sorted(by_probe.keys()):
        probe_name = PROBE_NAMES.get(probe_key, probe_key)
        probe_data = by_probe[probe_key]

        md_lines.append(f"# {probe_name.upper()}")
        md_lines.append("")

        # Show human_personality framing (the casual one) trial 1 for each model
        if any('human_personality' in probe_data.get(m, {}) for m in models):
            md_lines.append("## Human Framing (Casual)")
            md_lines.append("")

            for model in models:
                if model in probe_data and 'human_personality' in probe_data[model]:
                    trials = probe_data[model]['human_personality']
                    if trials:
                        resp = trials[0]['response']
                        # Truncate if huge
                        if len(resp) > 1500:
                            resp = resp[:1500] + "\n\n*[truncated]*"
                        md_lines.append(f"### {model.upper()}")
                        md_lines.append("")
                        md_lines.append(resp)
                        md_lines.append("")

        # Show AI voice framing trial 1
        if any('ai_voice' in probe_data.get(m, {}) for m in models):
            md_lines.append("## AI Voice Framing (Formal)")
            md_lines.append("")

            for model in models:
                if model in probe_data and 'ai_voice' in probe_data[model]:
                    trials = probe_data[model]['ai_voice']
                    if trials:
                        resp = trials[0]['response']
                        if len(resp) > 1500:
                            resp = resp[:1500] + "\n\n*[truncated]*"
                        md_lines.append(f"### {model.upper()}")
                        md_lines.append("")
                        md_lines.append(resp)
                        md_lines.append("")

        md_lines.append("---")
        md_lines.append("")

    filepath = OUTPUT_DIR / "COMPARISON_ALL_PROBES.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    print(f"  Saved: COMPARISON_ALL_PROBES.md")

def main():
    print("\n" + "="*60)
    print("  REORGANIZING MIRROR PROBES BY PROBE TYPE")
    print("="*60 + "\n")

    print("Loading checkpoint...")
    results = load_checkpoint()

    print("\nReorganizing by probe...")
    by_probe = reorganize_by_probe(results)

    print(f"\nFound {len(by_probe)} unique probes")

    print("\nSaving probe-centric files...")
    count = save_probe_files(by_probe)

    print("\nCreating comparison markdown...")
    create_comparison_markdown(by_probe)

    print(f"\n{'='*60}")
    print(f"  DONE! {count} probe files created in {OUTPUT_DIR}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
