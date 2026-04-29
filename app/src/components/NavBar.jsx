// Top navigation for the multi-view dashboard.
// Each link maps to a route registered in App.jsx.

import { NavLink } from "react-router-dom";

const VIEWS = [
  { to: "/", label: "Atlas", end: true },
  { to: "/forecast", label: "Forecast" },
  { to: "/discourse", label: "Discourse" },
  { to: "/simulate", label: "Simulate" },
  { to: "/library", label: "Library" },
  { to: "/timeline", label: "Timeline" },
];

export default function NavBar() {
  return (
    <nav className="nav-bar">
      <ul className="nav-list">
        {VIEWS.map((v) => (
          <li key={v.to}>
            <NavLink
              to={v.to}
              end={v.end}
              className={({ isActive }) =>
                "nav-link" + (isActive ? " nav-link-active" : "")
              }
            >
              {v.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
