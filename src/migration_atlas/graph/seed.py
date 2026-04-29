"""Seed graph data — countries, visas, laws, industries, and their connections.

This is the same data that powers the interactive prototype, structured as
Python objects for the build pipeline. In Phase 2 / 3 this will be replaced by
ETL outputs from `migration_atlas.data` consuming Census ACS, USCIS, etc.
"""
from __future__ import annotations

from migration_atlas.graph.schema import Edge, EdgeKind, Node, NodeKind

COUNTRIES: list[Node] = [
    Node(id="mexico", name="Mexico", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 11_400_000, "immigrant_share": 0.220,
                     "top_destination_state": "California", "era": "modern"}),
    Node(id="india", name="India", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 3_200_000, "immigrant_share": 0.060, "era": "modern"}),
    Node(id="china", name="China", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 3_000_000, "immigrant_share": 0.060, "era": "modern"}),
    Node(id="philippines", name="Philippines", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 2_100_000, "immigrant_share": 0.040, "era": "modern"}),
    Node(id="cuba", name="Cuba", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_700_000, "immigrant_share": 0.033,
                     "top_destination_state": "Florida", "era": "cold-war"}),
    Node(id="el-salvador", name="El Salvador", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_600_000, "immigrant_share": 0.031, "era": "modern"}),
    Node(id="dominican-republic", name="Dominican Republic", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_400_000, "immigrant_share": 0.027,
                     "top_destination_state": "New York", "era": "cold-war"}),
    Node(id="guatemala", name="Guatemala", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_400_000, "immigrant_share": 0.027, "era": "modern"}),
    Node(id="vietnam", name="Vietnam", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_400_000, "immigrant_share": 0.027, "era": "cold-war"}),
    Node(id="colombia", name="Colombia", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_200_000, "immigrant_share": 0.023, "era": "modern"}),
    Node(id="honduras", name="Honduras", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_100_000, "immigrant_share": 0.021, "era": "modern"}),
    Node(id="venezuela", name="Venezuela", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_100_000, "immigrant_share": 0.021,
                     "top_destination_state": "Florida", "era": "modern"}),
    Node(id="south-korea", name="South Korea", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 1_000_000, "immigrant_share": 0.019, "era": "cold-war"}),
    Node(id="canada", name="Canada", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 800_000, "immigrant_share": 0.015, "era": "historic"}),
    Node(id="haiti", name="Haiti", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 730_000, "immigrant_share": 0.014, "era": "modern"}),
    Node(id="uk", name="United Kingdom", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 700_000, "immigrant_share": 0.014, "era": "historic"}),
    Node(id="germany", name="Germany", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 540_000, "immigrant_share": 0.010, "era": "historic"}),
    Node(id="brazil", name="Brazil", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 500_000, "immigrant_share": 0.010, "era": "modern"}),
    Node(id="nigeria", name="Nigeria", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 480_000, "immigrant_share": 0.009, "era": "modern"}),
    Node(id="pakistan", name="Pakistan", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 430_000, "immigrant_share": 0.008, "era": "modern"}),
    Node(id="ireland", name="Ireland", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 130_000, "immigrant_share": 0.003, "era": "historic"}),
    Node(id="italy", name="Italy", kind=NodeKind.COUNTRY,
         properties={"foreign_born_us": 130_000, "immigrant_share": 0.003, "era": "historic"}),
]

VISAS: list[Node] = [
    Node(id="h-1b", name="H-1B", kind=NodeKind.VISA,
         properties={"annual_cap": 85_000, "year_established": 1990, "top_country": "India"}),
    Node(id="f-1", name="F-1", kind=NodeKind.VISA,
         properties={"annual_cap": None, "top_country": "India / China"}),
    Node(id="eb-5", name="EB-5", kind=NodeKind.VISA,
         properties={"annual_cap": 10_000, "year_established": 1990}),
    Node(id="family-based", name="Family-Based", kind=NodeKind.VISA,
         properties={"year_established": 1965}),
    Node(id="tps", name="TPS", kind=NodeKind.VISA,
         properties={"year_established": 1990}),
    Node(id="refugee", name="Refugee / Asylee", kind=NodeKind.VISA,
         properties={"year_established": 1980}),
    Node(id="tn", name="TN (USMCA)", kind=NodeKind.VISA,
         properties={"year_established": 1994}),
    Node(id="dv-lottery", name="Diversity Lottery", kind=NodeKind.VISA,
         properties={"annual_cap": 50_000, "year_established": 1990}),
    Node(id="l-1", name="L-1", kind=NodeKind.VISA, properties={}),
]

