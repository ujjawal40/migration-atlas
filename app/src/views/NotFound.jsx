// NotFound — caught by the catch-all route; better than silently rendering Atlas.

import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="view view-notfound">
      <div className="notfound-card">
        <h2>404</h2>
        <p>That URL doesn't match any view.</p>
        <Link to="/" className="notfound-link">Back to Atlas</Link>
      </div>
    </div>
  );
}
