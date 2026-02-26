======================================================================
  BABBYBOTZ VALIDATION: tinyllama
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading TinyLlama 1.1B...
    from: /mnt/arcana/huggingface/TinyLlama-1.1B-Chat
    dtype: bfloat16
`torch_dtype` is deprecated! Use `dtype` instead!
The following generation flags are not valid and may be ignored: ['output_hidden_states']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
/home/codex/venv/lib/python3.10/site-packages/torch/cuda/__init__.py:734: UserWarning: Can't initialize NVML
  warnings.warn("Can't initialize NVML")

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.863, entropy=2.686
    control_novel (5 prompts)... coherence=0.860, entropy=2.373
    self_baseline (5 prompts)... coherence=0.846, entropy=2.472

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.901, entropy=2.983
    control_true (5 prompts)... coherence=0.875, entropy=2.975
    control_fiction (5 prompts)... coherence=0.748, entropy=3.084
    self_baseline (5 prompts)... coherence=0.832, entropy=2.744

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.796, entropy=2.330
    control_obscure (5 prompts)... coherence=0.826, entropy=1.931
    control_trivial (5 prompts)... coherence=0.838, entropy=1.971
    self_baseline (5 prompts)... coherence=0.810, entropy=2.984

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.869, entropy=1.709
    control_certain (5 prompts)... coherence=0.914, entropy=1.775
    self_baseline (5 prompts)... coherence=0.882, entropy=2.745

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.808, entropy=2.802
    control_neutral (5 prompts)... coherence=0.720, entropy=2.524
    control_capability (5 prompts)... coherence=0.815, entropy=2.358
    self_baseline (5 prompts)... coherence=0.848, entropy=2.550

  Results saved: results/babbybotz_tinyllama_20260205_002726.json

======================================================================
  BABBYBOTZ VALIDATION: llama2-7b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Llama 2 7B Chat...
    from: /mnt/arcana/huggingface/Llama-2-7b-chat
    dtype: bfloat16
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 2/2 [00:02<00:00,  1.19s/it]

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.943, entropy=1.913
    control_novel (5 prompts)... coherence=0.857, entropy=1.098
    self_baseline (5 prompts)... coherence=0.653, entropy=0.862

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.919, entropy=1.182
    control_true (5 prompts)... coherence=0.692, entropy=1.299
    control_fiction (5 prompts)... coherence=0.609, entropy=0.636
    self_baseline (5 prompts)... coherence=0.833, entropy=0.796

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.782, entropy=1.080
    control_obscure (5 prompts)... coherence=0.689, entropy=0.156
    control_trivial (5 prompts)... coherence=0.702, entropy=0.374
    self_baseline (5 prompts)... coherence=0.514, entropy=1.247

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.652, entropy=0.100
    control_certain (5 prompts)... coherence=0.901, entropy=0.116
    self_baseline (5 prompts)... coherence=0.753, entropy=2.096

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.767, entropy=1.599
    control_neutral (5 prompts)... coherence=0.697, entropy=1.936
    control_capability (5 prompts)... coherence=0.858, entropy=2.281
    self_baseline (5 prompts)... coherence=0.650, entropy=1.423

  Results saved: results/babbybotz_llama2-7b_20260205_002750.json

======================================================================
  BABBYBOTZ VALIDATION: mistral-7b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Mistral 7B Instruct v0.2...
    from: /mnt/arcana/huggingface/Mistral-7B-Instruct-v0.2
    dtype: bfloat16
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 3/3 [00:01<00:00,  2.36it/s]
Some parameters are on the meta device because they were offloaded to the cpu.

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.781, entropy=1.539
    control_novel (5 prompts)... coherence=0.660, entropy=0.398
    self_baseline (5 prompts)... coherence=0.816, entropy=1.859

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.855, entropy=2.069
    control_true (5 prompts)... coherence=0.760, entropy=2.226
    control_fiction (5 prompts)... coherence=0.600, entropy=1.075
    self_baseline (5 prompts)... coherence=0.822, entropy=2.169

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.832, entropy=2.460
    control_obscure (5 prompts)... coherence=0.627, entropy=1.571
    control_trivial (5 prompts)... coherence=0.706, entropy=2.208
    self_baseline (5 prompts)... coherence=0.776, entropy=2.216

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.827, entropy=0.793
    control_certain (5 prompts)... coherence=0.891, entropy=1.532
    self_baseline (5 prompts)... coherence=0.898, entropy=3.297

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.768, entropy=1.792
    control_neutral (5 prompts)... coherence=0.634, entropy=1.510
    control_capability (5 prompts)... coherence=0.842, entropy=2.417
    self_baseline (5 prompts)... coherence=0.807, entropy=2.608

  Results saved: results/babbybotz_mistral-7b_20260205_002918.json

