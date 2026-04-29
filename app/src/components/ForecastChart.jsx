// ForecastChart — D3 line chart for the forecast endpoint output.
//
// Renders three series:
//   * Historical actuals (if returned by the API)
//   * Point forecast (yhat)
//   * 80%/95% prediction interval bands

import { useEffect, useRef } from "react";
import * as d3 from "d3";

const MARGIN = { top: 24, right: 24, bottom: 36, left: 64 };
const HEIGHT = 360;

export default function ForecastChart({ historical = [], forecast = [], width = 720 }) {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const innerW = width - MARGIN.left - MARGIN.right;
    const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;

    const g = svg
      .attr("viewBox", `0 0 ${width} ${HEIGHT}`)
      .append("g")
      .attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

    const all = [...historical, ...forecast];
    if (!all.length) {
      g.append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "var(--muted)")
        .attr("font-family", "JetBrains Mono, monospace")
        .attr("font-size", "12px")
        .text("No data");
      return;
    }

    const x = d3.scaleLinear()
      .domain(d3.extent(all, (d) => d.year))
      .range([0, innerW]);
    const y = d3.scaleLinear()
      .domain([
        Math.min(0, d3.min(all, (d) => d.yhat_lower ?? d.flow ?? d.yhat)),
        d3.max(all, (d) => d.yhat_upper ?? d.flow ?? d.yhat) * 1.05,
      ])
      .range([innerH, 0]);

    g.append("g")
      .attr("transform", `translate(0,${innerH})`)
      .call(d3.axisBottom(x).tickFormat(d3.format("d")));
    g.append("g").call(d3.axisLeft(y).tickFormat(d3.format("~s")));

    if (forecast.length) {
      const band = d3.area()
        .x((d) => x(d.year))
        .y0((d) => y(d.yhat_lower ?? d.yhat))
        .y1((d) => y(d.yhat_upper ?? d.yhat));
      g.append("path")
        .datum(forecast)
        .attr("fill", "var(--accent)")
        .attr("opacity", 0.18)
        .attr("d", band);
    }

    if (historical.length) {
      const histLine = d3.line()
        .x((d) => x(d.year))
        .y((d) => y(d.flow));
      g.append("path")
        .datum(historical)
        .attr("fill", "none")
        .attr("stroke", "var(--ink)")
        .attr("stroke-width", 1.5)
        .attr("d", histLine);
    }

    if (forecast.length) {
      const fLine = d3.line()
        .x((d) => x(d.year))
        .y((d) => y(d.yhat));
      g.append("path")
        .datum(forecast)
        .attr("fill", "none")
        .attr("stroke", "var(--accent)")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "4 3")
        .attr("d", fLine);
    }
  }, [historical, forecast, width]);

  return <svg ref={svgRef} className="forecast-chart" />;
}
