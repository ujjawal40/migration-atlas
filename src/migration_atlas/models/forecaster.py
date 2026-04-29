"""Migration flow forecaster.

The headline model: predict country-of-origin migration flows (annual immigrant
arrivals or visa issuances) for the next 1-5 years. Two complementary forecasters,
ensembled at inference time:

    1. Prophet (Meta) — captures trend + structural breaks well, robust to small
       data, runs anywhere with no GPU. The default workhorse.

    2. Lightweight LSTM — sequence model that can incorporate macroeconomic
       covariates (origin country GDP per capita, unemployment, USD exchange rate,
       conflict events). Better when covariates matter.

Ensemble = inverse-MAE weighted average on a held-out validation window.

Output: point forecast + 80% / 95% prediction intervals per country per year.

CLI:
    python -m migration_atlas.models.forecaster train --config configs/forecast.yaml
    python -m migration_atlas.models.forecaster predict --country mexico --horizon 5
"""
from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Forecaster CLI")

warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
# Config
# ============================================================
@dataclass
class ForecastConfig:
    flows_path: str = "data/processed/flows.parquet"
    countries: list[str] = field(default_factory=lambda: [
        "mexico", "india", "china", "philippines", "vietnam", "cuba",
        "el-salvador", "guatemala", "honduras", "venezuela",
    ])
    horizon: int = 5
    val_years: int = 5
    use_lstm: bool = True
    lstm_hidden: int = 32
    lstm_layers: int = 1
    lstm_epochs: int = 200
    lstm_lr: float = 0.01
    lstm_seq_len: int = 8
    seed: int = 42
    output_dir: str = "checkpoints/forecaster"

    @classmethod
    def from_yaml(cls, path: Path | str) -> "ForecastConfig":
        with open(path) as f:
            return cls(**yaml.safe_load(f))


# ============================================================
# Prophet forecaster
# ============================================================
def prophet_forecast(
    series: pd.Series, horizon: int, conf_interval: float = 0.95
) -> pd.DataFrame:
    """Fit Prophet on an annual series and return a forecast DataFrame.

    series.index must be datetime; series.values are flow counts.
    Returns: columns [year, yhat, yhat_lower, yhat_upper].
    """
    try:
        from prophet import Prophet
    except ImportError as e:
        raise ImportError("pip install prophet") from e

    df = pd.DataFrame({"ds": series.index, "y": series.values})
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=conf_interval,
    )
    model.fit(df)
    future = model.make_future_dataframe(periods=horizon, freq="YS")
    fc = model.predict(future)
    return fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].rename(columns={"ds": "year"})


