"""Stance classifier for immigration legislation.

Fine-tunes DistilBERT (or any compatible HuggingFace model) on hand-labeled
legal text to score four orthogonal axes:

    1. restrictiveness    (open ↔ closed borders)
    2. enforcement        (low ↔ high enforcement intensity)
    3. legalization       (pro-amnesty ↔ pro-removal)
    4. humanitarian       (security framing ↔ humanitarian framing)

Each axis is a regression target in [0, 1]. The model is multi-output: one
shared encoder, four regression heads.

CLI:
    python -m migration_atlas.models.stance_classifier train --config configs/stance.yaml
    python -m migration_atlas.models.stance_classifier predict --text "Section 287(g) authorizes..."
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
app = typer.Typer(help="Stance classifier CLI")

AXES = ["restrictiveness", "enforcement", "legalization", "humanitarian"]


# ============================================================
# Config
# ============================================================
@dataclass
class StanceConfig:
    """Training + inference config for the stance classifier."""

    base_model: str = "distilbert-base-uncased"
    max_length: int = 256
    batch_size: int = 16
    learning_rate: float = 2e-5
    num_epochs: int = 4
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    seed: int = 42
    train_path: str = "data/processed/stance_train.parquet"
    val_path: str = "data/processed/stance_val.parquet"
    output_dir: str = "checkpoints/stance-distilbert"
    use_wandb: bool = False
    axes: list[str] = field(default_factory=lambda: list(AXES))

    @classmethod
    def from_yaml(cls, path: Path | str) -> "StanceConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


# ============================================================
# Dataset
# ============================================================
class StanceDataset(Dataset):
    """Simple dataset for (text, [r, e, l, h]) pairs."""

    def __init__(self, df: pd.DataFrame, tokenizer: PreTrainedTokenizerBase,
                 max_length: int, axes: list[str]) -> None:
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


# ============================================================
# Model: shared encoder + 4 regression heads
# ============================================================
class StanceModel(nn.Module):
    """Multi-output stance regressor."""

    def __init__(self, base_model: str, num_axes: int = 4) -> None:
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model)
        hidden = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        # One linear head per axis. Sigmoid keeps outputs in [0, 1].
        self.heads = nn.ModuleList([nn.Linear(hidden, 1) for _ in range(num_axes)])

    def forward(self, input_ids: torch.Tensor,
                attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # Use the [CLS] / first-token representation
        cls = out.last_hidden_state[:, 0, :]
        cls = self.dropout(cls)
        scores = torch.cat([torch.sigmoid(h(cls)) for h in self.heads], dim=-1)
        return scores  # shape: (batch, num_axes)


# ============================================================
# Training
# ============================================================
def _setup_wandb(cfg: StanceConfig) -> Any:
    if not cfg.use_wandb:
        return None
    try:
        import wandb
    except ImportError:
        log.warning("wandb requested but not installed; skipping")
        return None
    settings = get_settings()
    if not settings.wandb_api_key:
        log.warning("WANDB_API_KEY not set; skipping wandb")
        return None
    wandb.init(
        project=settings.wandb_project,
        entity=settings.wandb_entity,
        config=cfg.__dict__,
        name="stance-distilbert",
    )
    return wandb


def train_model(cfg: StanceConfig) -> None:
    """Run the training loop."""
    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)
    settings = get_settings()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info("Device: %s", device)

    train_df = pd.read_parquet(cfg.train_path)
    val_df = pd.read_parquet(cfg.val_path)
    log.info("Train: %d  Val: %d", len(train_df), len(val_df))

    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
    train_ds = StanceDataset(train_df, tokenizer, cfg.max_length, cfg.axes)
    val_ds = StanceDataset(val_df, tokenizer, cfg.max_length, cfg.axes)
    train_dl = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=cfg.batch_size)

    model = StanceModel(cfg.base_model, num_axes=len(cfg.axes)).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
    )
    total_steps = len(train_dl) * cfg.num_epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, int(total_steps * cfg.warmup_ratio), total_steps
    )
    loss_fn = nn.MSELoss()

    wb = _setup_wandb(cfg)

    for epoch in range(cfg.num_epochs):
        model.train()
        train_loss = 0.0
        for batch in train_dl:
            optimizer.zero_grad()
            preds = model(batch["input_ids"].to(device), batch["attention_mask"].to(device))
            loss = loss_fn(preds, batch["labels"].to(device))
            loss.backward()
            optimizer.step()
            scheduler.step()
            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0.0
        per_axis_mae = np.zeros(len(cfg.axes))
        with torch.no_grad():
            for batch in val_dl:
                preds = model(batch["input_ids"].to(device), batch["attention_mask"].to(device))
                labels = batch["labels"].to(device)
                val_loss += loss_fn(preds, labels).item()
                per_axis_mae += (preds - labels).abs().mean(dim=0).cpu().numpy() * len(labels)
        per_axis_mae /= len(val_ds)

        log.info(
            "Epoch %d/%d  train_loss=%.4f  val_loss=%.4f  MAE: %s",
            epoch + 1, cfg.num_epochs,
            train_loss / len(train_dl),
            val_loss / len(val_dl),
            ", ".join(f"{a}={m:.3f}" for a, m in zip(cfg.axes, per_axis_mae)),
        )
        if wb:
            wb.log({"epoch": epoch + 1,
                    "train_loss": train_loss / len(train_dl),
                    "val_loss": val_loss / len(val_dl),
                    **{f"mae/{a}": m for a, m in zip(cfg.axes, per_axis_mae)}})

    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "model.pt")
    tokenizer.save_pretrained(out_dir)
    (out_dir / "config.json").write_text(json.dumps(cfg.__dict__, indent=2))
    log.info("Saved checkpoint to %s", out_dir)


# ============================================================
# Inference
# ============================================================
def load_model(checkpoint_dir: Path | str) -> tuple[StanceModel, PreTrainedTokenizerBase, StanceConfig]:
    """Load a trained checkpoint for inference."""
    checkpoint_dir = Path(checkpoint_dir)
    cfg_data = json.loads((checkpoint_dir / "config.json").read_text())
    cfg = StanceConfig(**cfg_data)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir)
    model = StanceModel(cfg.base_model, num_axes=len(cfg.axes))
    model.load_state_dict(torch.load(checkpoint_dir / "model.pt", map_location="cpu"))
    model.eval()
    return model, tokenizer, cfg


def predict_stance(text: str, model: StanceModel, tokenizer: PreTrainedTokenizerBase,
                   cfg: StanceConfig) -> dict[str, float]:
    """Score a single piece of legal text on all four axes."""
    enc = tokenizer(text, max_length=cfg.max_length, padding="max_length",
                    truncation=True, return_tensors="pt")
    with torch.no_grad():
        out = model(enc["input_ids"], enc["attention_mask"]).squeeze(0).numpy()
    return {axis: float(score) for axis, score in zip(cfg.axes, out)}


# ============================================================
# CLI
# ============================================================
@app.command()
def train(config: Path = typer.Option("configs/stance.yaml", "--config", "-c")) -> None:
    """Fine-tune the stance classifier."""
    cfg = StanceConfig.from_yaml(config)
    train_model(cfg)


@app.command()
def predict(
    text: str = typer.Option(..., "--text", "-t"),
    checkpoint: Path = typer.Option(None, "--checkpoint"),
) -> None:
    """Score a single piece of text."""
    settings = get_settings()
    ckpt = checkpoint or settings.stance_model_path
    model, tokenizer, cfg = load_model(ckpt)
    scores = predict_stance(text, model, tokenizer, cfg)
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    app()
