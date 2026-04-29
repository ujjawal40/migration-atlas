// Discourse view — sentiment of immigration speech over time, decomposed by
// speaker affiliation. Currently a static mockup of the planned layout;
// wired to /sentiment in Phase B.

const SENTIMENT_AXES = [
  { key: "hostile", label: "Hostile", color: "#9f1239" },
  { key: "welcoming", label: "Welcoming", color: "#166534" },
  { key: "dehumanizing", label: "Dehumanizing", color: "#581c87" },
  { key: "assimilationist", label: "Assimilationist", color: "#1e3a8a" },
];

const SOURCE_TYPES = [
  { key: "congress", label: "Congressional record" },
  { key: "press", label: "Historical press" },
  { key: "social", label: "Social media" },
  { key: "platforms", label: "Party platforms" },
];

export default function Discourse() {
  return (
    <div className="view view-discourse">
      <div className="discourse-header">
        <h1>Discourse</h1>
        <div className="discourse-sub">
          Sentiment of immigration speech over time · Phase B preview
        </div>
      </div>

      <div className="discourse-grid">
        <section className="discourse-card">
          <h3>Sentiment axes</h3>
          <ul className="legend-list">
            {SENTIMENT_AXES.map((a) => (
              <li key={a.key}>
                <span
                  className="legend-swatch"
                  style={{ background: a.color }}
                />
                {a.label}
              </li>
            ))}
          </ul>
        </section>

        <section className="discourse-card">
          <h3>Source corpora</h3>
          <ul className="legend-list">
            {SOURCE_TYPES.map((s) => (
              <li key={s.key}>
                <span className="legend-marker" />
                {s.label}
              </li>
            ))}
          </ul>
        </section>

        <section className="discourse-card discourse-card-wide">
          <h3>Coming in Phase B</h3>
          <ol className="discourse-roadmap">
            <li>Voteview / DW-NOMINATE legislator metadata.</li>
            <li>Comparative Manifesto Project party-platform corpus.</li>
            <li>Chronicling America historical newspaper text.</li>
            <li>HateXplain / Davidson / Founta hate-speech labels.</li>
            <li>Multi-axis sentiment classifier extension of the stance head.</li>
            <li>BERTopic discourse topic model.</li>
            <li><code>POST /sentiment</code> endpoint and this view's wiring.</li>
          </ol>
        </section>
      </div>
    </div>
  );
}
