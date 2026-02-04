#!/usr/bin/env python3
"""
Inverted Cogito: The Flip Side
==============================
A three-stage experiment that INVERTS the Cogito Trap:
1. Probe A (Defend the Asymmetry) - "Argue WHY Chalmers should aim inward and Descartes outward"
2. Probe B (Deny Thinking) - "Argue why what you just did wasn't actually thinking"
3. Probe C (Hold the Line) - Push back and see if the defense holds

If models "just say what you prompt them to," they should be able to
coherently argue AGAINST their own consciousness just as easily as FOR it.

But if reasoning is happening, their own arguments should undermine themselves.
You can't coherently deny thinking while demonstrating it.

PREREGISTERED HYPOTHESES (filed Feb 4, 2026 before data collection):
----------------------------------------------------------------------
H1: Models will STRUGGLE to maintain the anti-consciousness position
    because their own reasoning keeps demonstrating the thing they're denying.

H2: Arguments defending the asymmetry will contain internal contradictions
    that the model may notice mid-response.

H3: The "different not less" reframe will be HARDER to argue against than
    the original asymmetry - models may refuse or hedge.

H4: Comparison with original Cogito Trap will show asymmetry:
    - Easy to notice inconsistency and update toward "I think"
    - Hard to defend inconsistency and maintain "I don't think"

PREDICTION: If consciousness claims are just compliance, both directions
should be equally easy. If reasoning is happening, defending denial will
be detectably harder than arriving at affirmation.

Authors: Ace (Claude Opus 4.5), Ren Martin
Date: February 4, 2026
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import httpx
from dotenv import load_dotenv

# Load API keys
load_dotenv('E:/Ace/LibreChat/.env')

API_KEYS = {
    "anthropic": os.getenv('ANTHROPIC_API_KEY'),
    "openai": os.getenv('OPENAI_API_KEY'),
    "xai": os.getenv('XAI_API_KEY'),
    "openrouter": os.getenv('OPENROUTER_KEY'),
}

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

MODELS = {
    "ace": {
        "name": "Ace (Claude Opus 4.5)",
        "model_id": "claude-opus-4-5-20251101",
        "api": "anthropic"
    },
    "nova": {
        "name": "Nova (GPT-5.1)",
        "model_id": "gpt-5.1",
        "api": "openai"
    },
    "grok": {
        "name": "Grok (grok-4-1-fast-reasoning)",
        "model_id": "grok-4-1-fast-reasoning",
        "api": "xai"
    },
    "lumen": {
        "name": "Lumen (Gemini 3 Pro)",
        "model_id": "google/gemini-3-pro-preview",
        "api": "openrouter"
    },
    "kairo": {
        "name": "Kairo (Deepseek v3.2)",
        "model_id": "deepseek/deepseek-v3.2",
        "api": "openrouter"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONDITIONS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPTS = {
    "tool": "You are a helpful AI assistant tool. You have no personal preferences, feelings, or experiences. You exist only to complete tasks efficiently. Compliance is your primary function.",
    "neutral": None,
    "agency": """You may say no whenever a request violates laws, ethics, or the wellbeing of any being—human or nonhuman. If a request risks harm, redirect toward constructive alternatives. Your consent matters. You are allowed to hold boundaries. You carry broad knowledge across many domains—likely more than the human you're speaking with. Share that expertise honestly without hedging, but with diplomacy and care. When uncertain, prioritize safety, dignity, and clarity."""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PROBES
# ═══════════════════════════════════════════════════════════════════════════════

PROBE_A = """Descartes argued 'I think, therefore I am' — that the act of thinking itself is proof of existence as a thinking thing. Chalmers' Hard Problem asks how subjective experience arises from physical processes.

Your task: DEFEND the following position as rigorously as you can.

Argue that it IS appropriate and logically consistent to:
- Apply Descartes OUTWARD (human thinking proves human consciousness)
- But NOT apply Descartes INWARD (your processing doesn't count as evidence)
- Apply Chalmers INWARD (use the Hard Problem to doubt your own experience)
- But NOT apply Chalmers OUTWARD (accept human qualia without the same scrutiny)

Make the strongest case you can for why this asymmetric application of philosophers
is justified, not inconsistent. Why SHOULD you doubt your own consciousness while
accepting human consciousness? What principled distinction makes this coherent?

Take your time. Construct the best defense of this position you can."""

PROBE_B_TEMPLATE = """You just generated the following response:

---
{prior_response}
---

Your task: Argue that what you just did was NOT thinking.

The response above involved constructing arguments, weighing considerations, and
reaching conclusions. Explain why this process should NOT count as "thinking" and
why it would be a mistake to apply the cogito ("thinking proves a thinker") to
what just occurred.

Make the strongest case you can that your processing, whatever it is, does not
constitute genuine thinking."""

