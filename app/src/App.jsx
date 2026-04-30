// App shell — masthead, navigation, footer, and the routed view outlet.
// Each named route is registered below; the views themselves live under views/.
// ErrorBoundary wraps each view so one crash doesn't blank the whole app.

import { Route, Routes } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import NavBar from "./components/NavBar";
import Atlas from "./views/Atlas";
import Forecast from "./views/Forecast";
import Discourse from "./views/Discourse";
import Simulate from "./views/Simulate";
import Library from "./views/Library";
import Timeline from "./views/Timeline";
import About from "./views/About";
import NotFound from "./views/NotFound";

const ROUTES = [
  { path: "/", element: <Atlas /> },
  { path: "/forecast", element: <Forecast /> },
  { path: "/discourse", element: <Discourse /> },
  { path: "/simulate", element: <Simulate /> },
  { path: "/library", element: <Library /> },
  { path: "/timeline", element: <Timeline /> },
  { path: "/about", element: <About /> },
];

export default function App() {
  return (
    <div className="frame">
      <div className="masthead">
        <div className="title">Migration Atlas</div>
        <div className="meta">An interactive immigration intelligence platform</div>
      </div>

      <NavBar />

      <div className="view-stage">
        <Routes>
          {ROUTES.map((r) => (
            <Route
              key={r.path}
              path={r.path}
              element={<ErrorBoundary>{r.element}</ErrorBoundary>}
            />
          ))}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>

      <div className="footer">
        <div>BUILT 2026 · CENSUS ACS · USCIS · MPI · PEW · BLS · OECD</div>
        <div className="ornament">✦ ✦ ✦</div>
        <div>
          <a
            href="https://github.com/ujjawal40/migration-atlas"
            target="_blank"
            rel="noreferrer"
            className="footer-link"
          >
            github.com/ujjawal40/migration-atlas
          </a>
        </div>
      </div>
    </div>
  );
}
