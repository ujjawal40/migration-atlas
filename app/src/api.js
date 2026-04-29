// API client for the FastAPI backend.
// In dev, requests go through the Vite proxy (/api/*).
// In prod, set VITE_API_URL to the deployed backend (e.g., HF Spaces URL).

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  graph: () => request("/graph"),
  query: (query) =>
    request("/query", { method: "POST", body: JSON.stringify({ query }) }),
  forecast: (country, horizon = 5) =>
    request(`/forecast/${country}?horizon=${horizon}`),
  similar: (nodeId, topK = 10) =>
    request(`/similar/${nodeId}?top_k=${topK}`),
};
