"""Top-level CLI: `migration-atlas <command>`.

Wraps each subsystem's CLI under a unified namespace. Example:
    migration-atlas data download
    migration-atlas graph build
    migration-atlas models train-stance
    migration-atlas models predict --text "..."
"""
from __future__ import annotations

import typer

from migration_atlas import __version__

app = typer.Typer(help="Migration Atlas — knowledge graph & ML toolkit", no_args_is_help=True)


@app.callback()
def main() -> None:
    """Migration Atlas command-line interface."""


@app.command()
def version() -> None:
    """Print the package version."""
    print(f"migration-atlas v{__version__}")


# Sub-commands wire to module CLIs lazily so importing the top-level CLI
# doesn't pay the cost of pulling in torch / chromadb.
@app.command()
def graph(
    action: str = typer.Argument(..., help="Action: build"),
) -> None:
    """Graph operations."""
    if action == "build":
        from migration_atlas.graph.build import main as build_main
        build_main()
    else:
        raise typer.BadParameter(f"Unknown action: {action}")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    """Run the FastAPI backend."""
    import uvicorn
    uvicorn.run("migration_atlas.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()
