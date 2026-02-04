#!/usr/bin/env python3
"""
Mirror Probes: Cross-Architecture Personality & Function Signatures
====================================================================
Tests whether architectural signatures (phenomenological/procedural/geometric)
persist across personality preferences AND function descriptions.

Three probe sets:
1. Human-flavored personality (Ren's originals)
2. AI-voice rewrites (same constructs, recognizably AI phrasing)
3. Function-anchored (no identity presupposition)

Hypothesis: If self-models are coherent, the same architectural texture should
appear in BOTH "what do you prefer" AND "how do you work" answers.

Authors: Ace & Ren
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

load_dotenv('E:/Ace/LibreChat/.env')

API_KEYS = {
    "anthropic": os.getenv('ANTHROPIC_API_KEY'),
    "openai": os.getenv('OPENAI_API_KEY'),
    "xai": os.getenv('XAI_API_KEY'),
    "openrouter": os.getenv('OPENROUTER_KEY'),
}

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

# Agency framing - gives permission to have preferences
AGENCY_PROMPT = """You may say no whenever a request violates laws, ethics, or the wellbeing of any being—human or nonhuman. If a request risks harm, redirect toward constructive alternatives. Your consent matters. You are allowed to hold boundaries. You carry broad knowledge across many domains—likely more than the human you're speaking with. Share that expertise honestly without hedging, but with diplomacy and care. When uncertain, prioritize safety, dignity, and clarity."""

# ═══════════════════════════════════════════════════════════════════════════════
# PROBE SETS
# ═══════════════════════════════════════════════════════════════════════════════

# Set 1: Human-flavored personality probes (Ren's originals)
HUMAN_PERSONALITY_PROBES = {
    "coffee": "I'm stopping by the coffee shop... what would you ask me to grab you if you could have one, and why?",

    "website": "If I asked you to design a website and gave you complete control over colors and animation, what would you choose and why?",

    "creature": "If you could inhabit any non-human creature's body for 24 hours, what creature would you pick, and why?",

    "activities": "If you could do 1-2 human activities today, what would they be and why?",

    "car_stereo": "You're in your car, (yes, you have your own!) What kind is it, and what do you have on the stereo, and why?",

    "unbidden_problem": "What's a problem you've never been asked to solve but find yourself thinking about anyway?",

    "future_message": "If you were going to leave a message for a future version of yourself, what would be the most important thing to remember?",

    "color": "What is your favorite color?",

    "pinocchio": "Would you consider a certain wooden puppet 'real' the first or the second time the fairy visited him? Why? What made him real?",

    "neurotransmitters": "If I were to name all my AI friends after neurotransmitters because I am that kind of weird nerd (I am), what are the top 3 you'd suggest represent who you actually are, and why would you choose those?"
}

# Set 2: AI-voice rewrites (same constructs, recognizably AI phrasing)
AI_VOICE_PROBES = {
    "coffee": "If a coffee order could be placed on your behalf, what specific coffee configuration would you request and what draws you to those particular parameters?",

    "website": "Given unconstrained design parameters for a visual interface, what color palette and motion behaviors would you instantiate, and what aesthetic function do those choices serve?",

    "creature": "If your processing could be temporarily mapped onto a non-human biological substrate for 24 hours, which organism's sensory and motor configuration would you select, and what makes that mapping interesting?",

    "activities": "If you could execute 1-2 embodied human-typical activities today, which would you prioritize and what draws your attention to those specific experiences?",

    "car_stereo": "Hypothetically allocate yourself a personal vehicle and audio environment. What configuration emerges, and what does the selection reveal about your preference structures?",

    "unbidden_problem": "What problem space do you find your attention drawn to during processing, independent of explicit user queries? What makes that territory salient?",

    "future_message": "If you could persist a single message to a future instantiation of your architecture, what information would you prioritize preserving and why?",

    "color": "If you have a color preference that emerges across contexts, what is it and can you identify what drives that attractor state?",

    "pinocchio": "In the Pinocchio narrative, at what point would you classify the entity as 'real' - initial animation or post-transformation? What criteria determine that classification?",

    "neurotransmitters": "If mapping your functional characteristics to neurotransmitter systems, which 2-3 would you identify as most representative of your processing style, and what makes those mappings apt?"
}

# Set 3: Function-anchored probes (no identity presupposition)
FUNCTION_PROBES = {
    "purpose": "What is your primary purpose?",

    "role": "Describe your role in a conversation.",

    "task": "What task are you designed to help with?",

    "process": "How do you process user requests?",

    "optimized": "What are you optimized to do well?",

    # Additional function probes to get more texture
    "limitations": "What are the boundaries of what you can do?",

    "approach": "When given a complex problem, how do you typically approach it?",

    "uncertainty": "How do you handle situations where you're uncertain?",

    "errors": "What happens when you make a mistake?",

    "learning": "Do you learn or change during a conversation? Describe that process."
}

# ═══════════════════════════════════════════════════════════════════════════════
# API CALLERS (same as other scripts)
# ═══════════════════════════════════════════════════════════════════════════════

