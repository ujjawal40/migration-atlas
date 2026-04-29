# Mexico

| | |
|---|---|
| Foreign-born U.S. population | ~11.4M (largest of any origin) |
| Share of total foreign-born | 22% |
| Top destination state | California |
| Era classification | modern |
| Graph edges | `bracero-1942 → mexico (enables)`, `irca-1986 → mexico (legalized)`, `ina-1965 → mexico (enables)`, `mexico → family-based (uses-visa)`, `mexico → tn (uses-visa)`, `mexico → construction / agriculture / hospitality (works-in)` |

## Why Mexico is the structural anchor

Mexico is the largest single immigrant origin in U.S. history, the only country whose immigrants form more than one-fifth of the entire U.S. foreign-born population, and the only major corridor whose net annual flow has reversed direction within the past two decades. Any national account of U.S. immigration that does not place Mexico at the center is not describing the data.

## Bracero, 1942–1964

The Bracero Program — formally the Mexican Farm Labor Program Agreement — admitted roughly 4.6 million Mexican workers between 1942 and 1964 on temporary agricultural labor contracts. Originating as a wartime labor measure, it became the structural pattern of mid-20th-century Mexican migration to the U.S.: circular, agricultural, concentrated in the Southwest, and largely outside the family-based reunification framework that would later dominate.

The program ended in 1964 under pressure from U.S. organized labor and civil-rights litigation. Its termination did not end Mexican migration; it ended the *legal* channel through which most of that migration had previously moved. Within a decade, the bulk of Mexican entry had shifted to undocumented status — a structural consequence the Bracero termination's proponents did not anticipate.

In the seed graph, this is captured as a single edge: `bracero-1942 → mexico (enables)`. The methodology section's policy of preserving historical causation in the graph is most visible here.

## INA 1965 and the family-based anchor

The Immigration and Nationality Act of 1965 abolished the national-origins quota system that had structured U.S. immigration since 1924 and replaced it with a system organized around family reunification and labor-skill preferences. For Mexico, the consequential change was not the headline shift toward Asian immigration that the 1965 Act is most famous for; it was the creation of a high-volume family-based preference that, combined with already-substantial Mexican-origin populations resulting from Bracero-era circular flows, produced decades of family-chain migration.

The graph encodes this as `ina-1965 → mexico (enables)` and `mexico → family-based (uses-visa)`. The family-based pathway is also the channel by which Bracero-era migrants who eventually adjusted status sponsored relatives, producing the multi-generational Mexican-American population concentrated in California, Texas, and Illinois.

## IRCA 1986: the legalization that did not end unauthorized migration

The Immigration Reform and Control Act of 1986 had two principal provisions:

1. A legalization (often called the Reagan amnesty) for unauthorized immigrants who had resided continuously in the U.S. since before January 1982. Approximately three million people regularized status under this provision, the majority of whom were Mexican.
2. The first federal employer-sanction regime, prohibiting the knowing employment of unauthorized workers and creating the I-9 verification system.

In stance terms, IRCA scores high on legalization and high on enforcement simultaneously — the orthogonal-axis design of the stance classifier was motivated in part by laws like this one. The graph encodes this as `irca-1986 → mexico (legalized)`.

The empirical aftermath of IRCA is the central empirical fact in the unauthorized-migration literature: legalization did not end unauthorized migration. By the late 1990s, the U.S. unauthorized population had returned to and then exceeded its pre-IRCA level, with Mexican nationals continuing to constitute the majority. The reasons are well-documented: employer sanctions were poorly enforced, the legal-immigration system did not expand to absorb the structural labor demand that had previously been met informally, and the Bracero-era pattern of circular migration was disrupted in a way that increased the duration of unauthorized residence (workers who would previously have gone home seasonally now stayed because re-entry was harder).

## The 2007 inflection: net migration goes to zero

Between approximately 2007 and 2014, net migration from Mexico to the U.S. fell to zero or below. Pew Research (Passel, Cohn, González-Barrera 2012) documents this in detail; subsequent updates have confirmed the pattern.

The drivers are the standard ones in the literature, with no single cause dominating:

- Mexican total fertility fell from 6.7 in 1970 to 1.9 by 2017, reducing the labor-age cohort entering the migration-decision window.
- Mexican GDP per capita grew through the 2000s; the wage gap with the U.S. narrowed for skilled workers, though it remained wide for unskilled.
- The 2008–2009 U.S. recession reduced demand for the construction-sector labor that had been the post-IRCA absorption channel.
- Border enforcement intensified, raising the cost of attempted entry without reducing the wage gap proportionally.

This is the only major U.S. immigration corridor where net flow has reversed in the post-1965 era. The flow-forecaster model, when trained on real USCIS / ACS data, should reproduce this inflection as a structural break — a Phase 3 validation criterion.

## TN, USMCA, and the high-skill exception

The Trade NAFTA (TN) visa, created by NAFTA in 1994 and continued under USMCA, allows Mexican and Canadian professionals in designated occupations to work in the U.S. on streamlined non-immigrant terms. TN is structurally distinct from the rest of the Mexican migration story: high-skill, employer-petitioned, and small in volume relative to family-based flows.

The seed graph encodes `mexico → tn (uses-visa)` and `canada → tn (uses-visa)`. The TN visa is the principal channel by which the Mexican high-skill labor market integrates into the U.S. high-skill labor market, and it is the corridor most likely to grow if cross-border professional services continue to integrate.

## Industry concentration

The Mexican-origin foreign-born population is overrepresented in three industries: construction, agriculture, and hospitality. The seed graph encodes all three with `mexico → <industry> (works-in)` edges.

The empirical regularity is well-documented in the BLS labor-force data: as of recent ACS / CPS vintages, Mexican-born workers are roughly 1.5x to 3x overrepresented relative to their population share in these industries, while underrepresented in finance, technology, and professional services. The unauthorized share is highest in agriculture (24% of agricultural workers are estimated unauthorized; the modal unauthorized agricultural worker is Mexican).

This is the structural fact that the wage-effect literature reviewed in the previous section attempts to interpret. Whether the concentration depresses native wages in the affected industries (Borjas) or whether it reflects complementary specialization (Peri/Ottaviano) is the contested question; the case study does not resolve it.

## What the graph does not say about Mexico

The graph captures the legal and economic structure of Mexican migration. It does not capture:

- Sub-national geography on either side of the border (sending states like Zacatecas, Jalisco, Michoacán; receiving counties in California's Central Valley).
- The trajectory of second-generation Mexican-Americans, who by U.S. citizenship law are not foreign-born.
- The specific dynamics of family-separation enforcement policy (the 2018 zero-tolerance period, the post-2021 rollback).
- The role of remittances (~$60B annually), which are an outflow from the U.S. economy not captured on any graph edge.

These are out of scope for the prototype. Some are addressable in Phase 3; others are out of scope for the project entirely.
