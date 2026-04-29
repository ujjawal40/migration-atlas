"""Country code registry — the single source of truth for cross-source joins.

Every primary data source uses a different naming convention:

    Census ACS B05006   →  variable codes (e.g. B05006_138E for Cuba in 2023 ACS)
    USCIS Yearbook      →  English names (e.g. "Mexico", "El Salvador")
    BLS labor tables    →  region codes, no per-country breakdown
    OECD DIOC           →  ISO 3166-1 alpha-3 (MEX, IND, ...)
    Pew tabulations     →  English names, sometimes with parentheticals

Rather than scatter ad-hoc lookups across each source module, every cross-source
join goes through this registry. The canonical id is the lowercase-hyphenated
form used as the graph node id.

The Census variable codes for B05006 are deliberately *patterns* rather than
literal codes, because Census changes them across vintages. Each source module
resolves the pattern against the live variables.json metadata at fetch time.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CountryCode:
    """Cross-source identifiers for a single origin country."""

    id: str                       # canonical graph node id; lowercase, hyphenated
    name: str                     # display name
    iso3: str                     # ISO 3166-1 alpha-3
    census_label: str             # exact label fragment used by Census ACS B05006
    uscis_label: str              # name as it appears in USCIS Yearbook tables
    aliases: tuple[str, ...] = ()  # additional names seen in MPI / Pew / press

    def matches(self, label: str) -> bool:
        """True if `label` refers to this country in any known source."""
        norm = label.strip().lower()
        candidates = (
            self.name,
            self.census_label,
            self.uscis_label,
            *self.aliases,
        )
        return any(norm == c.strip().lower() for c in candidates)


# The 22 seed countries. Order matches graph/seed.py for readability.
COUNTRIES: tuple[CountryCode, ...] = (
    CountryCode(
        id="mexico", name="Mexico", iso3="MEX",
        census_label="Mexico", uscis_label="Mexico",
    ),
    CountryCode(
        id="india", name="India", iso3="IND",
        census_label="India", uscis_label="India",
    ),
    CountryCode(
        id="china", name="China", iso3="CHN",
        census_label="China",
        uscis_label="China, People's Republic",
        aliases=("China, mainland", "People's Republic of China", "PRC"),
    ),
    CountryCode(
        id="philippines", name="Philippines", iso3="PHL",
        census_label="Philippines", uscis_label="Philippines",
    ),
    CountryCode(
        id="cuba", name="Cuba", iso3="CUB",
        census_label="Cuba", uscis_label="Cuba",
    ),
    CountryCode(
        id="el-salvador", name="El Salvador", iso3="SLV",
        census_label="El Salvador", uscis_label="El Salvador",
    ),
    CountryCode(
        id="dominican-republic", name="Dominican Republic", iso3="DOM",
        census_label="Dominican Republic", uscis_label="Dominican Republic",
    ),
    CountryCode(
        id="guatemala", name="Guatemala", iso3="GTM",
        census_label="Guatemala", uscis_label="Guatemala",
    ),
    CountryCode(
        id="vietnam", name="Vietnam", iso3="VNM",
        census_label="Vietnam", uscis_label="Vietnam",
    ),
    CountryCode(
        id="colombia", name="Colombia", iso3="COL",
        census_label="Colombia", uscis_label="Colombia",
    ),
    CountryCode(
        id="honduras", name="Honduras", iso3="HND",
        census_label="Honduras", uscis_label="Honduras",
    ),
    CountryCode(
        id="venezuela", name="Venezuela", iso3="VEN",
        census_label="Venezuela", uscis_label="Venezuela",
    ),
    CountryCode(
        id="south-korea", name="South Korea", iso3="KOR",
        census_label="Korea", uscis_label="Korea, South",
        aliases=("Republic of Korea", "Korea (South)"),
    ),
    CountryCode(
        id="canada", name="Canada", iso3="CAN",
        census_label="Canada", uscis_label="Canada",
    ),
    CountryCode(
        id="haiti", name="Haiti", iso3="HTI",
        census_label="Haiti", uscis_label="Haiti",
    ),
    CountryCode(
        id="uk", name="United Kingdom", iso3="GBR",
        census_label="United Kingdom",
        uscis_label="United Kingdom",
        aliases=("Britain", "Great Britain", "England"),
    ),
    CountryCode(
        id="germany", name="Germany", iso3="DEU",
        census_label="Germany", uscis_label="Germany",
    ),
    CountryCode(
        id="brazil", name="Brazil", iso3="BRA",
        census_label="Brazil", uscis_label="Brazil",
    ),
    CountryCode(
        id="nigeria", name="Nigeria", iso3="NGA",
        census_label="Nigeria", uscis_label="Nigeria",
    ),
    CountryCode(
        id="pakistan", name="Pakistan", iso3="PAK",
        census_label="Pakistan", uscis_label="Pakistan",
    ),
    CountryCode(
        id="ireland", name="Ireland", iso3="IRL",
        census_label="Ireland", uscis_label="Ireland",
    ),
    CountryCode(
        id="italy", name="Italy", iso3="ITA",
        census_label="Italy", uscis_label="Italy",
    ),
)


_BY_ID = {c.id: c for c in COUNTRIES}
_BY_ISO3 = {c.iso3: c for c in COUNTRIES}


def by_id(country_id: str) -> CountryCode:
    """Look up by canonical graph node id. Raises KeyError if unknown."""
    return _BY_ID[country_id]


def by_iso3(iso3: str) -> CountryCode:
    """Look up by ISO 3166-1 alpha-3."""
    return _BY_ISO3[iso3.upper()]


def by_label(label: str) -> CountryCode | None:
    """Resolve a free-text label (any source) to a CountryCode, or None."""
    for c in COUNTRIES:
        if c.matches(label):
            return c
    return None


def all_ids() -> tuple[str, ...]:
    return tuple(c.id for c in COUNTRIES)


def all_iso3() -> tuple[str, ...]:
    return tuple(c.iso3 for c in COUNTRIES)
