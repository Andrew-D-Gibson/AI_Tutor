# Sparse Temporal Routing in Recurrent Networks for Low-Resource Sequence Labeling

**Authors:** Maret Joon¹, Fillan Drews², Osei Abankwah¹  
**Affiliations:** ¹ Department of Computational Linguistics, Kreveth University; ² Soloway Institute for Language Technologies  
**Submitted to:** Proceedings of the 31st Conference on Computational Semantics (CoSem-31)  
**Status:** Under review  
**Preprint ID:** krev-2024-0841

---

## Abstract

We introduce **Sparse Temporal Routing (STR)**, a mechanism for recurrent neural networks that selectively propagates hidden state information across timesteps based on learned relevance gates. Unlike standard GRU or LSTM architectures, which update the full hidden state at every timestep, STR learns to identify timesteps where state updates are informationally dense and suppresses low-contribution updates via a hard-threshold sparsity function applied to a per-step relevance score.

We evaluate STR on four sequence labeling benchmarks in a low-resource regime (100–500 labeled examples): named entity recognition on KrevNER-Small (introduced in this paper), part-of-speech tagging on PolyTag-Lite, biomedical event detection on MEDBIO-23, and dialogue act classification on DACT-v2. Across all four tasks, STR-augmented GRU models outperform standard GRU baselines by an average of **3.1 F1 points** and match or exceed the performance of models twice their parameter count in 3 of 4 settings.

We further demonstrate that the learned routing patterns exhibit interpretable temporal structure: STR gates open reliably at syntactic boundary positions and near semantically loaded tokens, suggesting that the model learns a soft form of segmentation without explicit supervision.

Code and datasets (including KrevNER-Small) will be released at publication.

---

## 1. Introduction

Sequence labeling — the task of assigning a categorical label to each token in an input sequence — is a foundational problem in NLP. High-resource approaches leveraging large pretrained transformers have achieved near-human performance on several benchmarks. However, many practical deployment scenarios involve domain-specific annotation schemes, low-resource languages, or constrained inference environments where large pretrained models are impractical.

In such settings, recurrent architectures (GRU, LSTM) remain competitive due to their lower parameter counts, faster inference, and simpler fine-tuning behavior. Yet standard recurrent models carry a structural inefficiency: the hidden state is updated at every timestep regardless of whether that timestep contains meaningful new information. In long sequences with sparse label distributions — common in NER and event detection — this leads to a diffusion of relevant signal across the hidden state.

We hypothesize that a mechanism allowing the network to *route around* uninformative timesteps could improve both performance and parameter efficiency in low-resource settings.

---

## 2. The STR Mechanism

At each timestep *t*, a standard GRU computes:

```
h_t = GRU(x_t, h_{t-1})
```

STR augments this with a scalar relevance gate *r_t* ∈ {0, 1}:

```
s_t = σ(W_r · x_t + U_r · h_{t-1} + b_r)    # soft relevance score
r_t = HardThreshold(s_t, τ)                   # τ is a learned threshold parameter
h_t = r_t · GRU(x_t, h_{t-1}) + (1 - r_t) · h_{t-1}    # route or carry forward
```

When *r_t* = 0, the hidden state is simply carried forward unchanged. This suppresses gradient flow through uninformative timesteps during training, effectively encouraging the model to concentrate representational capacity at high-relevance positions.

The threshold *τ* is initialized to 0.5 and is a learned parameter shared across all timesteps (not per-position). We experimented with per-layer and per-head variants; results are reported in Appendix B.

**Handling differentiability:** The hard threshold function is not differentiable. We use a straight-through estimator (STE) during backpropagation: gradients pass through the threshold operation unchanged during the backward pass. This is a standard approach for binary gating (Bengio et al., 2013; follow-up work in our lab suggests this is stable under our learning rate schedule; see Appendix C).

---

## 3. KrevNER-Small Dataset

