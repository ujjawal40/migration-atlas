# Data

This directory is .gitignored except for `README.md` and `.gitkeep` files. Run `make data` to populate it.

## Layout

```
data/
├── raw/            ← Downloaded source files (gitignored)
│   ├── census_acs/
│   ├── uscis_yearbook/
│   ├── mpi_tabulations/
│   ├── bls_lfs/
│   └── oecd_dioc/
├── processed/      ← Harmonized parquet outputs
│   ├── foreign_born_by_country.parquet
│   ├── visa_issuance.parquet
│   ├── flows.parquet
│   ├── labor_by_industry.parquet
│   └── chunks.parquet
└── corpus/         ← Research papers for RAG (PDF/MD/TXT)
```

## Where to put research papers

Drop PDFs, Markdown, or plain-text research papers into `data/corpus/`. The RAG indexer picks up everything recursively. Suggested papers are listed in [the RAG model docs](../docs/models/rag.md).

## Licensing notes

Each source has its own license. Public-domain U.S. government works (Census, USCIS, BLS) are unrestricted. MPI is free for non-commercial use. OECD has its own terms. Always cite sources in any analysis you publish.
