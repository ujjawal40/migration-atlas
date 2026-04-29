// Timeline view — synchronized history across legislation, flows, discourse,
// and literature. The cross-cutting view that ties every other view together.
// Currently a static structural mockup; reads from /timeline once that exists.

const TRACKS = [
  { id: "laws", label: "Legislation", color: "#581c87" },
  { id: "flows", label: "Flows", color: "#c2410c" },
  { id: "discourse", label: "Discourse", color: "#1e3a8a" },
  { id: "literature", label: "Literature", color: "#115e59" },
];

const MILESTONES = [
  { year: 1882, track: "laws", label: "Chinese Exclusion Act" },
  { year: 1912, track: "literature", label: "The Promised Land (Antin)" },
  { year: 1924, track: "laws", label: "Immigration Act / national-origins quotas" },
  { year: 1942, track: "flows", label: "Bracero Program begins" },
  { year: 1965, track: "laws", label: "Hart-Celler Act (INA 1965)" },
  { year: 1980, track: "flows", label: "Mariel boatlift" },
  { year: 1986, track: "laws", label: "IRCA legalization + employer sanctions" },
  { year: 1989, track: "literature", label: "Jasmine (Mukherjee)" },
  { year: 1990, track: "laws", label: "Immigration Act of 1990 (H-1B, EB-5, TPS, DV)" },
  { year: 2007, track: "flows", label: "Mexican net migration falls to zero" },
  { year: 2012, track: "laws", label: "DACA established" },
  { year: 2017, track: "flows", label: "Wet-foot/dry-foot terminated" },
];

const YEAR_MIN = 1880;
const YEAR_MAX = 2030;

function pct(year) {
  return ((year - YEAR_MIN) / (YEAR_MAX - YEAR_MIN)) * 100;
}

export default function Timeline() {
  return (
    <div className="view view-timeline">
      <div className="timeline-header">
        <h1>Timeline</h1>
        <div className="timeline-sub">
          Synchronized history · {YEAR_MIN}–{YEAR_MAX}
        </div>
      </div>

      <div className="timeline-axis">
        {[1880, 1900, 1920, 1940, 1960, 1980, 2000, 2020].map((y) => (
          <span
            key={y}
            className="axis-tick"
            style={{ left: `${pct(y)}%` }}
          >
            {y}
          </span>
        ))}
      </div>

      <div className="timeline-tracks">
        {TRACKS.map((t) => (
          <div key={t.id} className="timeline-track">
            <div className="timeline-label">{t.label}</div>
            <div className="timeline-rail">
              {MILESTONES.filter((m) => m.track === t.id).map((m) => (
                <div
                  key={m.year + m.label}
                  className="timeline-marker"
                  style={{ left: `${pct(m.year)}%`, background: t.color }}
                  title={`${m.year} — ${m.label}`}
                >
                  <span className="timeline-tooltip">
                    {m.year} · {m.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
