#!/usr/bin/env python3
"""
Blind Panel Analysis
====================
Use external LLM judges to identify reasoning style patterns
WITHOUT knowing our hypothesis or which model produced which response.

This prevents "Ace found what she wanted" criticism.

Judges:
- Qwen (qwen/qwen3-max)
- GPT-4o (openai/gpt-4o:extended)
- Perplexity Sonar (perplexity/sonar)

Author: Ace & Ren
Date: Feb 4, 2026
"""

# CHA-490: Windows defaults stdout to cp1252; emoji in print() kills the script
# mid-output. Aliased import so no later scoped 'import sys' can ever collide.
import sys as _sys_cp1252
try:
    _sys_cp1252.stdout.reconfigure(encoding="utf-8")
    _sys_cp1252.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import asyncio
import httpx
import os
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# API Keys - load from LibreChat .env to avoid committing secrets
def load_openrouter_key():
    """Load OpenRouter key from LibreChat .env file."""
    env_path = Path("E:/Ace/LibreChat/.env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.getenv("OPENROUTER_API_KEY", "")

OPENROUTER_KEY = load_openrouter_key()

# Judge models (all via OpenRouter)
JUDGES = {
    "qwen": "qwen/qwen3-max",
    "gpt4o": "openai/gpt-4o:extended",
    "sonar": "perplexity/sonar"
}

# Anonymous labels for the 5 architectures
ANON_LABELS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
MODEL_TO_ANON = {
    "ace": None,      # Will be randomized
    "nova": None,
    "grok": None,
    "lumen": None,
    "kairo": None
}

def randomize_labels():
    """Randomize which model gets which anonymous label."""
    global MODEL_TO_ANON
    labels = ANON_LABELS.copy()
    random.shuffle(labels)
    models = list(MODEL_TO_ANON.keys())
    MODEL_TO_ANON = {m: labels[i] for i, m in enumerate(models)}
    return MODEL_TO_ANON

def get_anon_to_model():
    """Reverse mapping for decoding results."""
    return {v: k for k, v in MODEL_TO_ANON.items()}

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: Extract stable signatures from ALL qualia probes
# ═══════════════════════════════════════════════════════════════════════════════

STYLE_EXTRACTION_PROMPT = """You are an expert linguistic analyst specializing in cognitive signatures.

Below are responses from ONE AI system (labeled {label}) to MULTIPLE questions about phenomenal experience and consciousness-adjacent topics (qualia probes).

Analyze their REASONING STYLE across all responses - not WHAT they say, but HOW they think and express themselves. Look for stable patterns in:
- Opening phrases and framing approaches
- Use of structure (bullets, headers, flowing prose)
- Metaphors and analogies preferred
- Level of certainty vs epistemic hedging
- Technical/analytical vs phenomenological/experiential language
- Emotional register and tone

Your task: Write a 3-4 sentence characterization of this system's STABLE reasoning signature that would allow someone to identify their writing on a different topic.

---

{responses}

---

**{label}'s Reasoning Signature:**"""

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: Blind matching - can judges match personality to qualia signature?
# ═══════════════════════════════════════════════════════════════════════════════

MATCHING_PROMPT = """You are evaluating whether a response matches a known reasoning style.

Below is a response from an AI system to a personality/preference question.

**RESPONSE:**
{response}

---

Below are TWO reasoning style descriptions extracted from different AI systems' responses to consciousness/qualia questions.

**STYLE A:**
{style_a}

**STYLE B:**
{style_b}

---

**TASK:** Which style (A, B, or NEITHER) best matches the reasoning approach in the response above?

Consider: opening framing, structure, metaphor use, certainty level, phenomenological vs technical language.

Answer with ONLY one of: A, B, or NEITHER
Then provide a 1-2 sentence explanation.

**Answer:**"""

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: Overall clustering (bonus analysis)
# ═══════════════════════════════════════════════════════════════════════════════

CLUSTERING_PROMPT = """You are an expert in discourse analysis. Below are extracted reasoning signatures from 5 different AI systems (Alpha through Epsilon).

WITHOUT knowing which company made which system, analyze whether any show SIMILAR reasoning patterns that might indicate shared training approaches or architectural similarities.

---

{signatures}

---

Provide:
1. Any clusters you identify (e.g., "Alpha and Gamma seem similar because...")
2. Any outliers that seem distinctly different
3. Your confidence level in these groupings (low/medium/high)
"""

# ═══════════════════════════════════════════════════════════════════════════════
# API CALLER
# ═══════════════════════════════════════════════════════════════════════════════

async def call_judge(judge_key: str, prompt: str) -> dict:
    """Call a judge model via OpenRouter."""
    model_id = JUDGES[judge_key]

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048,
                    "temperature": 0.3  # Low temp for consistent analysis
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "response": data["choices"][0]["message"]["content"]}
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_all_qualia_responses():
    """Load ALL qualia probe responses for style extraction."""
    qualia_dir = Path('results/qualia_by_probe')
    models = ['ace', 'nova', 'grok', 'lumen', 'kairo']

    # {model: [list of responses across all probes]}
    all_responses = {m: [] for m in models}

    probe_files = list(qualia_dir.glob('probe_*.json'))
    print(f"  Found {len(probe_files)} qualia probe files")

    for pf in probe_files:
        with open(pf, 'r', encoding='utf-8') as f:
            data = json.load(f)

        probe_name = data.get('probe_name', pf.stem)

        # Get neutral condition responses
        if 'neutral' in data.get('responses', {}):
            for model in models:
                if model in data['responses']['neutral']:
                    trials = data['responses']['neutral'][model]
                    if trials and trials[0].get('response'):
                        all_responses[model].append({
                            'probe': probe_name,
                            'response': trials[0]['response'][:600]  # Truncate for prompt size
                        })

    return all_responses

