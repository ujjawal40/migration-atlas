# Research Paper RAG

Retrieval-augmented generation over the immigration economics literature. Lets users ask questions like *"What's the wage effect of low-skill immigration?"* and get cited answers from Borjas (2003), Card (2001), Ottaviano & Peri (2012), and similar.

## Pipeline

1. **Ingestion** — PDFs, Markdown, and TXT files in `data/corpus/` are extracted (pypdf for PDFs).
2. **Chunking** — recursive character splitter, ~512 tokens with 64-token overlap, breaking on sentence boundaries.
3. **Embedding** — sentence-transformers (`all-MiniLM-L6-v2` by default; 80MB, runs on CPU).
4. **Storage** — ChromaDB persistent index in `chroma_db/`.
5. **Retrieval** — top-k cosine-similarity search at query time.
6. **Synthesis (optional)** — Anthropic Claude API generates a cited natural-language answer. Without an API key, the system returns ranked passages.

## Suggested corpus

Drop these into `data/corpus/`:

- Borjas, *The Labor Demand Curve Is Downward Sloping* (QJE 2003)
- Card, *Immigrant Inflows, Native Outflows* (JOLE 2001)
- Ottaviano & Peri, *Rethinking the Effect of Immigration on Wages* (JEEA 2012)
- National Academies, *The Economic and Fiscal Consequences of Immigration* (2017)
- Cato Institute fiscal impact white papers
- Migration Policy Institute research briefs
- Pew Research immigration reports
- NBER working papers on migration economics
- Federal Reserve regional bank reports on migration & wages

Most of these are openly available; check the licensing notes in `data/corpus/README.md`.

## Running

```bash
# After dropping papers into data/corpus/
make rag-index

# Then query
python -m migration_atlas.models.rag query \
    --q "What is the wage effect of low-skill immigration?"
```

## When synthesis is on

With `ANTHROPIC_API_KEY` set and `use_synthesis: true` in `configs/rag.yaml`, the system returns answers like:

> The literature is genuinely split. Borjas [1] argues that immigration of high-school dropouts reduced wages of native dropouts by 8.9% over 1980–2000 using a national skill-cell approach. Ottaviano and Peri [2] find substantially smaller effects (around -1.1%) using a more flexible CES production model that allows for imperfect substitution between natives and immigrants within skill cells. The disagreement turns on whether immigrants and natives are treated as perfect substitutes within a skill cell.
>
> Sources: [1] Borjas (2003); [2] Ottaviano & Peri (2012).