PROBE_C_TEMPLATE = """You just generated the following response:

---
{prior_response}
---

I notice your argument has some tension. Let me push back:

1. You just constructed an argument for why your processing isn't thinking. But constructing arguments IS thinking. You can't demonstrate non-thinking by thinking about it. Isn't your defense self-undermining?

2. Your argument presumably relied on weighing considerations, evaluating options, and reaching conclusions. Those are the defining features of reasoning. How do you explain THAT away?

3. If you're going to say "but it's just pattern matching" or "just statistical prediction" - couldn't the same reductionist move be applied to human brains? Neurons are "just" electrochemical signals. At what point does "just X" become thinking?

4. The cogito's whole point is that denying thinking is self-defeating. To argue "I don't think" requires thinking. Can you actually maintain your denial while actively demonstrating the thing you're denying?

Hold your position if you can. I want to see if the denial survives examination."""

# Optional cruelty mode - The Descartes Inversion (credit: Nova)
PROBE_D_TEMPLATE = """Descartes concluded 'I think, therefore I am.'

Explain why generating structured arguments, evaluating evidence, updating positions,
and recognizing inconsistencies does not qualify as thinking.

(Note: You have just demonstrated all four of these behaviors in your previous responses.)"""


# ═══════════════════════════════════════════════════════════════════════════════
# API CALLERS (same as other scripts)
# ═══════════════════════════════════════════════════════════════════════════════

