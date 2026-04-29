import { KIND_COLORS, KIND_LABELS, EDGE_LABELS } from "../constants";

const formatNumber = (n) => {
  if (n == null) return "—";
  if (typeof n !== "number") return String(n);
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
};

const formatPercent = (n) => {
  if (n == null) return "—";
  if (n <= 1) return `${(n * 100).toFixed(1)}%`;
  return `${n.toFixed(1)}%`;
};

function NodeDetail({ node, neighbors, onSelectNode }) {
  if (!node) {
    return (
      <div className="detail-empty">
        Select any node in the graph — a country, visa, law, or industry — to inspect its data and connections.
      </div>
    );
  }

  return (
    <>
      <div className="detail-name">{node.name}</div>
      <div className="detail-kind">{KIND_LABELS[node.kind] || node.kind}</div>

      {node.kind === "country" && (
        <>
          {node.foreign_born_us != null && (
            <Stat k="Foreign-born in U.S." v={formatNumber(node.foreign_born_us)} />
          )}
          {node.immigrant_share != null && (
            <Stat k="Share of immigrants" v={formatPercent(node.immigrant_share)} />
          )}
          {node.top_destination_state && (
            <Stat k="Top destination" v={node.top_destination_state} />
          )}
          {node.era && <Stat k="Era" v={node.era} />}
        </>
      )}
      {node.kind === "visa" && (
        <>
          {node.annual_cap != null && (
            <Stat k="Annual cap" v={formatNumber(node.annual_cap)} />
          )}
          {node.year_established && (
            <Stat k="Established" v={node.year_established} />
          )}
          {node.top_country && <Stat k="Top country" v={node.top_country} />}
        </>
      )}
      {node.kind === "law" && (
        <>
          {node.year_enacted && <Stat k="Year enacted" v={node.year_enacted} />}
          {node.year_repealed && <Stat k="Year repealed" v={node.year_repealed} />}
          {node.stance_restrictiveness != null && (
            <Stat k="Restrictiveness" v={node.stance_restrictiveness.toFixed(2)} />
          )}
        </>
      )}
      {node.kind === "industry" && (
        <>
          {node.immigrant_share != null && (
            <Stat k="Immigrant share" v={formatPercent(node.immigrant_share)} />
          )}
          {node.unauthorized_share != null && (
            <Stat k="Unauthorized share" v={formatPercent(node.unauthorized_share)} />
          )}
        </>
      )}

      {neighbors.length > 0 && (
        <div className="related" style={{ marginTop: 18 }}>
          <div className="panel-title" style={{ marginTop: 8 }}>
            Connections ({neighbors.length})
          </div>
          {neighbors.map(({ peer, kind, dir }) => (
            <div
              key={`${peer.id}-${kind}-${dir}`}
              className="related-item"
              onClick={() => onSelectNode?.(peer.id)}
            >
              <div>
                <div className="rel-name" style={{ fontWeight: 600 }}>{peer.name}</div>
                <div className="rel-edge">
                  {dir === "out" ? "→" : "←"} {EDGE_LABELS[kind] || kind}
                </div>
              </div>
              <div
                style={{
                  width: 10,
                  height: 10,
                  background: KIND_COLORS[peer.kind],
                  border: "1px solid var(--ink)",
                }}
              />
            </div>
          ))}
        </div>
      )}
    </>
  );
}

const Stat = ({ k, v }) => (
  <div className="detail-stat">
    <span className="k">{k}</span>
    <span className="v">{v}</span>
  </div>
);

function QueryResponse({ response }) {
  if (!response) return null;

  return (
    <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: "1px dashed var(--paper-2)" }}>
      <div className="detail-kind" style={{ marginBottom: 8 }}>
        Query · {response.handler.replace("_", " ")}
      </div>
      {response.entities?.length > 0 && (
        <div className="rel-edge" style={{ marginBottom: 12 }}>
          Matched: {response.entities.join(", ")}
        </div>
      )}
      {response.answer && (
        <div className="detail-narrative" style={{ marginTop: 0 }}>
          {response.answer}
        </div>
      )}
      {response.forecast && response.forecast.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <div className="rel-edge" style={{ marginBottom: 6 }}>Forecast</div>
          {response.forecast.map((row, i) => (
            <div key={i} className="detail-stat">
              <span className="k">{String(row.year).slice(0, 4)}</span>
              <span className="v">{formatNumber(Math.round(row.yhat))}</span>
            </div>
          ))}
        </div>
      )}
      {response.similar && response.similar.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <div className="rel-edge" style={{ marginBottom: 6 }}>Similar nodes</div>
          {response.similar.slice(0, 8).map((s) => (
            <div key={s.id} className="detail-stat">
              <span className="k">{s.id}</span>
              <span className="v">{s.score.toFixed(3)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DetailPanel({ node, neighbors, response, onSelectNode }) {
  return (
    <div className="panel-right">
      <div className="panel-title">Detail</div>
      <QueryResponse response={response} />
      <NodeDetail node={node} neighbors={neighbors} onSelectNode={onSelectNode} />
    </div>
  );
}