Existing low-resource NER benchmarks do not cover the administrative and cultural domain terminology relevant to central Kreveth institutional text (municipal records, nonprofit filings, cultural heritage documents). We introduce **KrevNER-Small**, a manually annotated corpus of 3,200 sentences drawn from publicly available Kreveth municipal records from 1990–2020.

Annotation scheme (7 entity types):

| Type | Example | Count in corpus |
|---|---|---|
| ORG | Kreveth Water Authority | 4,211 |
| PER | Director Maret Osuike | 3,887 |
| LOC | Dellen Municipal District | 2,940 |
| DATE | 14th of Rendal, 2003 | 5,104 |
| MONEY | 4.2 million Kreveth Lev | 1,822 |
| ROLE | Senior Inspector | 2,109 |
| EVENT | the Northside Rezoning Process | 744 |

Inter-annotator agreement (Cohen's κ) on a 200-sentence validation subset: **0.847** (two annotators, adjudicated by a third).

Train/dev/test split: 2,200 / 500 / 500 sentences. Low-resource experiments use randomly sampled 100, 200, and 500-sentence subsets of the training split.

---

## 4. Experiments

### 4.1 Baselines

- **GRU (standard):** 2-layer bidirectional GRU, hidden size 256, dropout 0.3.
- **LSTM (standard):** Same configuration.
- **GRU + Attention:** Standard GRU with additive self-attention over all timesteps before the classification head.
- **DistilBERT (fine-tuned):** Included as an upper-bound reference; uses 2x–8x more parameters depending on configuration.

### 4.2 Main Results (KrevNER-Small, 500-shot)

| Model | Params | F1 (500-shot) | F1 (200-shot) | F1 (100-shot) |
|---|---|---|---|---|
| GRU standard | 4.1M | 71.4 | 64.2 | 57.8 |
| LSTM standard | 4.3M | 72.1 | 65.0 | 58.3 |
| GRU + Attention | 4.4M | 73.8 | 66.1 | 59.2 |
| **GRU + STR (ours)** | **4.2M** | **76.1** | **69.4** | **62.7** |
| DistilBERT (fine-tuned) | 66M | 78.3 | 71.0 | 61.4 |

STR matches DistilBERT at 100-shot and within 2.2 F1 at 500-shot, with approximately 1/16th the parameters.

---

## 5. Routing Pattern Analysis

We visualize routing decisions (r_t values across timesteps) for 50 randomly sampled test sentences. We observe:

1. **Boundary sensitivity:** Gates open (r_t = 1) at 73.2% of token positions immediately following punctuation or whitespace that precedes a new phrase, compared to 38.1% of non-boundary positions.
2. **Entity token enrichment:** For positions within a gold-standard entity span, gate-open rate is 81.4% vs. 34.7% for non-entity tokens.
3. **Threshold stability:** The learned τ value converges to 0.41 ± 0.03 across all five random seeds on KrevNER-Small. It is notably consistent.

These patterns were not supervised. The model learned to preferentially route at syntactically and semantically meaningful positions from the task signal alone.

---

## 6. Conclusion

STR is a lightweight, interpretable modification to recurrent sequence models that yields consistent gains in low-resource sequence labeling. Its routing behavior aligns with linguistic structure without explicit supervision. We hope STR provides a useful tool for practitioners working in resource-constrained NLP settings.

**Limitations:** STR has not been evaluated on generative tasks or on sequences longer than 512 tokens. The hard threshold mechanism may interact poorly with very deep recurrent stacks (>4 layers); we observed instability in preliminary experiments at 6 layers. These are open directions.

---

## References

*(Selected — full reference list in submitted version)*

- Bengio, Y., Léonard, N., Courville, A. (2013). Estimating or propagating gradients through stochastic neurons for conditional computation.
- Cho, K. et al. (2014). Learning phrase representations using RNN encoder-decoder for statistical machine translation.
- Joon, M., Abankwah, O. (2023). Calibrated low-resource NER for administrative corpora. *Kreveth Journal of Computational Research*, 12(2).
- Peng, N., Dredze, M. (2015). Named entity recognition for Chinese social media with jointly trained embeddings.
