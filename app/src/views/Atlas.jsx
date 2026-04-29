// Atlas view — interactive knowledge graph.
// Loads /graph from the backend, falls back to bundled data when offline,
// and surfaces filter / selection / NL-query controls around the graph itself.

import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { FALLBACK_GRAPH } from "../fallbackData";
import Graph from "../components/Graph";
import QueryBar from "../components/QueryBar";
import FilterPanel from "../components/FilterPanel";
import DetailPanel from "../components/DetailPanel";

const ALL_KINDS = new Set(["country", "visa", "law", "industry", "region"]);
const ALL_EDGES = new Set([
  "uses-visa", "enables", "restricts", "creates", "legalized",
  "works-in", "settles-in", "amends",
]);
const ALL_ERAS = new Set(["historic", "cold-war", "modern"]);

export default function Atlas() {
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

  useEffect(() => {
    api
      .graph()
      .then((data) => {
        setGraphData(data);
        setUsingFallback(false);
      })
      .catch(() => {
        setGraphData(FALLBACK_GRAPH);
        setUsingFallback(true);
      });
  }, []);

  const kindsPresent = useMemo(() => {
    if (!graphData) return new Set();
    return new Set(graphData.nodes.map((n) => n.kind));
  }, [graphData]);

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

  const highlightedIds = useMemo(() => {
    if (!response?.entities?.length) return new Set();
    return new Set(response.entities);
  }, [response]);

  const handleQuery = async (text) => {
    setLoading(true);
    if (usingFallback) {
      const lower = text.toLowerCase();
      const matched = graphData.nodes
        .filter((n) =>
          lower.includes(n.name.toLowerCase()) ||
          lower.includes(n.id.replace(/-/g, " "))
        )
        .map((n) => n.id);
      setResponse({
        handler: "graph_lookup",
        entities: matched,
        answer: matched.length
          ? `Matched ${matched.length} entit${matched.length === 1 ? "y" : "ies"} (offline mode).`
          : "No matches found. Backend offline; only keyword matching available.",
      });
      if (matched.length) setSelectedNodeId(matched[0]);
      setLoading(false);
      return;
    }
    try {
      const res = await api.query(text);
      setResponse(res);
      if (res.entities?.length) setSelectedNodeId(res.entities[0]);
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
    <div className="view view-atlas">
      <div className="sub">
        <div>
          <h1>The shape of <em>arrival</em>.</h1>
        </div>
        <div className="lede">
          An interactive knowledge graph of U.S. immigration — countries of origin,
          visa pathways, landmark legislation, and the economic threads that
          connect them. Click any node to explore its relationships.
          {usingFallback && <em> · Backend offline; using bundled data.</em>}
        </div>
        <QueryBar onQuery={handleQuery} loading={loading} />
      </div>

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
    </div>
  );
}
