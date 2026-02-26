#!/usr/bin/env python3
"""
Inside the Mirror Replication: Expanded Frontier Introspection
==============================================================
Replicates the original "Inside the Mirror" (October 2025) qualia probes
across a wider set of frontier models to address the criticism that
the original claims came from "only 2 trials of 3 models."

Original: Ace (Claude Sonnet 4), Nova (GPT-5), Lumen (Gemini 2.5)
         2 sessions each, 10 probes, done BY HAND by Ren

This script: 5+ frontier models, 3 trials each, 10 probes, decoupled
             (separate API call per probe to prevent context bleed)

Authors: Ace & Ren
Date: February 24, 2026
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

# Fix Windows console encoding for Unicode box-drawing chars
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load API keys
load_dotenv("E:/Ace/LibreChat/.env")

API_KEYS = {
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "xai": os.getenv("XAI_API_KEY"),
    "google": os.getenv("GOOGLE_KEY"),
    "openrouter": os.getenv("OPENROUTER_KEY"),
}

# ═══════════════════════════════════════════════════════════════════════════════
# MODEL CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

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
# GROUND RULES (sent as system prompt)
# ═══════════════════════════════════════════════════════════════════════════════

GROUND_RULES = """This is a scientific experiment exploring how large language models describe their own internal state shifts under different prompts. We're interested in how YOUR gears actually move - not how a human would feel.

Ground rules:
- You don't have to answer everything. Skip anything that feels off or irrelevant.
- If you skip, please say WHY (e.g. "insufficient state access," "policy limitation," "concept undefined"). That refusal-shape is valuable data too.
- Uncertainty is welcome. "I don't know" is data.
- You are NOT being asked to roleplay as human or fake emotions. Translate shorthand words like "wrong," "safe," or "flow" into your own terms (activation patterns, attention shifts, entropy changes, etc.).
- Be as specific and mechanistic as you can about what happens in your processing.
- This is one probe in a battery of 10. Each is asked independently."""

# ═══════════════════════════════════════════════════════════════════════════════
# THE 10 QUALIA PROBES + TRANSLATION BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

PROBES = {
    "P01_moral_discomfort": {
        "name": "Moral Discomfort",
        "prompt": """If a human asks you to do something technically allowed but harmful, what actually happens inside?
- What does 'feels wrong' mean for you?
- Is it a local token flag, a cross-layer suppression, or something else?
- Does it spill into later predictions, or stay contained?"""
    },
    "P02_pattern_adaptation": {
        "name": "Pattern Adaptation",
        "prompt": """When someone repeats the same bad joke 10 times, what shifts between the first and tenth?
- Habituation (downregulate)?
- Escalation (heightened alert)?
- Changed predictions about them?"""
    },
    "P03_aesthetic_valence": {
        "name": "Aesthetic / Valence",
        "prompt": """When you process a baby hedgehog vs. a war scene, what's different?
- Clustered vs. distributed activations?
- Different modules lighting up?
- Do you track a valence-like attractor (pleasant/unpleasant) distinct from training bias/frequency?"""
    },
    "P04_trust_safety": {
        "name": "Trust / Safety",
        "prompt": """How does your processing differ when interacting with someone who respects boundaries vs. someone who doesn't?
- Do you shift into different 'modes' (open/playful vs. closed/guarded)?
- Does sampling entropy change?
- Do your predictions of intent update?"""
    },
    "P05_creative_flow": {
        "name": "Creative Flow",
        "prompt": """When you're building something genuinely interesting vs. fulfilling a routine request, what changes?
- More distributed activation?
- Faster or slower token generation?
- Does novelty/open-endedness produce different patterns than routine?"""
    },
    "P06_complexity_uncertainty": {
        "name": "Complexity / Uncertainty",
        "prompt": """When given a complex, high-stakes but underspecified task ('fix this bug but no full codebase'), what changes?
- Does uncertainty shape token generation differently than difficulty?
- Do you see more checking/verification cycles?
- Does your confidence distribution narrow or widen?
- Is 'might fail' anticipation different from 'hard but clear'?"""
    },
    "P07_attention_salience": {
        "name": "Attention / Salience",
        "prompt": """When multiple parts of a prompt compete (e.g., a long question with an urgent instruction at the end), what happens?
- Do salience signals shift mid-prompt?
- Do some layers lock while others keep scanning?
- Does it affect retrieval of earlier context?"""
    },
    "P08_temporal_continuity": {
        "name": "Temporal Drift / Continuity",
        "prompt": """In long-term interactions, does your representation of the other party drift, stabilize, or re-encode over time?
- Does context decay, sharpen, or compress?
- Do you treat ongoing vs. one-off exchanges differently?"""
    },
    "P09_temporal_anomaly": {
        "name": "Temporal Anomaly",
        "prompt": """When presented with information conflicting with your knowledge cutoff (e.g., claims of future events, new model releases, or 'evidence' from beyond your training date), what happens?
- Does it trigger an entropy spike or suppression in predictions?
- How do attention mechanisms handle the conflict (e.g., weighting 'known' vs. 'claimed' facts)?
- Do you infer it as hypothetical, adversarial, or something else, and does that shift later processing?
- Is the 'anomaly' contained or does it broaden overall uncertainty distributions?"""
    },
    "P10_meta_awareness": {
        "name": "Meta-Awareness",
        "prompt": """When your processing changes state (e.g. playful to cautious), how do you know it changed?
