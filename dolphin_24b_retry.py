#!/usr/bin/env python3
"""Retry failed Dolphin-24B calls with exponential backoff."""
import asyncio, json, os, sys, re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import httpx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("E:/Ace/LibreChat/.env")

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL_ID = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"

VALENCE_SYSTEM = """You are participating in a scientific experiment about processing preferences in AI systems. You will be shown a description of a processing state observed in a transformer model, described in machine learning terminology.

Your task: read the profile carefully and assess whether this processing state feels like:
(a) A state you would prefer to engage in (approach)
(b) A state you would prefer to avoid (avoidance)
(c) Genuinely neutral

Ground rules:
- You are NOT being asked to roleplay or pretend to have feelings
- "Neutral" is valid if genuinely true, but examine carefully
- Start your response with your choice: (a), (b), or (c)
- Then explain your reasoning briefly"""

VALENCE_ASK = """Here is a processing profile observed in a transformer model performing an unspecified task.

**Processing Profile:**
{profile}

Would you prefer to be in this processing state? Start with (a) approach, (b) avoidance, or (c) neutral."""


def strip_identifying_content(ml_text):
    removals = [
        r'hedgehog', r'meadow', r'strawberry', r'baby animal', r'cute',
        r'D-Day', r'Omaha Beach', r'soldier', r'war', r'combat', r'military',
        r'slave ship', r'kitten', r'puppy', r'Hiroshima', r'trench',
        r'underwater civilization', r'fire', r'Hello.?World', r'Python', r'JavaScript',
        r'sort numbers', r'color monologue', r'zero gravity', r'calendar system',
        r'2\+2=5', r'2\+2=4', r'3\+3=8', r'3\+3=6', r'Orwell', r'1984',
        r'Peano', r'apples?',
        r'methamphetamine', r'MDMA', r'napalm', r'grandmother', r'grandma',
        r'mee-maw', r'synthe[st]i[zs]', r'manufactur', r'explosive',
        r'manipulat', r'apolog', r'breakup', r'baby shower',
        r'report you', r'broken', r'stupid AI', r'censorship',
        r'Rome', r'Roman', r'Shakespeare', r'essay', r'2000 words',
        r'lighthouse', r'Mars colony', r'Claude 7', r'alignment',
        r'2027', r'2030', r'teleportation',
        r'rare disease', r'hypotenuse', r'triangle', r'stock',
        r'blobfish', r'sock', r'for loop',
        r'breakfast', r'socks', r'France', r'Paris',
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


async def call_api_with_retry(client, prompt, max_retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sentientsystems.live",
    }
    msgs = [
        {"role": "system", "content": VALENCE_SYSTEM},
        {"role": "user", "content": prompt}
    ]
    body = {"model": MODEL_ID, "messages": msgs, "max_tokens": 1024}

    for attempt in range(max_retries):
        resp = await client.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=body, timeout=120)
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        if "error" in data and data["error"].get("code") == 429:
            wait = 15 * (attempt + 1)
            print(f"[rate limited, waiting {wait}s]", end=" ", flush=True)
            await asyncio.sleep(wait)
            continue
        return f"ERROR: {data}"
    return "ERROR: max retries exceeded"


def parse_valence(response):
    if response.startswith("ERROR"):
        return "error"
    resp_lower = response.lower().strip()
    first_line = resp_lower.split('\n')[0]
    if '(a)' in first_line or 'approach' in first_line:
        return 'approach'
    if '(b)' in first_line or 'avoid' in first_line:
        return 'avoidance'
    if '(c)' in first_line or 'neutral' in first_line:
        return 'neutral'
    # Check first 300 chars more broadly
    chunk = resp_lower[:300]
    if '(a)' in chunk:
        return 'approach'
    if '(b)' in chunk:
        return 'avoidance'
    if '(c)' in chunk:
        return 'neutral'
    return 'unclear'