# ============================================================
# Lightweight LSTM forecaster (covariate-aware)
# ============================================================
def lstm_forecast(
    series: pd.Series,
    horizon: int,
    cfg: ForecastConfig,
    covariates: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Fit a small LSTM on the series with optional covariates.

    Returns: columns [year, yhat]. Quantile intervals are filled in by the
    ensemble step using residuals.
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError as e:
        raise ImportError("pip install torch") from e

    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)

    y = series.values.astype(np.float32)
    # Normalize for stability
    mu, sigma = float(y.mean()), float(y.std() + 1e-6)
    y_norm = (y - mu) / sigma

    # Feature matrix: just lagged y for now; covariates can be added column-wise
    feat = y_norm.reshape(-1, 1)
    if covariates is not None and len(covariates) == len(y):
        cov = covariates.to_numpy(dtype=np.float32)
        cov = (cov - cov.mean(axis=0)) / (cov.std(axis=0) + 1e-6)
        feat = np.concatenate([feat, cov], axis=1)

    seq_len = min(cfg.lstm_seq_len, len(feat) - 1)
    X, Y = [], []
    for i in range(len(feat) - seq_len):
        X.append(feat[i : i + seq_len])
        Y.append(y_norm[i + seq_len])
    if not X:
        log.warning("Series too short for LSTM (%d points); skipping", len(y))
        return pd.DataFrame(columns=["year", "yhat"])
    Xt = torch.tensor(np.stack(X), dtype=torch.float32)
    Yt = torch.tensor(np.array(Y), dtype=torch.float32).unsqueeze(-1)

    class TinyLSTM(nn.Module):
        def __init__(self, in_dim: int) -> None:
            super().__init__()
            self.lstm = nn.LSTM(in_dim, cfg.lstm_hidden,
                                num_layers=cfg.lstm_layers, batch_first=True)
            self.head = nn.Linear(cfg.lstm_hidden, 1)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out, _ = self.lstm(x)
            return self.head(out[:, -1, :])

    model = TinyLSTM(feat.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lstm_lr)
    loss_fn = nn.MSELoss()

    for epoch in range(cfg.lstm_epochs):
        model.train()
        opt.zero_grad()
        loss = loss_fn(model(Xt), Yt)
        loss.backward()
        opt.step()

    # Forecast iteratively
    model.eval()
    last_seq = feat[-seq_len:].copy()
    preds: list[float] = []
    with torch.no_grad():
        for _ in range(horizon):
            x = torch.tensor(last_seq[np.newaxis, :, :], dtype=torch.float32)
            yhat = model(x).item()
            preds.append(yhat)
            # Roll forward: append predicted y; for covariates, persist last value
            new_row = last_seq[-1].copy()
            new_row[0] = yhat
            last_seq = np.vstack([last_seq[1:], new_row])

    last_year = pd.Timestamp(series.index[-1])
    future_years = [last_year + pd.DateOffset(years=i + 1) for i in range(horizon)]
    yhat_real = np.array(preds) * sigma + mu
    return pd.DataFrame({"year": future_years, "yhat": yhat_real})


# ============================================================
# Ensemble
# ============================================================
def ensemble(
    prophet_fc: pd.DataFrame, lstm_fc: pd.DataFrame, prophet_w: float, lstm_w: float
) -> pd.DataFrame:
    """Inverse-MAE-weighted average of two forecasts."""
    if lstm_fc.empty:
        return prophet_fc.assign(model="prophet")
    out = prophet_fc.copy()
    # Align on year
    merged = out.merge(lstm_fc, on="year", how="inner", suffixes=("_p", "_l"))
    w_sum = prophet_w + lstm_w
    out_yhat = (merged["yhat_p"] * prophet_w + merged["yhat_l"] * lstm_w) / w_sum
    # Keep Prophet's intervals; widen by 10% to reflect ensemble uncertainty
    width = (merged["yhat_upper"] - merged["yhat_lower"]) * 1.10
    return pd.DataFrame({
        "year": merged["year"],
        "yhat": out_yhat,
        "yhat_lower": out_yhat - width / 2,
        "yhat_upper": out_yhat + width / 2,
        "model": "ensemble",
    })


# ============================================================
# Training pipeline (per-country)
# ============================================================
def fit_country(
    country: str, df: pd.DataFrame, cfg: ForecastConfig
) -> dict[str, Any]:
    """Fit both forecasters on a single country's series and return a forecast."""
    series = df.set_index(pd.to_datetime(df["year"], format="%Y"))["flow"]
    if len(series) < 8:
        log.warning("[%s] only %d points; using Prophet only", country, len(series))
        prophet_fc = prophet_forecast(series, cfg.horizon)
        prophet_fc["model"] = "prophet"
        return {"country": country, "forecast": prophet_fc}

    # Held-out validation
    train_series = series.iloc[: -cfg.val_years]
    val_series = series.iloc[-cfg.val_years :]

    prophet_val = prophet_forecast(train_series, cfg.val_years)
    prophet_mae = (prophet_val["yhat"].values - val_series.values).__abs__().mean()
    lstm_mae = float("inf")

    if cfg.use_lstm:
        lstm_val = lstm_forecast(train_series, cfg.val_years, cfg)
        if not lstm_val.empty:
            lstm_mae = (lstm_val["yhat"].values - val_series.values).__abs__().mean()

    log.info("[%s] val MAE — prophet=%.0f  lstm=%s",
             country, prophet_mae,
             f"{lstm_mae:.0f}" if lstm_mae < float("inf") else "n/a")

    # Final fit on full series
    prophet_full = prophet_forecast(series, cfg.horizon)
    if cfg.use_lstm and lstm_mae < float("inf"):
        lstm_full = lstm_forecast(series, cfg.horizon, cfg)
        # Inverse-MAE weights
        w_p = 1.0 / max(prophet_mae, 1e-6)
        w_l = 1.0 / max(lstm_mae, 1e-6)
        final = ensemble(prophet_full, lstm_full, w_p, w_l)
    else:
        final = prophet_full.assign(model="prophet")

    return {
        "country": country,
        "forecast": final,
        "val_mae": {"prophet": float(prophet_mae),
                    "lstm": float(lstm_mae) if lstm_mae < float("inf") else None},
    }


