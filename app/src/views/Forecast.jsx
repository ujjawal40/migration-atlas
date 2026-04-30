// Forecast view — flow projections per origin country.
//
// Layout:
//   sidebar    — country selector + horizon control
//   stage      — D3 chart with historical + forecast band
//   readout    — the table of point forecasts and intervals

import { useEffect, useState } from "react";
import { api } from "../api";
import { FORECASTABLE_COUNTRIES } from "../constants";
import CountrySelector from "../components/CountrySelector";
import HorizonControl from "../components/HorizonControl";
import ForecastChart from "../components/ForecastChart";
import { SkeletonBlock, SkeletonLine } from "../components/Skeleton";

export default function Forecast() {
  const [country, setCountry] = useState(FORECASTABLE_COUNTRIES[0].id);
  const [horizon, setHorizon] = useState(5);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancel = false;
    setLoading(true);
    setError(null);
    api
      .forecast(country, horizon)
      .then((res) => {
        if (cancel) return;
        setData(res);
      })
      .catch((err) => {
        if (cancel) return;
        setError(err.message);
        setData(null);
      })
      .finally(() => {
        if (!cancel) setLoading(false);
      });
    return () => {
      cancel = true;
    };
  }, [country, horizon]);

  const forecastRows = data?.forecast ?? [];
  const countryLabel =
    FORECASTABLE_COUNTRIES.find((c) => c.id === country)?.name ?? country;

  return (
    <div className="view view-forecast">
      <div className="forecast-layout">
        <aside className="forecast-sidebar">
          <CountrySelector
            countries={FORECASTABLE_COUNTRIES}
            value={country}
            onChange={setCountry}
          />
          <HorizonControl value={horizon} onChange={setHorizon} />
        </aside>

        <div className="forecast-stage">
          <header className="forecast-header">
            <h1>{countryLabel}</h1>
            <div className="forecast-sub">
              Flow forecast · {horizon}-year horizon · 80/95% prediction interval
            </div>
          </header>

          {loading && (
            <div className="forecast-loading" aria-busy="true">
              <SkeletonBlock height={360} />
            </div>
          )}
          {error && (
            <div className="forecast-status forecast-status-error">
              <strong>Could not reach the forecaster.</strong>
              <p>{error}</p>
              <p className="forecast-status-hint">
                The backend is probably offline. Set <code>VITE_API_URL</code> to a
                running instance, or run <code>make api</code> locally.
              </p>
            </div>
          )}
          {!loading && !error && (
            <ForecastChart historical={[]} forecast={forecastRows} />
          )}
        </div>

        <section className="forecast-readout">
          <h3>Point forecasts</h3>
          {loading ? (
            <div aria-busy="true">
              <SkeletonLine width="80%" />
              <SkeletonLine width="65%" />
              <SkeletonLine width="72%" />
              <SkeletonLine width="58%" />
            </div>
          ) : forecastRows.length === 0 ? (
            <p className="forecast-empty">
              No forecast available for {countryLabel}. The forecaster needs
              real flow data and a trained checkpoint — run{" "}
              <code>make data && make train-forecast</code> to generate it.
            </p>
          ) : (
            <table className="forecast-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Estimate</th>
                  <th>Lower</th>
                  <th>Upper</th>
                </tr>
              </thead>
              <tbody>
                {forecastRows.map((r) => (
                  <tr key={r.year}>
                    <td>{r.year}</td>
                    <td>{Math.round(r.yhat).toLocaleString()}</td>
                    <td>{Math.round(r.yhat_lower ?? r.yhat).toLocaleString()}</td>
                    <td>{Math.round(r.yhat_upper ?? r.yhat).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>
    </div>
  );
}
