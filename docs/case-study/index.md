# Case study: Migration as a relational structure

A book-length statistical literature has accumulated around U.S. immigration over the past four decades. Most of it is sliced one way: a wage paper, a fiscal paper, a refugee paper, a legalization paper. Each holds something fixed and varies one thing. Each is honest about its scope, which is narrow.

Migration Atlas is built on a different premise. Origin countries, visa pathways, landmark legislation, and industries of settlement are not separate research silos. They are nodes in a single graph, and most of the questions worth asking are questions about *paths* through that graph: how the 1965 Immigration and Nationality Act re-routed flows from southern Europe toward Asia, how the 1986 Immigration Reform and Control Act legalized roughly three million people but did not end unauthorized migration, why a country with India's level of arrivals is overrepresented in technology while a country with Mexico's level of arrivals is overrepresented in construction.

This case study walks the project end-to-end. It covers the literature it draws on, the data it ingests, the methodological choices it makes, five country-level deep-dives, four worked example queries, and an explicit accounting of what it does not and cannot claim.

## How this writeup is organized

| Section | Purpose |
|---------|---------|
| [Introduction](introduction.md) | Motivation, scope, the relational reframe |
| [Literature](literature.md) | The wage debate, complementarity, fiscal effects, refugee scholarship |
| [Methodology](methodology.md) | Data harmonization, graph construction, model design, evaluation |
| [Mexico](countries/mexico.md) | The largest corridor, and the only one whose net flow has reversed |
| [India](countries/india.md) | The H-1B pipeline and a category of immigration the 1965 Act did not anticipate |
| [China](countries/china.md) | From the only nationality ever excluded by name to the second-largest source of new graduate students |
| [Cuba](countries/cuba.md) | Cold-War refugee policy, the Cuban Adjustment Act, and the end of wet-foot/dry-foot |
| [El Salvador](countries/el-salvador.md) | Civil war, IRCA, and the long afterlife of Temporary Protected Status |
| [Findings](findings.md) | Four worked queries against the live system |
| [Limitations](limitations.md) | What the data, the graph, and the models cannot tell you |
| [References](references.md) | Bibliography |

## A note on framing

This is an academic case study, not a policy brief. Where a finding is contested, the case study cites the contest rather than picking a side. Where a model output is uncertain, the prediction interval is reported instead of a point estimate. Where the underlying data is synthetic, the writeup says so. The aspiration is to be useful to a reader who wants the full shape of the problem, not the shape that argues for any particular conclusion.