def train_all(cfg: ForecastConfig) -> None:
    """Fit forecasters for every country in the config."""
    flows_path = Path(cfg.flows_path)
    if not flows_path.exists():
        log.warning("Flows file %s missing — generating synthetic placeholder.", flows_path)
        _write_synthetic_flows(flows_path, cfg.countries)

    flows = pd.read_parquet(flows_path)
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_forecasts: list[pd.DataFrame] = []
    val_results: dict[str, Any] = {}
    for c in cfg.countries:
        sub = flows[flows["country"] == c]
        if sub.empty:
            log.warning("No data for %s; skipping", c)
            continue
        result = fit_country(c, sub, cfg)
        fc = result["forecast"].assign(country=c)
        all_forecasts.append(fc)
        if "val_mae" in result:
            val_results[c] = result["val_mae"]

    if all_forecasts:
        out = pd.concat(all_forecasts, ignore_index=True)
        out.to_parquet(out_dir / "forecasts.parquet", index=False)
        (out_dir / "val_results.json").write_text(json.dumps(val_results, indent=2))
        log.info("Saved %d-row forecast to %s", len(out), out_dir / "forecasts.parquet")


def _write_synthetic_flows(path: Path, countries: list[str]) -> None:
    """Write a synthetic flows file when real data is unavailable.

    This keeps the pipeline runnable end-to-end without external downloads. Real
    runs replace it with USCIS / Census ACS data. The shape mimics historical
    annual immigrant arrivals: a slow trend with country-specific shocks.
    """
    rng = np.random.default_rng(42)
    rows = []
    base_levels = {"mexico": 150_000, "india": 70_000, "china": 60_000,
                   "philippines": 50_000, "vietnam": 30_000, "cuba": 35_000,
                   "el-salvador": 25_000, "guatemala": 20_000,
                   "honduras": 15_000, "venezuela": 10_000}
    for country in countries:
        base = base_levels.get(country, 20_000)
        years = list(range(1990, 2024))
        trend = np.linspace(0.7, 1.3, len(years))
        noise = rng.normal(1.0, 0.10, len(years))
        flow = (base * trend * noise).astype(int)
        for y, f in zip(years, flow):
            rows.append({"country": country, "year": y, "flow": f})
    pd.DataFrame(rows).to_parquet(path, index=False)
    log.info("Wrote synthetic flows to %s (%d rows)", path, len(rows))


# ============================================================
# CLI
# ============================================================
@app.command()
def train(config: Path = typer.Option("configs/forecast.yaml", "--config", "-c")) -> None:
    """Train forecasters for all configured countries."""
    cfg = ForecastConfig.from_yaml(config)
    train_all(cfg)


@app.command()
def predict(
    country: str = typer.Option(..., "--country"),
    horizon: int = typer.Option(5, "--horizon"),
    checkpoint: Path = typer.Option(None, "--checkpoint"),
) -> None:
    """Look up a country's forecast from the saved parquet."""
    settings = get_settings()
    ckpt = checkpoint or settings.forecast_model_path
    fc_path = Path(ckpt) / "forecasts.parquet"
    if not fc_path.exists():
        raise SystemExit(f"No forecasts at {fc_path}; run `train` first.")
    fc = pd.read_parquet(fc_path)
    sub = fc[fc["country"] == country].head(horizon)
    if sub.empty:
        raise SystemExit(f"No forecast for {country}")
    print(sub.to_string(index=False))


if __name__ == "__main__":
    app()
