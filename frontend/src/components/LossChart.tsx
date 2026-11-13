import {
  CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { MetricRow } from "../api";

export default function LossChart({ rows, target }: { rows: MetricRow[]; target: number }) {
  if (rows.length === 0) return <p className="muted">No evaluations yet.</p>;
  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={rows} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--grid)" strokeDasharray="3 3" />
          <XAxis dataKey="iter" stroke="var(--muted)" tick={{ fontSize: 12 }} />
          <YAxis stroke="var(--muted)" tick={{ fontSize: 12 }} domain={[0, (max: number) => Math.ceil(max * 2) / 2]} />
          <Tooltip
            contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", color: "var(--fg)" }}
            formatter={(v: number) => v.toFixed(4)}
            labelFormatter={(l) => `iter ${l}`}
          />
          <Legend />
          <ReferenceLine y={target} stroke="var(--good)" strokeDasharray="6 4" label={{ value: `target ${target}`, fill: "var(--good)", fontSize: 12, position: "insideTopRight" }} />
          <Line type="monotone" dataKey="train" name="train loss" stroke="var(--series-1)" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="val" name="val loss" stroke="var(--series-2)" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
