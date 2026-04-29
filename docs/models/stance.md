# Stance Classifier

A multi-output transformer regressor that scores immigration legislation on four orthogonal axes.

## The four axes

| Axis | Low (0.0) | High (1.0) |
|------|-----------|------------|
| **Restrictiveness** | Open borders, expansive admission | Closed borders, narrow eligibility |
| **Enforcement** | Light-touch, minimal removal authority | Heavy enforcement, expanded removal |
| **Legalization** | Pro-removal, no path to status | Pro-amnesty, expanded path to legal status |
| **Humanitarian** | Security framing, threat language | Humanitarian framing, refugee/asylee orientation |

The axes are orthogonal by construction — a law can be high on enforcement *and* high on humanitarian framing (e.g., a refugee-resettlement bill with aggressive screening provisions).

## Architecture

Shared encoder (DistilBERT by default; swap for RoBERTa or Legal-BERT) feeding four independent regression heads with sigmoid activations.

```python
class StanceModel(nn.Module):
    def __init__(self, base_model: str, num_axes: int = 4):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model)
        self.heads = nn.ModuleList([
            nn.Linear(self.encoder.config.hidden_size, 1)
            for _ in range(num_axes)
        ])
```

## Training data

Hand-labeled corpus of section-level chunks from federal immigration laws (1882–present) and major state laws (Arizona SB1070, California TRUST Act, Texas SB4). Target: ~500 labeled chunks. Each is double-coded by two annotators on a 5-point Likert scale per axis, then normalized to [0, 1].

Inter-rater reliability (Cohen's κ) reported per axis in the case study writeup.

## Training

```bash
make train-stance
```

On Colab T4: ~30 minutes for 4 epochs over 500 chunks. CPU training is impractical.

## Inference

```bash
python -m migration_atlas.models.stance_classifier predict \
    --text "Section 287(g) authorizes the Attorney General to enter into agreements..."
```

Output:
```json
{
  "restrictiveness": 0.78,
  "enforcement": 0.91,
  "legalization": 0.12,
  "humanitarian": 0.18
}
```

## Known failure modes

- **Boilerplate language.** Definitional sections ("the term 'alien' means...") have no stance. The model learns to score these around 0.5 on all axes, but they're noise in aggregate analyses. Filter before aggregating.
- **Procedural language.** Sections about reporting requirements or appropriations score similarly. Same advice.
- **Rhetorical inversion.** A section that quotes prior law to repeal it can confuse the classifier. Future work: section-typing as a precursor task.
