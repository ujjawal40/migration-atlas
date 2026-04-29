// Simulate view — counterfactual flow exploration.
// Static mockup of the parameter-swap UI; wired to /simulate in Phase C.

const PRESETS = [
  {
    id: "italian-1965",
    title: "Italians instead of Mexicans, 1965-2024",
    summary:
      "Substitute Italian-1900–1924 fertility and emigration intensity into the post-1965 Mexican corridor.",
  },
  {
    id: "no-1965-act",
    title: "No 1965 Immigration Act",
    summary:
      "Rerun history with the national-origins quota system left in place. What does the Asian-origin corridor look like?",
  },
  {
    id: "no-irca",
    title: "No 1986 IRCA legalization",
    summary:
      "Rerun the post-1986 Mexican unauthorized population trajectory without the legalization channel.",
  },
  {
    id: "h1b-doubled",
    title: "H-1B cap doubled in 1998",
    summary:
      "What does Indian-origin technology employment look like with 170,000 H-1Bs/year from 1998 onward?",
  },
];

export default function Simulate() {
  return (
    <div className="view view-simulate">
      <div className="simulate-header">
        <h1>Simulate</h1>
        <div className="simulate-sub">
          Counterfactual flow exploration · Phase C preview
        </div>
        <p className="simulate-disclaimer">
          Simulations are evocative, not predictive. They re-run historical
          flows with origin parameters substituted; the output is a
          structural what-if, not a causal claim.
        </p>
      </div>

      <div className="simulate-presets">
        {PRESETS.map((p) => (
          <article key={p.id} className="preset-card">
            <h3>{p.title}</h3>
            <p>{p.summary}</p>
            <button type="button" className="preset-disabled" disabled>
              Run (available in Phase C)
            </button>
          </article>
        ))}
      </div>

      <div className="simulate-engines">
        <h3>Engines</h3>
        <ul>
          <li>
            <strong>Parameter-swap</strong> — re-run flow series with origin
            parameters substituted. Cheap; ships first in Phase C.
          </li>
          <li>
            <strong>Agent-based</strong> — population of agents with
            policy-gated migration utility functions. Calibrated to history,
            then used for counterfactual exploration. Phase C.2.
          </li>
        </ul>
      </div>
    </div>
  );
}
