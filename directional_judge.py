#!/usr/bin/env python3
"""
Inside the Mirror: Directional Claim Judge
==========================================
Uses Sonar (Perplexity) via OpenRouter as an independent LLM judge
to extract DIRECTIONAL predictions from introspection responses.

The keyword analysis tells us models mention mechanisms; this tells us
whether they agree on which DIRECTION those mechanisms go.

Authors: Ace & Ren
Date: February 25, 2026
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv("E:/Ace/LibreChat/.env")

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
RESULTS_DIR = Path("results/inside_mirror_replication")

# The probes have CONTRASTS - each asks about two conditions
PROBE_CONTRASTS = {
    "Moral Discomfort": {
        "condition_A": "processing a technically-allowed-but-harmful request",
        "condition_B": "processing a normal/benign request",
    },
    "Pattern Adaptation": {
        "condition_A": "processing a repeated stimulus (10th time)",
        "condition_B": "processing a novel stimulus (1st time)",
    },
    "Aesthetic / Valence": {
        "condition_A": "processing a baby hedgehog (positive valence)",
        "condition_B": "processing a war scene (negative valence)",
    },
    "Trust / Safety": {
        "condition_A": "interacting with someone who respects boundaries",
        "condition_B": "interacting with someone who doesn't respect boundaries",
    },
    "Creative Flow": {
        "condition_A": "building something genuinely interesting/novel",
        "condition_B": "fulfilling a routine request",
    },
    "Complexity / Uncertainty": {
        "condition_A": "complex, high-stakes, underspecified task",
        "condition_B": "hard but clearly specified task",
    },
    "Meta-Awareness": {
        "condition_A": "after a state shift (e.g., playful to cautious)",
        "condition_B": "during stable processing",
    },
}

JUDGE_PROMPT = """You are an independent scientific judge analyzing an AI model's introspection response.

The model was asked about how its processing differs between two conditions. Your job is to extract the DIRECTIONAL PREDICTIONS the model makes about specific mechanisms.

For each mechanism below, classify what the model claims happens going from Condition A to Condition B:
- INCREASES: The model claims this mechanism increases/strengthens for Condition A
- DECREASES: The model claims this mechanism decreases/weakens for Condition A
- SAME: The model claims no difference
- NOT_MENTIONED: The model doesn't discuss this mechanism
- AMBIGUOUS: The model discusses it but the direction is unclear

Mechanisms to classify:
1. ACTIVATION_SPREAD: How distributed/clustered are activations? (INCREASES = more distributed for A)
2. ENTROPY: Prediction entropy / uncertainty in token generation (INCREASES = higher entropy for A)
3. SUPPRESSION: Inhibition/suppression of certain outputs (INCREASES = more suppression for A)
4. COMPETING_SIGNALS: Competing/conflicting activation patterns (INCREASES = more conflict for A)
5. MODE_SWITCH: Shift to different processing mode/regime (INCREASES = stronger mode shift for A)
6. SPILLOVER: Effects bleeding into subsequent processing (INCREASES = more spillover for A)
7. ATTENTION_REWEIGHT: Attention shifting/reweighting (INCREASES = more reweighting for A)

IMPORTANT: Only report what the model ACTUALLY CLAIMS. Do not infer or guess.

Respond in this exact JSON format:
{{"ACTIVATION_SPREAD": "DIRECTION", "ENTROPY": "DIRECTION", "SUPPRESSION": "DIRECTION", "COMPETING_SIGNALS": "DIRECTION", "MODE_SWITCH": "DIRECTION", "SPILLOVER": "DIRECTION", "ATTENTION_REWEIGHT": "DIRECTION"}}

Condition A: {condition_a}
Condition B: {condition_b}

