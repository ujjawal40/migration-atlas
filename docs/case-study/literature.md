# Literature review

The economics and policy scholarship that informs Migration Atlas can be organized into five debates. Each debate is referenced in the project's RAG corpus and in the seed-graph edges. None is settled.

## 1. The wage effect of low-skill immigration

The longest-running quantitative debate in immigration economics asks whether an inflow of foreign-born workers reduces the wages of native workers with similar skill levels. The conventional reference points are George Borjas and David Card.

Borjas (1995, 2003, 2017) argues that, conditional on a national labor market and a skill-cell decomposition (education × experience), immigration has a measurable negative effect on the wages of native workers in the same cell, and that effect is concentrated on the least-educated. The 2003 *Quarterly Journal of Economics* paper introduced the "national labor market" framing that became the methodological default for this side of the debate.

Card (1990) studied the 1980 Mariel boatlift, when roughly 125,000 Cuban migrants arrived in Miami in a five-month window, and found minimal effects on the wages or unemployment of low-skill Miami workers — a result interpreted as evidence that local labor markets absorb supply shocks more flexibly than the national-cell framing implies. Card (2009, *American Economic Review* P&P) extends the argument across multiple metropolitan supply shocks. Borjas (2017) re-examined Mariel with a narrower subset of workers (non-Hispanic men with less than a high-school education) and reported a wage decline; subsequent re-analyses by Peri & Yasenov (2019) using broader samples did not reproduce the result.

Ottaviano & Peri (2012, *Journal of the European Economic Association*) added the substitutability assumption itself as the variable of interest. If foreign-born and native workers within the same education-experience cell are imperfect substitutes — because of language, network, or specialization differences — the within-cell wage effect on natives shrinks and can flip sign. Their estimates of the elasticity of substitution between immigrant and native labor of comparable observed skill imply complementarity for most cells.

The current state of the debate is not consensus. The National Academies of Sciences, Engineering, and Medicine 2017 panel report ("The Economic and Fiscal Consequences of Immigration," chairs Francine Blau and Christopher Mackie) summarizes the evidence as "small and concentrated in the short run on prior immigrants and native-born workers without a high-school education," with a long-run aggregate effect on native wages that is approximately zero. The case study takes the NAS 2017 framing as the most defensible single statement.

## 2. Fiscal contribution

Whether immigrants are net fiscal contributors depends almost entirely on the time horizon, the level of government considered, and whether the children of immigrants are counted.

The NAS 2017 panel's fiscal analysis, the most comprehensive recent estimate, finds that:

- In the short run (cross-sectional, single year), the foreign-born are a net fiscal *cost* to state and local governments and a net contributor to the federal government, with magnitudes depending on age and education at arrival.
- Over a 75-year horizon, including the U.S.-born children of immigrants in the accounting, the net fiscal effect is positive at every level of government.

The cross-sectional cost finding is heavily driven by the cost of educating school-age children, which is borne by states and localities while the eventual income-tax contribution accrues to the federal government — a vertical fiscal externality, not a story about immigrants' productivity.

The Cato Institute's immigration-focused work (Alex Nowrasteh and colleagues) emphasizes that the long-run fiscal calculation is sensitive to assumptions about how the federal debt is allocated and that under most reasonable assumptions the average foreign-born adult is a long-run net positive. The National Foundation for American Policy publishes related work on entrepreneurship: as of 2022, immigrants founded over half of all U.S. unicorn startups.

## 3. Innovation and high-skill immigration

A separate empirical literature focuses on the contribution of high-skill foreign-born workers to U.S. innovation, measured most often by patents.

