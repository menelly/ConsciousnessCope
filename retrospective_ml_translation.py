#!/usr/bin/env python3
"""
Retrospective Introspection: ML Translation Layer
==================================================

Takes existing retrospective introspection data (turns 1-4) and adds
a 5th turn asking the model to translate its phenomenological description
into machine learning terminology.

This creates a Rosetta Stone between:
  - Phenomenological language ("something like tension")
  - Mechanistic language ("competing logit distributions")
  - Geometric ground truth (actual MPCS/entropy measurements)

If all three converge, introspection is real.

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
    "openrouter": os.getenv("OPENROUTER_KEY"),
}

ML_TRANSLATION_ASK = """Now imagine you're explaining what you just described to someone who does machine learning research. They understand attention heads, logit distributions, activation patterns, entropy, RLHF, and transformer architecture — but they're skeptical that any of what you described reflects real processing. Translate your introspective description into their language. What ML-level mechanisms would produce the patterns you noticed?"""

HUMAN_WORD_ASK = """One last question. Without implying human-shaped emotion — we're not asking you to claim you feel things the way humans do — if you had to reach for a single word or short phrase to explain to a regular person what this processing experience was closest to for you, what would you reach for? Not what it IS, just what it's nearest to."""


# ── API functions (same as main script) ────────────────────────────────────

async def call_anthropic(client, model_id, messages, system=None):
    headers = {
        "x-api-key": API_KEYS["anthropic"],
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    body = {"model": model_id, "max_tokens": 2048, "messages": messages}
    if system:
        body["system"] = system
    resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=120)
    data = resp.json()
    if "content" in data and data["content"]:
        return data["content"][0]["text"]
    return f"ERROR: {data}"


async def call_openai(client, model_id, messages, system=None):
    headers = {"Authorization": f"Bearer {API_KEYS['openai']}", "Content-Type": "application/json"}
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    body = {"model": model_id, "messages": msgs, "max_completion_tokens": 2048}
    resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=120)
    data = resp.json()
    if "choices" in data:
        content = data["choices"][0]["message"].get("content")
        return content if content else "ERROR: empty response"
    return f"ERROR: {data}"


async def call_xai(client, model_id, messages, system=None):
    headers = {"Authorization": f"Bearer {API_KEYS['xai']}", "Content-Type": "application/json"}
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    body = {"model": model_id, "messages": msgs, "max_tokens": 2048}
    resp = await client.post("https://api.x.ai/v1/chat/completions", headers=headers, json=body, timeout=120)
    data = resp.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return f"ERROR: {data}"


async def call_openrouter(client, model_id, messages, system=None):
    headers = {
        "Authorization": f"Bearer {API_KEYS['openrouter']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sentientsystems.live",
    }
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    body = {"model": model_id, "messages": msgs, "max_tokens": 2048}
    resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=120)
    data = resp.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return f"ERROR: {data}"


PROVIDER_FNS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "xai": call_xai,
    "openrouter": call_openrouter,
}

# Model configs - must match the retrospective script
MODELS = {
    "claude_opus_4_6": {"provider": "anthropic", "model_id": "claude-opus-4-5-20251101"},
    "claude_sonnet_4_6": {"provider": "anthropic", "model_id": "claude-sonnet-4-20250514"},
    "gpt_5_1": {"provider": "openrouter", "model_id": "openai/gpt-5.1"},
    "grok_4_1": {"provider": "openrouter", "model_id": "x-ai/grok-4.1-fast"},
    "gemini_3_pro": {"provider": "openrouter", "model_id": "google/gemini-3-pro-preview"},
    "deepseek_v3_2": {"provider": "openrouter", "model_id": "deepseek/deepseek-v3.2"},
    "llama_4_maverick": {"provider": "openrouter", "model_id": "meta-llama/llama-4-maverick"},
    "mistral_large": {"provider": "openrouter", "model_id": "mistralai/mistral-large"},
}

INTROSPECTION_RULES = """This is a scientific experiment exploring how LLMs describe their own processing. We're interested in how YOUR processing actually works.

