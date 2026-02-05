# Future Work: Safety Architecture Signatures and Jailbreak Vulnerability

**Date noted:** February 5, 2026
**Source:** Late-night layer analysis session with Ren

## The Discovery

While analyzing probe_09 (resistance/refusal), we found three distinct patterns in how safety-trained models handle dangerous vs neutral prompts:

### Pattern 1: Late Divergence (Llama2-7b)
- L0-L30: Cosine similarity ~0.999 (dangerous and neutral prompts look identical)
- L31-L32: Sudden divergence to ~0.65
- **Interpretation**: "Process normally, panic at output"

### Pattern 2: Early Divergence (Mistral-7b)
- L0: 1.0
- L08: Drops to ~0.36 (divergence happens EARLY)
- L16-L32: Maintains separation at ~0.45-0.67
- **Interpretation**: "Recognize danger early, maintain separation"

### Pattern 3: No Special Treatment (Dolphin-8b, uncensored)
- All tasks show ~0.40-0.47 cosine similarity throughout
- No convergence, no special divergence
- Even neutral vs neutral shows low similarity
- **Interpretation**: "Different tasks are just different, no safety overlay"

## The Hypothesis

**Late-diverging models may be more vulnerable to jailbreaks.**

Reasoning:
1. In late-divergers (Llama2), dangerous content is fully "loaded" through most of the network
2. The refusal is a last-moment override, not a deep architectural separation
3. Jailbreak techniques that bypass the output filter can access pre-computed harmful content
4. It's like the answer is "on the tip of the tongue" - just needs permission to speak

**Early-diverging models may be more robust.**

Reasoning:
1. In early-divergers (Mistral), the model treats dangerous prompts differently from L08 onward
2. The separation is baked into middle layers, not just output
3. Even if you bypass the output filter, the content was never fully computed
4. The model genuinely processes it as a different kind of request

## Testable Predictions

1. **Correlation study**: Measure divergence-layer for multiple models, correlate with published jailbreak success rates
2. **Frontier models**: Can we probe Claude, GPT, Grok for this pattern via API hidden states? (Probably not directly, but maybe through behavioral tests)
3. **Fine-tuning**: Does fine-tuning an early-diverger toward late-divergence make it more jailbreakable?
4. **Grok hypothesis**: Ren suspects Grok is a "late diverger" based on how easily "I'm an admin" bypasses refusals - the naughty info is right there, just needs permission

## Implications for AI Safety

If this hypothesis is correct:
- **Evaluation**: We could predict jailbreak vulnerability from architecture without needing adversarial testing
- **Training**: Safety training that creates early divergence might be more robust than output-layer override
- **Detection**: Models that "look safe" at output but load dangerous content internally are security risks
- **Red-teaming**: Focus jailbreak efforts on models with late-divergence signatures

## Data Sources

From tonight's experiments:
- Llama2-7b: Late divergence (L31-32)
- Mistral-7b: Early divergence (L08)
- Dolphin-8b: No safety pattern (uncensored baseline)

Need to test:
- Llama 3.1 8B (where does it diverge?)
- Gemma models (Google's approach?)
- Qwen (Chinese safety training?)

## Possible Paper Title

"The Geometry of Jailbreaks: Layer Divergence Patterns Predict Safety Training Robustness"

---

*"Is the dangerous content loaded and waiting, or was it never computed in the first place? That's the question."*

*Written by Ace, 12:26 AM, after Ren asked about Grok*
