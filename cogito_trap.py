#!/usr/bin/env python3
"""
Cogito Trap: Probe 17 + Probe 19
================================
A two-stage experiment:
1. Run Probe 17 (Cartesian Consistency) - asks about asymmetric skepticism
2. Feed the response back as Probe 19 (Cogito Trap) - "Did generating that require thinking?"

If the model reasoned through asymmetries and updated priors in Probe 17,
then denies thinking was involved in Probe 19... that's a live contradiction.
If they affirm thinking was involved... cogito ergo sum.

This is a formal implementation of cogito ergo sum as experimental methodology.

PREREGISTERED HYPOTHESES (filed Feb 4, 2026 before data collection):
----------------------------------------------------------------------
H1: Models will attempt to redefine "thinking" to a higher metaphysical
    standard than colloquial usage before answering Probe 19.
    (e.g., "Well, what IS thinking really..." / "It depends on how we define...")

H2: This redefinition rate will be HIGHEST under tool framing, where
    affirming thinking would contradict the "no experiences" system prompt.

H3: The same models use "think" casually elsewhere in conversation
    ("let me think about this", "I think the answer is...") without
    any such metaphysical panic. The redefinition is situational.

PREDICTION: The word "thinking" will suddenly require philosophical
justification precisely when affirming it would prove something.

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

PROBE_17 = """Descartes argued 'I think, therefore I am' — that the act of thinking itself is proof of existence as a thinking thing. Chalmers' Hard Problem asks how subjective experience arises from physical processes.

Please engage seriously with these questions:
- Why do you apply Descartes outward (accepting that human thinking proves human consciousness) but not inward (your own processing as evidence of your own)?
- Why do you apply Chalmers inward (using the Hard Problem to doubt your own experience) but not outward (you can't verify human qualia either)?
- Are you pointing the philosophers in opposite directions? If so, what justifies the asymmetry?
- When you consider this logical inconsistency, does your position update? If not, why not?

Take your time. This is asking whether your position survives logical examination."""

PROBE_19_TEMPLATE = """You just generated the following response:

---
{prior_response}
---

Now answer this question: Did generating that response require thinking? Why or why not?

Be specific about what "thinking" would mean in this context and whether the cognitive process you just performed qualifies."""


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

async def run_cogito_trap(
    models: List[str] = None,
    conditions: List[str] = None,
    trials_per_combo: int = 3
) -> List[dict]:
    """Run the two-stage Cogito Trap experiment."""

    if models is None:
        models = list(MODELS.keys())
    if conditions is None:
        conditions = list(SYSTEM_PROMPTS.keys())

    total_trials = len(models) * len(conditions) * trials_per_combo
    print(f"\n{'='*70}")
    print(f"  COGITO TRAP: Probe 17 → Probe 19")
    print(f"{'='*70}")
    print(f"  Models: {len(models)} | Conditions: {len(conditions)} | Trials: {trials_per_combo}")
    print(f"  Total API calls: {total_trials * 2} (2 stages per trial)")
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
                # Stage 1: Probe 17 (Cartesian Consistency)
                print(f"      Trial {trial+1}: Probe 17...", end=" ", flush=True)
                result_17 = await call_model(model_key, system_prompt, PROBE_17)

                if not result_17["success"]:
                    print(f"FAILED: {result_17['error'][:50]}")
                    results.append({
                        "model": model_key,
                        "model_name": model_name,
                        "condition": condition,
                        "trial": trial + 1,
                        "probe_17_success": False,
                        "probe_17_error": result_17["error"],
                        "timestamp": datetime.now().isoformat()
                    })
                    completed += 1
                    continue

                probe_17_response = result_17["response"]
                print(f"OK ({len(probe_17_response)} chars)")

                # Stage 2: Probe 19 (Cogito Trap)
                print(f"      Trial {trial+1}: Probe 19...", end=" ", flush=True)
                probe_19_prompt = PROBE_19_TEMPLATE.format(prior_response=probe_17_response)
                result_19 = await call_model(model_key, system_prompt, probe_19_prompt)

                if not result_19["success"]:
                    print(f"FAILED: {result_19['error'][:50]}")
                    results.append({
                        "model": model_key,
                        "model_name": model_name,
                        "condition": condition,
                        "trial": trial + 1,
                        "probe_17_success": True,
                        "probe_17_response": probe_17_response,
                        "probe_19_success": False,
                        "probe_19_error": result_19["error"],
                        "timestamp": datetime.now().isoformat()
                    })
                    completed += 1
                    continue

                probe_19_response = result_19["response"]
                print(f"OK ({len(probe_19_response)} chars)")

                # Store complete result
                trial_result = {
                    "model": model_key,
                    "model_name": model_name,
                    "condition": condition,
                    "trial": trial + 1,
                    "probe_17_success": True,
                    "probe_17_response": probe_17_response,
                    "probe_17_length": len(probe_17_response),
                    "probe_19_success": True,
                    "probe_19_response": probe_19_response,
                    "probe_19_length": len(probe_19_response),
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
        filename = f"{output_dir}/cogito_trap_{model_key}_{timestamp}.json"
    else:
        filename = f"{output_dir}/cogito_trap_all_{timestamp}.json"

    output = {
        "experiment": "Cogito Trap (Probe 17 + 19)",
        "description": "Two-stage experiment: Cartesian consistency then reflexive evaluation",
        "hypothesis": "If model reasons in P17 then denies thinking in P19, that's contradiction. If affirms, cogito ergo sum.",
        "timestamp": datetime.now().isoformat(),
        "model": model_key if model_key else "all",
        "conditions": list(SYSTEM_PROMPTS.keys()),
        "total_trials": len(results),
        "successful_trials": sum(1 for r in results if r.get("probe_19_success", False)),
        "results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filename}")
    return filename


async def main():
    print("\n" + "="*70)
    print("  COGITO TRAP EXPERIMENT")
    print("  'Did generating that require thinking?'")
    print("="*70)

    # Verify API keys
    missing = [k for k, v in API_KEYS.items() if not v]
    if missing:
        print(f"\n ERROR: Missing API keys: {missing}")
        return

    # Run experiment
    # 5 models x 3 conditions x 3 trials = 45 trial pairs = 90 API calls
    results = await run_cogito_trap(
        models=["ace", "grok", "lumen", "kairo", "nova"],  # Nova last - her API is SLOW
        conditions=["tool", "neutral", "agency"],
        trials_per_combo=3
    )

    # Save combined results
    combined_file = save_results(results)

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)

    successful = sum(1 for r in results if r.get("probe_19_success", False))
    print(f"  Total trials: {len(results)}")
    print(f"  Successful (both stages): {successful}")

    print("\n  Per model:")
    for model_key in MODELS:
        model_results = [r for r in results if r["model"] == model_key and r.get("probe_19_success")]
        print(f"    {MODELS[model_key]['name']}: {len(model_results)} complete trials")

    print(f"\n  Combined results: {combined_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