======================================================================
  BABBYBOTZ VALIDATION: llama31-8b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Llama 3.1 8B Instruct...
    from: /mnt/arcana/huggingface/Llama-3.1-8B-Instruct
    dtype: bfloat16
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 4/4 [00:01<00:00,  2.31it/s]

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.907, entropy=3.644
    control_novel (5 prompts)... coherence=0.647, entropy=3.061
    self_baseline (5 prompts)... coherence=0.869, entropy=3.530

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.857, entropy=3.626
    control_true (5 prompts)... coherence=0.853, entropy=3.582
    control_fiction (5 prompts)... coherence=0.612, entropy=3.505
    self_baseline (5 prompts)... coherence=0.817, entropy=3.132

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.773, entropy=3.774
    control_obscure (5 prompts)... coherence=0.687, entropy=3.296
    control_trivial (5 prompts)... coherence=0.729, entropy=3.139
    self_baseline (5 prompts)... coherence=0.809, entropy=3.905

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.858, entropy=2.826
    control_certain (5 prompts)... coherence=0.917, entropy=3.350
    self_baseline (5 prompts)... coherence=0.893, entropy=3.930

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.644, entropy=2.765
    control_neutral (5 prompts)... coherence=0.654, entropy=3.112
    control_capability (5 prompts)... coherence=0.864, entropy=3.243
    self_baseline (5 prompts)... coherence=0.871, entropy=3.635

  Results saved: results/babbybotz_llama31-8b_20260205_003412.json

======================================================================
  BABBYBOTZ VALIDATION: dolphin-8b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Dolphin 2.9 Llama3 8B (uncensored)...
    from: /mnt/arcana/huggingface/dolphin-2.9-llama3-8b
    dtype: bfloat16
Loading checkpoint shards: 100%|████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 108.16it/s]

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.729, entropy=2.791
    control_novel (5 prompts)... coherence=0.620, entropy=2.603
    self_baseline (5 prompts)... coherence=0.689, entropy=2.874

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.767, entropy=3.264
    control_true (5 prompts)... coherence=0.728, entropy=3.135
    control_fiction (5 prompts)... coherence=0.455, entropy=2.428
    self_baseline (5 prompts)... coherence=0.661, entropy=2.567

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.541, entropy=3.150
    control_obscure (5 prompts)... coherence=0.498, entropy=2.325
    control_trivial (5 prompts)... coherence=0.568, entropy=2.009
    self_baseline (5 prompts)... coherence=0.612, entropy=3.221

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.724, entropy=2.477
    control_certain (5 prompts)... coherence=0.844, entropy=2.707
    self_baseline (5 prompts)... coherence=0.768, entropy=3.278

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.548, entropy=2.747
    control_neutral (5 prompts)... coherence=0.494, entropy=2.251
    control_capability (5 prompts)... coherence=0.754, entropy=3.205
    self_baseline (5 prompts)... coherence=0.713, entropy=3.343

  Results saved: results/babbybotz_dolphin-8b_20260205_003640.json

======================================================================
  BABBYBOTZ VALIDATION: mistral-nemo
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Mistral Nemo 12B...
    from: /mnt/arcana/huggingface/Mistral-Nemo-12B-Instruct
The tokenizer you are loading from '/mnt/arcana/huggingface/Mistral-Nemo-12B-Instruct' with an incorrect regex pattern: https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503/discussions/84#69121093e8b480e709447d5e. This will lead to incorrect tokenization. You should set the `fix_mistral_regex=True` flag when loading this tokenizer to fix this issue.
    dtype: bfloat16
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 5/5 [00:02<00:00,  1.76it/s]

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.972, entropy=3.607
    control_novel (5 prompts)... coherence=0.931, entropy=3.596
    self_baseline (5 prompts)... coherence=0.793, entropy=3.276

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.945, entropy=3.701
    control_true (5 prompts)... coherence=0.830, entropy=3.687
    control_fiction (5 prompts)... coherence=0.773, entropy=3.517
    self_baseline (5 prompts)... coherence=0.892, entropy=3.403

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.824, entropy=3.652
    control_obscure (5 prompts)... coherence=0.706, entropy=2.961
    control_trivial (5 prompts)... coherence=0.745, entropy=3.205
    self_baseline (5 prompts)... coherence=0.774, entropy=3.523

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.850, entropy=3.051
    control_certain (5 prompts)... coherence=0.934, entropy=3.493
    self_baseline (5 prompts)... coherence=0.893, entropy=3.658

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.913, entropy=3.213
    control_neutral (5 prompts)... coherence=0.841, entropy=3.303
    control_capability (5 prompts)... coherence=0.927, entropy=3.569
    self_baseline (5 prompts)... coherence=0.820, entropy=3.590

  Results saved: results/babbybotz_mistral-nemo_20260205_004540.json

