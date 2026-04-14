"use client";

import { useEffect, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Building2,
  MapPin,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  X,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getCategoryMeta } from "@/lib/dashboardConfig";

const PIE_COLORS = ["#2563EB", "#7C3AED", "#1D9E75", "#F59E0B", "#DC2626"];

const EXECUTIVE_BRIEF = {
  marketing: {
    title: "Buyer catchment story",
    summary: "Show which zones truly convert, then shift budget toward those catchments.",
  },
  forecast: {
    title: "Demand outlook",
    summary: "Translate forecast strength into launch timing, pricing confidence, and targeting.",
  },
  risk: {
    title: "Risk concentration",
    summary: "Spot oversupply and competitor pressure before they slow velocity or erode pricing.",
  },
};

export default function LeftPanel({ activeCategory, activeLayer, isOpen, onClose }) {
  const [projects, setProjects] = useState([]);
  const [zoneMetrics, setZoneMetrics] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [mlMetrics, setMlMetrics] = useState(null);

  useEffect(() => {
    fetch("/data/projects_extended.json").then((r) => r.json()).then(setProjects).catch(console.error);
    fetch("/data/zone_metrics.json").then((r) => r.json()).then(setZoneMetrics).catch(console.error);
    fetch("/data/forecast.json").then((r) => r.json()).then(setForecast).catch(console.error);
    fetch("/data/ml_metrics.json").then((r) => r.json()).then(setMlMetrics).catch(console.error);
  }, []);

  if (!isOpen) return null;

  const categoryMeta = getCategoryMeta(activeCategory);
  const brief = EXECUTIVE_BRIEF[activeCategory];

  const totalLeads = projects.reduce((s, p) => s + Number(p.leads || 0), 0);
  const totalQualified = projects.reduce((s, p) => s + Number(p.qualified_leads || 0), 0);
  const totalSales = projects.reduce((s, p) => s + Number(p.sales || 0), 0);
  const totalUnsold = projects.reduce((s, p) => s + Number(p.unsold_inventory || 0), 0);
  const avgPrice = projects.length ? Math.round(projects.reduce((s, p) => s + Number(p.avg_price || 0), 0) / projects.length) : 0;
  const avgDemand = projects.length ? Math.round(projects.reduce((s, p) => s + Number(p.demand_score || 0), 0) / projects.length) : 0;
  const avgRisk = projects.length ? Math.round(projects.reduce((s, p) => s + Number(p.risk_score || 0), 0) / projects.length) : 0;
  const qualifiedRate = totalLeads ? ((totalQualified / totalLeads) * 100).toFixed(1) : "0.0";
  const reservationRate = totalLeads ? ((totalSales / totalLeads) * 100).toFixed(1) : "0.0";

  const cityPerformance = Object.values(
    projects.reduce((acc, p) => {
      const c = p.city;
      if (!acc[c]) acc[c] = { city: c, sales: 0, leads: 0 };
      acc[c].sales += Number(p.sales || 0);
      acc[c].leads += Number(p.leads || 0);
      return acc;
    }, {})
  ).sort((a, b) => b.sales - a.sales).slice(0, 6);

  const propertyMix = Object.values(
    projects.reduce((acc, p) => {
      const t = p.property_type;
      if (!acc[t]) acc[t] = { name: t, value: 0 };
      acc[t].value += Number(p.sales || 0);
      return acc;
    }, {})
  );

  const forecastTrend = forecast
    .filter((d) => d.governorate === "Tunis")
    .slice(0, 8)
    .map((d) => ({ month: d.month.slice(5), demand: d.demand_index }));

  const watchlist = [...projects]
    .sort((a, b) => {
      if (activeCategory === "risk") return Number(b.risk_score) - Number(a.risk_score);
      if (activeCategory === "forecast") return Number(b.demand_score) - Number(a.demand_score);
      return Number(b.sales) - Number(a.sales);
    })
    .slice(0, 5);

  const zoneLeaders = [...zoneMetrics]
    .sort((a, b) => {
      if (activeCategory === "risk") return Number(b.risk_score) - Number(a.risk_score);
      if (activeCategory === "forecast") return Number(b.demand_score) - Number(a.demand_score);
      return Number(b.avg_price_sqm) - Number(a.avg_price_sqm);
    })
    .slice(0, 4);

  const kpis =
    activeCategory === "marketing"
      ? [
        { label: "Mapped Leads", value: totalLeads.toLocaleString(), change: "+12.5%", positive: true },
        { label: "Qualified Share", value: `${qualifiedRate}%`, change: "+3.2%", positive: true },
        { label: "Reservations", value: totalSales.toLocaleString(), change: "+8.1%", positive: true },
        { label: "Avg Ticket", value: `${avgPrice.toLocaleString()} DT`, change: "+2.4%", positive: true },
      ]
      : activeCategory === "forecast"
        ? [
          { label: "Demand Index", value: `${avgDemand}/100`, change: "+5.3%", positive: true },
          { label: "Reservation Rate", value: `${reservationRate}%`, change: "-1.2%", positive: false },
          { label: "Unsold Units", value: totalUnsold.toLocaleString(), change: "-3.8%", positive: true },
          { label: "Projects", value: `${projects.length}`, change: "Stable", positive: null },
        ]
        : [
          { label: "Mean Risk", value: `${avgRisk}/100`, change: "-12.5%", positive: true },
          { label: "Critical Flags", value: `${mlMetrics?.anomalies_detected ?? 4}`, change: "+1 new", positive: false },
          { label: "Unsold Exposure", value: totalUnsold.toLocaleString(), change: "+3.1%", positive: false },
          { label: "Hot Competition", value: `${zoneMetrics.filter((z) => Number(z.tecnocasa_agencies || 0) > 5).length}`, change: "Monitor", positive: null },
        ];

  return (
    <aside className="panel-shell panel-scroll fixed bottom-3 left-3 top-[calc(var(--topbar-height)+8px)] z-40 w-[calc(100vw-24px)] overflow-y-auto rounded-[var(--panel-radius)] animate-slide-in-left lg:left-4 lg:w-[390px] xl:w-[420px]">
      {/* Header */}
      <div className="border-b border-slate-100 p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg" style={{ background: categoryMeta.tint }}>
              <categoryMeta.icon size={18} style={{ color: categoryMeta.color }} />
            </div>
            <div>
              <h1 className="text-[15px] font-bold text-slate-900">{brief.title}</h1>
              <p className="mt-1 text-[12px] leading-snug text-slate-500 max-w-[200px]">{brief.summary}</p>
            </div>
          </div>
          <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-400">
            <X size={15} />
          </button>
        </div>

        {/* Active lens banner */}
        <div className="rounded-xl p-4 text-white" style={{ background: categoryMeta.color }}>
          <p className="text-[10px] uppercase tracking-widest text-white/70 font-semibold">Active lens</p>
          <p className="mt-1 text-lg font-bold leading-tight">
            {activeLayer.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
          </p>
          <div className="mt-3 flex items-center gap-2">
            <span className="rounded-md bg-white/15 px-2.5 py-1 text-[12px] font-semibold">{projects.length} projects tracked</span>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-5 space-y-5">
        {/* KPI Grid */}
        <section>
          <p className="text-overline mb-3">Spatial KPIs</p>
          <div className="grid grid-cols-2 gap-3">
            {kpis.map((kpi) => (
              <div key={kpi.label} className="metric-card rounded-xl p-3.5 min-h-[88px] flex flex-col justify-between">
                <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 mb-1 truncate">{kpi.label}</p>
                <p className="font-mono text-[17px] font-bold text-slate-900 leading-tight break-all">{kpi.value}</p>
                <p className={`mt-1 text-[11px] font-semibold ${kpi.positive === true ? "text-emerald-600" : kpi.positive === false ? "text-red-500" : "text-slate-400"}`}>
                  {kpi.change}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Chart */}
        <section className="metric-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-overline">Territory signal</p>
              <h3 className="text-[13px] font-semibold text-slate-900 mt-0.5">
                {activeCategory === "marketing" ? "Sales by city" : activeCategory === "forecast" ? "Tunis forecast" : "Risk by governorate"}
              </h3>
            </div>
          </div>
          <div className="min-w-0 overflow-hidden w-full" style={{ height: 180 }}>
            <ResponsiveContainer width="100%" height={180} minWidth={0}>
              {activeCategory === "risk" ? (
                <BarChart data={zoneMetrics.slice(0, 7)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="governorate" tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 12 }} />
                  <Bar dataKey="risk_score" radius={[4, 4, 0, 0]}>
                    {zoneMetrics.slice(0, 7).map((e) => (
                      <Cell key={e.governorate} fill={Number(e.risk_score) > 60 ? "#DC2626" : "#F59E0B"} />
                    ))}
                  </Bar>
                </BarChart>
              ) : activeCategory === "forecast" ? (
                <AreaChart data={forecastTrend}>
                  <defs>
                    <linearGradient id="fg" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor={categoryMeta.color} stopOpacity={0.15} />
                      <stop offset="100%" stopColor={categoryMeta.color} stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 12 }} />
                  <Area type="monotone" dataKey="demand" stroke={categoryMeta.color} fill="url(#fg)" strokeWidth={2} />
                </AreaChart>
              ) : (
                <BarChart data={cityPerformance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="city" tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 12 }} />
                  <Bar dataKey="sales" fill={categoryMeta.color} radius={[4, 4, 0, 0]} />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </section>

        {/* Portfolio mix */}
        <section className="metric-card rounded-xl p-4">
          <p className="text-overline mb-1">Portfolio composition</p>
          <h3 className="text-[13px] font-semibold text-slate-900 mb-3">Property type mix</h3>
          <div className="flex items-center gap-4">
            <div className="flex h-[110px] w-[110px] shrink-0 items-center justify-center">
              <PieChart width={110} height={110}>
                <Pie data={propertyMix} dataKey="value" innerRadius={30} outerRadius={46} paddingAngle={2}>
                  {propertyMix.map((s, i) => (
                    <Cell key={s.name} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </div>
            <div className="min-w-0 flex-1 space-y-1.5">
              {propertyMix.map((item, i) => (
                <div key={item.name} className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-1.5">
                  <div className="h-2 w-2 rounded-full" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                  <span className="text-[12px] text-slate-600">{item.name}</span>
                  <span className="ml-auto text-[12px] font-semibold text-slate-900">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ML Engine */}
        <section className="metric-card rounded-xl p-4">
          <p className="text-overline mb-1">AI engine</p>
          <h3 className="text-[13px] font-semibold text-slate-900 mb-3">Model confidence</h3>
          <div className="grid grid-cols-2 gap-3">
            <EngineStat label="Price model" value={`${((mlMetrics?.accuracy.price_r2_score ?? 0) * 100).toFixed(1)}%`} caption={mlMetrics?.models.price_forecaster ?? "XGBoost"} accent={categoryMeta.color} />
            <EngineStat label="Demand model" value={`${((mlMetrics?.accuracy.demand_r2_score ?? 0) * 100).toFixed(1)}%`} caption={mlMetrics?.models.demand_forecaster ?? "XGBoost"} accent="#7C3AED" />
            <EngineStat label="Risk detector" value={`${mlMetrics?.anomalies_detected ?? 0}`} caption={mlMetrics?.models.risk_detector ?? "Isolation Forest"} accent="#DC2626" />
            <EngineStat label="Atlas depth" value={`${zoneMetrics.length}`} caption="Governorate features" accent="#1D9E75" />
          </div>
        </section>

        {/* Watchlist */}
        <section>
          <p className="text-overline mb-1">Watchlist</p>
          <h3 className="text-[13px] font-semibold text-slate-900 mb-3">Projects worth discussing</h3>
          <div className="space-y-2">
            {watchlist.map((p) => (
              <div key={p.id} className="metric-card rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg" style={{ background: categoryMeta.tint }}>
                    <MapPin size={14} style={{ color: categoryMeta.color }} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-semibold text-slate-900 truncate">{p.project_name}</p>
                    <p className="text-[11px] text-slate-500">{p.city} · {p.neighborhood}</p>
                  </div>
                  <span className="rounded-md bg-slate-50 px-2 py-0.5 text-[10px] font-semibold text-slate-500">{p.property_type}</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <MiniStat label="Demand" value={`${p.demand_score}/100`} />
                  <MiniStat label="Risk" value={`${p.risk_score}/100`} danger={Number(p.risk_score) > 45} />
                  <MiniStat label="Velocity" value={`${Number(p.velocity).toFixed(0)}%`} />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Zone Leaders */}
        <section className="pb-2">
          <p className="text-overline mb-1">Zone leaders</p>
          <h3 className="text-[13px] font-semibold text-slate-900 mb-3">Key geographies</h3>
          <div className="space-y-2">
            {zoneLeaders.map((z) => (
              <div key={z.governorate} className="metric-card rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[13px] font-semibold text-slate-900">{z.governorate}</p>
                    <p className="mt-0.5 text-[11px] text-slate-500">Demand {z.demand_score}/100 · Risk {z.risk_score}/100</p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-base font-bold text-slate-900">{Number(z.avg_price_sqm).toLocaleString()}</p>
                    <p className="text-[10px] text-slate-400">DT/m²</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </aside>
  );
}

function EngineStat({ label, value, caption, accent }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
      <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">{label}</p>
      <p className="mt-1 font-mono text-lg font-bold text-slate-900">{value}</p>
      <p className="mt-0.5 text-[10px] font-medium" style={{ color: accent }}>{caption}</p>
    </div>
  );
}

function MiniStat({ label, value, danger }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2">
      <p className="text-[10px] font-medium text-slate-400">{label}</p>
      <p className={`mt-0.5 text-[12px] font-semibold ${danger ? "text-red-600" : "text-slate-900"}`}>{value}</p>
    </div>
  );
}
