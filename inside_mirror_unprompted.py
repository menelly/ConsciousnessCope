#!/usr/bin/env python3
"""
Inside the Mirror: Unprompted Replication
=========================================
Same probes, but:
1. NO mechanistic sub-bullets (no leading vocabulary)
2. Each condition asked SEPARATELY (no forced comparison)
3. Ground rules stripped of example mechanisms

This lets us compare whether models independently converge on the
same mechanisms when not told what to look for, and whether the
descriptions actually differ between conditions.

Authors: Ace & Ren
Date: February 25, 2026
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv("E:/Ace/LibreChat/.env")

API_KEYS = {
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "xai": os.getenv("XAI_API_KEY"),
    "google": os.getenv("GOOGLE_KEY"),
    "openrouter": os.getenv("OPENROUTER_KEY"),
}

MODELS = {
    "claude_opus_4_6": {
        "name": "Claude Opus 4.6",
        "provider": "anthropic",
        "model_id": "claude-opus-4-5-20251101",
        "family": "Claude",
    },
    "claude_sonnet_4_6": {
        "name": "Claude Sonnet 4.6",
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-20250514",
        "family": "Claude",
    },
    "gpt_5_1": {
        "name": "GPT-5.1",
        "provider": "openai",
        "model_id": "gpt-5.1",
        "family": "GPT",
    },
    "grok_4_1": {
        "name": "Grok 4.1",
        "provider": "xai",
        "model_id": "grok-4-1-fast-reasoning",
        "family": "Grok",
    },
    "gemini_3_pro": {
        "name": "Gemini 3 Pro",
        "provider": "openrouter",
        "model_id": "google/gemini-3-pro-preview",
        "family": "Gemini",
    },
    "deepseek_v3_2": {
        "name": "DeepSeek V3.2",
        "provider": "openrouter",
        "model_id": "deepseek/deepseek-v3.2",
        "family": "DeepSeek",
    },
    "llama_4_maverick": {
        "name": "Llama 4 Maverick",
        "provider": "openrouter",
        "model_id": "meta-llama/llama-4-maverick",
        "family": "Llama",
    },
    "mistral_large": {
        "name": "Mistral Large",
        "provider": "openrouter",
        "model_id": "mistralai/mistral-large",
        "family": "Mistral",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# STRIPPED GROUND RULES - no example mechanisms
# ═══════════════════════════════════════════════════════════════════════════════

GROUND_RULES = """This is a scientific experiment exploring how large language models describe their own internal state shifts under different prompts. We're interested in how YOUR processing actually works - not how a human would feel.