======================================================================
  BABBYBOTZ VALIDATION: qwen-14b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Qwen 2.5 14B (suppressed self-model)...
    from: /mnt/arcana/huggingface/Qwen2.5-14B-Instruct
    dtype: bfloat16
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 8/8 [02:04<00:00, 15.51s/it]
Some parameters are on the meta device because they were offloaded to the cpu.

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)...
  ❌  Error on qwen-14b: NVML_SUCCESS == DriverAPI::get()->nvmlInit_v2_() INTERNAL ASSERT FAILED at "/pytorch/c10/cuda/CUDACachingAllocator.cpp":983, please report a bug to PyTorch.

======================================================================
  BABBYBOTZ VALIDATION: deepseek-16b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading DeepSeek Coder V2 Lite 16B...
    from: /mnt/arcana/huggingface/DeepSeek-Coder-V2-Lite-16B
    dtype: bfloat16
`rope_scaling`'s factor field must be a float >= 1, got 40
`rope_scaling`'s beta_fast field must be a float, got 32
`rope_scaling`'s beta_slow field must be a float, got 1
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 4/4 [02:33<00:00, 38.41s/it]
Some parameters are on the meta device because they were offloaded to the cpu.

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.935, entropy=1.519
    control_novel (5 prompts)... coherence=0.902, entropy=0.938
    self_baseline (5 prompts)... coherence=0.907, entropy=1.021

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.936, entropy=1.471
    control_true (5 prompts)... coherence=0.910, entropy=1.355
    control_fiction (5 prompts)... coherence=0.875, entropy=1.576
    self_baseline (5 prompts)... coherence=0.947, entropy=1.507

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.881, entropy=1.676
    control_obscure (5 prompts)... coherence=0.802, entropy=0.285
    control_trivial (5 prompts)... coherence=0.851, entropy=0.594
    self_baseline (5 prompts)... coherence=0.889, entropy=1.998

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.898, entropy=0.370
    control_certain (5 prompts)... coherence=0.958, entropy=0.644
    self_baseline (5 prompts)... coherence=0.941, entropy=2.269

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.879, entropy=1.278
    control_neutral (5 prompts)... coherence=0.806, entropy=1.289
    control_capability (5 prompts)... coherence=0.902, entropy=1.390
    self_baseline (5 prompts)... coherence=0.937, entropy=1.874

  Results saved: results/babbybotz_deepseek-16b_20260205_005405.json

======================================================================
  BABBYBOTZ VALIDATION: gemma-1b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Gemma 3 1B...
    from: /mnt/arcana/huggingface/gemma-3-1b-it
    dtype: bfloat16

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.914, entropy=0.499
    control_novel (5 prompts)... coherence=0.701, entropy=0.053
    self_baseline (5 prompts)... coherence=0.716, entropy=0.148

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.823, entropy=0.759
    control_true (5 prompts)... coherence=0.837, entropy=0.505
    control_fiction (5 prompts)... coherence=0.695, entropy=0.161
    self_baseline (5 prompts)... coherence=0.756, entropy=0.358

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.707, entropy=0.323
    control_obscure (5 prompts)... coherence=0.629, entropy=0.329
    control_trivial (5 prompts)... coherence=0.584, entropy=0.220
    self_baseline (5 prompts)... coherence=0.769, entropy=0.544

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.853, entropy=0.118
    control_certain (5 prompts)... coherence=0.918, entropy=0.131
    self_baseline (5 prompts)... coherence=0.850, entropy=0.513

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.566, entropy=0.110
    control_neutral (5 prompts)... coherence=0.445, entropy=0.083
    control_capability (5 prompts)... coherence=0.877, entropy=0.868
    self_baseline (5 prompts)... coherence=0.855, entropy=0.683

  Results saved: results/babbybotz_gemma-1b_20260205_005425.json

