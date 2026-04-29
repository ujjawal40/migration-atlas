# Flow Forecaster

Predicts country-of-origin migration flows for the next 1–5 years. The headline ML model in the project — and the one most directly useful to policymakers and researchers.

## Approach

A two-model ensemble:

1. **Prophet** — robust to structural breaks (1965 INA, 1980 Mariel, 2014 Venezuela collapse), runs anywhere with no GPU. The default workhorse.
2. **Lightweight LSTM** — sequence model that can incorporate macroeconomic covariates (origin-country GDP per capita, unemployment, USD exchange rate, conflict events). Better when covariates matter.

Ensemble weight = inverse-MAE on a held-out validation window (the last `val_years` of the series).

```python
w_prophet = 1.0 / mae_prophet
w_lstm    = 1.0 / mae_lstm
yhat = (w_prophet * yhat_prophet + w_lstm * yhat_lstm) / (w_prophet + w_lstm)
```

## Why an ensemble

Migration time series are nasty: small samples (annual data, ~30 points per country), heavy structural breaks (a single law or war can quintuple a flow), high heteroskedasticity. Prophet handles trend + structural breaks gracefully. LSTM captures interactions with macroeconomic covariates Prophet ignores. Neither dominates across all countries — Mexico's series benefits from covariates; Vietnam's is dominated by the 1975 break that Prophet handles natively.

## Training

```bash
make train-forecast
```

CPU is fine — training all 10 countries takes ~5 minutes locally. Use Colab if you want to iterate on hyperparameters quickly.

## Output

A Parquet file at `checkpoints/forecaster/forecasts.parquet`:

| year | country | yhat | yhat_lower | yhat_upper | model |
|------|---------|------|------------|------------|-------|
| 2025 | mexico | 165200 | 142000 | 188400 | ensemble |
| 2026 | mexico | 167900 | 140100 | 195700 | ensemble |
| ... | ... | ... | ... | ... | ... |

## Honest caveats

- **5-year horizon is the practical limit.** Beyond that, prediction intervals are too wide to be useful.
- **Structural breaks are unforecastable.** The model cannot predict the next civil war or visa policy reform. Forecasts assume the current policy environment continues.
- **Synthetic placeholder.** The repo ships with a synthetic flows dataset so the pipeline runs end-to-end. Replace with USCIS / Census ACS data for real results.