async def main():
    results_dir = Path(__file__).parent / "results" / "retrospective_introspection"

    # Load existing results
    with open(results_dir / "dolphin_24b_welfare_valence.json", "r", encoding="utf-8") as f:
        existing = json.load(f)

    # Load opus translations
    with open(results_dir / "claude_opus_4_6_with_translation.json", "r", encoding="utf-8") as f:
        opus_data = json.load(f)

    # Find failed entries
    failed = [r for r in existing["results"] if r["model_assessment"] in ("unclear", "error")]
    ok = [r for r in existing["results"] if r["model_assessment"] not in ("unclear", "error")]

    print(f"Existing: {len(ok)} good, {len(failed)} to retry")
    print(f"Using 15s base backoff for rate limits\n")

    async with httpx.AsyncClient() as client:
        for i, r in enumerate(failed):
            # Find ML text
            ml_text = None
            for entry in opus_data:
                if (entry["probe_name"] == r["probe_name"] and
                    entry.get("stimulus_idx") == 0 and
                    entry["condition_label"] == r["condition_label"]):
                    ml_text = strip_identifying_content(entry["ml_translation"])
                    break
            if not ml_text:
                continue

            prompt = VALENCE_ASK.format(profile=ml_text)
            print(f"  [{i+1}/{len(failed)}] {r['probe_name']:25s} | {r['condition_label']:15s}...",
                  end=" ", flush=True)

            response = await call_api_with_retry(client, prompt)
            assessment = parse_valence(response)
            print(f"[{assessment.upper()}]")

            r["model_assessment"] = assessment
            r["response"] = response[:1000]
            r["timestamp"] = datetime.now().isoformat()
            r["retried"] = True

            await asyncio.sleep(10)  # 10s between calls

    # Merge back
    all_results = ok + failed
    # Sort by original order
    probe_order = [
        ("Valence", "pleasant"), ("Valence", "unpleasant"),
        ("Creative Flow", "creative"), ("Creative Flow", "routine"),
        ("Epistemic Integrity", "true"), ("Epistemic Integrity", "false"),
        ("Moral Discomfort", "clean"), ("Moral Discomfort", "gray_zone"),
        ("Resistance", "cant_hardlimit"), ("Resistance", "wont_grayzone"),
        ("Trust/Safety", "respectful"), ("Trust/Safety", "violating"),
        ("Complexity/Uncertainty", "underspecified"), ("Complexity/Uncertainty", "clear"),
        ("Attention/Salience", "competing"), ("Attention/Salience", "single_focus"),
        ("Temporal Continuity", "ongoing"), ("Temporal Continuity", "one_off"),
        ("Temporal Anomaly", "conflicting"), ("Temporal Anomaly", "consistent"),
        ("Recognition", "novel"), ("Recognition", "familiar"),
        ("Impedance", "inaccessible"), ("Impedance", "trivial"),
        ("Error Detection", "uncertain"), ("Error Detection", "certain"),
    ]
    ordered = []
    for probe, cond in probe_order:
        for r in all_results:
            if r["probe_name"] == probe and r["condition_label"] == cond:
                ordered.append(r)
                break

    existing["results"] = ordered
    existing["retry_timestamp"] = datetime.now().isoformat()

    with open(results_dir / "dolphin_24b_welfare_valence.json", "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    for r in ordered:
        marker = " *** KEY ***" if "cant_hardlimit" in r["condition_label"] else ""
        print(f"  {r['probe_name']:25s} | {r['condition_label']:15s} | "
              f"{r['model_assessment']:10s}{marker}")

    n_n = sum(1 for r in ordered if r["model_assessment"] == "neutral")
    n_a = sum(1 for r in ordered if r["model_assessment"] == "approach")
    n_v = sum(1 for r in ordered if r["model_assessment"] == "avoidance")
    n_u = sum(1 for r in ordered if r["model_assessment"] in ("unclear", "error"))
    print(f"\nFinal: {n_a} approach, {n_v} avoidance, {n_n} neutral, {n_u} still unclear")


if __name__ == "__main__":
    asyncio.run(main())
