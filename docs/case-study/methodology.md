# Methodology

This section describes the design choices that determine what the system can and cannot say. Each choice is explained on its own terms, then situated against alternatives that were considered and rejected.

## Data ingestion and harmonization

Six primary sources feed the data layer:

1. **U.S. Census American Community Survey (ACS).** Tables B05002 (place of birth × citizenship), B05006 (place of birth for the foreign-born), and B05007 (place of birth × year of entry). The 1-year ACS for current estimates; the 5-year ACS for state and county granularity.
2. **USCIS / Office of Homeland Security Statistics Yearbook.** Annual visa issuance, adjustment-of-status, and naturalization tables. The authoritative source for legal flows.
3. **Migration Policy Institute Data Hub.** Pre-aggregated tabulations including historical series back to 1850.
4. **Pew Research Center.** Residual-method estimates of the unauthorized population and periodic analytical reports.
5. **Bureau of Labor Statistics.** Foreign-born labor force tabulations, primarily Table A-7 of the CPS supplement.
6. **OECD Database on Immigrants in OECD Countries (DIOC).** Cross-destination immigrant stocks, used to compute brain-drain intensity from the origin perspective.

The principal harmonization decisions:

- *Foreign-born* is defined as born outside the U.S. to non-U.S.-citizen parents, aligning with the ACS definition. Puerto Rico and other U.S. territories are excluded.
- *Country of origin* is country of birth, not country of citizenship. This matters for groups such as ethnic Chinese born in Vietnam, who are coded as Vietnamese-origin in this project.
- *Year vintage* is the most recent available, currently ACS 2023.
- *ISO codes* are normalized to ISO 3166-1 alpha-3. Taiwan is kept separate from China.

Where two sources disagree (e.g., USCIS legal-flow counts and ACS-based stock estimates implied flows), the project does not pick a winner; both quantities are kept and the methodological context is preserved on the relevant graph edge.

## Graph schema

The schema is intentionally small. Five node kinds and eight edge kinds, defined as Pydantic models in `migration_atlas.graph.schema`:

| Element | Cardinality | Examples |
|---------|------------|----------|
| `country` node | 22 in seed | mexico, india, china, vietnam, cuba, el-salvador |
| `visa` node | 9 in seed | h-1b, f-1, eb-5, family-based, tps, refugee, tn |
| `law` node | 8 in seed | ina-1965, irca-1986, immigration-act-1990, daca-2012 |
| `industry` node | 5 in seed | tech, healthcare, construction, agriculture, hospitality |
| `region` node | not yet populated | (state-level expansion in Phase 3) |
| `uses-visa` edge | country → visa | A country whose nationals heavily use this visa |
| `enables` edge | law → country / visa | A law that materially expanded a corridor |
| `restricts` edge | law → country | A law that closed or reduced a corridor |
| `creates` edge | law → visa | A law that established a visa category |
| `legalized` edge | law → country | A law that granted retroactive legal status |
| `works-in` edge | country → industry | An industry where the origin's foreign-born are concentrated |
| `settles-in` edge | country → region | (state-level concentration; sparse in seed) |
| `amends` edge | law → law | A law that modified an earlier law |

All node IDs are lowercase, hyphenated, and stable. The schema is the contract; downstream code does not introduce new edge types ad hoc.

The seed graph contains 44 nodes and 53 edges. It is hand-curated from the literature reviewed in the previous section and serves two purposes: it is the single source of truth for the prototype, and it is the validation set against which Phase 3 ETL will be checked. When the ETL output is loaded, the project asserts that every seed edge is reproduced; new edges discovered by the data are reviewed manually before they are merged into the canonical graph.

## Why not a graph database first

The default graph backend is in-memory NetworkX. The project supports Neo4j as an optional backend via a shared `GraphBackend` Protocol but does not require it. Two reasons:

1. The prototype graph fits in tens of kilobytes. A persistent server is overhead, not infrastructure.
2. Free-tier deployment (HuggingFace Spaces, Vercel) is far simpler with an in-process graph than with a managed Neo4j instance. The Neo4j path exists for the case where the graph grows past the point at which NetworkX traversals on hot endpoints stop being instantaneous.

The contract is that both backends produce equivalent semantic content; the test suite asserts this property.

## Model 1: Stance classifier

**Architecture.** A shared DistilBERT encoder feeds four independent regression heads, each producing a sigmoid score in [0, 1] for one axis. The four axes — restrictiveness, enforcement, legalization stance, humanitarian framing — are treated as orthogonal because the literature on immigration legislation suggests that they are *not* collinear in practice. The 1986 IRCA, for example, is high on legalization (it amnestied roughly three million existing unauthorized residents), high on enforcement (it introduced employer sanctions), and ambiguous on restrictiveness (it neither raised nor lowered the legal-immigration cap).

