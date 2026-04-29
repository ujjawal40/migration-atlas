# India

| | |
|---|---|
| Foreign-born U.S. population | ~3.2M (second-largest of any origin) |
| Share of total foreign-born | 6% |
| Era classification | modern |
| Graph edges | `ina-1965 → india (enables)`, `india → h-1b (uses-visa, weight=0.70)`, `india → f-1`, `india → l-1`, `india → eb-5 (uses-visa)`, `india → tech / healthcare (works-in)` |

## A pathway the 1965 Act did not anticipate

The Immigration and Nationality Act of 1965 was framed and debated as a family-reunification measure. The Asian-origin immigration that it enabled was a side effect that congressional supporters of the bill did not predict; in floor debate, the legislation's sponsors explicitly anticipated continued European dominance of admissions, with Senator Edward Kennedy stating that "our cities will not be flooded with a million immigrants annually" and that "the ethnic mix of this country will not be upset."

The empirical trajectory was different. Indian migration to the U.S., a trickle before 1965, grew steadily through the 1970s and 1980s on the strength of educational and employment-based preferences, and then accelerated sharply after 1990 on the strength of a single visa category — the H-1B — that the Immigration Act of 1990 had created for an entirely different stated purpose.

## H-1B: the dominant channel

The H-1B visa was created by the Immigration Act of 1990 as a temporary professional-worker visa with an annual cap (currently 85,000, including 20,000 for U.S.-graduate-degree holders). It was framed as a general-purpose high-skill admission, not as a country-specific channel.

In practice, Indian nationals account for approximately 70 percent of new H-1B initial approvals in recent fiscal years, with Chinese nationals second at roughly 12 percent. The graph encodes this concentration as `india → h-1b (uses-visa, weight=0.70)`. No other origin-visa pair in the seed graph carries a weight as high.

Three structural reasons explain the concentration:

1. **English-medium STEM education.** India's elite engineering institutions (IITs, NITs, BITS) graduate at scale in English in fields directly aligned with H-1B-eligible occupations. Chinese STEM education has caught up in raw quality but a larger share of Chinese applicants enter the U.S. high-skill pipeline through F-1 graduate study rather than direct H-1B hiring.
2. **Employer concentration.** A handful of Indian-headquartered IT services firms (Infosys, TCS, Wipro, HCL, Tech Mahindra) have for decades been the largest individual sponsors of H-1B petitions, optimizing their hiring pipelines around the cap-and-lottery structure.
3. **Network effects.** Existing Indian H-1B holders refer subsequent applicants and create the firm-level institutional knowledge that lowers the cost of additional Indian hires; this is the labor-economics standard story of network-driven migration.

The seed graph also encodes `india → l-1 (uses-visa)` (intracompany transferee), `india → f-1 (uses-visa)` (student, the precursor pipeline), and `india → eb-5 (uses-visa)` (investor, smaller in volume but growing).

## The green-card backlog

The single most distinctive feature of the Indian high-skill migration trajectory is the employment-based green-card backlog. U.S. permanent residency is allocated by employment-based category (EB-1 through EB-5) with a per-country cap of 7 percent of total annual issuances. For nationals of a country with high petition volume, this cap binds.

For Indian-born EB-2 and EB-3 applicants — the categories most H-1B holders eventually transition into — the practical wait between petition filing and green-card issuance is now estimated by the U.S. Citizenship and Immigration Services and tracked monthly by the State Department's Visa Bulletin. The estimates run to multiple decades for some sub-categories. A meaningful fraction of currently working Indian H-1B holders will not receive permanent residency before retirement.

This is not in the seed graph; the graph is structural rather than longitudinal. The backlog is a structural feature of the law (the 7 percent per-country cap), not of any particular country, and the case study notes it here rather than encoding it as an edge.

## Industry concentration

The Indian-origin foreign-born population is overrepresented in technology and healthcare relative to its share of the foreign-born population overall. The seed graph encodes both: `india → tech (works-in)` and `india → healthcare (works-in)`.

The technology overrepresentation is a direct consequence of the H-1B and F-1 pipelines feeding into computer-related occupations. Indian-born inventors are named on a disproportionate share of U.S. patents in software, semiconductors, and pharmaceuticals; Hunt & Gauthier-Loiselle (2010), reviewed in the literature section, documents this for the broader high-skill foreign-born population, with Indian and Chinese inventors as the principal contributors.

The healthcare overrepresentation reflects a separate channel: Indian-trained physicians have historically migrated to the U.S. through the J-1 medical exchange visa, with conditional waivers attached to service in medically underserved areas. The result is a substantial Indian-origin presence in primary-care and specialty medicine in U.S. counties that would otherwise have struggled to retain physicians.

## Median income and the H-1B selection effect

Indian-origin households have the highest median income of any major U.S. immigrant group in the ACS, exceeding $130,000 as of recent vintages and substantially above the U.S. median. This is a selection effect, not a feature of Indian-origin populations as such: the H-1B and F-1 channels select for educational attainment that translates into high lifetime earnings, and the Indian-origin population in the U.S. is selected on these dimensions.

The case study notes this because it is a frequent locus of public confusion. The high median income does not say anything about Indian-origin populations not in the U.S.; it says that the U.S. immigration system, as currently structured, admits a sample of Indian-origin migrants drawn heavily from the educational top decile.

## What changes if the H-1B changes

The Indian-U.S. corridor is the project's clearest example of a single-policy-channel dependency. If the H-1B cap were doubled, the prediction interval on Indian inflows over the next five years would widen and shift upward; if the per-country cap on green cards were removed, the long-run stock of Indian-origin permanent residents would converge much faster to the levels implied by current flows; if employer sanctions on H-1B abuse were tightened, the Indian-headquartered IT-services share of petitions would shrink first.

These are forecastable in principle. The flow forecaster, trained on real USCIS data and configured with H-1B-cap covariates, is the model designed to surface them. In the prototype, with synthetic flow data, the forecasts are illustrative rather than predictive.
