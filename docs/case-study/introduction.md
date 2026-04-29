# Introduction

## The problem with statistics-as-list

The standard public artifact about U.S. immigration is a fact sheet. A fact sheet tells you that 13.9 percent of the U.S. population is foreign-born, that Mexico is the largest origin, that the H-1B has an annual cap of 85,000. It tells you these things in parallel, with no relations between them.

The questions people actually ask are relational. *Why* did Indian arrivals begin to dominate the H-1B program in the late 1990s? *How* did the Refugee Act of 1980 connect Vietnamese resettlement to later Cuban entrants and to El Salvadoran TPS holders? *What* would happen to construction labor supply if the Bracero-era pattern of circular migration with Mexico were re-established? Fact sheets cannot answer these questions because the relevant entities live on different pages.

Migration Atlas is the same body of facts re-encoded as a typed graph. Nodes are countries, visas, laws, industries, and regions. Edges are the kinds of relationships that recur in the policy and economic literature: a country *uses* a visa heavily, a law *enables* or *restricts* a corridor, a law *creates* a visa category, a country's nationals *work in* a particular industry. The schema is small enough to fit on a page (44 nodes, 53 edges in the seed graph) and large enough to capture the structural claims that quantitative immigration scholarship has converged on.

## Why the four models, and why these four

The graph alone is not enough. A graph stores what is known; a model says something about what is plausible, predicted, or implied. We picked four models that target distinct cognitive tasks and use distinct stacks, so the project demonstrates competence across the modern ML toolkit without any one model carrying the others.

1. **Stance classifier (DistilBERT, fine-tuned).** Immigration legislation is rarely *only* restrictive or *only* humanitarian. The 1986 IRCA was simultaneously a legalization for existing unauthorized immigrants and the first major employer-sanction regime. The Refugee Act of 1980 codified humanitarian admissions and tightened the bureaucratic gating that determined who qualified. Reducing each law to a single score erases the ambivalence that the laws actually contain. We therefore score on four orthogonal axes — restrictiveness, enforcement, legalization stance, humanitarian framing — each in [0, 1].
2. **Research-paper RAG (sentence-transformers + ChromaDB + optional Claude synthesis).** The economics literature has converged in places (the fiscal contribution of the foreign-born is positive on aggregate over a long horizon) and stayed contested in others (the wage effect on low-skill natives in the short run). A retrieval system that can return cited passages from the actual literature is more honest about that contestedness than a model that answers in its own voice.
3. **Flow forecaster (Prophet + LSTM ensemble).** Annual country-of-origin flows have enough structural breaks (Mariel 1980, Bracero termination 1964, post-2008 Mexican net-zero, post-2014 Central American surge) that no single forecasting model is sufficient. Prophet handles trend with structural breaks well; an LSTM with covariates can capture cases where origin-country GDP, conflict, or exchange rates dominate.
4. **Graph embeddings (Node2Vec).** With ~50 nodes, a graph neural network would be over-parameterized. Node2Vec on the typed adjacency captures the property we actually want: countries with similar visa, law, and industry profiles have neighboring embeddings. This is the basis for both the similarity API and a link-prediction probe that flags structurally plausible edges absent from the seed.

## Scope and what is out of scope

In scope:

- The United States as the destination country.
- Twenty-two origin countries that together account for roughly 73 percent of the U.S. foreign-born population.
- Federal-level law (no state-level pre-emption decisions, no municipal ordinances).
- Quantitative outcomes: flows, populations, industry shares, fiscal aggregates.
- Public-domain or research-permitted data sources.

Out of scope:

- Causal claims about wage effects, fiscal effects, or labor-market crowding. The graph captures known historical causation (the 1965 Act enabled Asian flows) but the four models do not run regressions and the case study does not assert effects beyond what cited studies find.
- Sub-state geography. State-level destination is a property of country nodes; county or metro-area concentration is referenced where relevant but not modeled.
- Policy advocacy. Where a finding has been mobilized by both restrictionist and pro-immigration positions in public debate, the case study notes both rather than choosing.
- Internal migration of immigrants once in the U.S.

## Reader expectations

A reader who already knows the field will find the literature review terse. A reader new to it will find the country deep-dives self-contained. Both readers should find the limitations section longer than they expect; this is intentional. The model layer is intentionally compute-constrained — every model fits on Colab's free tier — and that constraint is documented rather than hidden.
