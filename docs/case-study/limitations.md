# Limitations

This section is deliberately longer than a reader of a typical model card might expect. The project is a portfolio case study, and the aspiration is that a reader can use it as a starting point for their own work; that aspiration requires explicit accounting of what the system does not do well.

## Definitional drift across sources

Every primary data source uses slightly different definitions of the population it tabulates. Foreign-born in the ACS is not the same set of people as the legally admitted immigrants in the USCIS Yearbook; the unauthorized population estimated by Pew is not the population estimated by the Migration Policy Institute, even though both use the residual method. The harmonization decisions documented in the methodology section reduce this drift but do not eliminate it. Where two sources imply different counts for the same nominal quantity (e.g., the size of the foreign-born population from a given origin in a given year), the project keeps both and surfaces the discrepancy rather than picking a winner.

This is a real limitation. A reader who pulls a single number out of the system to use in a downstream argument is implicitly choosing a definitional frame, and the system does not always make that frame loud enough.

## Recency lag

Country-of-origin breakdowns from the ACS lag the present by 12–18 months. The current default vintage is 2023 ACS, released September 2024. Live policy questions about the post-2024 humanitarian flows, the post-2025 administrative changes, or this fiscal year's USCIS adjustments cannot be answered from the data already in the pipeline; they require either more recent USCIS administrative data (which is partial and lagged differently) or the next ACS vintage.

The forecaster operates on annual data and does not produce intra-year estimates. A reader who needs current-quarter flow estimates is reaching for a tool the project does not provide.

## Causal claims, and their absence

The graph captures association and known historical causation as documented in the cited literature. The four models classify, retrieve, forecast, and embed; none of them runs causal regressions, none of them claims to identify the marginal effect of any policy or any inflow on any economic outcome. Where the case study uses the language of cause ("the 1965 INA caused the post-1965 Asian-origin growth"), the claim is anchored to historical sources that document legislative intent and the time-series response, not to a model output.

The wage-effects, fiscal-effects, and innovation-effects literatures reviewed in the literature section make causal claims; the project surfaces those claims through the RAG model with citation. The project does not produce competing causal estimates.

## Sentiment subjectivity in the stance classifier

The four-axis stance scoring is interpretive. The orthogonal-axis design (restrictiveness, enforcement, legalization, humanitarian) is informed by the legislative-history literature but is not the only defensible decomposition. Three annotators per passage produces a measurable inter-annotator agreement statistic; in pilot labeling, agreement on the restrictiveness and enforcement axes was substantially higher than on the legalization and humanitarian axes, where annotators disagreed about whether the same statutory language was best read as a humanitarian admission or a discretionary screening tool.

The model inherits this subjectivity. A user of the stance classifier should treat the four scores as a structured summary of one annotator team's reading rather than as an objective measurement.

## Forecast horizons

The flow forecaster produces five-year forecasts because that is the horizon at which annual flow data and the available covariate series support useful prediction intervals. Beyond five years, intervals widen to the point that any projected number is consistent with the data, and the system surfaces this rather than producing point estimates.

Demographic projections at 25-year or 50-year horizons exist in the literature (the Pew Research projections, the Census Bureau population projections) and use methodologies — cohort-component analysis, parameterized fertility/mortality assumptions — that are structurally different from time-series forecasting on flows. The project does not compete with those projections at long horizons.

## Training-data scarcity for the stance classifier

The stance classifier is the model most exposed to training-data scarcity. Labeled passages from the legal corpus number in the low hundreds in the prototype and are targeted for ~500 chunks in Phase 3. This is small for a regression task with four outputs.

Two mitigations are in place: the model is the smallest defensible (DistilBERT, not RoBERTa-large), and the labeling protocol uses three annotators per passage. The honest expectation is that the production stance scores for laws outside the labeled set will be noisier than the held-out validation MAE suggests, particularly for laws whose linguistic register (highly technical statutory text, dense cross-reference) is underrepresented in the training set.

## The U.S.-only frame

The project is a case study of U.S. immigration. It does not generalize to other destination countries. Some structural features (large family-reunification preference; per-country green-card cap; humanitarian admissions through TPS and refugee categories) are specific to U.S. law; other features (national-origin quotas, the H-1B-style high-skill cap-and-lottery) have analogs in other destination-country systems but with substantially different parameterizations.

A reader interested in adapting the framework to Canada, Germany, or the U.K. would need to rebuild the graph schema, replace the legal corpus, and re-validate the methodology. The codebase supports this but the project does not.

## What the seed graph leaves out

The 22 origin countries in the seed graph cover roughly 73 percent of the U.S. foreign-born population. The remaining 27 percent are distributed across approximately 200 nationalities; the prototype does not include them as nodes. The decision is pragmatic: the empirical structure for small-flow corridors is dominated by noise in the data, and the value of an additional node in the graph diminishes quickly past the largest 20 or so origins.

A user with a specific interest in a corridor not represented in the seed graph (Brazil, Iran, Argentina) can extend the graph with the procedure documented in the README; the case study writeup will not cover it.

## Sub-state geography is sparse

The graph schema includes a `region` node kind, but the seed graph does not yet populate it. State-of-residence concentrations live as properties on country nodes (`top_destination_state: California`) rather than as edges to region nodes. This is a Phase 3 expansion item.

Until then, queries that ask "which countries' immigrants concentrate in which states" cannot be answered from the graph alone; the answer lives in the underlying ACS tables, accessible programmatically but not surfaced in the API.

## Politically charged topics

Several immigration topics that arise in public debate — the structural relationship between cartel violence and Northern Triangle migration, the role of remittances in origin-country economies, the empirical question of unauthorized migrants' fiscal contribution at the state and local level — are addressed in the case study only where the academic literature is empirically firm. Where the literature is contested or where the data does not support a clean claim, the project does not assert one.

This is a deliberate framing choice. The system is intended as a research and pedagogical tool; readers who want a policy advocacy framing should look elsewhere, and readers who want to use the system to argue for any particular policy outcome should be aware that the evidence base they are drawing on is structurally constrained to what the system surfaces.
