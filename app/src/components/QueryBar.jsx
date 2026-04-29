import { useState } from "react";
import { PRESET_QUERIES } from "../constants";

export default function QueryBar({ onQuery, loading }) {
  const [text, setText] = useState("");
  const [activePreset, setActivePreset] = useState(null);

  const submit = (q) => {
    const value = q ?? text;
    if (!value.trim() || loading) return;
    onQuery(value);
  };

  return (
    <>
      <div className="query-bar">
        <span className="label">QUERY</span>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="e.g. How is India connected to the H-1B program?"
          disabled={loading}
        />
        <button onClick={() => submit()} disabled={loading || !text.trim()}>
          {loading ? "..." : "ASK"}
        </button>
      </div>
      <div className="chip-row">
        {PRESET_QUERIES.map((p) => (
          <button
            key={p.label}
            className={`chip ${activePreset === p.label ? "active" : ""}`}
            onClick={() => {
              setText(p.q);
              setActivePreset(p.label);
              submit(p.q);
            }}
          >
            {p.label}
          </button>
        ))}
      </div>
    </>
  );
}
