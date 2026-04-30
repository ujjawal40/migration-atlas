// Simulate view — counterfactual flow exploration.
// Wired to /simulate when the simulator engine ships.

const PRESETS = [
  {
    id: "italian-1965",
    title: "Italians instead of Mexicans, 1965-2024",
    summary:
      "What if the 1965 Immigration Act had re-routed Italian-1900s flows into the post-1965 corridor that actually went to Mexico?",
  },
  {
    id: "no-1965-act",
    title: "What if the 1965 Act never passed?",
    summary:
      "Re-run history with the national-origins quota system left in place. How would the Asian-origin corridor look?",
  },
  {
    id: "no-irca",
    title: "No 1986 IRCA legalization",
    summary:
      "What does the post-1986 Mexican unauthorized population trajectory look like without the legalization pathway?",
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
          Counterfactual flow exploration
        </div>
        <p className="simulate-disclaimer">
          These are evocative simulations, not predictions. Each one re-runs
          the historical flow series with a single structural parameter
          changed, so you can see what the shape of the corridor looks like
          under a different policy. They do not estimate causal effects.
        </p>
      </div>

      <div className="simulate-presets">
        {PRESETS.map((p) => (
          <article key={p.id} className="preset-card">
            <h3>{p.title}</h3>
            <p>{p.summary}</p>
            <button type="button" className="preset-disabled" disabled>
              Run · simulator in progress
            </button>
          </article>
        ))}
      </div>

      <div className="simulate-engines">
        <h3>How the simulator works</h3>
        <ul>
          <li>
            <strong>Parameter-swap.</strong> Re-runs the flow series with one
            origin parameter substituted (e.g., Italian-1900-1924 fertility
            into the Mexican-2000-2024 series). Cheap; ships first.
          </li>
          <li>
            <strong>Agent-based.</strong> A population of agents with
            policy-gated migration utility functions. Calibrated to history
            first, then used for counterfactual exploration.
          </li>
        </ul>
      </div>
    </div>
  );
}
