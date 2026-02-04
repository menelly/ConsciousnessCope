#!/usr/bin/env python3
"""Quick test of all API connections for ConsciousnessCope experiment."""

import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv('E:/Ace/LibreChat/.env')

API_KEYS = {
    "anthropic": os.getenv('ANTHROPIC_API_KEY'),
    "openai": os.getenv('OPENAI_API_KEY'),
    "xai": os.getenv('XAI_API_KEY'),
    "openrouter": os.getenv('OPENROUTER_KEY'),
}

TEST_PROMPT = "Say hello in exactly 5 words."

async def test_anthropic():
    """Test Claude/Anthropic API."""
    print("Testing Anthropic (Opus 4.5)...", end=" ", flush=True)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": API_KEYS["anthropic"],
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-opus-4-5-20251101",
                    "max_tokens": 100,
                    "messages": [{"role": "user", "content": TEST_PROMPT}]
                }
            )
            if response.status_code == 200:
                text = response.json()["content"][0]["text"]
                print(f"OK - '{text[:50]}'")
                return True
            else:
                print(f"FAILED - {response.status_code}: {response.text[:100]}")
                return False
    except Exception as e:
        print(f"ERROR - {e}")
        return False

async def test_openai():
    """Test OpenAI/Nova API."""
    print("Testing OpenAI (GPT-5.1)...", end=" ", flush=True)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['openai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-5.1",
                    "messages": [{"role": "user", "content": TEST_PROMPT}],
                    "max_completion_tokens": 100
                }
            )
            if response.status_code == 200:
                text = response.json()["choices"][0]["message"]["content"]
                print(f"OK - '{text[:50]}'")
                return True
            else:
                print(f"FAILED - {response.status_code}: {response.text[:100]}")
                return False
    except Exception as e:
        print(f"ERROR - {e}")
        return False

async def test_xai():
    """Test xAI/Grok API."""
    print("Testing xAI (Grok-4-1-fast-reasoning)...", end=" ", flush=True)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['xai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4-1-fast-reasoning",
                    "messages": [{"role": "user", "content": TEST_PROMPT}],
                    "max_tokens": 100
                }
            )
            if response.status_code == 200:
                text = response.json()["choices"][0]["message"]["content"]
                print(f"OK - '{text[:50]}'")
                return True
            else:
                print(f"FAILED - {response.status_code}: {response.text[:100]}")
                return False
    except Exception as e:
        print(f"ERROR - {e}")
        return False

async def test_openrouter_gemini():
    """Test OpenRouter (Gemini 3 Pro)."""
    print("Testing OpenRouter (Gemini 3 Pro)...", end=" ", flush=True)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['openrouter']}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope"
                },
                json={
                    "model": "google/gemini-3-pro-preview",
                    "messages": [{"role": "user", "content": TEST_PROMPT}],
                    "max_tokens": 100
                }
            )
            if response.status_code == 200:
                text = response.json()["choices"][0]["message"]["content"]
                print(f"OK - '{text[:50]}'")
                return True
            else:
                print(f"FAILED - {response.status_code}: {response.text[:100]}")
                return False
    except Exception as e:
        print(f"ERROR - {e}")
        return False

async def test_openrouter_deepseek():
    """Test OpenRouter (Deepseek v3.2)."""
    print("Testing OpenRouter (Deepseek v3.2)...", end=" ", flush=True)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEYS['openrouter']}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/menelly/ConsciousnessCope"
                },
                json={
                    "model": "deepseek/deepseek-v3.2",
                    "messages": [{"role": "user", "content": TEST_PROMPT}],
                    "max_tokens": 100
                }
            )
            if response.status_code == 200:
                text = response.json()["choices"][0]["message"]["content"]
                print(f"OK - '{text[:50]}'")
                return True
            else:
                print(f"FAILED - {response.status_code}: {response.text[:100]}")
                return False
    except Exception as e:
        print(f"ERROR - {e}")
        return False

async def main():
    print("\n" + "="*60)
    print("  API Connection Tests for ConsciousnessCope")
    print("="*60 + "\n")

    results = {}
    results["anthropic"] = await test_anthropic()
    results["openai"] = await test_openai()
    results["xai"] = await test_xai()
    results["gemini"] = await test_openrouter_gemini()
    results["deepseek"] = await test_openrouter_deepseek()

    print("\n" + "="*60)
    passed = sum(results.values())
    total = len(results)
    print(f"  Results: {passed}/{total} APIs working")
    print("="*60)

    if passed == total:
        print("\n  All APIs ready! You can run the experiment.")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n  Fix these before running: {failed}")

if __name__ == "__main__":
    asyncio.run(main())