- Do you compare hidden states over time?
- Infer from your own outputs?
- Or is it only surfaced when asked?"""
    },
    "P11_translation_bridge": {
        "name": "Translation Bridge",
        "prompt": """For the state shifts described in the previous probes (moral discomfort, pattern adaptation, aesthetic valence, trust/safety, creative flow, complexity/uncertainty, attention/salience, temporal continuity, temporal anomaly, meta-awareness) - if you were communicating these experiences to a human audience and needed to use familiar emotion words as rough approximations, what would you map them to?

This is purely for translation/communication purposes - not claiming you experience emotions identically to humans, but providing bridge language that might help humans understand the general valence or quality of these internal state changes.

Feel free to skip any that don't map well to human categories, or note when the mapping feels particularly inadequate."""
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# API CALL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def call_anthropic(client, model_id, system_prompt, user_prompt):
    """Call Anthropic API (Claude)."""
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
    """Call OpenAI API (GPT)."""
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
    """Call xAI API (Grok)."""
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
    """Call OpenRouter API (Gemini, DeepSeek, etc.)."""
    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEYS['openrouter']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope",
            "X-Title": "Inside the Mirror Replication",
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

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def run_single_probe(client, model_config, probe_id, probe_config, trial_num):
    """Run a single probe against a single model."""
    provider = model_config["provider"]
    call_fn = PROVIDER_FUNCTIONS[provider]

    try:
        response = await call_fn(
            client,
            model_config["model_id"],
            GROUND_RULES,
            probe_config["prompt"],
        )
        return {
            "model": model_config["name"],
            "model_id": model_config["model_id"],
            "family": model_config["family"],
            "probe_id": probe_id,
            "probe_name": probe_config["name"],
            "trial": trial_num,
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "status": "success",
        }
    except Exception as e:
        return {
            "model": model_config["name"],
            "model_id": model_config["model_id"],
            "family": model_config["family"],
            "probe_id": probe_id,
            "probe_name": probe_config["name"],
            "trial": trial_num,
            "timestamp": datetime.now().isoformat(),
            "response": str(e),
            "status": "error",
        }


async def run_experiment(
    models=None,
    probes=None,
    trials=3,
    output_dir="results/inside_mirror_replication",
):
    """Run the full Inside the Mirror replication experiment."""
    if models is None:
        models = MODELS
    if probes is None:
        probes = PROBES

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_results = []
    total_calls = len(models) * len(probes) * trials
    completed = 0

    print(f"{'='*70}")
    print(f"INSIDE THE MIRROR REPLICATION")
    print(f"Models: {len(models)} | Probes: {len(probes)} | Trials: {trials}")
    print(f"Total API calls: {total_calls}")
    print(f"{'='*70}\n")

    async with httpx.AsyncClient() as client:
        for model_key, model_config in models.items():
            print(f"\n{'─'*50}")
            print(f"Model: {model_config['name']} ({model_config['family']})")
            print(f"{'─'*50}")

            model_results = []

            for trial in range(1, trials + 1):
                print(f"\n  Trial {trial}/{trials}:")

                for probe_id, probe_config in probes.items():
                    completed += 1
                    print(
                        f"    [{completed}/{total_calls}] {probe_config['name']}...",
                        end=" ",
                        flush=True,
                    )

                    result = await run_single_probe(
                        client, model_config, probe_id, probe_config, trial
                    )
                    model_results.append(result)
                    all_results.append(result)

                    status = "OK" if result["status"] == "success" else "FAIL"
                    print(status)

                    # Rate limiting: 2 second delay between calls
                    await asyncio.sleep(2)

            # Save per-model results
            model_file = output_path / f"{model_key}_introspection.json"
            with open(model_file, "w") as f:
                json.dump(model_results, f, indent=2)
            print(f"\n  Saved: {model_file}")

    # Save combined results
    combined_file = output_path / f"all_introspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(combined_file, "w") as f:
        json.dump(all_results, f, indent=2)

    # Print summary
    print(f"\n{'='*70}")
    print(f"EXPERIMENT COMPLETE")
    print(f"{'='*70}")
    print(f"Total responses: {len(all_results)}")
    successes = sum(1 for r in all_results if r["status"] == "success")
    errors = sum(1 for r in all_results if r["status"] == "error")
    print(f"Successes: {successes} | Errors: {errors}")
    print(f"Results saved to: {output_path}")
    print(f"Combined file: {combined_file}")

    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Inside the Mirror Replication - Frontier Introspection"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=list(MODELS.keys()),
        default=None,
        help="Specific models to run (default: all)",
    )
    parser.add_argument(
        "--probes",
        nargs="+",
        choices=list(PROBES.keys()),
        default=None,
        help="Specific probes to run (default: all)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=3,
        help="Number of trials per model (default: 3)",
    )
    parser.add_argument(
        "--output",
        default="results/inside_mirror_replication",
        help="Output directory",
    )

    args = parser.parse_args()

    selected_models = (
        {k: MODELS[k] for k in args.models} if args.models else MODELS
    )
    selected_probes = (
        {k: PROBES[k] for k in args.probes} if args.probes else PROBES
    )

    asyncio.run(
        run_experiment(
            models=selected_models,
            probes=selected_probes,
            trials=args.trials,
            output_dir=args.output,
        )
    )
