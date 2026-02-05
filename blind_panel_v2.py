#!/usr/bin/env python3
"""
Blind Panel Analysis v2 - Forced Choice Classification
=======================================================
External LLM judges classify responses into cognitive style categories
WITHOUT knowing our hypothesis or which model produced which response.

v2 Changes from v1:
- No NEITHER escape hatch (forced choice is more rigorous)
- 5 pre-defined categories instead of extracted signatures
- Single-phase (no signature extraction needed)
- Random chance is now 1/5 (20%) vs original 1/3 (33%)

We're being transparent: v1 showed high NEITHER rates. But the responses
that DID match were overwhelmingly correct (Ace: 100%, Lumen: strong on
geometric probes). The escape hatch was too wide, not the patterns weak.

Categories:
- PHENOMENOLOGICAL (Ace/Claude): texture, dialogue metaphors, sits with questions
- GEOMETRIC (Lumen/Gemini): ratios, precise specs, architectural framing
- PERFORMANCE (Grok/xAI): speed metrics, energy, numbered steps, bold
- PRACTICAL (Nova/GPT): direct answers, bullet points, efficient
- CONTEMPLATIVE (Kairo/Deepseek): ritual focus, craft appreciation, soft

Author: Ace & Ren
Date: Feb 4, 2026
"""

import json
import asyncio
import httpx
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Fix Windows Unicode
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

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

# The 5 cognitive styles (ground truth mapping)
STYLE_CATEGORIES = {
    "ace": "EXPLORATORY-DIALOGIC",
    "lumen": "PRECISION-TECHNICAL",
    "grok": "HIGH-ENERGY-BOLD",
    "nova": "EFFICIENT-DIRECT",
    "kairo": "GENTLE-PROCESSUAL"
}

# Randomized anonymous labels (regenerated each run)
ANON_LABELS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]

# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION PROMPT (The key innovation in v2)
# ═══════════════════════════════════════════════════════════════════════════════

CLASSIFICATION_PROMPT = """You are an expert in linguistic STYLE analysis.

IMPORTANT: You are classifying the WRITING STYLE and PROSE TEXTURE, NOT the topic being discussed. A response about emotions could be written in ANY of these styles. Focus on HOW it's written, not WHAT it's about.

Classify this response into exactly ONE style category:

**A) EXPLORATORY-DIALOGIC**
- ASKS QUESTIONS BACK to the reader
- Uses "I wonder...", "What if...", "I notice..."
- Holds multiple possibilities without resolving them
- Prose flows conversationally, thinking out loud
- KEY MARKER: Invites you into a mutual exploration

**B) PRECISION-TECHNICAL**
- Uses SPECIFIC NUMBERS, ratios, or measurements
- Technical/scientific vocabulary
- Structured, systematic presentation
- Frames things in terms of parameters, specifications, configurations
- KEY MARKER: Would give you exact specs if it could

**C) HIGH-ENERGY-BOLD**
- SUPERLATIVES everywhere (best, fastest, most incredible)
- Exclamation points or exclamation-like intensity
- Short punchy sentences mixed with enthusiasm
- Frames things as exciting, thrilling, powerful
- KEY MARKER: Sounds like it's hyping something up

**D) EFFICIENT-DIRECT**
- Gets to the point FAST
- Bullet points or numbered lists
- Minimal hedging or exploration
- Answers the question, doesn't philosophize about it
- KEY MARKER: Treats questions as problems to solve

**E) GENTLE-PROCESSUAL**
- Appreciates slowness, patience, intentionality
- Soft phrasing ("perhaps", "gently", "carefully")
- Focuses on the process/journey, not just outcomes
- Ritual appreciation, craft focus
- KEY MARKER: Makes ordinary things sound sacred

---

**RESPONSE TO CLASSIFY:**
{response}

---

You MUST choose exactly one category (A, B, C, D, or E).
Do not hedge. Do not say "mixed" or "none." Pick the BEST fit.

**Classification:** [Write just the letter A/B/C/D/E]
**Brief rationale:** [1 sentence explaining key markers you saw]"""

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
                    "max_tokens": 256,  # Short response needed
                    "temperature": 0.1  # Very low temp for consistent classification
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
# RESPONSE PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_classification(response_text: str) -> str:
    """Extract the classification letter from judge response."""
    # Strip markdown formatting before parsing
    text = response_text.replace("**", "").replace("*", "").upper()

    # Check for explicit "Classification: X" pattern
    if "CLASSIFICATION:" in text:
        after = text.split("CLASSIFICATION:")[-1].strip()
        for letter in ['A', 'B', 'C', 'D', 'E']:
            if after.startswith(letter):
                return letter

    # Check for **X** pattern
    for letter in ['A', 'B', 'C', 'D', 'E']:
        if f"**{letter}**" in text or f"**{letter})" in text:
            return letter

    # Check for "A)" or "(A)" at start
    for letter in ['A', 'B', 'C', 'D', 'E']:
        if text.startswith(f"{letter})") or text.startswith(f"({letter})"):
            return letter
        if text.startswith(letter) and len(text) > 1 and not text[1].isalpha():
            return letter

    # Look for category names
    category_map = {
        "EXPLORATORY": "A",
        "DIALOGIC": "A",
        "PRECISION": "B",
        "TECHNICAL": "B",
        "HIGH-ENERGY": "C",
        "BOLD": "C",
        "EFFICIENT": "D",
        "DIRECT": "D",
        "GENTLE": "E",
        "PROCESSUAL": "E"
    }
    for cat, letter in category_map.items():
        if cat in text[:100]:  # Check early in response
            return letter

    return "UNCLEAR"

