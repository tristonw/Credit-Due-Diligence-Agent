// Lightweight zero-dependency SVG visual components.

export function RadialProgress({ progress = 0, size = 96, stroke = 7, color = "#fff", label }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const off = c * (1 - Math.max(0, Math.min(1, progress)));
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeDasharray={c}
        strokeDashoffset={off}
        strokeLinecap="round"
        style={{ transition: "stroke-dashoffset 0.6s ease" }}
      />
      {label}
    </svg>
  );
}

export function BarChart({ data, height = 180, max }) {
  // data: [{label, value, color}]
  const hi = max ?? Math.max(1, ...data.map((d) => d.value));
  const barW = 70;
  const gap = 40;
  const topPad = 22;
  const botPad = 28;
  const w = data.length * (barW + gap) + gap;
  return (
    <svg width={w} height={height + topPad + botPad}>
      {data.map((d, i) => {
        const h = (d.value / hi) * height;
        const x = gap + i * (barW + gap);
        const y = topPad + height - h;
        return (
          <g key={i}>
            <rect x={x} y={y} width={barW} height={h} rx={6} fill={d.color || "#4f46e5"} />
            <text x={x + barW / 2} y={y - 6} textAnchor="middle" fontSize="13" fontWeight="600" fill="#111827">
              {d.value}
            </text>
            <text x={x + barW / 2} y={topPad + height + 18} textAnchor="middle" fontSize="12" fill="#6b7280">
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export function LineChart({ points, width = 640, height = 200, color = "#4f46e5", fill = "rgba(79,70,229,0.12)" }) {
  // points: [{x:number,y:number}] in data space
  if (!points.length) return <p className="muted">暂无数据</p>;
  const pad = { l: 36, r: 12, t: 12, b: 24 };
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = 0, maxY = Math.max(1, ...ys);
  const sx = (x) => pad.l + ((x - minX) / Math.max(1, maxX - minX)) * (width - pad.l - pad.r);
  const sy = (y) => height - pad.b - ((y - minY) / (maxY - minY)) * (height - pad.t - pad.b);
  const line = points.map((p, i) => `${i ? "L" : "M"}${sx(p.x)},${sy(p.y)}`).join(" ");
  const area = `${line} L${sx(maxX)},${height - pad.b} L${sx(minX)},${height - pad.b} Z`;
  const ticks = 4;
  return (
    <svg width={width} height={height} style={{ maxWidth: "100%" }}>
      {Array.from({ length: ticks + 1 }).map((_, i) => {
        const v = (maxY / ticks) * i;
        const y = sy(v);
        return (
          <g key={i}>
            <line x1={pad.l} y1={y} x2={width - pad.r} y2={y} stroke="#eef0f4" />
            <text x={pad.l - 6} y={y + 4} textAnchor="end" fontSize="10" fill="#9ca3af">{Math.round(v)}</text>
          </g>
        );
      })}
      <path d={area} fill={fill} />
      <path d={line} fill="none" stroke={color} strokeWidth="2.5" />
      {points.map((p, i) => (
        <circle key={i} cx={sx(p.x)} cy={sy(p.y)} r="3.5" fill={color} />
      ))}
    </svg>
  );
}

export function ProficiencyDots({ value, max = 5 }) {
  return (
    <span style={{ letterSpacing: 2 }}>
      {Array.from({ length: max }).map((_, i) => (
        <span key={i} style={{ color: i < value ? "#4f46e5" : "#d1d5db" }}>●</span>
      ))}
    </span>
  );
}

export function StatCard({ label, value, accent = "#4f46e5" }) {
  return (
    <div className="card" style={{ flex: 1, minWidth: 150, marginBottom: 0, textAlign: "center" }}>
      <div style={{ fontSize: 30, fontWeight: 700, color: accent }}>{value}</div>
      <div className="muted">{label}</div>
    </div>
  );
}