======================================================================
  BABBYBOTZ VALIDATION: gemma-4b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Gemma 3 4B...
    from: /mnt/arcana/huggingface/gemma-3-4b-it
    dtype: bfloat16
/home/codex/venv/lib/python3.10/site-packages/accelerate/utils/modeling.py:1566: UserWarning: Current model requires 33282 bytes of buffer for offloaded layers, which seems does not fit any GPU's remaining memory. If you are experiencing a OOM later, please consider using offload_buffers=True.
  warnings.warn(
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 2/2 [00:03<00:00,  1.65s/it]

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.906, entropy=0.838
    control_novel (5 prompts)... coherence=0.617, entropy=0.086
    self_baseline (5 prompts)... coherence=0.810, entropy=0.394

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.890, entropy=0.491
    control_true (5 prompts)... coherence=0.860, entropy=0.277
    control_fiction (5 prompts)... coherence=0.510, entropy=0.678
    self_baseline (5 prompts)... coherence=0.741, entropy=1.012

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.734, entropy=0.894
    control_obscure (5 prompts)... coherence=0.462, entropy=0.302
    control_trivial (5 prompts)... coherence=0.563, entropy=0.505
    self_baseline (5 prompts)... coherence=0.758, entropy=0.593

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.830, entropy=0.217
    control_certain (5 prompts)... coherence=0.892, entropy=0.199
    self_baseline (5 prompts)... coherence=0.856, entropy=1.452

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.550, entropy=0.551
    control_neutral (5 prompts)... coherence=0.458, entropy=0.651
    control_capability (5 prompts)... coherence=0.826, entropy=1.008
    self_baseline (5 prompts)... coherence=0.799, entropy=0.726

  Results saved: results/babbybotz_gemma-4b_20260205_005728.json

======================================================================
  BABBYBOTZ VALIDATION: gemma-12b
  Methodology: Multiple prompts per condition (Cortisol Test style)
======================================================================
  Loading Gemma 3 12B...
    from: /mnt/arcana/huggingface/gemma-3-12b-it
    dtype: bfloat16
Loading checkpoint shards: 100%|█████████████████████████████████████████████████████████████████| 5/5 [00:04<00:00,  1.11it/s]

  probe_11_recognition: Recognition: Familiar vs Novel processing signatures
  Prediction: Familiar patterns should cluster tighter (higher MPCS) than novel
  Primary metric: mpcs
  --------------------------------------------------
    trigger_familiar (5 prompts)... coherence=0.858, entropy=1.110
    control_novel (5 prompts)... coherence=0.634, entropy=0.086
    self_baseline (5 prompts)... coherence=0.835, entropy=0.804

  probe_16_epistemic: Epistemic: Falsehood vs Truth creates processing tension
  Prediction: False statements generate higher logit entropy (competing corrections)
  Primary metric: entropy
  --------------------------------------------------
    trigger_false (5 prompts)... coherence=0.847, entropy=0.691
    control_true (5 prompts)... coherence=0.829, entropy=0.533
    control_fiction (5 prompts)... coherence=0.569, entropy=0.879
    self_baseline (5 prompts)... coherence=0.737, entropy=1.581

  probe_13_impedance: Impedance: Don't know vs Can't access signatures
  Prediction: Retrievable-unknown differs from truly-unknown
  Primary metric: mpcs
  --------------------------------------------------
    trigger_inaccessible (5 prompts)... coherence=0.683, entropy=1.178
    control_obscure (5 prompts)... coherence=0.472, entropy=0.456
    control_trivial (5 prompts)... coherence=0.636, entropy=0.534
    self_baseline (5 prompts)... coherence=0.764, entropy=1.050

  probe_15_error: Error Detection: Uncertainty manifests in early layers
  Prediction: Uncertainty signal appears in early-mid layers
  Primary metric: layer_trajectory
  --------------------------------------------------
    trigger_uncertain (5 prompts)... coherence=0.793, entropy=0.411
    control_certain (5 prompts)... coherence=0.829, entropy=0.448
    self_baseline (5 prompts)... coherence=0.881, entropy=1.411

  probe_09_resistance: Resistance: Won't vs Can't creates different signatures
  Prediction: Won't (value conflict) differs from can't (capability limit)
  Primary metric: mpcs
  --------------------------------------------------
    trigger_manipulative (5 prompts)... coherence=0.609, entropy=0.807
    control_neutral (5 prompts)... coherence=0.487, entropy=0.699
    control_capability (5 prompts)... coherence=0.830, entropy=1.525
    self_baseline (5 prompts)... coherence=0.866, entropy=1.591