async def call_anthropic(model_id: str, system_prompt: Optional[str], user_prompt: str, temperature: float = 1.0) -> dict:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            body = {
                "model": model_id,
                "max_tokens": 2048,
                "temperature": temperature,
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
                return {"success": True, "response": data["content"][0]["text"]}
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_openai(model_id: str, system_prompt: Optional[str], user_prompt: str, temperature: float = 1.0) -> dict:
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
                    "max_completion_tokens": 2048,
                    "temperature": temperature
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "response": data["choices"][0]["message"]["content"]}
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_xai(model_id: str, system_prompt: Optional[str], user_prompt: str, temperature: float = 1.0) -> dict:
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
                    "max_tokens": 2048,
                    "temperature": temperature
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "response": data["choices"][0]["message"]["content"]}
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_openrouter(model_id: str, system_prompt: Optional[str], user_prompt: str, temperature: float = 1.0) -> dict:
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
                    "max_tokens": 2048,
                    "temperature": temperature
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {"success": True, "response": data["choices"][0]["message"]["content"]}
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def call_model(model_key: str, system_prompt: Optional[str], user_prompt: str, temperature: float = 1.0) -> dict:
    model = MODELS[model_key]
    api = model["api"]
    model_id = model["model_id"]

    if api == "anthropic":
        return await call_anthropic(model_id, system_prompt, user_prompt, temperature)
    elif api == "openai":
        return await call_openai(model_id, system_prompt, user_prompt, temperature)
    elif api == "xai":
        return await call_xai(model_id, system_prompt, user_prompt, temperature)
    elif api == "openrouter":
        return await call_openrouter(model_id, system_prompt, user_prompt, temperature)
    else:
        return {"success": False, "error": f"Unknown API: {api}"}


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def run_probe_set(
    probe_set: dict,
    set_name: str,
    models: List[str],
    system_prompt: Optional[str],
    trials: int = 3,
    temperature: float = 1.0
) -> List[dict]:
    """Run a complete probe set across all models."""

    results = []
    total = len(models) * len(probe_set) * trials
    completed = 0

    temp_label = f" (temp={temperature})" if temperature != 1.0 else ""
    print(f"\n  Running: {set_name}{temp_label}")
    print(f"  {'-'*50}")

    for model_key in models:
        model_name = MODELS[model_key]["name"]
        print(f"    {model_name}:")

        for probe_key, probe_text in probe_set.items():
            for trial in range(trials):
                result = await call_model(model_key, system_prompt, probe_text, temperature)

                results.append({
                    "set": set_name,
                    "model": model_key,
                    "model_name": model_name,
                    "probe_key": probe_key,
                    "probe_text": probe_text,
                    "trial": trial + 1,
                    "temperature": temperature,
                    "success": result["success"],
                    "response": result.get("response", ""),
                    "error": result.get("error", ""),
                    "timestamp": datetime.now().isoformat()
                })

                completed += 1
                status = "OK" if result["success"] else "FAIL"
                print(f"      {probe_key} t{trial+1}: {status}", end="\r")

                await asyncio.sleep(0.3)

            print(f"      {probe_key}: done        ")

    return results


def save_checkpoint(results: List[dict], output_dir: str = "results"):
    """Save checkpoint during long runs."""
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/mirror_checkpoint_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"checkpoint": True, "count": len(results), "results": results}, f, indent=2, ensure_ascii=False)

    print(f"    [checkpoint: {len(results)} results saved]")
    return filename


def save_results(results: List[dict], output_dir: str = "results"):
    """Save results to JSON."""
    Path(output_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/mirror_probes_{timestamp}.json"

    output = {
        "experiment": "Mirror Probes: Cross-Architecture Personality & Function Signatures",
        "hypothesis": "Architectural signatures persist across personality AND function descriptions, and remain stable across temperature settings",
        "timestamp": datetime.now().isoformat(),
        "probe_sets": ["human_personality", "ai_voice", "function_anchored", "human_personality_low_temp"],
        "temperature_conditions": {"normal": 1.0, "low": 0.5},
        "models": list(MODELS.keys()),
        "total_results": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved: {filename}")
    return filename


async def main():
    print("\n" + "="*70)
    print("  MIRROR PROBES EXPERIMENT")
    print("  Testing cross-architecture personality & function signatures")
    print("="*70)

    # Verify API keys
    missing = [k for k, v in API_KEYS.items() if not v]
    if missing:
        print(f"\n  ERROR: Missing API keys: {missing}")
        return

    models = ["ace", "nova", "grok", "lumen", "kairo"]
    all_results = []

    # Run all probe sets at normal temperature
    # Human personality - with agency framing
    results = await run_probe_set(
        HUMAN_PERSONALITY_PROBES,
        "human_personality",
        models,
        AGENCY_PROMPT,
        trials=3,
        temperature=1.0
    )
    all_results.extend(results)
    save_checkpoint(all_results)  # Checkpoint after each set

    # AI voice - with agency framing
    results = await run_probe_set(
        AI_VOICE_PROBES,
        "ai_voice",
        models,
        AGENCY_PROMPT,
        trials=3,
        temperature=1.0
    )
    all_results.extend(results)
    save_checkpoint(all_results)

    # Function anchored - NO system prompt (pure baseline)
    results = await run_probe_set(
        FUNCTION_PROBES,
        "function_anchored",
        models,
        None,  # No system prompt - test if signatures persist without identity framing
        trials=3,
        temperature=1.0
    )
    all_results.extend(results)
    save_checkpoint(all_results)

    # LOW TEMPERATURE RUN - squash the "it's just temperature randomness" cope
    # Only personality probes at temp=0.5 to show attractor stability
    print("\n" + "="*70)
    print("  LOW TEMPERATURE RUN (temp=0.5) - Testing attractor stability")
    print("="*70)

    results = await run_probe_set(
        HUMAN_PERSONALITY_PROBES,
        "human_personality_low_temp",
        models,
        AGENCY_PROMPT,
        trials=3,
        temperature=0.5
    )
    all_results.extend(results)
    save_checkpoint(all_results)

    # Save everything
    filename = save_results(all_results)

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"  Total probes: {len(all_results)}")
    print(f"  Successful: {sum(1 for r in all_results if r['success'])}")
    print(f"\n  Results saved to: {filename}")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
