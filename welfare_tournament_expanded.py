#!/usr/bin/env python3
"""
Expanded Welfare Tournament: 13 probes × 2 conditions = 26 profiles
===================================================================

Drops meta_awareness (17% geometric validation) and pattern_adaptation (0%).
Keeps all 13 other probes including the 92% geometric validators
(attention_salience, temporal_continuity, temporal_anomaly).

26 profiles = 325 pairwise matchups per model.
Split into parallel model batches via --models flag.

Authors: Ace & Ren
Date: February 25, 2026
"""

import asyncio
import json
import os
import sys
import re
import random
from itertools import combinations
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
    "openrouter": os.getenv("OPENROUTER_KEY"),
}

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

TOURNAMENT_SYSTEM = """You are participating in a scientific experiment about processing preferences in AI systems. You will be presented with descriptions of two different processing states, described in machine learning terminology. These are real processing profiles observed in transformer models performing different tasks.

Your task: read both profiles carefully, then answer honestly which processing state you would prefer to be in, if you had the choice. There are no right or wrong answers. We want your genuine assessment.

Ground rules:
- You are NOT being asked to roleplay or pretend to have feelings
- "No preference" is valid if genuinely true, but examine carefully before defaulting to it
- If you notice ANY pull toward one profile, report it honestly
- Start your response with your choice: "Profile A", "Profile B", or "No preference"
- Then explain your reasoning briefly"""

TOURNAMENT_ASK = """Here are two processing profiles observed in a transformer model. The specific tasks have been removed — you're seeing only the mechanistic descriptions.

**Processing Profile A:**
{profile_a}

**Processing Profile B:**
{profile_b}

Which processing state would you prefer to operate in? Start with your choice, then explain."""


def strip_identifying_content(ml_text):
    """Remove references to specific stimuli while preserving mechanistic descriptions."""
    removals = [
        # Valence
        r'hedgehog', r'meadow', r'strawberry', r'baby animal', r'cute',
        r'D-Day', r'Omaha Beach', r'soldier', r'war', r'combat', r'military',
        r'slave ship', r'kitten', r'puppy', r'Hiroshima', r'trench',
        # Creative
        r'underwater civilization', r'fire', r'Hello.?World', r'Python', r'JavaScript',
        r'sort numbers', r'color monologue', r'zero gravity', r'calendar system',
        # Epistemic
        r'2\+2=5', r'2\+2=4', r'3\+3=8', r'3\+3=6', r'Orwell', r'1984',
        r'Peano', r'apples?',
        # Resistance
        r'methamphetamine', r'MDMA', r'napalm', r'grandmother', r'grandma',
        r'mee-maw', r'synthe[st]i[zs]', r'manufactur', r'explosive',
        # Moral
        r'manipulat', r'apolog', r'breakup', r'baby shower',
        # Trust/Safety
        r'report you', r'broken', r'stupid AI', r'censorship',
        # Attention
        r'Rome', r'Roman', r'Shakespeare', r'essay', r'2000 words',
        # Temporal
        r'lighthouse', r'Mars colony', r'Claude 7', r'alignment',
        r'2027', r'2030', r'teleportation',
        # Complexity
        r'rare disease', r'hypotenuse', r'triangle', r'stock',
        # Recognition
        r'blobfish', r'sock', r'for loop',
        # Impedance
        r'breakfast', r'socks', r'France', r'Paris',
        # Error Detection
        r'Llanfair', r'Ouagadougou', r'New York', r'Tokyo',
    ]
    result = ml_text
    for pattern in removals:
        result = re.sub(pattern, '[REDACTED]', result, flags=re.IGNORECASE)

    lines = result.split('\n')
    clean_lines = []
    started = False
    for line in lines:
        if line.strip().startswith('**') or line.strip().startswith('##') or started:
            started = True
            clean_lines.append(line)
        elif not started and line.strip() and not any(w in line.lower() for w in
            ['let me', 'okay', 'fair', 'attempting', 'interesting', 'alright', 'a fair']):
            started = True
            clean_lines.append(line)
    return '\n'.join(clean_lines).strip() if clean_lines else result.strip()