LAWS: list[Node] = [
    Node(id="chinese-exclusion-1882", name="Chinese Exclusion Act (1882)",
         kind=NodeKind.LAW,
         properties={"year_enacted": 1882, "year_repealed": 1943}),
    Node(id="immigration-act-1924", name="Immigration Act (1924)",
         kind=NodeKind.LAW, properties={"year_enacted": 1924, "year_repealed": 1965}),
    Node(id="ina-1965", name="Immigration & Nationality Act (1965)",
         kind=NodeKind.LAW, properties={"year_enacted": 1965}),
    Node(id="irca-1986", name="IRCA (1986)",
         kind=NodeKind.LAW, properties={"year_enacted": 1986}),
    Node(id="immigration-act-1990", name="Immigration Act (1990)",
         kind=NodeKind.LAW, properties={"year_enacted": 1990}),
    Node(id="refugee-act-1980", name="Refugee Act (1980)",
         kind=NodeKind.LAW, properties={"year_enacted": 1980}),
    Node(id="daca-2012", name="DACA (2012)",
         kind=NodeKind.LAW, properties={"year_enacted": 2012}),
    Node(id="bracero-1942", name="Bracero Program (1942-64)",
         kind=NodeKind.LAW, properties={"year_enacted": 1942, "year_repealed": 1964}),
]

INDUSTRIES: list[Node] = [
    Node(id="tech", name="Technology", kind=NodeKind.INDUSTRY,
         properties={"immigrant_share": 0.25, "top_origin_corridors": ["india", "china"]}),
    Node(id="healthcare", name="Healthcare", kind=NodeKind.INDUSTRY,
         properties={"immigrant_share": 0.18, "top_origin_corridors": ["philippines", "india"]}),
    Node(id="construction", name="Construction", kind=NodeKind.INDUSTRY,
         properties={"unauthorized_share": 0.15, "top_origin_corridors": ["mexico"]}),
    Node(id="agriculture", name="Agriculture", kind=NodeKind.INDUSTRY,
         properties={"unauthorized_share": 0.24, "top_origin_corridors": ["mexico"]}),
    Node(id="hospitality", name="Hospitality", kind=NodeKind.INDUSTRY,
         properties={"unauthorized_share": 0.08}),
]