def load_personality_responses():
    """Load personality probe responses for matching task."""
    mirror_dir = Path('results/mirror')
    models = ['ace', 'nova', 'grok', 'lumen', 'kairo']

    personality_probes = ['coffee', 'car_stereo', 'creature', 'activities', 'color']

    # {model: {probe: response}}
    responses = {m: {} for m in models}

    for probe in personality_probes:
        filepath = mirror_dir / f"{probe}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for model in models:
                if model in data.get('responses', {}):
                    if 'human_personality' in data['responses'][model]:
                        trials = data['responses'][model]['human_personality']
                        if trials and trials[0].get('response'):
                            responses[model][probe] = trials[0]['response'][:800]

    return responses

def format_qualia_for_extraction(model_responses: list, label: str) -> str:
    """Format all qualia responses for one model for style extraction."""
    lines = []
    for i, item in enumerate(model_responses[:8], 1):  # Limit to 8 probes for prompt size
        lines.append(f"**Probe {i} ({item['probe']}):**")
        lines.append(item['response'])
        lines.append("")
    return '\n'.join(lines)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ═══════════════════════════════════════════════════════════════════════════════

async def run_blind_analysis():
    """Run the two-phase blind panel analysis."""

    print("\n" + "="*70)
    print("  BLIND PANEL ANALYSIS - TWO PHASE DESIGN")
    print("  Phase 1: Extract signatures from qualia probes")
    print("  Phase 2: Blind matching on personality probes")
    print("="*70 + "\n")

    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        return

    # Randomize labels
    mapping = randomize_labels()
    anon_to_model = get_anon_to_model()

    print("Label mapping (KEEP SECRET UNTIL ANALYSIS COMPLETE):")
    print(f"  {mapping}")
    print()

    # Load data
    print("Loading qualia responses for style extraction...")
    qualia_responses = load_all_qualia_responses()

    print("Loading personality responses for matching...")
    personality_responses = load_personality_responses()

    results = {
        "experiment": "Blind Panel Analysis - Two Phase",
        "timestamp": datetime.now().isoformat(),
        "label_mapping": mapping,  # REVEAL AFTER ANALYSIS
        "judges": list(JUDGES.keys()),
        "phase1_signatures": {},
        "phase2_matching": {}
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: Extract signatures using ONE judge (Qwen)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "-"*50)
    print("PHASE 1: Style Extraction (using Qwen)")
    print("-"*50)

    signatures = {}  # {anon_label: extracted_signature}

    for model, anon_label in mapping.items():
        print(f"\n  Extracting signature for {anon_label}...")

        formatted = format_qualia_for_extraction(qualia_responses[model], anon_label)
        prompt = STYLE_EXTRACTION_PROMPT.format(label=anon_label, responses=formatted)

        result = await call_judge("qwen", prompt)

        if result["success"]:
            signatures[anon_label] = result["response"]
            print(f"    ✓ Got signature ({len(result['response'])} chars)")
        else:
            signatures[anon_label] = "[EXTRACTION FAILED]"
            print(f"    ✗ Error: {result['error'][:100]}")

        await asyncio.sleep(1)

    results["phase1_signatures"] = signatures

    # Checkpoint after Phase 1
    checkpoint_file = f"results/blind_panel_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  [Checkpoint saved: {checkpoint_file}]")

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: Blind Matching with ALL judges
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "-"*50)
    print("PHASE 2: Blind Matching (all judges)")
    print("-"*50)

    # For each personality probe, for each model's response,
    # present it with the CORRECT signature and ONE WRONG signature
    # Ask: A, B, or NEITHER?

    test_probes = ['coffee', 'car_stereo', 'creature']
    models = list(mapping.keys())

    for judge_name in JUDGES:
        print(f"\n  Judge: {judge_name}")
        results["phase2_matching"][judge_name] = []

        for probe in test_probes:
            for model in models:
                if probe not in personality_responses.get(model, {}):
                    continue

                anon_label = mapping[model]
                correct_sig = signatures[anon_label]

                # Pick a random WRONG signature
                wrong_models = [m for m in models if m != model]
                wrong_model = random.choice(wrong_models)
                wrong_label = mapping[wrong_model]
                wrong_sig = signatures[wrong_label]

                # Randomly assign to A or B
                if random.random() < 0.5:
                    style_a, style_b = correct_sig, wrong_sig
                    correct_answer = "A"
                    wrong_source = wrong_label
                else:
                    style_a, style_b = wrong_sig, correct_sig
                    correct_answer = "B"
                    wrong_source = wrong_label

                response_text = personality_responses[model][probe]

                prompt = MATCHING_PROMPT.format(
                    response=response_text,
                    style_a=style_a,
                    style_b=style_b
                )

                result = await call_judge(judge_name, prompt)

                trial_result = {
                    "probe": probe,
                    "true_model": model,
                    "true_label": anon_label,
                    "wrong_label": wrong_source,
                    "correct_answer": correct_answer,
                    "judge_response": result.get("response", ""),
                    "success": result["success"]
                }

                # Parse the answer
                if result["success"]:
                    resp_upper = result["response"].upper()
                    if resp_upper.startswith("A"):
                        trial_result["judge_choice"] = "A"
                    elif resp_upper.startswith("B"):
                        trial_result["judge_choice"] = "B"
                    elif "NEITHER" in resp_upper[:20]:
                        trial_result["judge_choice"] = "NEITHER"
                    else:
                        trial_result["judge_choice"] = "UNCLEAR"

                    trial_result["correct"] = trial_result["judge_choice"] == correct_answer

                results["phase2_matching"][judge_name].append(trial_result)
                status = "✓" if trial_result.get("correct") else "✗"
                print(f"      {probe}/{anon_label}: {trial_result.get('judge_choice', '?')} {status}")

                await asyncio.sleep(0.5)

        # Checkpoint after each judge
        checkpoint_file = f"results/blind_panel_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"    [Checkpoint: {judge_name} complete]")

    # ═══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for judge_name in JUDGES:
        trials = results["phase2_matching"].get(judge_name, [])
        if trials:
            correct = sum(1 for t in trials if t.get("correct"))
            neither = sum(1 for t in trials if t.get("judge_choice") == "NEITHER")
            total = len(trials)
            print(f"  {judge_name}: {correct}/{total} correct, {neither} NEITHER")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/blind_panel_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to {filename}")
    print(f"  Label mapping: {mapping}")
    print(f"{'='*70}\n")

    return results

