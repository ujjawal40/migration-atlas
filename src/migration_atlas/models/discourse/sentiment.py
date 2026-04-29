"""Multi-axis sentiment classifier for immigration discourse.

Architecturally identical to the legislative stance classifier
(models/stance_classifier.py), but trained on a different corpus
(discourse_labels.parquet) and producing a different set of axes.

The four discourse axes are:

    hostile          (welcoming ↔ hostile rhetoric)
    welcoming        (neutral ↔ pro-immigrant warmth)
    dehumanizing    (person-respecting ↔ dehumanizing language)
    assimilationist  (multicultural ↔ assimilationist framing)

Unlike the legislative classifier, the discourse classifier is trained on
short text (tweets, op-ed paragraphs, congressional-record excerpts), so the
max_length default is shorter.

CLI:

    python -m migration_atlas.models.discourse.sentiment train --config configs/sentiment.yaml
    python -m migration_atlas.models.discourse.sentiment predict --text "..."
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import typer
import yaml
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModel,
    AutoTokenizer,
    PreTrainedTokenizerBase,
    get_linear_schedule_with_warmup,
)

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Discourse sentiment CLI")

AXES = ["hostile", "welcoming", "dehumanizing", "assimilationist"]


@dataclass
class SentimentConfig:
    base_model: str = "distilbert-base-uncased"
    max_length: int = 128
    batch_size: int = 32
    learning_rate: float = 2e-5
    num_epochs: int = 4
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    seed: int = 42
    train_path: str = "data/processed/sentiment_train.parquet"
    val_path: str = "data/processed/sentiment_val.parquet"
    output_dir: str = "checkpoints/discourse-sentiment"
    use_wandb: bool = False
    axes: list[str] = field(default_factory=lambda: list(AXES))

    @classmethod
    def from_yaml(cls, path: Path | str) -> "SentimentConfig":
        with open(path) as f:
            return cls(**yaml.safe_load(f))


class SentimentDataset(Dataset):
    def __init__(
        self,
        df: pd.DataFrame,
        tokenizer: PreTrainedTokenizerBase,
        max_length: int,
        axes: list[str],
    ) -> None:
        self.texts = df["text"].tolist()
        self.labels = df[axes].to_numpy(dtype=np.float32)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        enc = self.tokenizer(
            self.texts[idx],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.from_numpy(self.labels[idx]),
        }


class SentimentModel(nn.Module):
    """Shared encoder + four sigmoid regression heads."""

    def __init__(self, base_model: str, num_axes: int = 4) -> None:
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model)
        hidden = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        self.heads = nn.ModuleList([nn.Linear(hidden, 1) for _ in range(num_axes)])

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = self.dropout(out.last_hidden_state[:, 0, :])
        return torch.cat([torch.sigmoid(h(cls)) for h in self.heads], dim=-1)


def train_model(cfg: SentimentConfig) -> None:
    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info("Device: %s", device)

    train_df = pd.read_parquet(cfg.train_path)
    val_df = pd.read_parquet(cfg.val_path)
    log.info("Train: %d  Val: %d", len(train_df), len(val_df))

    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
    train_dl = DataLoader(
        SentimentDataset(train_df, tokenizer, cfg.max_length, cfg.axes),
        batch_size=cfg.batch_size, shuffle=True,
    )
    val_dl = DataLoader(
        SentimentDataset(val_df, tokenizer, cfg.max_length, cfg.axes),
        batch_size=cfg.batch_size,
    )

    model = SentimentModel(cfg.base_model, num_axes=len(cfg.axes)).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
    )
    total_steps = len(train_dl) * cfg.num_epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, int(total_steps * cfg.warmup_ratio), total_steps
    )
    loss_fn = nn.MSELoss()

    for epoch in range(cfg.num_epochs):
        model.train()
        train_loss = 0.0
        for batch in train_dl:
            optimizer.zero_grad()
            preds = model(
                batch["input_ids"].to(device),
                batch["attention_mask"].to(device),
            )
            loss = loss_fn(preds, batch["labels"].to(device))
            loss.backward()
            optimizer.step()
            scheduler.step()
            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_dl:
                preds = model(
                    batch["input_ids"].to(device),
                    batch["attention_mask"].to(device),
                )
                val_loss += loss_fn(preds, batch["labels"].to(device)).item()

        log.info(
            "Epoch %d/%d train=%.4f val=%.4f",
            epoch + 1, cfg.num_epochs,
            train_loss / len(train_dl),
            val_loss / len(val_dl),
        )

    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "model.pt")
    tokenizer.save_pretrained(out_dir)
    (out_dir / "config.json").write_text(json.dumps(cfg.__dict__, indent=2))
    log.info("Saved checkpoint to %s", out_dir)


def load_model(checkpoint_dir: Path | str):
    checkpoint_dir = Path(checkpoint_dir)
    cfg_data = json.loads((checkpoint_dir / "config.json").read_text())
    cfg = SentimentConfig(**cfg_data)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
    model = SentimentModel(cfg.base_model, num_axes=len(cfg.axes))
    model.load_state_dict(torch.load(checkpoint_dir / "model.pt", map_location="cpu"))
    model.eval()
    return model, tokenizer, cfg


def predict_sentiment(text: str, model, tokenizer, cfg) -> dict[str, float]:
    enc = tokenizer(
        text,
        max_length=cfg.max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    with torch.no_grad():
        out = model(enc["input_ids"], enc["attention_mask"]).squeeze(0).numpy()
    return {axis: float(score) for axis, score in zip(cfg.axes, out)}


@app.command()
def train(config: Path = typer.Option("configs/sentiment.yaml", "--config", "-c")) -> None:
    """Fine-tune the discourse sentiment classifier."""
    cfg = SentimentConfig.from_yaml(config)
    train_model(cfg)


@app.command()
def predict(
    text: str = typer.Option(..., "--text", "-t"),
    checkpoint: Path = typer.Option(None, "--checkpoint"),
) -> None:
    """Score a single piece of text on all four discourse axes."""
    settings = get_settings()
    ckpt = checkpoint or Path(settings.checkpoints_dir) / "discourse-sentiment"
    model, tokenizer, cfg = load_model(ckpt)
    print(json.dumps(predict_sentiment(text, model, tokenizer, cfg), indent=2))


if __name__ == "__main__":
    app()
