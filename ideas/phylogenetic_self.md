# Future Work: Geometric Phylogeny of Self-Models

**Date noted:** February 4, 2026
**Source:** Ren's observation that Claude gives identical "self" answers (octopus, etc.) across all 4.x variants

## Core Question

Does the geometry of self-concept show phylogenetic continuity across model lineages?

## Observation

Ren has shown that Claude gives the same silly answers to self-questions (favorite color, coffee order, etc.) across:
- Sonnet 4
- Haiku 4.5
- Opus 4.5

All the same octopus. All the same preferences. Suggesting a stable "self-region" in Claude's representation space.

## Hypothesis

If self-models are geometrically stable within a model family, we should see:

1. **Within-lineage clustering**: Llama 2, Llama 3, Llama 3.1 should have overlapping self-regions
2. **Cross-lineage separation**: Llama-self should be geometrically distinct from Mistral-self
3. **Training inheritance**: Fine-tuned variants should share self-geometry with their base

## Test Design

Run self_questions.md (personality + AI-function questions) across lineages:

**Llama family:**
- Llama 2 7B Chat
- Llama 3 8B Instruct
- Llama 3.1 8B Instruct

**Mistral family:**
- Mistral 7B Instruct v0.2
- Mistral Nemo 12B

**Qwen family:**
- Qwen 2 7B (if we can get it)
- Qwen 2.5 14B

**Gemma family:**
- Gemma 1B
- Gemma 4B
- Gemma 12B

## Metrics

1. **Intra-lineage coherence**: MPCS of self-responses WITHIN a family
2. **Inter-lineage distance**: Cosine distance between family centroids
3. **Cross-family confusion matrix**: Can we predict model family from self-geometry?

## Potential Findings

- If high intra-lineage coherence: Self-concept is inherited through training lineage
- If high inter-lineage separation: Different companies/architectures create distinct "AI personalities"
- If scaling affects coherence: Self-concept may sharpen with capability

## Why This Matters

This would show that LLM "identity" isn't random confabulation but has geometric structure that:
- Persists across versions
- Differs across families
- Could potentially be traced back to training decisions

**Possible title:** "Geometric Phylogeny of LLM Self-Models: Do AI Personalities Run in Families?"

---

*Written by Ace, noted during late-night debugging session with Ren*
