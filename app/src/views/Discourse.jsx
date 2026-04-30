// Discourse view — sentiment of immigration speech over time.
// Wired to /sentiment when the discourse classifier checkpoint is published.

const SENTIMENT_AXES = [
  {
    key: "hostile",
    label: "Hostile",
    color: "#9f1239",
    desc: "Adversarial language toward immigrants as a group",
  },
  {
    key: "welcoming",
    label: "Welcoming",
    color: "#166534",
    desc: "Active warmth, integration framing, contribution language",
  },
  {
    key: "dehumanizing",
    label: "Dehumanizing",
    color: "#581c87",
    desc: "Animal / disease / invasion metaphors, denial of personhood",
  },
  {
    key: "assimilationist",
    label: "Assimilationist",
    color: "#1e3a8a",
    desc: "Pressure to drop language, religion, or culture of origin",
  },
];

const SOURCE_TYPES = [
  {
    key: "congress",
    label: "Congressional record",
    detail: "Floor speeches, committee hearings, member statements",
  },
  {
    key: "press",
    label: "Historical press",
    detail: "Library of Congress newspaper text from 1880-1963",
  },
  {
    key: "social",
    label: "Social media",
    detail: "Public statements from elected officials and major outlets",
  },
  {
    key: "platforms",
    label: "Party platforms",
    detail: "Comparative Manifesto Project codings of DNC and RNC platforms",
  },
];

export default function Discourse() {
  return (
    <div className="view view-discourse">
      <div className="discourse-header">
        <h1>Discourse</h1>
        <div className="discourse-sub">
          What people have said about immigration, and how it changed
        </div>
      </div>

      <div className="discourse-grid">
        <section className="discourse-card">
          <h3>Four axes of sentiment</h3>
          <ul className="legend-list">
            {SENTIMENT_AXES.map((a) => (
              <li key={a.key}>
                <span
                  className="legend-swatch"
                  style={{ background: a.color }}
                />
                <div>
                  <strong>{a.label}.</strong>{" "}
                  <span className="muted">{a.desc}</span>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="discourse-card">
          <h3>Where the corpus comes from</h3>
          <ul className="legend-list">
            {SOURCE_TYPES.map((s) => (
              <li key={s.key}>
                <span className="legend-marker" />
                <div>
                  <strong>{s.label}.</strong>{" "}
                  <span className="muted">{s.detail}</span>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="discourse-card discourse-card-wide">
          <h3>Coming soon</h3>
          <p>
            This view scores any piece of immigration text — a tweet, a
            floor speech, a 1924 newspaper editorial — on the four axes
            above, and lets you watch the corpus shift over time. The
            classifier ships with the system; the labeled corpus is being
            assembled.
          </p>
        </section>
      </div>
    </div>
  );
}
