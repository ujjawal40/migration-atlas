// Shared UI constants.

export const KIND_COLORS = {
  country: "#c2410c",
  visa: "#1e3a8a",
  law: "#581c87",
  industry: "#115e59",
  region: "#9f1239",
};

export const KIND_LABELS = {
  country: "Country",
  visa: "Visa Type",
  law: "Law / Policy",
  industry: "Industry",
  region: "Region",
};

export const EDGE_LABELS = {
  "uses-visa": "uses visa",
  restricts: "restricted by",
  enables: "enabled by",
  creates: "created",
  legalized: "legalized",
  "works-in": "concentrated in",
  "settles-in": "settles in",
  amends: "amends",
};

export const ERA_LABELS = {
  historic: "Pre-1924 (historic)",
  "cold-war": "1924–1980 (Cold War)",
  modern: "Post-1965 (modern)",
};

export const PRESET_QUERIES = [
  { label: "1965 Act & origins", q: "How did the 1965 Immigration Act change origins?" },
  { label: "H-1B network", q: "Which countries are connected to the H-1B visa?" },
  { label: "Forecast Mexico", q: "Forecast Mexico migration in 5 years" },
  { label: "Similar to Vietnam", q: "Find countries similar to Vietnam" },
  { label: "Wage effects", q: "What is the wage effect of low-skill immigration?" },
];

// Node radius depends on kind + population (for countries).
export const nodeRadius = (n) => {
  if (n.kind === "country") {
    if (!n.foreign_born_us) return 8;
    return Math.max(8, Math.min(28, Math.sqrt(n.foreign_born_us) / 320));
  }
  if (n.kind === "visa") return 12;
  if (n.kind === "law") return 11;
  if (n.kind === "industry") return 13;
  return 10;
};