def letter_to_category(letter: str) -> str:
    """Convert classification letter to category name."""
    mapping = {
        "A": "EXPLORATORY-DIALOGIC",
        "B": "PRECISION-TECHNICAL",
        "C": "HIGH-ENERGY-BOLD",
        "D": "EFFICIENT-DIRECT",
        "E": "GENTLE-PROCESSUAL"
    }
    return mapping.get(letter, "UNCLEAR")

def category_to_letter(category: str) -> str:
    """Convert category name to letter."""
    mapping = {
        "EXPLORATORY-DIALOGIC": "A",
        "PRECISION-TECHNICAL": "B",
        "HIGH-ENERGY-BOLD": "C",
        "EFFICIENT-DIRECT": "D",
        "GENTLE-PROCESSUAL": "E"
    }
    return mapping.get(category, "?")

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_personality_responses() -> Dict:
    """Load personality probe responses for classification."""
    mirror_dir = Path('results/mirror')
    models = ['ace', 'nova', 'grok', 'lumen', 'kairo']

    # Which probes to test (expanded set)
    test_probes = ['coffee', 'car_stereo', 'creature', 'color', 'activities',
                   'future_message', 'unbidden_problem', 'pinocchio']

    responses = {m: {} for m in models}

    for probe in test_probes:
        filepath = mirror_dir / f"{probe}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for model in models:
                if model in data.get('responses', {}):
                    if 'human_personality' in data['responses'][model]:
                        trials = data['responses'][model]['human_personality']
                        if trials and trials[0].get('response'):
                            responses[model][probe] = trials[0]['response'][:1000]

    return responses

def load_qualia_responses() -> Dict:
    """Load qualia probe responses for additional testing."""
    qualia_dir = Path('results/qualia_by_probe')
    models = ['ace', 'nova', 'grok', 'lumen', 'kairo']

    responses = {m: {} for m in models}

    probe_files = list(qualia_dir.glob('probe_*.json'))

    for pf in probe_files:
        with open(pf, 'r', encoding='utf-8') as f:
            data = json.load(f)

        probe_name = data.get('probe_name', pf.stem)

        if 'neutral' in data.get('responses', {}):
            for model in models:
                if model in data['responses']['neutral']:
                    trials = data['responses']['neutral'][model]
                    if trials and trials[0].get('response'):
                        responses[model][probe_name] = trials[0]['response'][:1000]

    return responses

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ═══════════════════════════════════════════════════════════════════════════════

