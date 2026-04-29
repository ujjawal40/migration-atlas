# Models overview

Migration Atlas ships with four trained ML models. Each is independently runnable and the API layer exposes them through a unified `/query` endpoint.

| Model | Stack | Compute | Training time |
|-------|-------|---------|---------------|
| [Stance Classifier](stance.md) | DistilBERT + 4 regression heads | Colab T4 | ~30 min |
| [Research RAG](rag.md) | sentence-transformers + ChromaDB | CPU | ~10 min |
| [Flow Forecaster](forecaster.md) | Prophet + LSTM ensemble | CPU | ~5 min |
| [Graph Embeddings](embeddings.md) | Node2Vec | CPU | ~2 min |

All four are designed to run on free Colab + a laptop. Pre-trained checkpoints are published to HuggingFace Hub so you don't have to retrain from scratch.
