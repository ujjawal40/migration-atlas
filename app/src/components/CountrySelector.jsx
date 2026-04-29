// Country selector — chip-style picker for the forecast view.
// Used independently of the graph, so it owns its own minimal layout.

export default function CountrySelector({ countries, value, onChange }) {
  return (
    <div className="country-selector">
      <div className="country-selector-label">Country of origin</div>
      <ul className="country-selector-list">
        {countries.map((c) => (
          <li key={c.id}>
            <button
              type="button"
              className={
                "country-chip" + (value === c.id ? " country-chip-active" : "")
              }
              onClick={() => onChange(c.id)}
            >
              {c.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
