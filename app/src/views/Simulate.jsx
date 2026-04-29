// Simulate view — counterfactual exploration. "What if Italians instead?"
// Wired in Phase C once the parameter-swap simulator and /simulate endpoint land.

export default function Simulate() {
  return (
    <div className="view view-simulate">
      <div className="view-placeholder">
        <h2>Simulate</h2>
        <p>
          Counterfactual flow simulation. Side-by-side real vs. swap series
          with parameter sliders. Phase C deliverable.
        </p>
      </div>
    </div>
  );
}
