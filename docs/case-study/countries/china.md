# China

| | |
|---|---|
| Foreign-born U.S. population | ~3.0M |
| Share of total foreign-born | 6% |
| Era classification | modern (with a deep historical foundation) |
| Graph edges | `chinese-exclusion-1882 → china (restricts)`, `ina-1965 → china (enables)`, `china → f-1 / h-1b / eb-5 (uses-visa)`, `china → tech (works-in)` |

## The only nationality ever excluded by name

The Chinese Exclusion Act of 1882 is the only U.S. immigration statute in history that singled out a national origin for exclusion. It barred the entry of Chinese laborers, prohibited the naturalization of Chinese-born residents, and was renewed in 1892 and made permanent in 1902. It remained in force until the Magnuson Act of 1943 repealed it, and even then admitted Chinese immigrants only at a token quota of 105 per year under the national-origins system.

The graph encodes this as `chinese-exclusion-1882 → china (restricts)`. The seed graph carries year-of-enactment and year-of-repeal properties on law nodes precisely so that the historical scope of edges like this one is preserved.

The Exclusion Act's effects compounded across generations. The U.S. Chinese-origin population in the late 19th century was overwhelmingly male and labor-aged (the "bachelor society" of West Coast Chinatowns), a demographic structure that the Exclusion Act locked in by preventing family reunification. By the 1950s the U.S.-resident Chinese-origin population had grown only modestly from its 1880 peak; the population trajectories of other early-arriving groups, by contrast, had compounded over the same window.

## INA 1965 and the post-Exclusion baseline

Chinese migration to the U.S. effectively restarted in 1965 from a population baseline that was an order of magnitude lower than it would have been under any non-restrictive policy. The 1965 Act admitted Chinese nationals on the same terms as any other origin under family-based and employment-based preferences; the seed graph encodes `ina-1965 → china (enables)`.

For the first two decades after 1965, Taiwan-origin migration dominated the Chinese-origin admissions counts, reflecting the diplomatic recognition pattern of the period and the structure of academic exchanges. After the U.S. normalization of relations with the People's Republic in 1979, mainland-origin admissions grew rapidly. The seed graph keeps Taiwan separate from China per the harmonization policy described in the methodology section.

## The 1992 Chinese Student Protection Act

The 1989 Tiananmen Square events triggered an executive-branch response (deferred enforced departure for Chinese nationals already in the U.S.) and a 1992 statutory response: the Chinese Student Protection Act, which granted permanent residence to Chinese nationals who had been in the U.S. on the relevant date and met continuous-residence requirements. Roughly 80,000 people adjusted status under the Act.

This is one of several humanitarian-adjustment statutes in U.S. immigration history that target a specific nationality in response to a specific foreign-policy event (the Cuban Adjustment Act of 1966 is the best-known precedent; NACARA in 1997 served a similar function for some Central American nationalities). The seed graph does not currently encode the Chinese Student Protection Act as a node; it is a candidate for Phase 3 expansion of the law-node set.

## F-1 and the graduate-student pipeline

The dominant Chinese-origin entry channel is the F-1 student visa, especially for graduate programs in STEM fields. The seed graph encodes `china → f-1 (uses-visa)`.

As of recent open-doors data, China is the second-largest country of origin for international students in the U.S. (India has overtaken it in the most recent vintages). At the graduate level, Chinese-origin students are heavily concentrated in engineering, computer science, and the physical sciences, with subsequent transition into U.S. labor markets via Optional Practical Training and (for those who clear the lottery) the H-1B.

The F-1 → OPT → H-1B → green-card pipeline is structurally identical for Indian and Chinese nationals; the difference is volume composition. Indian H-1B intake is dominated by IT-services-firm sponsorship of bachelor's-degree holders directly from India; Chinese H-1B intake is dominated by U.S.-graduate-degree holders transitioning out of F-1 status.

## EB-5 and the investment channel

The EB-5 immigrant investor visa, created by the Immigration Act of 1990, allocates roughly 10,000 visas annually to applicants who invest a designated minimum (currently $800,000 in targeted employment areas, $1,050,000 elsewhere) in a U.S. enterprise that creates at least 10 full-time jobs. The seed graph encodes `china → eb-5 (uses-visa)` and `india → eb-5 (uses-visa)`.

For most of the 2010s, Chinese nationals accounted for roughly 80 percent of EB-5 visa issuances, the highest single-country concentration of any U.S. visa category in the modern era. Indian usage has grown more recently but remains below Chinese in both stock and flow terms.

The EB-5 program has been the subject of ongoing congressional reauthorization debate, primarily over fraud-detection failures in regional-center investments and over whether the investment thresholds are calibrated correctly. The case study notes the program structure and the empirical concentration without taking a position on the reauthorization question.

## Industry concentration: technology

The Chinese-origin foreign-born population is, like the Indian-origin, overrepresented in technology occupations relative to population share. The seed graph encodes `china → tech (works-in)`.

The empirical pattern in the patent and labor-economics literature is consistent: Chinese-origin inventors and engineers are disproportionately represented in semiconductors, machine learning, biotechnology, and (during the relevant decades) computer hardware. Kerr & Lincoln's H-1B / patenting work, cited in the literature section, documents the firm-level effect; the underlying labor-supply pipeline is the F-1 → OPT → H-1B channel described above.

## What the graph does not say about China

The current Chinese-origin foreign-born population is heterogeneous on dimensions the graph does not encode:

- The Cantonese-speaking, Pearl-River-Delta-origin diaspora that built the original West Coast Chinese-American population is structurally different from the Mandarin-speaking, post-1979 graduate-student-pipeline population, but both code as `china` in the graph.
- Hong Kong is not yet a separate node; under the current schema it codes as `china`. Phase 3 expansion may split it.
- The Tibetan and Uyghur populations admitted on humanitarian grounds, while small, are analytically distinct from the dominant flow and are not yet captured.

These are limitations of the prototype's resolution rather than of the framing.
