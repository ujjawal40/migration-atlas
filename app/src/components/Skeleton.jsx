// Skeleton — generic shimmer placeholder for loading states.
// Three flavors: line (text), block (cards), graph (force-directed stand-in).

export function SkeletonLine({ width = "100%" }) {
  return <span className="sk sk-line" style={{ width }} />;
}

export function SkeletonBlock({ height = 120 }) {
  return <div className="sk sk-block" style={{ height }} />;
}

export function SkeletonGraph() {
  return (
    <div className="sk-graph" aria-label="Loading graph">
      <div className="sk-graph-grid" />
      <div className="sk-graph-msg">Loading the graph…</div>
    </div>
  );
}