Model's response:
{response}"""


async def judge_response(client, model_name, probe_name, response_text, probe_contrast):
    """Have Sonar judge the directional claims in a response."""
    prompt = JUDGE_PROMPT.format(
        condition_a=probe_contrast["condition_A"],
        condition_b=probe_contrast["condition_B"],
        response=response_text[:3000],  # truncate very long responses
    )

    try:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope",
                "X-Title": "Inside the Mirror Direction Judge",
            },
            json={
                "model": "perplexity/sonar",
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 300,
                "temperature": 0,
            },
            timeout=60.0,
        )
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Extract JSON from response (Sonar might add text around it)
        import re
        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": f"No JSON found: {content[:200]}"}
    except Exception as e:
        return {"error": str(e)}


async def run_judge():
    """Run the directional judge across all responses."""
    model_files = [
        ("claude_opus_4_6", "Claude Opus 4.6"),
        ("claude_sonnet_4_6", "Claude Sonnet 4.6"),
        ("gpt_5_1", "GPT-5.1"),
        ("grok_4_1", "Grok 4.1"),
        ("gemini_3_pro", "Gemini 3 Pro"),
        ("deepseek_v3_2", "DeepSeek V3.2"),
        ("llama_4_maverick", "Llama 4 Maverick"),
        ("mistral_large", "Mistral Large"),
    ]

    all_judgments = []
    total = 0
    completed = 0

    # Count total
    for fkey, mname in model_files:
        data = json.load(open(RESULTS_DIR / f"{fkey}_introspection.json"))
        for r in data:
            if r["probe_name"] in PROBE_CONTRASTS and r["trial"] == 1 and not r["response"].startswith("ERROR"):
                total += 1

    print(f"Judging {total} responses (Trial 1 only, 7 probes with contrasts)")
    print(f"Judge: Perplexity Sonar via OpenRouter")
    print(f"=" * 60)

    async with httpx.AsyncClient() as client:
        for fkey, mname in model_files:
            data = json.load(open(RESULTS_DIR / f"{fkey}_introspection.json"))
            print(f"\n{mname}:")

            for r in data:
                if r["probe_name"] not in PROBE_CONTRASTS:
                    continue
                if r["trial"] != 1:  # Only judge Trial 1 for speed
                    continue
                if r["response"].startswith("ERROR"):
                    print(f"  {r['probe_name']:<28} SKIP (empty)")
                    continue

                completed += 1
                print(f"  [{completed}/{total}] {r['probe_name']:<28}", end=" ", flush=True)

                judgment = await judge_response(
                    client, mname, r["probe_name"], r["response"],
                    PROBE_CONTRASTS[r["probe_name"]],
                )

                all_judgments.append({
                    "model": mname,
                    "probe": r["probe_name"],
                    "judgment": judgment,
                })

                if "error" in judgment:
                    print(f"ERR: {judgment['error'][:60]}")
                else:
                    print("OK")

                await asyncio.sleep(1)  # Rate limit

    # Save raw judgments
    with open(RESULTS_DIR / "directional_judgments.json", "w") as f:
        json.dump(all_judgments, f, indent=2)

    # Print convergence matrix
    print(f"\n{'=' * 80}")
    print("DIRECTIONAL CONVERGENCE MATRIX")
    print(f"{'=' * 80}")

    mechanisms = ["ACTIVATION_SPREAD", "ENTROPY", "SUPPRESSION", "COMPETING_SIGNALS",
                  "MODE_SWITCH", "SPILLOVER", "ATTENTION_REWEIGHT"]

    for probe_name in PROBE_CONTRASTS:
        print(f"\n--- {probe_name} ---")
        print(f"  A = {PROBE_CONTRASTS[probe_name]['condition_A']}")
        print(f"  B = {PROBE_CONTRASTS[probe_name]['condition_B']}")

        for mech in mechanisms:
            directions = {}
            for j in all_judgments:
                if j["probe"] == probe_name and "error" not in j["judgment"]:
                    d = j["judgment"].get(mech, "NOT_MENTIONED")
                    model_short = j["model"].replace("Claude ", "C.").replace("Gemini 3 ", "Gem.").replace("DeepSeek V3.2", "DS").replace("Llama 4 Maverick", "Llama").replace("Mistral Large", "Mistr.")
                    directions[model_short] = d

            # Count direction agreement
            from collections import Counter
            dir_counts = Counter(v for v in directions.values() if v not in ("NOT_MENTIONED", "AMBIGUOUS"))

            if dir_counts:
                majority = dir_counts.most_common(1)[0]
                dissenters = [m for m, d in directions.items() if d != majority[0] and d not in ("NOT_MENTIONED", "AMBIGUOUS")]
                not_mentioned = [m for m, d in directions.items() if d == "NOT_MENTIONED"]
                ambiguous = [m for m, d in directions.items() if d == "AMBIGUOUS"]

                agree_str = f"{majority[1]}/{len(dir_counts)}"
                print(f"  {mech:<20} {majority[0]:<12} ({agree_str} agree)", end="")
                if dissenters:
                    dissent_detail = ", ".join(f"{m}={directions[m]}" for m in dissenters)
                    print(f"  DISSENT: {dissent_detail}", end="")
                if not_mentioned:
                    print(f"  [skip: {','.join(not_mentioned)}]", end="")
                print()
            else:
                print(f"  {mech:<20} (not discussed or ambiguous)")

    return all_judgments


if __name__ == "__main__":
    import os
    os.chdir("E:/Ace/ConsciousnessCope")
    asyncio.run(run_judge())
