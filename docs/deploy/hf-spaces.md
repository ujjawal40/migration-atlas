# Deploy backend to HuggingFace Spaces

HuggingFace Spaces is the right home for the backend: free CPU tier, free T4 burst, native ML hosting, and it's a recognizable signal on a portfolio.

## Two options

### Option A — Docker space (recommended)

Push the repo's `Dockerfile` directly. HF Spaces runs it.

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space):
   - **SDK**: Docker
   - **Visibility**: Public
   - **Hardware**: CPU basic (free) is enough for inference; upgrade to T4 if running stance training there.

2. Add the Space as a remote:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/migration-atlas
   git push hf main
   ```

3. The Dockerfile already exposes port `7860` for HF (override default 8000):
   ```dockerfile
   ENV PORT=7860
   CMD ["uvicorn", "migration_atlas.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

### Option B — Gradio space (simplest for a demo)

Wrap the FastAPI endpoints in a Gradio interface. Good for low-effort demos but loses the React frontend.

## Secrets

Set these in **Settings → Variables and secrets** on the Space:

- `ANTHROPIC_API_KEY` — for RAG synthesis (optional)
- `LOG_LEVEL` — defaults to `INFO`

## Persisting model checkpoints

The free CPU tier resets on each deploy. Store checkpoints on the **HuggingFace Hub** as a model repo and load them at startup:

```python
from huggingface_hub import snapshot_download
snapshot_download("YOUR_USERNAME/migration-atlas-stance",
                  local_dir="checkpoints/stance-distilbert")
```

This decouples model weights from the Space deploy.
