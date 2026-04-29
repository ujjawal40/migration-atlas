# Migration Atlas — frontend

React + D3 single-page app. The interactive prototype from the case study lives here, productionized.

## Dev

```bash
npm install
npm run dev      # → http://localhost:5173
```

The dev server proxies `/api/*` to the FastAPI backend at `http://localhost:8000`.

## Build

```bash
npm run build    # outputs to dist/
```

## Architecture

- `src/App.jsx` — top-level layout (masthead, sub-head, query bar, three-column main)
- `src/components/Graph.jsx` — D3 force-directed graph (the centerpiece)
- `src/components/QueryBar.jsx` — natural-language input + chip suggestions
- `src/components/DetailPanel.jsx` — right-rail node detail
- `src/components/FilterPanel.jsx` — left-rail filters
- `src/api.js` — fetch wrapper for the backend

## Deploying

See [docs/deploy/vercel.md](../docs/deploy/vercel.md).