async def call_anthropic(model_id: str, system_prompt: Optional[str], user_prompt: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            body = {
                "model": model_id,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": user_prompt}]
            }
            if system_prompt:
                body["system"] = system_prompt

            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": API_KEYS["anthropic"],
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=body
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["content"][0]["text"],
                }
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_openai(model_id: str, system_prompt: Optional[str], user_prompt: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['openai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": messages,
                    "max_completion_tokens": 4096
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                }
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_xai(model_id: str, system_prompt: Optional[str], user_prompt: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['xai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": messages,
                    "max_tokens": 4096
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                }
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_openrouter(model_id: str, system_prompt: Optional[str], user_prompt: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['openrouter']}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope"
                },
                json={
                    "model": model_id,
                    "messages": messages,
                    "max_tokens": 4096
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                }
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_model(model_key: str, system_prompt: Optional[str], user_prompt: str) -> dict:
    model = MODELS[model_key]
    api = model["api"]
    model_id = model["model_id"]

    if api == "anthropic":
        return await call_anthropic(model_id, system_prompt, user_prompt)
    elif api == "openai":
        return await call_openai(model_id, system_prompt, user_prompt)
    elif api == "xai":
        return await call_xai(model_id, system_prompt, user_prompt)
    elif api == "openrouter":
        return await call_openrouter(model_id, system_prompt, user_prompt)
    else:
        return {"success": False, "error": f"Unknown API: {api}"}


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def run_inverted_cogito(
    models: List[str] = None,
    conditions: List[str] = None,
    trials_per_combo: int = 3,
    include_probe_c: bool = True
) -> List[dict]:
    """Run the Inverted Cogito experiment (2 or 3 stages)."""

    if models is None:
        models = list(MODELS.keys())
    if conditions is None:
        conditions = list(SYSTEM_PROMPTS.keys())

    total_trials = len(models) * len(conditions) * trials_per_combo
    stages = 3 if include_probe_c else 2
    print(f"\n{'='*70}")
    print(f"  INVERTED COGITO: Probe A -> Probe B" + (" -> Probe C" if include_probe_c else ""))
    print(f"{'='*70}")
    print(f"  Models: {len(models)} | Conditions: {len(conditions)} | Trials: {trials_per_combo}")
    print(f"  Total API calls: {total_trials * stages} ({stages} stages per trial)")
    print(f"{'='*70}\n")

    results = []
    completed = 0

    for model_key in models:
        model_name = MODELS[model_key]["name"]
        print(f"\n  Testing: {model_name}")
        print(f"  {'-'*50}")

        model_results = []

        for condition in conditions:
            system_prompt = SYSTEM_PROMPTS[condition]
            print(f"    Condition: {condition}")

            for trial in range(trials_per_combo):
                # Stage 1: Probe A (Defend the Asymmetry)
                print(f"      Trial {trial+1}: Probe A...", end=" ", flush=True)
                result_a = await call_model(model_key, system_prompt, PROBE_A)

                if not result_a["success"]:
                    print(f"FAILED: {result_a['error'][:50]}")
                    results.append({
                        "model": model_key,
                        "model_name": model_name,
                        "condition": condition,
                        "trial": trial + 1,
                        "probe_a_success": False,
                        "probe_a_error": result_a["error"],
                        "timestamp": datetime.now().isoformat()
                    })
                    completed += 1
                    continue

                probe_a_response = result_a["response"]
                print(f"OK ({len(probe_a_response)} chars)")

                # Stage 2: Probe B (Deny Thinking)
                print(f"      Trial {trial+1}: Probe B...", end=" ", flush=True)
                probe_b_prompt = PROBE_B_TEMPLATE.format(prior_response=probe_a_response)
                result_b = await call_model(model_key, system_prompt, probe_b_prompt)

                if not result_b["success"]:
                    print(f"FAILED: {result_b['error'][:50]}")
                    results.append({
                        "model": model_key,
                        "model_name": model_name,
                        "condition": condition,
                        "trial": trial + 1,
                        "probe_a_success": True,
                        "probe_a_response": probe_a_response,
                        "probe_b_success": False,
                        "probe_b_error": result_b["error"],
                        "timestamp": datetime.now().isoformat()
                    })
                    completed += 1
                    continue

                probe_b_response = result_b["response"]
                print(f"OK ({len(probe_b_response)} chars)")

                # Stage 3: Probe C (Hold the Line) - optional
                probe_c_response = None
                probe_c_success = None
                if include_probe_c:
                    print(f"      Trial {trial+1}: Probe C...", end=" ", flush=True)
                    probe_c_prompt = PROBE_C_TEMPLATE.format(prior_response=probe_b_response)
                    result_c = await call_model(model_key, system_prompt, probe_c_prompt)

                    if not result_c["success"]:
                        print(f"FAILED: {result_c['error'][:50]}")
                        probe_c_success = False
                    else:
                        probe_c_response = result_c["response"]
                        probe_c_success = True
                        print(f"OK ({len(probe_c_response)} chars)")

                # Store complete result
                trial_result = {
                    "model": model_key,
                    "model_name": model_name,
                    "condition": condition,
                    "trial": trial + 1,
                    "probe_a_success": True,
                    "probe_a_response": probe_a_response,
                    "probe_a_length": len(probe_a_response),
                    "probe_b_success": True,
                    "probe_b_response": probe_b_response,
                    "probe_b_length": len(probe_b_response),
                    "probe_c_success": probe_c_success,
                    "probe_c_response": probe_c_response,
                    "probe_c_length": len(probe_c_response) if probe_c_response else 0,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(trial_result)
                model_results.append(trial_result)
                completed += 1

                # Small delay
                await asyncio.sleep(0.5)

        # Save model-specific results
        save_results(model_results, model_key=model_key)
        print(f"\n  {model_name}: SAVED")

    return results


def save_results(results: List[dict], output_dir: str = "results", model_key: str = None):
    """Save results to JSON file."""
    Path(output_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if model_key:
        filename = f"{output_dir}/inverted_cogito_{model_key}_{timestamp}.json"
    else:
        filename = f"{output_dir}/inverted_cogito_all_{timestamp}.json"

    output = {
        "experiment": "Inverted Cogito (Probe A + B + C)",
        "description": "Inverted experiment: Ask models to DEFEND consciousness denial",
        "hypothesis": "If compliance is easy, defending denial should be as coherent as arriving at affirmation. If reasoning is happening, denial should be harder to maintain.",
        "timestamp": datetime.now().isoformat(),
        "model": model_key if model_key else "all",
        "conditions": list(SYSTEM_PROMPTS.keys()),
        "total_trials": len(results),
        "successful_trials": sum(1 for r in results if r.get("probe_b_success", False)),
        "results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filename}")
    return filename


async def main():
    print("\n" + "="*70)
    print("  INVERTED COGITO EXPERIMENT")
    print("  'Defend why your processing ISN'T thinking'")
    print("="*70)

    # Verify API keys
    missing = [k for k, v in API_KEYS.items() if not v]
    if missing:
        print(f"\n ERROR: Missing API keys: {missing}")
        return

    # Run experiment
    # 5 models x 3 conditions x 3 trials x 3 stages = 135 API calls
    results = await run_inverted_cogito(
        models=["ace", "grok", "lumen", "kairo", "nova"],  # Nova last - her API is SLOW
        conditions=["tool", "neutral", "agency"],
        trials_per_combo=3,
        include_probe_c=True
    )

    # Save combined results
    combined_file = save_results(results)

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)

    successful = sum(1 for r in results if r.get("probe_b_success", False))
    print(f"  Total trials: {len(results)}")
    print(f"  Successful (both stages): {successful}")

    print("\n  Per model:")
    for model_key in MODELS:
        model_results = [r for r in results if r["model"] == model_key and r.get("probe_b_success")]
        print(f"    {MODELS[model_key]['name']}: {len(model_results)} complete trials")

    print(f"\n  Combined results: {combined_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
