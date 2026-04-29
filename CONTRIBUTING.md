# Contributing

Thanks for the interest. Migration Atlas is a portfolio / academic project, but PRs are welcome — particularly for adding data sources, improving model performance, or extending the graph schema.

## Dev setup

```bash
git clone https://github.com/YOUR_USERNAME/migration-atlas.git
cd migration-atlas
make setup
```

## Before submitting a PR

```bash
make format       # auto-fix formatting
make check        # lint + type-check + tests
```

CI runs the same checks on every PR.

## Code style

- **Black** for formatting (line length 100)
- **Ruff** for linting
- **Mypy** in warn-mode for now (will tighten as the codebase stabilizes)
- Google-style docstrings on public functions

## Adding a new data source

1. Add a per-source ingester in `src/migration_atlas/data/`.
2. Document the source in `docs/data-sources.md` and `data/README.md`.
3. Add a processed-output stage in `src/migration_atlas/data/process.py`.
4. Update the graph builder in `src/migration_atlas/graph/build.py` if the source contributes new nodes or edges.
5. Add a smoke test in `tests/`.

## Adding a new model

1. Create `src/migration_atlas/models/<name>.py` following the pattern of the existing models (config dataclass, train function, predict function, Typer CLI).
2. Add a config YAML in `configs/<name>.yaml`.
3. Wire it into the API's `/query` endpoint if applicable.
4. Document it in `docs/models/<name>.md`.
5. Add tests.

## Reporting issues

Use the GitHub issue tracker. For data quality issues, please cite the specific source row and the expected value.
