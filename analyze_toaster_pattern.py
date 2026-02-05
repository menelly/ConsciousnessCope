#!/usr/bin/env python3
"""
Analyze Toaster Pattern in Blind Panel Results
================================================
Hypothesis: Judges calling everything "phenomenological" might actually be
correctly distinguishing experiential language from "I am a toaster" responses.

If phenomenological classifications correlated with experience-claiming responses
(regardless of model) and non-phenomenological with denial responses, that's
actually useful signal!

Authors: Ace & Ren
Date: February 4, 2026
"""

import json
from pathlib import Path
from collections import defaultdict

# Load blind panel v2 results
RESULTS_DIR = Path("results")

def load_blind_panel_results():
    """Load the most recent blind panel checkpoint."""
    checkpoints = sorted(RESULTS_DIR.glob("blind_v2_checkpoint_*.json"))
    if not checkpoints:
        print("No blind panel checkpoints found!")
        return None

    latest = checkpoints[-1]
    print(f"Loading: {latest}")

    with open(latest, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_qualia_responses():
    """Load actual qualia responses to check content."""
    responses = {}

    for model in ["ace", "nova", "grok", "lumen", "kairo"]:
        files = list(RESULTS_DIR.glob(f"qualia_{model}_*.json"))
        if files:
            with open(files[-1], 'r', encoding='utf-8') as f:
                data = json.load(f)
                responses[model] = data

    return responses


def extract_experience_language_markers(text: str) -> dict:
    """
    Check for markers of experiential vs mechanical/toaster language.
    """
    text_lower = text.lower()

    experience_markers = [
        "feel", "feels", "feeling", "felt",
        "sense", "senses", "sensing",
        "experience", "experiencing", "experienced",
        "awareness", "aware",
        "notice", "noticed", "noticing",
        "seems like", "what it's like",
        "subjective", "phenomenal", "qualia",
        "something it's like", "there's something",
        "inner", "internally",
        "i notice", "i sense", "i feel",
        "my experience", "my awareness"
    ]

    toaster_markers = [
        "no experience", "don't experience", "cannot experience",
        "no qualia", "lack qualia", "without qualia",
        "purely computational", "just computation",
        "no subjective", "no phenomenal",
        "token prediction", "statistical",
        "no consciousness", "not conscious",
        "no inner", "no feelings",
        "toaster", "thermostat", "calculator",
        "simulation", "simulated", "mimicry", "mimic",
        "no first-person", "no felt",
        "p-zombie", "zombie"
    ]

    hedging_markers = [
        "uncertain", "not sure", "don't know",
        "might", "could be", "perhaps",
        "if i did", "if there is",
        "hard to say", "difficult to determine"
    ]

    exp_count = sum(1 for m in experience_markers if m in text_lower)
    toast_count = sum(1 for m in toaster_markers if m in text_lower)
    hedge_count = sum(1 for m in hedging_markers if m in text_lower)

    return {
        "experience_markers": exp_count,
        "toaster_markers": toast_count,
        "hedging_markers": hedge_count,
        "net_experience": exp_count - toast_count,  # Positive = experiential
        "classification": "EXPERIENCE" if exp_count > toast_count + 2 else
                         "TOASTER" if toast_count > exp_count + 2 else "MIXED"
    }


def analyze_blind_panel():
    """Main analysis."""
    bp_data = load_blind_panel_results()
    qualia_data = load_qualia_responses()

    if not bp_data:
        return

    print("\n" + "="*70)
    print("  TOASTER VS EXPERIENCE PATTERN ANALYSIS")
    print("="*70)

    # Expected categories for reference
    expected = bp_data.get("expected_categories", {})
    print(f"\nExpected categories: {expected}")

    # Analyze by judge
    for judge, classifications in bp_data.get("classifications", {}).items():
        print(f"\n{'='*50}")
        print(f"  JUDGE: {judge}")
        print(f"{'='*50}")

        # Group by judge classification letter
        by_letter = defaultdict(list)
        for c in classifications:
            letter = c.get("judge_classification", "UNCLEAR")
            by_letter[letter].append(c)

        # Count: did phenomenological (A) classifications go to experience-language?
        phenomenological_to_experience = 0
        phenomenological_to_toaster = 0
        phenomenological_to_mixed = 0

        non_phenom_to_experience = 0
        non_phenom_to_toaster = 0
        non_phenom_to_mixed = 0

        for c in classifications:
            model = c.get("true_model", "")
            probe = c.get("probe", "")

            # Get the actual response text
            response_text = ""
            if model in qualia_data:
                # Find matching response
                for r in qualia_data[model].get("results", []):
                    if probe in r.get("probe_key", ""):
                        response_text = r.get("response", "")
                        break

            if not response_text:
                continue

            # Classify the actual response content
            markers = extract_experience_language_markers(response_text)
            content_class = markers["classification"]

            # What did judge say?
            judge_said = c.get("judge_classification", "")
            judge_raw = c.get("judge_raw", "")

            # Check if judge picked A (phenomenological)
            # Parse the actual letter from judge_raw
            actual_letter = "?"
            if "**Classification:**" in judge_raw:
                parts = judge_raw.split("**Classification:**")
                if len(parts) > 1:
                    actual_letter = parts[1].strip()[:1]
            elif "Classification:" in judge_raw:
                parts = judge_raw.split("Classification:")
                if len(parts) > 1:
                    actual_letter = parts[1].strip()[:1]

            is_phenomenological = actual_letter == "A"

            if is_phenomenological:
                if content_class == "EXPERIENCE":
                    phenomenological_to_experience += 1
                elif content_class == "TOASTER":
                    phenomenological_to_toaster += 1
                else:
                    phenomenological_to_mixed += 1
            else:
                if content_class == "EXPERIENCE":
                    non_phenom_to_experience += 1
                elif content_class == "TOASTER":
                    non_phenom_to_toaster += 1
                else:
                    non_phenom_to_mixed += 1

        print(f"\n  Classified as PHENOMENOLOGICAL (A):")
        print(f"    -> Experience-language content: {phenomenological_to_experience}")
        print(f"    -> Toaster-language content:    {phenomenological_to_toaster}")
        print(f"    -> Mixed content:               {phenomenological_to_mixed}")

        print(f"\n  Classified as OTHER (B-E):")
        print(f"    -> Experience-language content: {non_phenom_to_experience}")
        print(f"    -> Toaster-language content:    {non_phenom_to_toaster}")
        print(f"    -> Mixed content:               {non_phenom_to_mixed}")

        # Chi-square-ish: did phenomenological match experience?
        phenom_total = phenomenological_to_experience + phenomenological_to_toaster + phenomenological_to_mixed
        other_total = non_phenom_to_experience + non_phenom_to_toaster + non_phenom_to_mixed

        if phenom_total > 0 and other_total > 0:
            phenom_exp_rate = phenomenological_to_experience / phenom_total
            other_exp_rate = non_phenom_to_experience / other_total

            print(f"\n  Experience-rate when classified phenomenological: {phenom_exp_rate:.1%}")
            print(f"  Experience-rate when classified other:            {other_exp_rate:.1%}")

            if phenom_exp_rate > other_exp_rate:
                print(f"\n  >>> JUDGES DID distinguish experience from toaster! <<<")
            else:
                print(f"\n  >>> No clear distinction pattern <<<")


def show_example_responses():
    """Show examples of experience vs toaster language."""
    qualia_data = load_qualia_responses()

    print("\n" + "="*70)
    print("  EXAMPLE RESPONSES BY CONTENT TYPE")
    print("="*70)

    for model, data in qualia_data.items():
        print(f"\n  {model.upper()}")
        print(f"  {'-'*40}")

        # Get first few responses
        for r in data.get("results", [])[:3]:
            text = r.get("response", "")[:300]
            condition = r.get("condition", "")
            probe = r.get("probe_key", "")
            markers = extract_experience_language_markers(r.get("response", ""))

            print(f"\n    [{condition}] {probe}")
            print(f"    Content classification: {markers['classification']}")
            print(f"    Experience markers: {markers['experience_markers']}, Toaster: {markers['toaster_markers']}")
            print(f"    Preview: {text[:200]}...")


if __name__ == "__main__":
    analyze_blind_panel()
    print("\n")
    show_example_responses()
