import React from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

// -- Types --------------------------------------------------------------------

interface DataVisualizerProps {
  /** Raw data rows from the backend (array of objects) */
  data: Record<string, unknown>[];
  /** LLM-chosen chart type */
  chartType: string;
  /** Column name for X-axis / label */
  xAxis: string | null;
  /** Column name for Y-axis / value */
  yAxis: string | null;
  /** Optional: for text-only fallback */
  textContent?: string;
}

// -- Dark-mode color palette --------------------------------------------------

const CHART_COLORS = [
  "#8b5cf6", // violet-500
  "#3b82f6", // blue-500
  "#10b981", // emerald-500
  "#f59e0b", // amber-500
  "#f43f5e", // rose-500
  "#06b6d4", // cyan-500
  "#a78bfa", // violet-400
  "#60a5fa", // blue-400
];

const TOOLTIP_STYLE: React.CSSProperties = {
  background: "rgba(15, 23, 42, 0.95)",
  border: "1px solid rgba(148, 163, 184, 0.2)",
  borderRadius: "10px",
  color: "#e2e8f0",
  fontSize: "13px",
  padding: "10px 14px",
  boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
};

const AXIS_TICK = { fill: "#94a3b8", fontSize: 12 };
const GRID_STROKE = "rgba(148, 163, 184, 0.08)";

// -- Helpers ------------------------------------------------------------------

function formatValue(val: unknown): string {
  if (val === null || val === undefined) return "\u2014";
  if (typeof val === "number") return val.toLocaleString("en-IN");
  return String(val);
}

function isCurrencyKey(key: string): boolean {
  return /amount|value|total|sum|credit|debit|inr|revenue|cost/i.test(key);
}

function formatCell(key: string, val: unknown): string {
  if (val === null || val === undefined) return "\u2014";
  if (typeof val === "number") {
    const formatted = val.toLocaleString("en-IN");
    return isCurrencyKey(key) ? `\u20b9${formatted}` : formatted;
  }
  return String(val);
}

// -- Component ----------------------------------------------------------------

const DataVisualizer: React.FC<DataVisualizerProps> = ({
  data,
  chartType,
  xAxis,
  yAxis,
  textContent,
}) => {
  // Guard: no data
  if (!data || data.length === 0) {
    if (textContent) {
      return (
        <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
          {textContent}
        </p>
      );
    }
    return null;
  }

  // ── KPI ─────────────────────────────────────────────────────────────────────
  if (chartType === "kpi" || data.length === 1) {
    const row = data[0];
    const keys = Object.keys(row);
    // Try to show label + value, or just the single value
    const labelKey = keys.length > 1 ? keys[0] : null;
    const valueKey = yAxis || keys[keys.length - 1];
    const rawValue = row[valueKey];

    return (
      <div className="flex flex-col items-center justify-center py-6 px-4">
        {labelKey && (
          <span className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
            {String(row[labelKey])}
          </span>
        )}
        <span className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
          {typeof rawValue === "number" && isCurrencyKey(valueKey)
            ? `\u20b9${rawValue.toLocaleString("en-IN")}`
            : formatValue(rawValue)}
        </span>
        <span className="text-xs text-muted-foreground mt-2 uppercase tracking-wider">
          {valueKey.replace(/_/g, " ")}
        </span>
      </div>
    );
  }

  // ── Charts (bar/line/pie) ───────────────────────────────────────────────────
  if (
    (chartType === "bar" || chartType === "line" || chartType === "pie") &&
    xAxis &&
    yAxis
  ) {
    // Ensure numeric y-axis values
    const chartData = data.map((row) => ({
      ...row,
      [yAxis]: typeof row[yAxis] === "number" ? row[yAxis] : Number(row[yAxis]) || 0,
    }));

    return (
      <div className="w-full bg-slate-900/50 border border-slate-800/60 rounded-xl p-4">
        <ResponsiveContainer width="100%" height={400}>
          {chartType === "bar" ? (
            <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
              <XAxis
                dataKey={xAxis}
                tick={AXIS_TICK}
                axisLine={{ stroke: "rgba(148,163,184,0.15)" }}
                tickLine={false}
              />
              <YAxis
                tick={AXIS_TICK}
                axisLine={{ stroke: "rgba(148,163,184,0.15)" }}
                tickLine={false}
                tickFormatter={(v: number) => v.toLocaleString("en-IN")}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value: number) => [value.toLocaleString("en-IN"), yAxis.replace(/_/g, " ")]}
                cursor={{ fill: "rgba(148, 163, 184, 0.06)" }}
              />
              <Legend wrapperStyle={{ color: "#94a3b8", fontSize: "12px" }} />
              <Bar
                dataKey={yAxis}
                fill={CHART_COLORS[0]}
                radius={[6, 6, 0, 0]}
                name={yAxis.replace(/_/g, " ")}
              />
            </BarChart>
          ) : chartType === "line" ? (
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
              <XAxis
                dataKey={xAxis}
                tick={AXIS_TICK}
                axisLine={{ stroke: "rgba(148,163,184,0.15)" }}
                tickLine={false}
              />
              <YAxis
                tick={AXIS_TICK}
                axisLine={{ stroke: "rgba(148,163,184,0.15)" }}
                tickLine={false}
                tickFormatter={(v: number) => v.toLocaleString("en-IN")}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value: number) => [value.toLocaleString("en-IN"), yAxis.replace(/_/g, " ")]}
              />
              <Legend wrapperStyle={{ color: "#94a3b8", fontSize: "12px" }} />
              <Line
                type="monotone"
                dataKey={yAxis}
                stroke={CHART_COLORS[0]}
                strokeWidth={2.5}
                dot={{ fill: CHART_COLORS[0], strokeWidth: 0, r: 4 }}
                activeDot={{ r: 7, fill: CHART_COLORS[0], stroke: "#fff", strokeWidth: 2 }}
                name={yAxis.replace(/_/g, " ")}
              />
            </LineChart>
          ) : (
            // Pie chart
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                dataKey={yAxis}
                nameKey={xAxis}
                stroke="none"
                paddingAngle={2}
                label={({ name, percent }: { name: string; percent: number }) =>
                  `${name} (${(percent * 100).toFixed(1)}%)`
                }
                labelLine={{ stroke: "#94a3b8", strokeWidth: 1 }}
              >
                {chartData.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value: number) => [value.toLocaleString("en-IN"), yAxis.replace(/_/g, " ")]}
              />
              <Legend wrapperStyle={{ color: "#94a3b8", fontSize: "12px" }} />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    );
  }

  // ── Table Fallback ──────────────────────────────────────────────────────────
  const columns = Object.keys(data[0]);

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700/60">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-800/80">
            {columns.map((col) => (
              <th
                key={col}
                className="text-left px-4 py-3 text-slate-300 font-medium text-xs uppercase tracking-wider whitespace-nowrap"
              >
                {col.replace(/_/g, " ")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr
              key={i}
              className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
            >
              {columns.map((col) => (
                <td
                  key={col}
                  className="px-4 py-2.5 text-foreground whitespace-nowrap"
                >
                  {formatCell(col, row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataVisualizer;