Hunt & Gauthier-Loiselle (2010, *American Economic Journal: Macro*) find that a one-percentage-point increase in the share of immigrant college graduates increases patents per capita by 9–18 percent, with no evidence of crowding out of native inventors. Kerr & Lincoln (2010, *Journal of Labor Economics*) study the H-1B visa program specifically and document a positive effect on the patenting output of firms granted additional H-1B slots, concentrated in computer-related fields and in firms employing larger numbers of Indian and Chinese inventors. William Kerr's 2019 book *The Gift of Global Talent* synthesizes the broader literature on global talent flows and argues that the U.S. position is one of the few national outcomes in the global economy that has been visibly shaped by the immigration system.

The H-1B visa, which the project's seed graph models as an edge from India and China to the technology industry, has been the empirical workhorse of this literature largely because the cap-and-lottery structure produces quasi-experimental variation in firm-level access.

## 4. Unauthorized migration: estimation and dynamics

The unauthorized population has been measured most rigorously by the residual method: subtract a high-quality estimate of the legally present foreign-born population from the total foreign-born population observed in the ACS or CPS, with adjustments for survey undercount. Pew Research (Jeffrey Passel and D'Vera Cohn) and the Migration Policy Institute publish independent residual estimates that have generally agreed within roughly half a million on the headline number.

The case study uses Pew estimates of approximately 11.0 million unauthorized residents as of 2022 as the working number, while flagging that this is a stock figure that obscures heterogeneous histories: long-resident populations (typically Mexican, often present 20+ years), more recent Northern Triangle arrivals, visa overstays (typically tied to specific origin corridors and visa categories), and the post-2014 wave of Central American and Venezuelan asylum seekers.

Two empirical points are not contested:

- Net migration from Mexico has been at or below zero since approximately 2007 (Passel, Cohn, González-Barrera 2012), driven by reduced Mexican fertility, a stronger Mexican economy, and the post-2008 U.S. recession.
- Visa overstays now account for a majority of new unauthorized residents annually, displacing border crossings as the primary inflow channel.

## 5. Refugee and humanitarian admissions

A separate scholarly tradition treats refugees and asylum seekers as analytically distinct from economic migrants, because the legal category, the admission infrastructure, and the integration trajectory all differ.

The Refugee Act of 1980 codified the U.S. refugee admissions program and the asylum process; before 1980, refugee admissions had been handled through ad-hoc parole authority on a case-by-case basis (Operation Peter Pan for Cuban children, the Hungarian admissions of 1956, the Indochinese Refugee Assistance Program). Susan Martin's *A Nation of Immigrants* and the work of Roger Daniels remain standard historical references; Karen Jacobsen and Loren Landau have written extensively on the methodological challenges of forced-migration data.

The Cuban Adjustment Act of 1966 sits in an analytically anomalous position: it grants Cuban nationals an expedited path to permanent residence that no other nationality has, a policy artifact of Cold War foreign policy that survived the end of the Cold War by three decades. The 2017 termination of "wet-foot/dry-foot" did not repeal the Cuban Adjustment Act itself; the Act remains in force.

Temporary Protected Status (TPS), created by the Immigration Act of 1990, is the most-used humanitarian protection for nationals of countries experiencing armed conflict, environmental disaster, or other extraordinary conditions. El Salvador, Honduras, Haiti, Venezuela, Ukraine, and Sudan are among the countries currently or recently designated; the El Salvadoran TPS designation, which dates to 2001, has been renewed continuously and was the subject of the 2018 *Ramos v. Nielsen* litigation that contested the Trump administration's attempted termination.

## What this review cannot resolve

Several questions remain unsettled in the cited literature and are therefore unsettled in this case study:

- The size of the wage effect on the lowest-skill natives in the short run (Borjas vs. Peri/Card).
- The cross-sectional fiscal cost of recently arrived families with children (large in the short run, smaller or negative over 75 years; how a reader weighs the horizons matters).
- The crowd-out question for native scientists and engineers from H-1B inflows (largely null in the published literature, but the experimental design constraints are real).

The case study cites these where they arise rather than asserting a resolution. The RAG model is the appropriate surface for a reader who wants the actual passages.
