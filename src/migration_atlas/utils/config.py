"""Centralized configuration loaded from environment + .env file."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Runtime configuration for Migration Atlas.

    Values are loaded from environment variables, falling back to .env, falling back
    to the defaults below. Anything sensitive (API keys) is never logged.
    """

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ----- Paths -----
    repo_root: Path = REPO_ROOT
    data_dir: Path = REPO_ROOT / "data"
    raw_dir: Path = REPO_ROOT / "data" / "raw"
    processed_dir: Path = REPO_ROOT / "data" / "processed"
    corpus_dir: Path = REPO_ROOT / "data" / "corpus"
    checkpoints_dir: Path = REPO_ROOT / "checkpoints"

    # ----- API keys -----
    anthropic_api_key: str | None = None
    wandb_api_key: str | None = None
    wandb_project: str = "migration-atlas"
    wandb_entity: str | None = None

    # ----- Graph backend -----
    graph_backend: Literal["networkx", "neo4j"] = "networkx"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "atlasdev"

    # ----- App -----
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ----- Model paths -----
    stance_model_path: Path = Field(default=REPO_ROOT / "checkpoints" / "stance-distilbert")
    rag_index_path: Path = Field(default=REPO_ROOT / "chroma_db")
    forecast_model_path: Path = Field(default=REPO_ROOT / "checkpoints" / "forecaster")
    embeddings_path: Path = Field(default=REPO_ROOT / "checkpoints" / "node2vec.kv")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def ensure_dirs(self) -> None:
        """Create directories that should exist if missing."""
        for p in [self.data_dir, self.raw_dir, self.processed_dir,
                  self.corpus_dir, self.checkpoints_dir]:
            p.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance. Use this everywhere."""
    return Settings()
