import { KIND_COLORS, KIND_LABELS, EDGE_LABELS, ERA_LABELS } from "../constants";

export default function FilterPanel({ filters, setFilters, kindsPresent }) {
  const toggle = (group, value) => {
    const next = new Set(filters[group]);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    setFilters({ ...filters, [group]: next });
  };

  return (
    <div className="panel-left">
      <div className="panel-title">Node Types</div>
      <div className="filter-group">
        {Object.entries(KIND_LABELS).map(([k, label]) => {
          if (!kindsPresent.has(k)) return null;
          return (
            <div className="legend-item" key={k}>
              <input
                type="checkbox"
                id={`ft-${k}`}
                checked={filters.kinds.has(k)}
                onChange={() => toggle("kinds", k)}
              />
              <span
                className="legend-dot"
                style={{ background: KIND_COLORS[k] }}
              />
              <span className="legend-label">{label}</span>
            </div>
          );
        })}
      </div>

      <div className="panel-title">Edge Types</div>
      <div className="filter-group">
        {Object.entries(EDGE_LABELS).map(([k, label]) => (
          <div className="filter-toggle" key={k}>
            <input
              type="checkbox"
              id={`fe-${k}`}
              checked={filters.edges.has(k)}
              onChange={() => toggle("edges", k)}
            />
            <label htmlFor={`fe-${k}`}>{label}</label>
          </div>
        ))}
      </div>

      <div className="panel-title">Eras</div>
      <div className="filter-group">
        {Object.entries(ERA_LABELS).map(([k, label]) => (
          <div className="filter-toggle" key={k}>
            <input
              type="checkbox"
              id={`fr-${k}`}
              checked={filters.eras.has(k)}
              onChange={() => toggle("eras", k)}
            />
            <label htmlFor={`fr-${k}`}>{label}</label>
          </div>
        ))}
      </div>
    </div>
  );
}