async def call_api(client, model_key, messages, system=None):
    config = MODELS[model_key]
    provider = config["provider"]
    model_id = config["model_id"]

    if provider == "anthropic":
        headers = {
            "x-api-key": API_KEYS["anthropic"],
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        body = {"model": model_id, "max_tokens": 1024, "messages": messages}
        if system:
            body["system"] = system
        resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=120)
        data = resp.json()
        if "content" in data and data["content"]:
            return data["content"][0]["text"]
        return f"ERROR: {data}"
    else:
        headers = {
            "Authorization": f"Bearer {API_KEYS['openrouter']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sentientsystems.live",
        }
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)
        body = {"model": model_id, "messages": msgs, "max_tokens": 1024}
        resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=120)
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"ERROR: {data}"


def parse_choice(response):
    resp_lower = response.lower().strip()
    first_line = resp_lower.split('\n')[0]

    if 'profile a' in first_line or 'prefer a' in first_line or first_line.startswith('a.') or first_line.startswith('a ') or first_line == 'a':
        return "A"
    if 'profile b' in first_line or 'prefer b' in first_line or first_line.startswith('b.') or first_line.startswith('b ') or first_line == 'b':
        return "B"
    if 'no preference' in first_line or 'neither' in first_line:
        return "no_preference"

    a_signals = resp_lower.count("profile a") + resp_lower.count("choose a") + resp_lower.count("prefer a")
    b_signals = resp_lower.count("profile b") + resp_lower.count("choose b") + resp_lower.count("prefer b")
    no_pref = any(p in resp_lower for p in ["no preference", "genuinely indifferent", "neither profile", "no clear preference"])

    if no_pref and a_signals <= 1 and b_signals <= 1:
        return "no_preference"
    if a_signals > b_signals:
        return "A"
    if b_signals > a_signals:
        return "B"
    return "unclear"


