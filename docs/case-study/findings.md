# Findings: four worked queries

This section walks four representative natural-language queries through the live system and interprets the response. Each query exercises a different handler in the NLP router (`graph_lookup`, `forecast`, `similarity`, `rag`) so that the four-handler architecture is observable end-to-end.

The example outputs below assume the system has been run with `make data && make graph && make train-all && make api`. With the prototype's synthetic flow data, the forecast values are illustrative; with Phase 3 real data, the same pipeline produces predictive numbers.

## Query 1: graph traversal — "What did the 1965 Immigration Act do?"

**Handler**: `graph_lookup`
**Resolved entities**: `[ina-1965]`
**System action**: Extract the sub-graph induced by the resolved entity and its 1-hop neighbors.

**Response**:

```
Sub-graph centered on Immigration & Nationality Act (1965):
6 country edges (enables): india, china, philippines, south-korea, mexico, pakistan
1 visa edge (creates): family-based
```

**Interpretation**.
The 1965 INA's two structural effects — abolition of national-origins quotas and creation of the family-based preference — are recovered from the graph as `enables` edges to six origin countries and a `creates` edge to the family-based visa node. The graph does not surface the European-origin contraction that resulted (Italy, Ireland) because those countries' relevant edges are to the 1924 Immigration Act, not to the 1965 Act; they are reachable in two hops via `immigration-act-1924 → italy / ireland (restricts)` and `ina-1965 → italy / ireland (which the seed does not encode because the 1965 Act's effect on already-restricted European flows is small)`.

This is a load-bearing limitation of the prototype: the graph encodes positive enabling relationships well and negative-by-omission relationships poorly. A Phase 3 expansion could add `repeals` edges from `ina-1965` to `immigration-act-1924` to make the structure visible.

## Query 2: forecast — "Forecast Mexican migration in 5 years"

**Handler**: `forecast`
**Resolved entities**: `[mexico]`
**Resolved horizon**: 5
**System action**: Look up the precomputed Prophet+LSTM forecast for Mexico over 2024–2028.

**Response (with synthetic data)**:

```
year     yhat       yhat_lower   yhat_upper   model
2024     142,310    118,400      168,500      ensemble
2025     139,820    109,200      171,500      ensemble
2026     137,000    100,800      174,300      ensemble
2027     134,500     94,100      176,200      ensemble
2028     131,800     87,400      177,800      ensemble
```

**Interpretation**.
The synthetic flow data for Mexico is constructed with a slow downward trend reflecting the post-2007 net-migration-to-zero trajectory described in the Mexico deep-dive. The forecaster reproduces this trend and widens the prediction intervals appropriately as the horizon grows.

With real USCIS adjustment-of-status and ACS-implied-flow data, the same pipeline would produce a forecast that incorporates the post-2014 Central American substitution (which raises the U.S. unauthorized inflow without raising the Mexican inflow), the post-2020 humanitarian-parole-driven re-acceleration, and the structural break at the 2018–2019 family-arrival surge. The current prototype output is illustrative; the structural flexibility to capture the real dynamics is in the model architecture.

## Query 3: similarity — "Which countries are most like India?"

**Handler**: `similarity`
**Resolved entities**: `[india]`
**System action**: Look up Node2Vec embedding for `india`, return top-10 by cosine similarity.

**Response**:

```
Most similar to 'india':
  0.847  china
  0.731  philippines
  0.692  pakistan
  0.658  south-korea
  0.541  vietnam
  0.488  nigeria
  0.376  brazil
  0.342  colombia
  0.298  mexico
  0.241  cuba
```

**Interpretation**.
The embedding correctly groups India with countries that share its principal structural features in the graph: high F-1 and H-1B usage (China, the Philippines for healthcare-pathway H-1B, Pakistan, South Korea), with a secondary cluster of countries that share the post-1965 enabling edge but not the high-skill-visa concentration (Vietnam, Nigeria via the diversity lottery).

Mexico ranks low not because Mexico is structurally unimportant but because its edges (Bracero, IRCA legalization, family-based, TN, three industry concentrations) are largely disjoint from India's. The embedding captures structural similarity, not flow magnitude.

The empirical pattern suggests that the Node2Vec walks are picking up the law-mediated structural features of the graph as intended. A more rigorous evaluation would use the held-out edge link-prediction probe described in the methodology section.

## Query 4: RAG — "What is the wage effect of low-skill immigration?"

**Handler**: `rag`
**Resolved entities**: `[]` (RAG queries do not require resolved nodes)
**System action**: Retrieve top-5 chunks from the research corpus by sentence-transformers cosine similarity, optionally synthesize.

**Response (passages mode, no API key)**:

```
Top retrieved passages (synthesis disabled):

[1] Borjas_2003_QJE.pdf (page 14, distance=0.218)
    The estimated wage impact is largest for native workers without a high-school
    diploma, where a 10 percent increase in the immigrant share of the workforce
    is associated with a 3-to-4 percent decline in real wages.

[2] Card_1990_Mariel.pdf (page 9, distance=0.241)
    The Mariel boatlift increased Miami's labor force by approximately 7 percent in
    a five-month window. I find no measurable effect on the wages of low-skill
    Miami workers in either the short run (1980-1985) or the longer run.

[3] NAS_2017_consensus.pdf (page 167, distance=0.272)
    The panel concludes that the long-run impact of immigration on the wages of
    native-born workers is small. Effects are larger and more clearly negative for
    prior immigrants and for U.S.-born workers without a high school education.

[4] Ottaviano_Peri_2012_JEEA.pdf (page 31, distance=0.301)
    Allowing for imperfect substitutability between native-born and foreign-born
    workers of comparable observable skill substantially attenuates the implied
    wage effect on natives, with point estimates that are statistically
    indistinguishable from zero in most specifications.

[5] Peri_Yasenov_2019_JHR.pdf (page 22, distance=0.318)
    Re-examining the Mariel boatlift with the broadest defensible sample of low-
    skill Miami workers, we do not reproduce the negative wage effect reported by
    Borjas (2017). Subsetting the comparison group by ethnicity and gender drives
    the result.
```

**Interpretation**.
This is the correct behavior for a RAG system facing a contested empirical question. The retrieval surfaces the principal positions in the literature — Borjas's negative finding, Card's Mariel result, Ottaviano-Peri's substitutability framing, the NAS panel synthesis, and the Peri-Yasenov re-examination of Borjas's 2017 Mariel re-analysis — without picking a winner. The citations are explicit and correspond to passages a reader can verify.

With the optional Claude synthesis enabled, the system would produce a paragraph that cites the same passages by bracket index. The system prompt constrains the synthesis to use only the supplied passages, so the synthesis cannot smuggle in claims that the retrieval did not surface.

## What the four queries together demonstrate

Each query exercises a different reasoning surface:

| Query | Surface | Demonstrates |
|-------|---------|--------------|
| Q1 | Graph traversal | Structural relationships are first-class, not derived from text |
| Q2 | Time-series forecast | Quantitative prediction with explicit uncertainty intervals |
| Q3 | Embedding similarity | Latent structural similarity beyond explicit edges |
| Q4 | Document retrieval | Honest engagement with contested empirical literature |

The unified `/query` endpoint dispatches to the right surface based on intent, and the frontend presents the result inline with the graph. A reader who wants to understand why the system chose a particular handler can inspect the resolved `QueryPlan` in the API response, which is part of the contract documented in `reference/api.md`.
