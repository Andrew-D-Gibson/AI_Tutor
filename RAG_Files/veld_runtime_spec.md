# Technical Specification: Veld Runtime v0.9 (Pre-Release)
**Document Owner:** Niamh Calvert, VP Product — Orenth Systems  
**Classification:** Internal / Engineering Review  
**Last Updated:** 2024-09-18  
**Status:** Feature-complete; pending final performance validation

---

## 1. Overview

Veld is a quantized ML inference runtime designed to run on the Duravel-4X sensor hardware platform. Its primary purpose is to execute trained anomaly detection and predictive maintenance models locally — without cloud or edge-server offload — within the computational and thermal constraints of the Duravel embedded environment.

The goal of Veld is to close the gap between Lithos Pro (cloud-dependent ML) and Lithos Enterprise (managed on-device ML for high-spec deployments) by enabling meaningful on-device inference on hardware that was not originally designed for it.

---

## 2. Target Hardware

| Platform | MCU | RAM | Flash | Clock Speed |
|---|---|---|---|---|
| Duravel-4X (primary) | Orenth OC-9 (ARM Cortex-M7 derivative) | 512 KB SRAM + 2 MB PSRAM | 8 MB | 480 MHz |
| Duravel-7G (stretch goal) | Orenth OC-11 | 512 KB SRAM + 4 MB PSRAM | 8 MB | 480 MHz |
| Duravel-9M | Orenth OC-9 | 512 KB SRAM + 2 MB PSRAM | 8 MB | 480 MHz |

Veld is **not** currently targeted at the Duravel-11S subsea platform due to that platform's stricter thermal dissipation limits and distinct firmware architecture.

---

## 3. Quantization Approach

Veld uses **INT8 post-training quantization (PTQ)** with per-channel weight quantization and per-tensor activation quantization. This approach was selected over QAT (quantization-aware training) for initial release to minimize the burden on customers providing custom-trained models — PTQ requires no modification to training pipelines.

Accuracy impact on our internal benchmark suite (see: §7) is under 2.5% F1 degradation relative to FP32 baseline for all validated model architectures.

Future releases may add INT4 support for weight-only quantization to support larger model families, pending internal evaluation.

---

## 4. Supported Model Architectures (v0.9)

Veld v0.9 supports a constrained set of operator types. Models must be exported to ONNX (opset 17 or earlier) and pass the Veld model validator tool before deployment.

**Supported:**
- Dense (fully connected) layers
- 1D Convolution (Conv1d) — stride 1 or 2, kernel sizes 3, 5, 7
- BatchNorm (fused to preceding layer at export time)
- ReLU, ReLU6, GELU (approximated)
- GlobalAveragePooling1D
- LSTM (single-layer only; bidirectional not supported)
- Reshape, Squeeze, Unsqueeze, Concat (limited dims)

**Not yet supported:**
- 2D Convolution (not relevant to current sensor data types)
- Attention / Transformer blocks (memory footprint too large for target hardware)
- Dynamic shapes (all input shapes must be static at compile time)
- TensorFlow Lite source models (ONNX conversion required)

---

## 5. Inference Pipeline

```
[Raw Sensor Stream]
        │
        ▼
[Preprocessing Stage]
  - Windowing (configurable: 64, 128, 256 samples)
  - Normalization (z-score; mean/std stored in model metadata)
  - Optional: FFT feature extraction (Veld built-in)
        │
        ▼
[Veld Model Executor]
  - INT8 quantized forward pass
  - Output: class probabilities or regression value
        │
        ▼
[Lithos Alert Engine]
  - Threshold evaluation
  - Alert emission (local + uplink)
```

Total inference latency on Duravel-4X (128-sample window, 3-layer dense model): **~2.1 ms**.

---

## 6. Memory Budget

| Component | RAM Usage |
|---|---|
| Veld runtime overhead | ~48 KB |
| Model parameters (max supported) | ~380 KB |
| Activation scratch buffer | ~64 KB |
| Preprocessing buffers | ~16 KB |
| **Total max** | **~508 KB** |

This leaves approximately 4 KB headroom against the 512 KB SRAM limit. PSRAM is available as overflow for non-latency-critical storage (e.g., model metadata, logging buffers) but cannot be used for inference activations due to latency constraints.

**Important:** Deploying models exceeding the parameter budget will cause a runtime initialization failure with error code `VELD_E_MEM_OVERFLOW`. The validator tool enforces this limit at compile time.

---

## 7. Internal Benchmark Suite

Validation was performed against four synthetic datasets and two real-world customer datasets (anonymized, shared under data use agreements):

| Dataset | Task | Model Used | FP32 F1 | INT8 F1 | Δ |
|---|---|---|---|---|---|
| SynthVibe-A | Bearing fault classification (4 class) | 3-layer dense | 0.941 | 0.926 | -1.6% |
| SynthVibe-B | Imbalance detection (binary) | LSTM + dense | 0.978 | 0.955 | -2.3% |
| SynthTemp-1 | Thermal runaway prediction (binary) | Conv1D + dense | 0.913 | 0.893 | -2.2% |
| RailAxle-Demo | Axle fault detection (6 class) | Conv1D + LSTM | 0.887 | 0.866 | -2.4% |
| [Customer A] — mining | Pump cavitation (binary) | Dense | 0.961 | 0.948 | -1.4% |
| [Customer B] — offshore | Valve leak detection (binary) | Conv1D | 0.902 | 0.882 | -2.2% |

All datasets validated on held-out test splits. No dataset used for quantization calibration.

---

## 8. Known Limitations and Open Issues

- **Issue #VLD-114:** LSTM layer output precision degrades slightly when sequence length exceeds 200 timesteps. Workaround: keep inference window ≤ 200 samples for LSTM-containing models. Fix targeted for v1.0.
- **Issue #VLD-131:** GELU approximation introduces a max error of ~0.4% vs. exact GELU on edge cases near input = ±3.2. Not expected to materially affect model output but flagged for transparency.
- **Calibration sensitivity:** PTQ calibration quality is highly dependent on calibration dataset size and representativeness. Minimum recommendation: 500 samples covering expected operating range. Models calibrated on fewer samples show higher INT8 accuracy loss.
- **No hardware float fallback:** Veld has no FP32 fallback path. If a model fails INT8 validation, it cannot run on Veld at all.

---

## 9. Integration with Lithos Platform

Veld is integrated as a module within Lithos Core and Pro (from v3.0 onward). The Lithos device management console provides:

- Model upload and validator execution (pre-deployment check)
- Calibration dataset submission
- Remote deployment and versioning
- Inference result logging and drift monitoring

Veld models deployed via Lithos are versioned independently from Lithos firmware. A model rollback can be performed without a full firmware update.

---

## 10. Roadmap

| Release | Target Date | Key Features |
|---|---|---|
| v0.9 (current) | Q4 2024 | INT8 PTQ, supported arch list above, Duravel-4X/9M |
| v1.0 | Q1 2025 | VLD-114 fix, Duravel-7G support, improved calibration tooling |
| v1.2 | H1 2025 | INT4 weight-only quant (experimental), extended operator support |
| v2.0 | H2 2025 | Transformer block support (evaluated pending memory architecture changes) |
