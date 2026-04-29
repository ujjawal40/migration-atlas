// Horizon control — slider for the forecast prediction window (1-5 years).

export default function HorizonControl({ value, onChange, min = 1, max = 5 }) {
  return (
    <div className="horizon-control">
      <div className="horizon-label">
        Forecast horizon
        <span className="horizon-value">{value} year{value === 1 ? "" : "s"}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <div className="horizon-ticks">
        {Array.from({ length: max - min + 1 }, (_, i) => min + i).map((y) => (
          <span key={y}>{y}</span>
        ))}
      </div>
    </div>
  );
}
