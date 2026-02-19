import { TrendingUp, TrendingDown } from "lucide-react";
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
} from "recharts";

interface DataVisualizerProps {
  data: {
    type: "kpi" | "chart" | "table" | "text";
    value?: string;
    change?: string;
    changeDirection?: "up" | "down";
    chartType?: "line" | "bar" | "pie";
    data?: Array<{ name: string; value: number }>;
    columns?: string[];
    rows?: string[][];
    content?: string;
  };
}

const CHART_COLORS = [
  "hsl(174, 70%, 45%)",
  "hsl(250, 80%, 62%)",
  "hsl(200, 70%, 55%)",
  "hsl(280, 65%, 55%)",
  "hsl(140, 60%, 45%)",
  "hsl(30, 80%, 55%)",
];

const DataVisualizer = ({ data }: DataVisualizerProps) => {
  if (data.type === "kpi") {
    return (
      <div className="flex flex-col items-center py-4">
        <span className="text-4xl md:text-5xl font-bold text-kpi">{data.value}</span>
        {data.change && (
          <div
            className={`flex items-center gap-1 mt-2 text-sm font-medium ${
              data.changeDirection === "up" ? "text-accent" : "text-destructive"
            }`}
          >
            {data.changeDirection === "up" ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {data.change} vs last month
          </div>
        )}
      </div>
    );
  }

  if (data.type === "chart" && data.data) {
    return (
      <div className="w-full h-64">
        <ResponsiveContainer width="100%" height="100%">
          {data.chartType === "bar" ? (
            <BarChart data={data.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(228, 15%, 18%)" />
              <XAxis dataKey="name" tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 12 }} />
              <YAxis tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  background: "hsl(228, 20%, 10%)",
                  border: "1px solid hsl(228, 15%, 22%)",
                  borderRadius: "8px",
                  color: "hsl(210, 40%, 93%)",
                }}
              />
              <Bar dataKey="value" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          ) : data.chartType === "pie" ? (
            <PieChart>
              <Pie
                data={data.data}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                stroke="none"
              >
                {data.data.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "hsl(228, 20%, 10%)",
                  border: "1px solid hsl(228, 15%, 22%)",
                  borderRadius: "8px",
                  color: "hsl(210, 40%, 93%)",
                }}
              />
            </PieChart>
          ) : (
            <LineChart data={data.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(228, 15%, 18%)" />
              <XAxis dataKey="name" tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 12 }} />
              <YAxis tick={{ fill: "hsl(215, 15%, 55%)", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  background: "hsl(228, 20%, 10%)",
                  border: "1px solid hsl(228, 15%, 22%)",
                  borderRadius: "8px",
                  color: "hsl(210, 40%, 93%)",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={CHART_COLORS[0]}
                strokeWidth={2}
                dot={{ fill: CHART_COLORS[0], strokeWidth: 0, r: 4 }}
                activeDot={{ r: 6, fill: CHART_COLORS[0] }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    );
  }

  if (data.type === "table" && data.columns && data.rows) {
    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border/50">
              {data.columns.map((col) => (
                <th
                  key={col}
                  className="text-left px-3 py-2 text-muted-foreground font-medium text-xs uppercase tracking-wider"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, i) => (
              <tr key={i} className="border-b border-border/20 hover:bg-secondary/30 transition-colors">
                {row.map((cell, j) => (
                  <td key={j} className="px-3 py-2.5 text-foreground">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (data.type === "text") {
    return (
      <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
        {data.content}
      </p>
    );
  }

  return null;
};

export default DataVisualizer;