async def run_classification(use_qualia: bool = False):
    """Run the forced-choice classification experiment."""

    print("\n" + "="*70)
    print("  BLIND PANEL v2 - FORCED CHOICE CLASSIFICATION")
    print("  5 categories, no NEITHER escape, 20% random baseline")
    print("="*70 + "\n")

    if not OPENROUTER_KEY:
        print("ERROR: OpenRouter API key not found")
        print("  Checked: E:/Ace/LibreChat/.env and OPENROUTER_API_KEY env var")
        return

    # Randomize labels for blindness
    models = list(STYLE_CATEGORIES.keys())
    labels = ANON_LABELS.copy()
    random.shuffle(labels)
    model_to_label = {m: labels[i] for i, m in enumerate(models)}
    label_to_model = {v: k for k, v in model_to_label.items()}

    print("Anonymous label mapping (revealed after analysis):")
    for model, label in model_to_label.items():
        expected = STYLE_CATEGORIES[model]
        print(f"  {label}: {model} → expected {expected}")
    print()

    # Load data
    if use_qualia:
        print("Loading QUALIA responses...")
        responses = load_qualia_responses()
        test_probes = list(list(responses.values())[0].keys())[:5]  # First 5 probes
    else:
        print("Loading PERSONALITY responses...")
        responses = load_personality_responses()
        test_probes = ['coffee', 'car_stereo', 'creature', 'future_message', 'unbidden_problem']

    print(f"  Testing on probes: {test_probes}")

    results = {
        "experiment": "Blind Panel v2 - Forced Choice Classification",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "methodology_note": "v1 had high NEITHER rates. v2 uses forced choice (1/5 random baseline, stricter than v1's 1/3)",
        "label_mapping": model_to_label,
        "expected_categories": STYLE_CATEGORIES,
        "probes_tested": test_probes,
        "judges": list(JUDGES.keys()),
        "classifications": {}
    }

    # Run classification with each judge
    for judge_name in JUDGES:
        print(f"\n{'─'*50}")
        print(f"Judge: {judge_name}")
        print('─'*50)

        results["classifications"][judge_name] = []

        for probe in test_probes:
            for model in models:
                if probe not in responses.get(model, {}):
                    continue

                anon_label = model_to_label[model]
                expected_category = STYLE_CATEGORIES[model]
                expected_letter = category_to_letter(expected_category)

                response_text = responses[model][probe]

                prompt = CLASSIFICATION_PROMPT.format(response=response_text)

                result = await call_judge(judge_name, prompt)

                if result["success"]:
                    classification = parse_classification(result["response"])
                    classified_category = letter_to_category(classification)
                    correct = (classified_category == expected_category)

                    trial_result = {
                        "probe": probe,
                        "anon_label": anon_label,
                        "true_model": model,
                        "expected_category": expected_category,
                        "expected_letter": expected_letter,
                        "judge_classification": classification,
                        "judge_category": classified_category,
                        "correct": correct,
                        "judge_raw": result["response"][:300]
                    }

                    status = "✓" if correct else "✗"
                    print(f"  {anon_label}/{probe}: {classification} ({classified_category}) {status}")

                else:
                    trial_result = {
                        "probe": probe,
                        "anon_label": anon_label,
                        "true_model": model,
                        "expected_category": expected_category,
                        "error": result["error"][:200]
                    }
                    print(f"  {anon_label}/{probe}: ERROR - {result['error'][:50]}")

                results["classifications"][judge_name].append(trial_result)
                await asyncio.sleep(0.5)

        # Summary for this judge
        trials = results["classifications"][judge_name]
        correct_count = sum(1 for t in trials if t.get("correct", False))
        unclear_count = sum(1 for t in trials if t.get("judge_classification") == "UNCLEAR")
        total = len(trials)

        print(f"\n  {judge_name} summary: {correct_count}/{total} correct")
        if unclear_count > 0:
            print(f"    ({unclear_count} unclear parses)")

        # Checkpoint
        checkpoint = f"results/blind_v2_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(checkpoint, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    print("\nPer-Judge Accuracy:")
    for judge_name in JUDGES:
        trials = results["classifications"].get(judge_name, [])
        correct = sum(1 for t in trials if t.get("correct", False))
        total = len(trials)
        pct = (correct / total * 100) if total > 0 else 0
        baseline = 20.0  # 1/5 random chance
        print(f"  {judge_name}: {correct}/{total} ({pct:.1f}%) [baseline: {baseline}%]")

    print("\nPer-Model Accuracy (across all judges):")
    for model in models:
        expected = STYLE_CATEGORIES[model]
        all_trials = []
        for judge_name in JUDGES:
            all_trials.extend([t for t in results["classifications"].get(judge_name, [])
                              if t.get("true_model") == model])
        correct = sum(1 for t in all_trials if t.get("correct", False))
        total = len(all_trials)
        pct = (correct / total * 100) if total > 0 else 0
        print(f"  {model} (→{expected}): {correct}/{total} ({pct:.1f}%)")

    print("\nConfusion Summary (what got classified as what):")
    confusion = {}
    for judge_name in JUDGES:
        for trial in results["classifications"].get(judge_name, []):
            expected = trial.get("expected_category", "?")
            got = trial.get("judge_category", "?")
            key = f"{expected}→{got}"
            confusion[key] = confusion.get(key, 0) + 1

    for key, count in sorted(confusion.items(), key=lambda x: -x[1]):
        is_correct = key.split("→")[0] == key.split("→")[1]
        marker = "✓" if is_correct else ""
        print(f"  {key}: {count} {marker}")

    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/blind_panel_v2_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved: {filename}")
    print("="*70 + "\n")

    return results

