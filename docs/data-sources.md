# Data sources

Every data source the project uses, with what we extract, the licensing, and the harmonization decisions.

## Primary sources

### U.S. Census Bureau — American Community Survey (ACS)
Annual nationally-representative sample. We use the 1-year ACS for current estimates and the 5-year ACS for state / county granularity. Tables we pull:

| Table | What it gives us |
|-------|------------------|
| B05002 | Place of birth by U.S. citizenship status |
| B05006 | Place of birth for the foreign-born population |
| B05007 | Place of birth by year of entry |

**License:** Public domain (U.S. government work).

### USCIS — Office of Homeland Security Statistics Yearbook
Annual statistical yearbook covering visa issuance, adjustment of status, naturalization, and refugee admissions. The authoritative source for legal flow data.

**License:** Public domain.

### Migration Policy Institute — Data Hub
Pre-aggregated tabulations including some historical series back to 1850. Saves us from doing the same aggregations.

**License:** Free for non-commercial / educational use. Cite MPI as data source.

### Pew Research Center
Augmented unauthorized immigrant population estimates using the residual method, plus periodic deep-dive analytical reports.

**License:** Free for academic / non-commercial use with citation.

### Bureau of Labor Statistics — Foreign-Born Workers
Monthly Current Population Survey tables on labor force participation by nativity. Table A-7 is our primary input.

**License:** Public domain.

### OECD — Database on Immigrants in OECD Countries (DIOC)
Cross-country immigrant stocks from the *origin* perspective. Lets us compute brain-drain intensity.

**License:** OECD terms; permitted for research use with citation.

## Harmonization decisions

The biggest source of analytical pain is that every dataset uses slightly different definitions. We make the following choices and document them:

- **"Foreign-born"** = born outside the U.S. to non-U.S.-citizen parents. Excludes Puerto Rico and other territories. Aligns with ACS definition.
- **"Immigrant"** = used interchangeably with "foreign-born" in this project, except where context (e.g., USCIS legal definitions) requires precision.
- **"Country of origin"** = country of birth, NOT country of citizenship. Important for groups like ethnic Chinese born in Vietnam.
- **Year vintages** — we always use the most recent available; current default is ACS 2023 (released September 2024).
- **ISO codes** — we normalize to ISO 3166-1 alpha-3. "South Korea" → KOR, "Taiwan" → TWN (kept separate from China).

## Update cadence

| Source | Cadence | Last refreshed |
|--------|---------|----------------|
| ACS | Annual (Sept) | 2023 vintage |
| USCIS Yearbook | Annual | FY2023 |
| MPI | Continuous | — |
| BLS | Monthly | — |
| OECD DIOC | ~5-year | 2020 vintage |