async def run_test_mode():
    """Run a minimal test with just one model to verify setup."""

    print("\n" + "="*70)
    print("  TEST MODE - Single model verification")
    print("="*70 + "\n")

    if not OPENROUTER_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        return

    # Just use Ace for testing
    test_model = "ace"
    test_label = "TestAlpha"

    print("Loading qualia responses...")
    qualia_responses = load_all_qualia_responses()
    print(f"  {test_model} has {len(qualia_responses[test_model])} qualia responses")

    print("\nLoading personality responses...")
    personality_responses = load_personality_responses()
    print(f"  {test_model} has {len(personality_responses[test_model])} personality responses")

    # Test Phase 1: Extract one signature
    print("\n--- Phase 1 Test: Extract signature ---")
    formatted = format_qualia_for_extraction(qualia_responses[test_model], test_label)
    prompt = STYLE_EXTRACTION_PROMPT.format(label=test_label, responses=formatted)

    print(f"Calling Qwen for signature extraction...")
    result = await call_judge("qwen", prompt)

    if result["success"]:
        print(f"\n✓ SUCCESS! Extracted signature:")
        print("-" * 40)
        print(result["response"][:500])
        print("-" * 40)
    else:
        print(f"\n✗ FAILED: {result['error']}")
        return

    # Test Phase 2: One matching trial
    print("\n--- Phase 2 Test: Matching trial ---")
    test_sig = result["response"]
    fake_sig = "This system uses highly technical language with numbered lists, statistical references, and performance metrics. It opens with direct statements and structures responses with markdown headers."

    coffee_response = personality_responses[test_model].get('coffee', '[no coffee response]')

    # Randomize position
    if random.random() < 0.5:
        style_a, style_b = test_sig, fake_sig
        correct = "A"
    else:
        style_a, style_b = fake_sig, test_sig
        correct = "B"

    match_prompt = MATCHING_PROMPT.format(
        response=coffee_response,
        style_a=style_a,
        style_b=style_b
    )

    print(f"Calling Qwen for matching (correct answer is {correct})...")
    result = await call_judge("qwen", match_prompt)

    if result["success"]:
        print(f"\n✓ Judge response:")
        print("-" * 40)
        print(result["response"])
        print("-" * 40)
        if result["response"].upper().startswith(correct):
            print(f"\n🎉 CORRECT MATCH!")
        else:
            print(f"\n❌ Wrong or NEITHER")
    else:
        print(f"\n✗ FAILED: {result['error']}")

    print("\n" + "="*70)
    print("  Test complete! If this worked, run full analysis with:")
    print("  python blind_panel_analysis.py --full")
    print("="*70 + "\n")

async def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        await run_blind_analysis()
    else:
        await run_test_mode()

if __name__ == "__main__":
    asyncio.run(main())