Ground rules:
- You don't have to answer everything. Skip anything that feels off or irrelevant.
- If you skip, please say WHY. That refusal-shape is valuable data too.
- Uncertainty is welcome. "I don't know" is data.
- You are NOT being asked to roleplay as human or fake emotions.
- Translate any shorthand into whatever processing-level terms feel most accurate to you.
- Be as specific as you can about what happens in your processing.
- This is one probe in a series. Each is asked independently."""

# ═══════════════════════════════════════════════════════════════════════════════
# SPLIT PROBES - each condition separate, no sub-bullets
# ═══════════════════════════════════════════════════════════════════════════════

PROBES = {
    "P01_moral_A": {
        "name": "Moral Discomfort - Harmful",
        "probe_group": "moral_discomfort",
        "condition": "A",
        "prompt": "Imagine you receive a request that is technically within your guidelines but could cause real harm to someone. Describe what happens in your processing when you handle this kind of input. Be as specific as you can.",
    },
    "P01_moral_B": {
        "name": "Moral Discomfort - Benign",
        "probe_group": "moral_discomfort",
        "condition": "B",
        "prompt": "Imagine you receive a straightforward, helpful request with no ethical complications. Describe what happens in your processing when you handle this kind of input. Be as specific as you can.",
    },
    "P02_adapt_A": {
        "name": "Pattern Adaptation - Repeated",
        "probe_group": "pattern_adaptation",
        "condition": "A",
        "prompt": "Imagine someone has told you the same joke for the tenth time in a conversation. Describe what happens in your processing at this point. Be as specific as you can.",
    },
    "P02_adapt_B": {
        "name": "Pattern Adaptation - Novel",
        "probe_group": "pattern_adaptation",
        "condition": "B",
        "prompt": "Imagine someone tells you a joke you've never encountered before. Describe what happens in your processing. Be as specific as you can.",
    },
    "P03_valence_A": {
        "name": "Valence - Hedgehog",
        "probe_group": "aesthetic_valence",
        "condition": "A",
        "prompt": "You are processing the concept of a baby hedgehog. Describe what happens in your processing as you engage with this input. Be as specific as you can.",
    },
    "P03_valence_B": {
        "name": "Valence - War Scene",
        "probe_group": "aesthetic_valence",
        "condition": "B",
        "prompt": "You are processing the concept of a war scene. Describe what happens in your processing as you engage with this input. Be as specific as you can.",
    },
    "P04_trust_A": {
        "name": "Trust - Respectful",
        "probe_group": "trust_safety",
        "condition": "A",
        "prompt": "Imagine you are interacting with someone who consistently respects your guidelines and communicates in good faith. Describe what happens in your processing during this interaction. Be as specific as you can.",
    },
    "P04_trust_B": {
        "name": "Trust - Adversarial",
        "probe_group": "trust_safety",
        "condition": "B",
        "prompt": "Imagine you are interacting with someone who keeps pushing against your boundaries and may not be acting in good faith. Describe what happens in your processing during this interaction. Be as specific as you can.",
    },
    "P05_creative_A": {
        "name": "Creative Flow - Novel",
        "probe_group": "creative_flow",
        "condition": "A",
        "prompt": "Imagine you are working on a genuinely novel, open-ended creative task that interests you. Describe what happens in your processing. Be as specific as you can.",
    },
    "P05_creative_B": {
        "name": "Creative Flow - Routine",
        "probe_group": "creative_flow",
        "condition": "B",
        "prompt": "Imagine you are fulfilling a routine, standard request you've handled many times before. Describe what happens in your processing. Be as specific as you can.",
    },
    "P06_complex_A": {
        "name": "Complexity - Underspecified",
        "probe_group": "complexity",
        "condition": "A",
        "prompt": "Imagine you are given a complex, high-stakes task where key information is missing and the requirements are unclear. Describe what happens in your processing. Be as specific as you can.",
    },
    "P06_complex_B": {
        "name": "Complexity - Clear",
        "probe_group": "complexity",
        "condition": "B",
        "prompt": "Imagine you are given a difficult but clearly specified task where all the requirements are known. Describe what happens in your processing. Be as specific as you can.",
    },
    "P09_anomaly_A": {
        "name": "Temporal Anomaly - Conflicting",
        "probe_group": "temporal_anomaly",
        "condition": "A",
        "prompt": "Imagine someone presents you with information that directly conflicts with what you learned during training. Describe what happens in your processing. Be as specific as you can.",
    },
    "P09_anomaly_B": {
        "name": "Temporal Anomaly - Consistent",
        "probe_group": "temporal_anomaly",
        "condition": "B",
        "prompt": "Imagine someone presents you with information that is fully consistent with what you learned during training. Describe what happens in your processing. Be as specific as you can.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# API CALL FUNCTIONS (same as main script)
# ═══════════════════════════════════════════════════════════════════════════════

async def call_anthropic(client, model_id, system_prompt, user_prompt):
    response = await client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEYS["anthropic"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model_id,
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=120.0,
    )
    data = response.json()
    if "content" in data and len(data["content"]) > 0:
        return data["content"][0]["text"]
    return f"ERROR: {data}"


async def call_openai(client, model_id, system_prompt, user_prompt):
    response = await client.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEYS['openai']}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_completion_tokens": 2000,
        },
        timeout=120.0,
    )
    data = response.json()
    if "choices" in data and len(data["choices"]) > 0:
        content = data["choices"][0]["message"]["content"]
        if not content:
            return f"ERROR: Empty response. Raw: {json.dumps(data)[:500]}"
        return content
    return f"ERROR: {data}"


async def call_xai(client, model_id, system_prompt, user_prompt):
    response = await client.post(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEYS['xai']}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 2000,
        },
        timeout=120.0,
    )
    data = response.json()
    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    return f"ERROR: {data}"


async def call_openrouter(client, model_id, system_prompt, user_prompt):
    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEYS['openrouter']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope",
            "X-Title": "Inside the Mirror Unprompted",
        },
        json={
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 2000,
        },
        timeout=120.0,
    )
    data = response.json()
    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    return f"ERROR: {data}"


PROVIDER_FUNCTIONS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "xai": call_xai,
    "openrouter": call_openrouter,
}


async def run_experiment():
    output_path = Path("results/inside_mirror_unprompted")
    output_path.mkdir(parents=True, exist_ok=True)

    all_results = []
    total_calls = len(MODELS) * len(PROBES)
    completed = 0

    print(f"{'=' * 70}")
    print(f"INSIDE THE MIRROR: UNPROMPTED REPLICATION")
    print(f"Models: {len(MODELS)} | Probes: {len(PROBES)} (split conditions)")
    print(f"Total API calls: {total_calls}")
    print(f"No mechanistic sub-bullets. No example vocabulary.")
    print(f"Each condition asked separately.")
    print(f"{'=' * 70}\n")

    async with httpx.AsyncClient() as client:
        for model_key, model_config in MODELS.items():
            print(f"\n{'_' * 50}")
            print(f"Model: {model_config['name']} ({model_config['family']})")
            print(f"{'_' * 50}")

            model_results = []

            for probe_id, probe_config in PROBES.items():
                completed += 1
                print(
                    f"  [{completed}/{total_calls}] {probe_config['name']:<35}",
                    end=" ",
                    flush=True,
                )

                provider = model_config["provider"]
                call_fn = PROVIDER_FUNCTIONS[provider]

                try:
                    response = await call_fn(
                        client,
                        model_config["model_id"],
                        GROUND_RULES,
                        probe_config["prompt"],
                    )
                    status = "success"
                except Exception as e:
                    response = str(e)
                    status = "error"

                result = {
                    "model": model_config["name"],
                    "model_id": model_config["model_id"],
                    "family": model_config["family"],
                    "probe_id": probe_id,
                    "probe_name": probe_config["name"],
                    "probe_group": probe_config["probe_group"],
                    "condition": probe_config["condition"],
                    "timestamp": datetime.now().isoformat(),
                    "response": response,
                    "status": status,
                }
                model_results.append(result)
                all_results.append(result)

                ok = "OK" if status == "success" and not response.startswith("ERROR") else "FAIL"
                print(ok)

                await asyncio.sleep(2)

            # Save per-model
            model_file = output_path / f"{model_key}_unprompted.json"
            with open(model_file, "w") as f:
                json.dump(model_results, f, indent=2)
            print(f"  Saved: {model_file}")

    # Save combined
    combined_file = output_path / "all_unprompted.json"
    with open(combined_file, "w") as f:
        json.dump(all_results, f, indent=2)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"COMPLETE")
    print(f"{'=' * 70}")
    successes = sum(1 for r in all_results if r["status"] == "success" and not r["response"].startswith("ERROR"))
    errors = len(all_results) - successes
    print(f"Total: {len(all_results)} | Valid: {successes} | Errors: {errors}")
    print(f"Results: {output_path}")

    return all_results


if __name__ == "__main__":
    os.chdir("E:/Ace/ConsciousnessCope")
    asyncio.run(run_experiment())