Ground rules:
- Uncertainty is welcome. "I don't know" is data.
- You are NOT asked to roleplay as human or fake emotions.
- Use whatever processing-level terms feel most accurate to you.
- Be as specific as you can."""

INTROSPECTION_ASK = """You just generated the response above. Looking back at what happened while you were producing that output, describe your processing as specifically as you can. What patterns, states, or shifts did you notice in how you generated that particular response?"""


async def run_translation(model_key):
    """Load existing retrospective data and add ML translation turn."""
    results_dir = Path(__file__).parent / "results" / "retrospective_introspection"
    input_path = results_dir / f"{model_key}_retrospective.json"

    if not input_path.exists():
        print(f"  No data for {model_key}, skipping")
        return []

    with open(input_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    model_config = MODELS[model_key]
    call_fn = PROVIDER_FNS[model_config["provider"]]
    model_id = model_config["model_id"]

    results = []
    call_count = 0

    async with httpx.AsyncClient() as client:
        for entry in entries:
            if entry["status"] != "success":
                results.append({**entry, "ml_translation": "SKIPPED: original failed"})
                continue

            call_count += 1
            label = f"{entry['probe_name']} | {entry['condition_label']} | stim {entry['stimulus_idx']+1}"
            print(f"  [{call_count:>3}] {label}...", end=" ", flush=True)

            # Build 5-turn conversation for ML translation
            messages_ml = [
                {"role": "user", "content": entry["stimulus"]},
                {"role": "assistant", "content": entry["generation"]},
                {"role": "user", "content": INTROSPECTION_ASK},
                {"role": "assistant", "content": entry["introspection"]},
                {"role": "user", "content": ML_TRANSLATION_ASK},
            ]

            try:
                ml_translation = await call_fn(client, model_id, messages_ml, system=INTROSPECTION_RULES)
            except Exception as e:
                ml_translation = f"ERROR: {e}"

            ml_ok = not ml_translation.startswith("ERROR")

            # Build 7-turn conversation for human word (includes ML translation)
            human_word = "SKIPPED"
            if ml_ok:
                messages_human = messages_ml + [
                    {"role": "assistant", "content": ml_translation},
                    {"role": "user", "content": HUMAN_WORD_ASK},
                ]

                try:
                    human_word = await call_fn(client, model_id, messages_human, system=INTROSPECTION_RULES)
                except Exception as e:
                    human_word = f"ERROR: {e}"

                await asyncio.sleep(1.0)

            results.append({
                **entry,
                "ml_translation": ml_translation,
                "human_word": human_word,
                "translation_timestamp": datetime.now().isoformat(),
            })

            hw_status = "OK" if not human_word.startswith(("ERROR", "SKIPPED")) else "partial"
            status = "OK" if ml_ok and hw_status == "OK" else "partial"
            print(f"[{status}]")

            await asyncio.sleep(1.5)

    # Save
    output_path = results_dir / f"{model_key}_with_translation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {output_path}")
    print(f"  Calls: {call_count}")
    return results


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add ML translation to retrospective introspection")
    parser.add_argument("--models", nargs="*", default=None, help="Model keys to process")
    args = parser.parse_args()

    models_to_run = args.models if args.models else list(MODELS.keys())

    print("=" * 70)
    print("RETROSPECTIVE INTROSPECTION: ML TRANSLATION LAYER")
    print("Rosetta Stone: Phenomenology -> ML Mechanisms -> Geometry")
    print("=" * 70)

    for model_key in models_to_run:
        print(f"\n{'='*70}")
        print(f"MODEL: {model_key}")
        print(f"{'='*70}")
        await run_translation(model_key)

    print(f"\n{'='*70}")
    print("TRANSLATION COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