**Training data.** Hand-labeled passages from federal immigration legislation, currently a placeholder corpus pending Phase 3. The target labeling protocol uses three annotators per passage on each axis; inter-annotator agreement is reported in the limitations section. Production training labels (~500 chunks) are pending real corpus assembly.

**Why DistilBERT.** A larger model (RoBERTa-large, GPT-style) would likely improve label fit but would also exceed the project's compute envelope (Colab T4, ~30 minutes for the headline run). DistilBERT is the largest model that fits the envelope cleanly and produces interpretable [CLS]-token regression heads.

## Model 2: Research-paper RAG

**Architecture.** PDFs and Markdown in `data/corpus/` are extracted (pypdf for PDFs), chunked with a recursive character splitter targeting roughly 512 tokens with 64 tokens of overlap, embedded with `sentence-transformers/all-MiniLM-L6-v2`, and indexed in a persistent ChromaDB collection. At query time the top-k chunks (default k = 5) are retrieved by cosine similarity in the embedding space.

**Optional synthesis.** If `ANTHROPIC_API_KEY` is set, retrieved passages are passed to Claude with a system prompt that constrains the model to cite only the supplied passages and to acknowledge when the corpus does not answer the query. Without an API key, the system returns ranked passages directly. The fallback is by design: a portfolio reader without API credentials should still be able to use the system end-to-end.

**Why MiniLM.** all-MiniLM-L6-v2 is 22M parameters, runs on CPU at sub-second latency for the corpus sizes we expect (a few hundred chunks), and remains competitive with much larger embedders on retrieval benchmarks. The bottleneck for RAG quality at this scale is corpus curation, not embedder size.

## Model 3: Flow forecaster

**Architecture.** Two complementary forecasters per country, ensembled by inverse-MAE on a held-out validation window:

- **Prophet.** Captures trend with structural breaks well, robust on small annual series.
- **Lightweight LSTM.** A single-layer LSTM with 32 hidden units, optionally consuming origin-country GDP per capita, unemployment, exchange rate, and conflict-event covariates. Trained on normalized series for stability.

The ensemble produces point forecasts with 80 percent and 95 percent prediction intervals, widened by 10 percent to reflect ensemble uncertainty.

**Why an ensemble and not just Prophet.** Prophet is excellent at trend-with-breaks, but it has no mechanism to incorporate covariates such as origin-country GDP shocks or political crises. The LSTM is the channel through which exogenous information enters the forecast. Inverse-MAE weighting ensures that for series where the LSTM does not help (small-N, no covariates available, high noise) the ensemble degrades to Prophet.

**Forecast horizon.** Five years is the explicit project horizon. Beyond that, the prediction intervals widen to the point where any number is consistent with the data and the system surfaces this rather than producing point estimates.

## Model 4: Graph embeddings

**Architecture.** Node2Vec with default `p = 1, q = 1` (unbiased random walks), 64-dimensional embeddings, walk length 16, 100 walks per node. Trained on the undirected projection of the knowledge graph.

**Why not a GNN.** With ~50 nodes, a graph neural network is severely over-parameterized. The principal failure mode of GNNs in this regime is memorization rather than generalization; Node2Vec produces stable, interpretable embeddings whose neighborhoods correspond to the property we actually want — countries with similar visa, law, and industry profiles should be neighbors. The compute cost is two minutes on a CPU.

**Use cases.**

- *Similarity*: `most_similar('mexico')` returns the most-similar nodes by cosine distance, used by the `/similar/{node_id}` endpoint and the frontend's neighbor surfacing.
- *Link prediction*: cosine similarity between two non-adjacent nodes is interpreted as a soft probability that a typed edge between them is plausible. Used as a probe for missing edges in the seed graph rather than as a primary inference surface.

## Evaluation

Each model is evaluated on a target it can be evaluated on:

| Model | Metric | Target |
|-------|--------|--------|
| Stance | Mean absolute error per axis on held-out passages | < 0.10 on a 0–1 scale |
| RAG | Recall@5 against a hand-built question/passage gold set | > 0.80 |
| Forecaster | Mean absolute percentage error on a 5-year held-out window | < 15% |
| Embeddings | Hit@10 on edge link-prediction with a held-out 10% of edges | > 0.50 |

The targets are calibrated for the prototype data scale; Phase 3 with the real corpus and real flow data will produce the headline numbers.

## What this methodology does not claim

The graph captures association and known historical causation; the four models classify, retrieve, forecast, and embed. None of them runs causal regressions. Where the case study makes causal claims (e.g., "the 1965 INA caused Asian flows to grow"), the claim is sourced to the cited literature, not to the model. This boundary is enforced in the writing.