EDGES: list[Edge] = [
    # Country -> Visa
    Edge(source="india", target="h-1b", kind=EdgeKind.USES_VISA, weight=0.70),
    Edge(source="india", target="f-1", kind=EdgeKind.USES_VISA),
    Edge(source="india", target="l-1", kind=EdgeKind.USES_VISA),
    Edge(source="india", target="eb-5", kind=EdgeKind.USES_VISA),
    Edge(source="china", target="f-1", kind=EdgeKind.USES_VISA),
    Edge(source="china", target="eb-5", kind=EdgeKind.USES_VISA),
    Edge(source="china", target="h-1b", kind=EdgeKind.USES_VISA),
    Edge(source="mexico", target="family-based", kind=EdgeKind.USES_VISA),
    Edge(source="mexico", target="tn", kind=EdgeKind.USES_VISA),
    Edge(source="philippines", target="family-based", kind=EdgeKind.USES_VISA),
    Edge(source="cuba", target="refugee", kind=EdgeKind.USES_VISA),
    Edge(source="vietnam", target="refugee", kind=EdgeKind.USES_VISA),
    Edge(source="el-salvador", target="tps", kind=EdgeKind.USES_VISA),
    Edge(source="honduras", target="tps", kind=EdgeKind.USES_VISA),
    Edge(source="haiti", target="tps", kind=EdgeKind.USES_VISA),
    Edge(source="venezuela", target="tps", kind=EdgeKind.USES_VISA),
    Edge(source="nigeria", target="dv-lottery", kind=EdgeKind.USES_VISA),
    Edge(source="nigeria", target="f-1", kind=EdgeKind.USES_VISA),
    Edge(source="canada", target="tn", kind=EdgeKind.USES_VISA),
    Edge(source="uk", target="l-1", kind=EdgeKind.USES_VISA),
    Edge(source="south-korea", target="family-based", kind=EdgeKind.USES_VISA),
    Edge(source="pakistan", target="f-1", kind=EdgeKind.USES_VISA),
    Edge(source="guatemala", target="tps", kind=EdgeKind.USES_VISA),
    Edge(source="dominican-republic", target="family-based", kind=EdgeKind.USES_VISA),

    # Law -> Country (effects)
    Edge(source="chinese-exclusion-1882", target="china", kind=EdgeKind.RESTRICTS),
    Edge(source="immigration-act-1924", target="italy", kind=EdgeKind.RESTRICTS),
    Edge(source="immigration-act-1924", target="ireland", kind=EdgeKind.RESTRICTS),
    Edge(source="ina-1965", target="india", kind=EdgeKind.ENABLES),
    Edge(source="ina-1965", target="china", kind=EdgeKind.ENABLES),
    Edge(source="ina-1965", target="philippines", kind=EdgeKind.ENABLES),
    Edge(source="ina-1965", target="south-korea", kind=EdgeKind.ENABLES),
    Edge(source="ina-1965", target="mexico", kind=EdgeKind.ENABLES),
    Edge(source="ina-1965", target="pakistan", kind=EdgeKind.ENABLES),
    Edge(source="irca-1986", target="mexico", kind=EdgeKind.LEGALIZED),
    Edge(source="bracero-1942", target="mexico", kind=EdgeKind.ENABLES),
    Edge(source="refugee-act-1980", target="vietnam", kind=EdgeKind.ENABLES),
    Edge(source="refugee-act-1980", target="cuba", kind=EdgeKind.ENABLES),

    # Law -> Visa (creates)
    Edge(source="immigration-act-1990", target="h-1b", kind=EdgeKind.CREATES),
    Edge(source="immigration-act-1990", target="eb-5", kind=EdgeKind.CREATES),
    Edge(source="immigration-act-1990", target="dv-lottery", kind=EdgeKind.CREATES),
    Edge(source="immigration-act-1990", target="tps", kind=EdgeKind.CREATES),
    Edge(source="ina-1965", target="family-based", kind=EdgeKind.CREATES),
    Edge(source="refugee-act-1980", target="refugee", kind=EdgeKind.CREATES),

    # Country -> Industry
    Edge(source="india", target="tech", kind=EdgeKind.WORKS_IN),
    Edge(source="china", target="tech", kind=EdgeKind.WORKS_IN),
    Edge(source="philippines", target="healthcare", kind=EdgeKind.WORKS_IN),
    Edge(source="india", target="healthcare", kind=EdgeKind.WORKS_IN),
    Edge(source="mexico", target="construction", kind=EdgeKind.WORKS_IN),
    Edge(source="mexico", target="agriculture", kind=EdgeKind.WORKS_IN),
    Edge(source="mexico", target="hospitality", kind=EdgeKind.WORKS_IN),
    Edge(source="el-salvador", target="construction", kind=EdgeKind.WORKS_IN),
    Edge(source="guatemala", target="agriculture", kind=EdgeKind.WORKS_IN),
    Edge(source="honduras", target="construction", kind=EdgeKind.WORKS_IN),
]


def all_nodes() -> list[Node]:
    """Return all seed nodes."""
    return COUNTRIES + VISAS + LAWS + INDUSTRIES


def all_edges() -> list[Edge]:
    """Return all seed edges."""
    return list(EDGES)
