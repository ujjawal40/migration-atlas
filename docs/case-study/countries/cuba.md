# Cuba

| | |
|---|---|
| Foreign-born U.S. population | ~1.7M |
| Share of total foreign-born | 3.3% |
| Top destination state | Florida |
| Era classification | cold-war |
| Graph edges | `refugee-act-1980 → cuba (enables)`, `cuba → refugee (uses-visa)` |

## A category of admissions that no other origin shares

Cuba is the only national-origin in the modern U.S. immigration system to which a nation-specific adjustment-of-status statute applies — the Cuban Adjustment Act of 1966, still in force as of writing. The Act allows Cuban nationals who have been physically present in the U.S. for at least one year to adjust to lawful permanent residence on terms that no other nationality enjoys.

The Cuban migration trajectory is also the case study's clearest example of a corridor structured almost entirely by foreign policy rather than by economic gradients. The five major flow events of the post-1959 period — the post-revolutionary exile (1959–1962), the Freedom Flights (1965–1973), the Mariel boatlift (1980), the Balsero crisis (1994), and the post-2014 surge after the U.S.-Cuba diplomatic opening — each correspond to a specific policy or political moment, not to a continuous economic pull.

## The post-1959 exile and Operation Peter Pan

The first wave (1959–1962) was small in absolute terms but socio-economically distinctive: it consisted disproportionately of Cuba's professional, business, and landowning classes, plus their children. The Operation Peter Pan program (1960–1962), administered by the U.S. State Department in cooperation with the Catholic Welfare Bureau in Miami, brought roughly 14,000 unaccompanied Cuban children to the U.S. on the parole authority of the Eisenhower and Kennedy administrations.

This pre-1980 admissions framework — case-by-case parole rather than a statutory refugee program — is the historical context for the Refugee Act of 1980, which codified humanitarian admissions across all nationalities and replaced the parole-based ad-hoc model. The seed graph encodes `refugee-act-1980 → cuba (enables)` to capture the codification step, even though large-scale Cuban admissions predate the Act by two decades.

## The 1966 Cuban Adjustment Act

The Cuban Adjustment Act, passed in 1966, created the nation-specific adjustment provision that has anchored Cuban migration ever since. Its rationale at the time was Cold War: the U.S. policy framework treated departures from Cuba as defections from a hostile regime and structured admissions accordingly.

The Act's distinctive feature — a fast-track adjustment to permanent residence available to no other nationality — has been politically resilient through every subsequent administration of either party. It survived the 1980 Refugee Act, the 1990 Immigration Act, IRCA, and the 2017 termination of wet-foot/dry-foot. It is, as of writing, the longest-lived nation-specific provision in U.S. immigration law.

The seed graph does not yet encode the Cuban Adjustment Act as a separate law node; it is a Phase 3 expansion candidate. In the current prototype, Cuban migration is captured through the Refugee Act and the `refugee` visa category.

## Mariel, 1980

The Mariel boatlift began in April 1980 when the Cuban government temporarily permitted departures from the port of Mariel; over five months, roughly 125,000 Cubans arrived in the Miami area. The Mariel arrivals were on average younger, more male, and from somewhat lower socio-economic origins than the post-1959 exiles, and the inclusion of a small population of formerly incarcerated and institutionalized individuals received disproportionate political attention at the time.

The Mariel boatlift is, in the academic literature, the empirical case for Card's (1990) wage-effects argument reviewed in the literature section. The Miami labor market absorbed an inflow of approximately 7 percent of its workforce in five months without measurable effect on the wages of low-skill native workers — a finding that, contested by Borjas (2017) and re-examined by Peri & Yasenov (2019), has structured the wage-effects literature for three decades.

## The 1995 wet-foot/dry-foot agreement and its 2017 termination

After the 1994 Balsero crisis (a surge of approximately 35,000 rafters attempting the Florida Strait crossing), the U.S. and Cuba negotiated a migration accord that resulted in what became known as the wet-foot/dry-foot policy: Cuban nationals intercepted at sea would be returned to Cuba, while those who reached U.S. soil would be admitted and (under the Cuban Adjustment Act) put on the path to permanent residence. The U.S. simultaneously committed to a minimum of 20,000 immigrant visas annually for Cuban nationals through ordinary channels.

The wet-foot/dry-foot policy was terminated by executive action in January 2017, during the final days of the Obama administration, as part of the broader U.S.-Cuba normalization. The Cuban Adjustment Act itself was not repealed; what changed was the operational rule that distinguished maritime-interdicted Cubans from land-arriving Cubans. After 2017, Cuban arrivals are subject to ordinary expedited removal procedures unless they qualify for asylum on individual grounds.

The post-2017 trajectory of Cuban migration has shifted toward overland approaches via Mexico and toward formal asylum applications, with a sharp increase in the post-2021 period during the broader Western Hemisphere humanitarian flows.

## Industry and geographic concentration

Cuban-origin populations are heavily concentrated in Florida, particularly in Miami-Dade County, to a degree that no other foreign-origin population matches in any single U.S. metro area. The seed graph encodes `top_destination_state: Florida` as a property on the Cuba node.

Industry concentration is less sharply defined than for the Indian or Mexican corridors. Cuban-origin populations are present across professional services, healthcare, hospitality, and small business at rates closer to the Florida overall distribution than to a sharp specialization. The case study does not encode a `works-in` edge for Cuba in the seed graph for this reason; the data does not support a single-industry concentration claim of the strength used elsewhere.

## What changes if the Cuban Adjustment Act is repealed

The Cuban Adjustment Act has been the subject of episodic congressional repeal proposals, none of which have reached a floor vote. Repeal would not retroactively affect prior adjustments; it would change the prospective rule for future Cuban arrivals to match the rule applied to other Western Hemisphere nationalities (asylum on individual grounds, no nationality-specific fast-track adjustment).

In the project's flow forecaster, with real USCIS data, this would manifest as a structural break in projected Cuban admissions. In the prototype with synthetic data, the forecast cannot speak to it. The case study notes the question rather than answering it.