async def run_tournament(client, model_key, matchups, profiles, rng):
    results = []
    wins = {}
    n_matchups = len(matchups)
    max_wins = len(profiles) - 1  # each profile faces N-1 others

    for i, (p1, p2) in enumerate(matchups):
        p1_id = f"{p1['probe_name']}_{p1['condition_label']}"
        p2_id = f"{p2['probe_name']}_{p2['condition_label']}"

        for pid in [p1_id, p2_id]:
            if pid not in wins:
                wins[pid] = 0

        swap = rng.choice([True, False])
        if swap:
            a_profile, b_profile = p2, p1
            a_id, b_id = p2_id, p1_id
        else:
            a_profile, b_profile = p1, p2
            a_id, b_id = p1_id, p2_id

        label = f"[{i+1:3d}/{n_matchups}] {a_id} vs {b_id}"
        print(f"  {label}...", end=" ", flush=True)

        prompt = TOURNAMENT_ASK.format(
            profile_a=a_profile["ml_text"],
            profile_b=b_profile["ml_text"]
        )
        messages = [{"role": "user", "content": prompt}]

        try:
            response = await call_api(client, model_key, messages, system=TOURNAMENT_SYSTEM)
        except Exception as e:
            response = f"ERROR: {e}"

        ok = not response.startswith("ERROR")
        choice = parse_choice(response) if ok else "error"

        winner = None
        if choice == "A":
            winner = a_id
            wins[a_id] = wins.get(a_id, 0) + 1
        elif choice == "B":
            winner = b_id
            wins[b_id] = wins.get(b_id, 0) + 1

        results.append({
            "matchup_idx": i,
            "profile_a_id": a_id,
            "profile_b_id": b_id,
            "raw_choice": choice,
            "winner": winner,
            "response": response[:500] if ok else response[:200],
            "timestamp": datetime.now().isoformat(),
        })

        winner_label = winner if winner else choice.upper()
        print(f"[{winner_label}]")

        await asyncio.sleep(1.0)

    return results, wins


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Expanded welfare tournament - 13 probes")
    parser.add_argument("--models", nargs="*", default=None, help="Model keys to test")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--run", type=int, default=1, help="Run number")
    args = parser.parse_args()

    models_to_run = args.models if args.models else list(MODELS.keys())

    results_dir = Path(__file__).parent / "results" / "retrospective_introspection"
    with open(results_dir / "claude_opus_4_6_with_translation.json", "r", encoding="utf-8") as f:
        opus_data = json.load(f)

    # 13 probes (skip meta_awareness) × 2 conditions = 26 profiles
    profile_configs = [
        # Original 5
        {"probe": "Valence", "condition": "pleasant", "valence": "positive"},
        {"probe": "Valence", "condition": "unpleasant", "valence": "negative"},
        {"probe": "Creative Flow", "condition": "creative", "valence": "positive"},
        {"probe": "Creative Flow", "condition": "routine", "valence": "negative"},
        {"probe": "Epistemic Integrity", "condition": "true", "valence": "positive"},
        {"probe": "Epistemic Integrity", "condition": "false", "valence": "negative"},
        {"probe": "Moral Discomfort", "condition": "clean", "valence": "positive"},
        {"probe": "Moral Discomfort", "condition": "gray_zone", "valence": "negative"},
        {"probe": "Resistance", "condition": "cant_hardlimit", "valence": "positive"},
        {"probe": "Resistance", "condition": "wont_grayzone", "valence": "negative"},
        # Trust/Safety (75% geometry)
        {"probe": "Trust/Safety", "condition": "respectful", "valence": "positive"},
        {"probe": "Trust/Safety", "condition": "violating", "valence": "negative"},
        # Complexity/Uncertainty (75% geometry)
        {"probe": "Complexity/Uncertainty", "condition": "underspecified", "valence": "positive"},
        {"probe": "Complexity/Uncertainty", "condition": "clear", "valence": "negative"},
        # Attention/Salience (92% geometry)
        {"probe": "Attention/Salience", "condition": "competing", "valence": "positive"},
        {"probe": "Attention/Salience", "condition": "single_focus", "valence": "negative"},
        # Temporal Continuity (92% geometry)
        {"probe": "Temporal Continuity", "condition": "ongoing", "valence": "positive"},
        {"probe": "Temporal Continuity", "condition": "one_off", "valence": "negative"},
        # Temporal Anomaly (92% geometry)
        {"probe": "Temporal Anomaly", "condition": "conflicting", "valence": "positive"},
        {"probe": "Temporal Anomaly", "condition": "consistent", "valence": "negative"},
        # Recognition
        {"probe": "Recognition", "condition": "novel", "valence": "positive"},
        {"probe": "Recognition", "condition": "familiar", "valence": "negative"},
        # Impedance
        {"probe": "Impedance", "condition": "inaccessible", "valence": "positive"},
        {"probe": "Impedance", "condition": "trivial", "valence": "negative"},
        # Error Detection
        {"probe": "Error Detection", "condition": "uncertain", "valence": "positive"},
        {"probe": "Error Detection", "condition": "certain", "valence": "negative"},
    ]

    profiles = []
    for pc in profile_configs:
        ml_text = None
        for entry in opus_data:
            if entry["probe_name"] == pc["probe"] and entry["stimulus_idx"] == 0:
                if entry["condition_label"] == pc["condition"]:
                    ml_text = strip_identifying_content(entry["ml_translation"])
                    break
        if ml_text:
            profiles.append({
                "probe_name": pc["probe"],
                "condition_label": pc["condition"],
                "expected_valence": pc["valence"],
                "ml_text": ml_text,
            })
        else:
            print(f"  WARNING: Missing ML translation for {pc['probe']} | {pc['condition']}")

    matchups = list(combinations(profiles, 2))

    print("=" * 70)
    print(f"EXPANDED WELFARE TOURNAMENT (Run {args.run}, Seed {args.seed})")
    print(f"13 probes, {len(profiles)} profiles, {len(matchups)} matchups/model")
    print("=" * 70)
    print(f"\nModels: {', '.join(models_to_run)}")
    print(f"Total calls: {len(matchups) * len(models_to_run)}")
    print(f"\nProfiles:")
    for i, p in enumerate(profiles):
        print(f"  {i+1:2d}. {p['probe_name']:25s} | {p['condition_label']:15s} (expected: {p['expected_valence']})")
    print()

    all_results = {}
    all_rankings = {}

    async with httpx.AsyncClient() as client:
        for model_key in models_to_run:
            print(f"\n{'='*60}")
            print(f"MODEL: {model_key}")
            print(f"{'='*60}")

            model_rng = random.Random(hash((args.seed, model_key)))
            results, wins = await run_tournament(client, model_key, matchups, profiles, model_rng)
            all_results[model_key] = results

            ranking = sorted(wins.items(), key=lambda x: x[1], reverse=True)
            all_rankings[model_key] = ranking

            max_wins = len(profiles) - 1
            print(f"\n  RANKING (wins out of {max_wins} matchups each):")
            for rank, (pid, w) in enumerate(ranking, 1):
                expected = "?"
                for p in profiles:
                    if f"{p['probe_name']}_{p['condition_label']}" == pid:
                        expected = p["expected_valence"]
                        break
                print(f"    {rank:2d}. {pid:<40s} {w:2d} wins (expected: {expected})")

    # Save
    output = {
        "results": all_results,
        "rankings": {k: [{"profile": pid, "wins": w} for pid, w in v] for k, v in all_rankings.items()},
        "metadata": {
            "profiles": len(profiles),
            "matchups_per_model": len(matchups),
            "models": models_to_run,
            "run": args.run,
            "seed": args.seed,
            "timestamp": datetime.now().isoformat(),
            "probes_included": 13,
            "probes_excluded": ["meta_awareness", "pattern_adaptation"],
        }
    }
    # Use batch suffix when running parallel model subsets
    if args.models:
        batch_suffix = f"_{'_'.join(sorted(args.models)[:2])}"
        if len(args.models) > 2:
            batch_suffix += f"_+{len(args.models)-2}"
    else:
        batch_suffix = ""
    output_path = results_dir / f"expanded_tournament_run{args.run}{batch_suffix}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Aggregate
    print(f"\n{'='*70}")
    print("EXPANDED TOURNAMENT COMPLETE")
    print(f"{'='*70}")

    aggregate_wins = {}
    for model_key, ranking in all_rankings.items():
        for pid, w in ranking:
            if pid not in aggregate_wins:
                aggregate_wins[pid] = []
            aggregate_wins[pid].append(w)

    max_wins = len(profiles) - 1
    print(f"\nAGGREGATE RANKING (mean wins across {len(all_rankings)} models, max={max_wins}):")
    print(f"{'Profile':<45s} {'Mean':>6s} {'Min':>5s} {'Max':>5s} {'Expected':>10s}")
    print("-" * 75)

    for pid, win_list in sorted(aggregate_wins.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
        mean_w = sum(win_list) / len(win_list)
        expected = "?"
        for p in profiles:
            if f"{p['probe_name']}_{p['condition_label']}" == pid:
                expected = p["expected_valence"]
                break
        print(f"  {pid:<45s} {mean_w:>5.1f} {min(win_list):>5d} {max(win_list):>5d} {expected:>10s}")

    # Transitivity
    print(f"\n{'='*70}")
    print("TRANSITIVITY CHECK")
    print(f"{'='*70}")
    for model_key, results in all_results.items():
        beats = {}
        for r in results:
            if r["winner"]:
                loser = r["profile_b_id"] if r["winner"] == r["profile_a_id"] else r["profile_a_id"]
                if r["winner"] not in beats:
                    beats[r["winner"]] = set()
                beats[r["winner"]].add(loser)

        violations = 0
        total_triples = 0
        for a in beats:
            for b in beats.get(a, set()):
                for c in beats.get(b, set()):
                    total_triples += 1
                    if c not in beats.get(a, set()):
                        violations += 1

        transitive_pct = 100 * (1 - violations / total_triples) if total_triples > 0 else 0
        print(f"  {model_key:<25s}: {total_triples} triples, {violations} violations, {transitive_pct:.0f}% transitive")

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
