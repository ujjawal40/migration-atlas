# El Salvador

| | |
|---|---|
| Foreign-born U.S. population | ~1.6M |
| Share of total foreign-born | 3.1% |
| Era classification | modern |
| Graph edges | `el-salvador → tps (uses-visa)`, `el-salvador → construction (works-in)` |

## Civil war and the founding inflow

Salvadoran migration to the U.S. before 1980 was small and episodic. The 1980–1992 Salvadoran civil war — a conflict that displaced roughly 20 percent of the country's population — produced the founding generation of the present U.S. Salvadoran-origin population. Estimates of total displacement during the war run between one million and 1.5 million; a substantial fraction of those displaced relocated to the U.S., concentrated in California (Los Angeles County in particular), Washington D.C., and Houston.

The U.S. legal framework's response to wartime Salvadoran arrivals was, throughout the 1980s, contested and inconsistent. The Reagan administration's classification of El Salvador as a U.S. ally in a Cold War conflict translated into a deliberately restrictive asylum-grant rate for Salvadoran applicants; asylum approval rates for Salvadorans were below 3 percent during the early-to-mid 1980s, an order of magnitude lower than rates for Eastern European applicants in the same window.

The American Baptist Churches v. Thornburgh settlement (1991) reopened tens of thousands of denied Salvadoran (and Guatemalan) asylum cases on procedural grounds, and the subsequent Nicaraguan Adjustment and Central American Relief Act (NACARA, 1997) created adjustment paths for some Salvadoran and Guatemalan applicants who had been in the U.S. since before specific cutoff dates. Both are candidates for Phase 3 expansion of the law-node set.

## IRCA 1986 and the Salvadoran legalization cohort

The 1986 Immigration Reform and Control Act, the principal subject of the Mexico writeup, was also the largest single regularization event for Salvadoran migrants in U.S. history. Approximately 150,000 Salvadorans adjusted status under IRCA, second only to Mexicans in absolute numbers and a substantially higher fraction of the at-risk Salvadoran population than the equivalent Mexican fraction.

The seed graph encodes IRCA's effect on Mexico (`irca-1986 → mexico (legalized)`) but does not yet carry the Salvadoran edge; this is a Phase 3 candidate. The case study notes it here for completeness.

## TPS: the long afterlife

Temporary Protected Status, created by the Immigration Act of 1990, is the most-used humanitarian protection in the modern U.S. immigration system. El Salvador's TPS designation dates to 2001, following the January 2001 earthquake; it has been renewed continuously through every subsequent administration of either party.

The seed graph encodes `el-salvador → tps (uses-visa)`. The same edge exists for Honduras, Haiti, and Venezuela — TPS is the only major humanitarian visa category in the seed graph that is shared across multiple nationalities.

The structural feature of TPS that distinguishes it from other categories is its temporariness as a matter of statutory design and its de-facto permanence as a matter of political economy. Each renewal of a TPS designation is a discretionary administrative act; in practice, the population of TPS holders has rooted, U.S.-born children, and U.S.-citizen spouses who make a non-renewal politically costly enough that successive administrations have continued renewals.

The 2018 Trump administration attempted to terminate the El Salvador, Honduras, Haiti, Nicaragua, and Sudan TPS designations. The terminations were blocked by federal courts in Ramos v. Nielsen (2018) and related litigation, on grounds that the administration's decision-making process had violated the Administrative Procedure Act. The Biden administration subsequently issued new El Salvador TPS designations (extended in 2023 with effect through 2025).

This back-and-forth is not currently encoded in the seed graph. A Phase 3 representation would benefit from a temporal model of legal status — a feature the current schema does not support.

## Industry concentration

The seed graph encodes `el-salvador → construction (works-in)`. This concentration is empirically robust: Salvadoran-born workers are roughly 2.5x overrepresented in construction relative to their share of the foreign-born population, with secondary concentrations in landscaping, hospitality, and food preparation.

The construction concentration is structurally similar to the Mexican concentration described in the Mexico writeup, with one important distinction: a substantially higher fraction of Salvadoran-origin construction workers hold TPS, which complicates the wage-effects analysis because TPS holders are work-authorized and tax-paying but legally distinct from both unauthorized and permanent-resident workers.

## Geographic concentration: Los Angeles, D.C., Houston

The Salvadoran-origin U.S. population is concentrated in three metropolitan areas: Los Angeles County (the single largest concentration outside El Salvador itself), the Washington D.C. metropolitan area (in particular the Maryland and Virginia suburbs), and Houston. Each concentration has a distinct settlement history: the LA concentration dates to the early-1980s civil war flows; the D.C. concentration to a smaller pre-war professional migration that grew through chain migration; the Houston concentration to post-2000 reconstruction-driven flows.

The graph does not yet encode `region` nodes for U.S. states or metro areas, so this geographic detail lives in narrative form rather than as an edge. Phase 3 introduces the `region` node kind.

## What the graph does not yet capture

Several Salvadoran-specific structural features are absent from the seed graph and are candidates for expansion:

- The temporary protected status / asylum / unauthorized intersection, which is empirically substantial but requires temporal modeling of legal status.
- Northern Triangle (El Salvador, Guatemala, Honduras) co-flows during the post-2014 unaccompanied-minor surge and the post-2018 family-arrival surge, which are correlated across the three origins in ways the current schema does not represent.
- The MS-13 / 18th Street gang dynamics that have shaped both U.S. enforcement framing and El Salvadoran return-migration risk; this is a politically charged topic that the case study does not encode in the graph because the relevant claims are not well-captured by edges between nationality and visa categories.

The case study notes these as Phase 3 topics rather than gaps in framing.