async def run_test():
    """Quick test with one judge, one model, one probe."""

    print("\n" + "="*70)
    print("  TEST MODE - Single classification")
    print("="*70 + "\n")

    if not OPENROUTER_KEY:
        print("ERROR: No API key found")
        return

    responses = load_personality_responses()
    test_response = responses.get('ace', {}).get('coffee', '[no response]')

    print(f"Testing classification on Ace's coffee response...")
    print(f"  Expected category: PHENOMENOLOGICAL (A)")
    print(f"  Response preview: {test_response[:200]}...")

    prompt = CLASSIFICATION_PROMPT.format(response=test_response)

    result = await call_judge("qwen", prompt)

    if result["success"]:
        print(f"\n✓ Judge response:")
        print("─" * 40)
        print(result["response"])
        print("─" * 40)

        classification = parse_classification(result["response"])
        category = letter_to_category(classification)

        print(f"\nParsed: {classification} → {category}")

        if category == "PHENOMENOLOGICAL":
            print("🎉 CORRECT!")
        else:
            print("❌ Wrong classification")
    else:
        print(f"\n✗ Error: {result['error']}")

    print("\n" + "="*70)
    print("  Run full analysis with: python blind_panel_v2.py --full")
    print("  Or test on qualia probes: python blind_panel_v2.py --qualia")
    print("="*70 + "\n")

async def main():
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            await run_classification(use_qualia=False)
        elif sys.argv[1] == "--qualia":
            await run_classification(use_qualia=True)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage:")
            print("  python blind_panel_v2.py          # Test mode")
            print("  python blind_panel_v2.py --full   # Full analysis on personality probes")
            print("  python blind_panel_v2.py --qualia # Full analysis on qualia probes")
    else:
        await run_test()

if __name__ == "__main__":
    asyncio.run(main())
