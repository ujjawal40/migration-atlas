import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { KIND_COLORS, nodeRadius } from "../constants";

/**
 * Force-directed knowledge graph.
 *
 * Props:
 *   data            — { nodes, links }
 *   selectedNodeId  — id of the currently focused node (highlighted)
 *   onSelectNode    — fired when a node is clicked
 *   filters         — { kinds: Set, edges: Set, eras: Set }
 *   highlightedIds  — Set of node ids to emphasize (e.g., from a query response)
 */
export default function Graph({
  data,
  selectedNodeId,
  onSelectNode,
  filters,
  highlightedIds,
}) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const simulationRef = useRef(null);
  const zoomRef = useRef(null);

  // ----- Build / rebuild simulation when data changes -----
  useEffect(() => {
    if (!data || !data.nodes.length || !svgRef.current || !containerRef.current) {
      return;
    }
    const container = containerRef.current;
    const w = container.clientWidth;
    const h = container.clientHeight;

    const svg = d3
      .select(svgRef.current)
      .attr("viewBox", `0 0 ${w} ${h}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    svg.selectAll("*").remove();

    const zoom = d3.zoom().scaleExtent([0.4, 3]).on("zoom", (event) => {
      gZoom.attr("transform", event.transform);
    });
    svg.call(zoom);
    zoomRef.current = { svg, zoom };

    const gZoom = svg.append("g");

    // Defensive copies so D3 can mutate
    const nodes = data.nodes.map((d) => ({ ...d }));
    const links = data.links.map((d) => ({ ...d }));

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d) => d.id)
          .distance((d) => (d.kind === "creates" ? 70 : d.kind === "works-in" ? 90 : 110))
          .strength(0.45)
      )
      .force("charge", d3.forceManyBody().strength(-340))
      .force("center", d3.forceCenter(w / 2, h / 2))
      .force(
        "collision",
        d3.forceCollide().radius((d) => nodeRadius(d) + 16)
      )
      .force("x", d3.forceX(w / 2).strength(0.04))
      .force("y", d3.forceY(h / 2).strength(0.05));

    simulationRef.current = simulation;

    const linkSel = gZoom
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("data-edge", (d) => d.kind);

    const nodeG = gZoom
      .append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", "node-group")
      .attr("data-id", (d) => d.id)
      .attr("data-kind", (d) => d.kind)
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation();
        onSelectNode?.(d.id);
      })
      .call(
        d3
          .drag()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    nodeG
      .append("circle")
      .attr("class", "node-circle")
      .attr("r", (d) => nodeRadius(d))
      .attr("fill", (d) => KIND_COLORS[d.kind] || "#999");

    nodeG
      .append("text")
      .attr("class", "node-label")
      .attr("dy", (d) => nodeRadius(d) + 14)
      .text((d) => d.name);

    svg.on("click", () => onSelectNode?.(null));

    simulation.on("tick", () => {
      linkSel
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      nodeG.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [data, onSelectNode]);

  // ----- Apply selection / highlight styling -----
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const nodeG = svg.selectAll("g.node-group");
    const linkSel = svg.selectAll("line.link");

    // Reset
    nodeG.classed("dimmed", false);
    nodeG.select("circle").classed("selected", false);
    linkSel.classed("highlighted", false).classed("dimmed", false);

    const focusId = selectedNodeId;
    if (focusId) {
      const neighbors = new Set([focusId]);
      data.links.forEach((l) => {
        const s = typeof l.source === "object" ? l.source.id : l.source;
        const t = typeof l.target === "object" ? l.target.id : l.target;
        if (s === focusId) neighbors.add(t);
        if (t === focusId) neighbors.add(s);
      });
      nodeG.classed("dimmed", (d) => !neighbors.has(d.id));
      nodeG.filter((d) => d.id === focusId).select("circle").classed("selected", true);
      linkSel
        .classed("dimmed", (l) => {
          const s = typeof l.source === "object" ? l.source.id : l.source;
          const t = typeof l.target === "object" ? l.target.id : l.target;
          return !(s === focusId || t === focusId);
        })
        .classed("highlighted", (l) => {
          const s = typeof l.source === "object" ? l.source.id : l.source;
          const t = typeof l.target === "object" ? l.target.id : l.target;
          return s === focusId || t === focusId;
        });
    } else if (highlightedIds && highlightedIds.size > 0) {
      nodeG.classed("dimmed", (d) => !highlightedIds.has(d.id));
    }
  }, [selectedNodeId, highlightedIds, data]);

  // ----- Apply filters -----
  useEffect(() => {
    if (!svgRef.current || !filters) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("g.node-group").style("display", (d) => {
      if (!filters.kinds.has(d.kind)) return "none";
      if (d.kind === "country" && d.era && !filters.eras.has(d.era)) return "none";
      return null;
    });
    svg.selectAll("line.link").style("display", (l) => {
      if (!filters.edges.has(l.kind)) return "none";
      const sn = typeof l.source === "object" ? l.source : data.nodes.find((n) => n.id === l.source);
      const tn = typeof l.target === "object" ? l.target : data.nodes.find((n) => n.id === l.target);
      if (!sn || !tn) return "none";
      if (!filters.kinds.has(sn.kind) || !filters.kinds.has(tn.kind)) return "none";
      if (sn.era && !filters.eras.has(sn.era)) return "none";
      if (tn.era && !filters.eras.has(tn.era)) return "none";
      return null;
    });
  }, [filters, data]);

  const zoomIn = () => {
    if (!zoomRef.current) return;
    zoomRef.current.svg.transition().call(zoomRef.current.zoom.scaleBy, 1.4);
  };
  const zoomOut = () => {
    if (!zoomRef.current) return;
    zoomRef.current.svg.transition().call(zoomRef.current.zoom.scaleBy, 0.7);
  };
  const reset = () => {
    if (!zoomRef.current) return;
    zoomRef.current.svg.transition().call(zoomRef.current.zoom.transform, d3.zoomIdentity);
    onSelectNode?.(null);
  };

  return (
    <div className="graph-stage" ref={containerRef}>
      <div className="stage-overlay">
        FORCE-DIRECTED · {data?.nodes?.length ?? 0} NODES · {data?.links?.length ?? 0} EDGES
      </div>
      <svg ref={svgRef}></svg>
      <div className="stage-controls">
        <button className="ctrl-btn" onClick={zoomIn} title="Zoom in">+</button>
        <button className="ctrl-btn" onClick={zoomOut} title="Zoom out">−</button>
        <button className="ctrl-btn" onClick={reset} title="Reset">⟲</button>
      </div>
    </div>
  );
}
