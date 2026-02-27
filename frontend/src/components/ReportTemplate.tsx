import React from 'react';
import {
    BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';

export interface ReportTemplateProps {
    messages: any[];
}

const COLORS = [
    '#4f46e5', '#0ea5e9', '#8b5cf6', '#ec4899',
    '#f59e0b', '#10b981', '#3b82f6', '#f43f5e', '#6366f1'
];

export const ReportTemplate: React.FC<ReportTemplateProps> = ({ messages }) => {
    const date = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    return (
        <div id="insightx-corporate-report" className="bg-white text-slate-900 p-10 w-[800px] mx-auto font-sans">
            <header className="border-b-2 border-slate-200 pb-4 mb-8">
                <h1 className="text-3xl font-bold text-slate-900">InsightX Executive Summary</h1>
                <p className="text-sm text-slate-500 mt-2">Generated on: {date}</p>
            </header>

            <div className="flex flex-col gap-12">
                {messages.map((msg, idx) => {
                    // Filter out user chat bubbles directly as requested
                    if (msg.role === 'user') return null;

                    // Find the preceding user question to use as the section header
                    let userQuestion = "Insight";
                    for (let i = idx - 1; i >= 0; i--) {
                        if (messages[i].role === 'user') {
                            userQuestion = messages[i].content;
                            break;
                        }
                    }

                    // Strip mic icon if present
                    if (userQuestion.startsWith('🎤 "')) {
                        userQuestion = userQuestion.replace('🎤 "', '').replace('"', '');
                    }

                    const { data } = msg;
                    if (!data) return null;

                    const chartType = data.chartType;
                    const chartData = data.rawData || [];

                    let resolvedX = data.xAxis;
                    let resolvedY = data.yAxis;

                    const isChartType = chartType === "bar" || chartType === "line" || chartType === "pie";

                    if (isChartType && chartData.length > 0) {
                        const dataKeys = Object.keys(chartData[0]);
                        if ((!resolvedX || !resolvedY) && dataKeys.length >= 2) {
                            if (!resolvedX) resolvedX = dataKeys[0];
                            if (!resolvedY) {
                                const numericKey = dataKeys.find((k) => k !== resolvedX && typeof chartData[0][k] === "number");
                                resolvedY = numericKey ?? dataKeys[1];
                            }
                        }
                    }

                    const isKpi = chartType === "kpi" || (chartType !== "text" && chartData.length === 1 && !isChartType);

                    return (
                        <div key={msg.id} className="print-avoid-break">
                            <h3 className="text-lg font-bold text-violet-700 mt-8 mb-4">{userQuestion}</h3>

                            <p className="text-slate-700 mb-6 leading-relaxed whitespace-pre-wrap">
                                {msg.content || data.summary}
                            </p>

                            {isKpi && chartData.length > 0 && (
                                <div className="flex flex-col items-center justify-center p-8 border border-slate-200 rounded-xl bg-slate-50 mb-8 mx-auto w-1/2 shadow-sm">
                                    <span className="text-5xl font-extrabold text-[#0f172a] mb-2">
                                        {(() => {
                                            const row = chartData[0];
                                            const keys = Object.keys(row);
                                            const valKey = resolvedY || keys[keys.length - 1];
                                            const val = row[valKey];
                                            return typeof val === "number" && (valKey.includes("amount") || valKey.includes("balance") || valKey.includes("inr"))
                                                ? `₹${val.toLocaleString("en-IN")}`
                                                : val;
                                        })()}
                                    </span>
                                    <span className="text-sm font-medium text-slate-500 uppercase tracking-wider text-center">
                                        {(() => {
                                            const row = chartData[0];
                                            const keys = Object.keys(row);
                                            const valKey = resolvedY || keys[keys.length - 1];
                                            return valKey.replace(/_/g, " ");
                                        })()}
                                    </span>
                                </div>
                            )}

                            {isChartType && resolvedX && resolvedY && chartData.length > 1 && (
                                <div className="flex justify-center my-6">
                                    {chartType === "bar" && (
                                        <BarChart width={700} height={350} data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis dataKey={resolvedX} tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} />
                                            <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} tickFormatter={(v) => v.toLocaleString("en-IN")} />
                                            <Tooltip cursor={{ fill: '#f8fafc' }} formatter={(val) => [Number(val).toLocaleString("en-IN"), resolvedY!.replace(/_/g, " ")]} />
                                            <Legend wrapperStyle={{ color: '#475569', fontSize: 13, paddingTop: 10 }} />
                                            <Bar dataKey={resolvedY} fill="#4f46e5" radius={[4, 4, 0, 0]} name={resolvedY.replace(/_/g, " ")} />
                                        </BarChart>
                                    )}
                                    {chartType === "line" && (
                                        <LineChart width={700} height={350} data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis dataKey={resolvedX} tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} />
                                            <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} tickFormatter={(v) => v.toLocaleString("en-IN")} />
                                            <Tooltip formatter={(val) => [Number(val).toLocaleString("en-IN"), resolvedY!.replace(/_/g, " ")]} />
                                            <Legend wrapperStyle={{ color: '#475569', fontSize: 13, paddingTop: 10 }} />
                                            <Line type="monotone" dataKey={resolvedY} stroke="#4f46e5" strokeWidth={3} dot={{ fill: '#4f46e5', r: 4, strokeWidth: 0 }} activeDot={{ r: 6, stroke: "#fff", strokeWidth: 2 }} name={resolvedY.replace(/_/g, " ")} />
                                        </LineChart>
                                    )}
                                    {chartType === "pie" && (
                                        <PieChart width={700} height={350}>
                                            <Pie
                                                data={chartData} cx="50%" cy="50%" innerRadius={80} outerRadius={130}
                                                dataKey={resolvedY} nameKey={resolvedX} stroke="none"
                                                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(1)}%)`}
                                                labelLine={{ stroke: '#94a3b8', strokeWidth: 1 }}
                                            >
                                                {chartData.map((_, i) => (
                                                    <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(val) => [Number(val).toLocaleString("en-IN"), resolvedY!.replace(/_/g, " ")]} />
                                            <Legend wrapperStyle={{ color: '#475569', fontSize: 13, paddingTop: 10 }} />
                                        </PieChart>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
