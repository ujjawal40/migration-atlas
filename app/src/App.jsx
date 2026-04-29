// App shell — masthead, navigation, footer, and the routed view outlet.
// Each named route is registered below; the views themselves live under views/.

import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import Atlas from "./views/Atlas";
import Forecast from "./views/Forecast";
import Discourse from "./views/Discourse";
import Simulate from "./views/Simulate";
import Library from "./views/Library";
import Timeline from "./views/Timeline";

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
          <Route path="/" element={<Atlas />} />
          <Route path="/forecast" element={<Forecast />} />
          <Route path="/discourse" element={<Discourse />} />
          <Route path="/simulate" element={<Simulate />} />
          <Route path="/library" element={<Library />} />
          <Route path="/timeline" element={<Timeline />} />
        </Routes>
      </div>

      <div className="footer">
        <div>SOURCES · PEW · MPI · CENSUS ACS · USCIS · CATO 2026</div>
        <div className="ornament">✦ ✦ ✦</div>
        <div>v0.2.0</div>
      </div>
    </div>
  );
}
