import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { FALLBACK_GRAPH } from "./fallbackData";
import Graph from "./components/Graph";
import QueryBar from "./components/QueryBar";
import FilterPanel from "./components/FilterPanel";
import DetailPanel from "./components/DetailPanel";

const ALL_KINDS = new Set(["country", "visa", "law", "industry", "region"]);
const ALL_EDGES = new Set([
  "uses-visa", "enables", "restricts", "creates", "legalized",
  "works-in", "settles-in", "amends",
]);
const ALL_ERAS = new Set(["historic", "cold-war", "modern"]);

export default function App() {
  const [graphData, setGraphData] = useState(null);
  const [usingFallback, setUsingFallback] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    kinds: ALL_KINDS,
    edges: ALL_EDGES,
    eras: ALL_ERAS,
  });

  // ----- Load graph on mount, with API fallback -----
  useEffect(() => {
    api
      .graph()
      .then((data) => {
        setGraphData(data);
        setUsingFallback(false);
      })
      .catch(() => {
        // Backend unreachable → use bundled data so the demo still works
        setGraphData(FALLBACK_GRAPH);
        setUsingFallback(true);
      });
  }, []);

  // ----- Derived: which kinds are actually present (for filter UI) -----
  const kindsPresent = useMemo(() => {
    if (!graphData) return new Set();
    return new Set(graphData.nodes.map((n) => n.kind));
  }, [graphData]);

  // ----- Selected node + neighbors -----
  const selected = useMemo(() => {
    if (!graphData || !selectedNodeId) return null;
    return graphData.nodes.find((n) => n.id === selectedNodeId) ?? null;
  }, [graphData, selectedNodeId]);

  const neighbors = useMemo(() => {
    if (!graphData || !selectedNodeId) return [];
    const out = [];
    for (const l of graphData.links) {
      const s = typeof l.source === "object" ? l.source.id : l.source;
      const t = typeof l.target === "object" ? l.target.id : l.target;
      if (s === selectedNodeId) {
        const peer = graphData.nodes.find((n) => n.id === t);
        if (peer) out.push({ peer, kind: l.kind, dir: "out" });
      } else if (t === selectedNodeId) {
        const peer = graphData.nodes.find((n) => n.id === s);
        if (peer) out.push({ peer, kind: l.kind, dir: "in" });
      }
    }
    return out;
  }, [graphData, selectedNodeId]);

  // ----- Highlighted ids from query response (for graph emphasis) -----
  const highlightedIds = useMemo(() => {
    if (!response?.entities?.length) return new Set();
    return new Set(response.entities);
  }, [response]);

  // ----- Query handler -----
  const handleQuery = async (text) => {
    setLoading(true);
    if (usingFallback) {
      // No backend — do a simple client-side entity match
      const lower = text.toLowerCase();
      const matched = graphData.nodes
        .filter((n) => lower.includes(n.name.toLowerCase()) ||
                      lower.includes(n.id.replace(/-/g, " ")))
        .map((n) => n.id);
      setResponse({
        handler: "graph_lookup",
        entities: matched,
        answer: matched.length
          ? `Matched ${matched.length} entit${matched.length === 1 ? "y" : "ies"} (offline mode — backend not reachable).`
          : "No matches found. The backend is offline; only simple keyword matching is available.",
      });
      if (matched.length) setSelectedNodeId(matched[0]);
      setLoading(false);
      return;
    }
    try {
      const res = await api.query(text);
      setResponse(res);
      if (res.entities?.length) {
        setSelectedNodeId(res.entities[0]);
      }
    } catch (err) {
      setResponse({
        handler: "error",
        entities: [],
        answer: `Request failed: ${err.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="frame">
      {/* Masthead */}
      <div className="masthead">
        <div className="title">Migration Atlas</div>
        <div className="meta">
          {usingFallback ? "Offline · Bundled data" : "Live · API connected"}
        </div>
      </div>

      {/* Sub-head + query */}
      <div className="sub">
        <div>
          <h1>The shape of <em>arrival</em>.</h1>
        </div>
        <div className="lede">
          An interactive knowledge graph of U.S. immigration — countries of origin,
          visa pathways, landmark legislation, and the economic threads that
          connect them. Click any node to explore its relationships.
        </div>
        <QueryBar onQuery={handleQuery} loading={loading} />
      </div>

      {/* Main */}
      <div className="main">
        <FilterPanel
          filters={filters}
          setFilters={setFilters}
          kindsPresent={kindsPresent}
        />

        {graphData ? (
          <Graph
            data={graphData}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
            filters={filters}
            highlightedIds={highlightedIds}
          />
        ) : (
          <div className="graph-stage" style={{ display: "grid", placeItems: "center" }}>
            <div className="stage-overlay" style={{ position: "static" }}>LOADING GRAPH...</div>
          </div>
        )}

        <DetailPanel
          node={selected}
          neighbors={neighbors}
          response={response}
          onSelectNode={setSelectedNodeId}
        />
      </div>

      {/* Footer */}
      <div className="footer">
        <div>SOURCES · PEW · MPI · CENSUS ACS · USCIS · CATO 2026</div>
        <div className="ornament">✦ ✦ ✦</div>
        <div>v0.1.0</div>
      </div>
    </div>
  );
}
