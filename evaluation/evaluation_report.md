# PII Redaction Tool — Evaluation Report

## 1. Dataset & Overview
- **Evaluated Document**: `examples/synthetic_test.docx`
- **Evaluation Method**: Comparison against manually verified ground truth (`evaluation/ground_truth.json`).
- **Note**: Evaluation results below are derived from the synthetic test dataset. The confidential assignment DOCX will be evaluated separately by the developer.

## 2. Evaluation Methodology
Metrics are computed using standard statistical definitions:
- **Precision**: `TP / (TP + FP)` — Measures how many of the detected entities were actual PII.
- **Recall**: `TP / (TP + FN)` — Measures how many actual PII entities were successfully detected.
- **F1 Score**: `2 × Precision × Recall / (Precision + Recall)` — Harmonic mean of Precision and Recall.
- **Accuracy**: `(TP + TN) / (TP + TN + FP + FN)` — Overall prediction accuracy.

> [!NOTE]
> Precision, Recall, and F1 are the primary metrics for PII detection because non-PII text constitutes the vast majority of document content.

## 3. Detailed Results by PII Type

| PII Type | Ground Truth | Detected | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **ADDRESS** | 1 | 1 | 1 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **CREDIT_CARD** | 1 | 1 | 1 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **DOB** | 1 | 1 | 1 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **EMAIL** | 6 | 6 | 6 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **IP** | 2 | 2 | 2 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **ORG** | 5 | 6 | 5 | 1 | 0 | 0.8333 | 1.0000 | 0.9091 |
| **PERSON** | 10 | 11 | 10 | 1 | 0 | 0.9091 | 1.0000 | 0.9524 |
| **PHONE** | 5 | 5 | 5 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **SSN** | 1 | 1 | 1 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **URL** | 5 | 5 | 5 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **OVERALL** | **37** | **39** | **37** | **2** | **0** | **0.9487** | **1.0000** | **0.9737** |

## 4. Discussion of False Positives & False Negatives
- **False Positives**: Can occur when generic company names or address fragments overlap with general business terminology. Controlled via validation filters.
- **False Negatives**: Can occur if an address or person name lacks contextual indicators and is missed by default SpaCy model rules.

## 5. Known Limitations & Future Improvements
1. **OCR / Embedded Images**: PII embedded inside raster images is not extracted or modified.
2. **Custom Regional Entities**: Regional identity numbers (e.g. Aadhaar, PAN) can be added via the plugin detector architecture.
3. **Complex Tables**: Nested tables or rotated text elements are preserved as default python-docx blocks.