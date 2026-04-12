"use client";

import { useEffect, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Building2,
  MapPin,
  ShieldAlert,
  Sparkles,
  Target,
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
    badge: "Atlas builder active",
  },
  forecast: {
    title: "Demand outlook",
    summary: "Translate forecast strength into launch timing, pricing confidence, and targeting.",
    badge: "12-month horizon",
  },
  risk: {
    title: "Risk concentration",
    summary: "Spot oversupply and competitor pressure before they slow velocity or erode pricing.",
    badge: "Mitigation mode",
  },
};

export default function LeftPanel({ activeCategory, activeLayer, isOpen, onClose }) {
  const [projects, setProjects] = useState([]);
  const [zoneMetrics, setZoneMetrics] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [mlMetrics, setMlMetrics] = useState(null);

  useEffect(() => {
    fetch("/data/projects_extended.json").then((response) => response.json()).then(setProjects).catch(console.error);
    fetch("/data/zone_metrics.json").then((response) => response.json()).then(setZoneMetrics).catch(console.error);
    fetch("/data/forecast.json").then((response) => response.json()).then(setForecast).catch(console.error);
    fetch("/data/ml_metrics.json").then((response) => response.json()).then(setMlMetrics).catch(console.error);
  }, []);

  if (!isOpen) {
    return null;
  }

  const categoryMeta = getCategoryMeta(activeCategory);
  const brief = EXECUTIVE_BRIEF[activeCategory];

  const totalLeads = projects.reduce((sum, project) => sum + Number(project.leads || 0), 0);
  const totalQualified = projects.reduce((sum, project) => sum + Number(project.qualified_leads || 0), 0);
  const totalSales = projects.reduce((sum, project) => sum + Number(project.sales || 0), 0);
  const totalUnsold = projects.reduce((sum, project) => sum + Number(project.unsold_inventory || 0), 0);
  const avgPrice = projects.length
    ? Math.round(projects.reduce((sum, project) => sum + Number(project.avg_price || 0), 0) / projects.length)
    : 0;
  const avgDemand = projects.length
    ? Math.round(projects.reduce((sum, project) => sum + Number(project.demand_score || 0), 0) / projects.length)
    : 0;
  const avgRisk = projects.length
    ? Math.round(projects.reduce((sum, project) => sum + Number(project.risk_score || 0), 0) / projects.length)
    : 0;
  const qualifiedRate = totalLeads ? ((totalQualified / totalLeads) * 100).toFixed(1) : "0.0";
  const reservationRate = totalLeads ? ((totalSales / totalLeads) * 100).toFixed(1) : "0.0";

  const cityPerformance = Object.values(
    projects.reduce((accumulator, project) => {
      const city = project.city;
      if (!accumulator[city]) {
        accumulator[city] = { city, sales: 0, leads: 0 };
      }
      accumulator[city].sales += Number(project.sales || 0);
      accumulator[city].leads += Number(project.leads || 0);
      return accumulator;
    }, {})
  )
    .sort((left, right) => right.sales - left.sales)
    .slice(0, 6);

  const propertyMix = Object.values(
    projects.reduce((accumulator, project) => {
      const propertyType = project.property_type;
      if (!accumulator[propertyType]) {
        accumulator[propertyType] = { name: propertyType, value: 0 };
      }
      accumulator[propertyType].value += Number(project.sales || 0);
      return accumulator;
    }, {})
  );

  const forecastTrend = forecast
    .filter((item) => item.governorate === "Tunis")
    .slice(0, 8)
    .map((item) => ({
      month: item.month.slice(5),
      demand: item.demand_index,
    }));

  const watchlist = [...projects]
    .sort((left, right) => {
      if (activeCategory === "risk") {
        return Number(right.risk_score) - Number(left.risk_score);
      }
      if (activeCategory === "forecast") {
        return Number(right.demand_score) - Number(left.demand_score);
      }
      return Number(right.sales) - Number(left.sales);
    })
    .slice(0, 5);

  const zoneLeaders = [...zoneMetrics]
    .sort((left, right) => {
      if (activeCategory === "risk") {
        return Number(right.risk_score) - Number(left.risk_score);
      }
      if (activeCategory === "forecast") {
        return Number(right.demand_score) - Number(left.demand_score);
      }
      return Number(right.avg_price_sqm) - Number(left.avg_price_sqm);
    })
    .slice(0, 4);

  const highlightMetrics =
    activeCategory === "marketing"
      ? [
          { label: "Mapped Leads", value: totalLeads.toLocaleString("en-US"), change: "+12.5%", tone: "positive" },
          { label: "Qualified Share", value: `${qualifiedRate}%`, change: "+3.2%", tone: "positive" },
          { label: "Reservations", value: totalSales.toLocaleString("en-US"), change: "+8.1%", tone: "positive" },
          { label: "Avg Ticket", value: `${avgPrice.toLocaleString("en-US")} DT`, change: "+2.4%", tone: "positive" },
        ]
      : activeCategory === "forecast"
        ? [
            { label: "Demand Index", value: `${avgDemand}/100`, change: "+5.3%", tone: "positive" },
            { label: "Reservation Rate", value: `${reservationRate}%`, change: "-1.2%", tone: "negative" },
            { label: "Unsold Units", value: totalUnsold.toLocaleString("en-US"), change: "-3.8%", tone: "positive" },
            { label: "Projects In View", value: `${projects.length}`, change: "Stable", tone: "neutral" },
          ]
        : [
            { label: "Mean Risk", value: `${avgRisk}/100`, change: "-12.5%", tone: "positive" },
            { label: "Critical Flags", value: `${mlMetrics?.anomalies_detected ?? 4}`, change: "+1 new", tone: "negative" },
            { label: "Unsold Exposure", value: totalUnsold.toLocaleString("en-US"), change: "+3.1%", tone: "negative" },
            { label: "Hot Competition", value: `${zoneMetrics.filter((zone) => Number(zone.tecnocasa_agencies || 0) > 5).length}`, change: "Monitor", tone: "neutral" },
          ];

  const storyCards =
    activeCategory === "marketing"
      ? [
          { title: "Budget Shift", value: "+18%", detail: "Move spend toward Lac 2, Menzah, and Ariana catchments." },
          { title: "Lead Quality", value: `${qualifiedRate}%`, detail: "Qualified leads come from a tighter corridor than top-of-funnel traffic." },
        ]
      : activeCategory === "forecast"
        ? [
            { title: "Demand Outlook", value: `${avgDemand}/100`, detail: "Forecast remains strongest in Tunis and Ariana next quarter." },
            { title: "Sell-through Pace", value: `${reservationRate}%`, detail: "Faster zones support acceleration. Weaker ones need tighter sequencing." },
          ]
        : [
            { title: "Critical Exposure", value: `${mlMetrics?.anomalies_detected ?? 4}`, detail: "A small set of zones is driving outsized portfolio risk." },
            { title: "Unsold Pressure", value: totalUnsold.toLocaleString("en-US"), detail: "Inventory drag is uneven. Mitigate where absorption is already slowing." },
          ];

  return (
    <aside className="panel-shell panel-scroll fixed bottom-3 left-3 top-[calc(var(--topbar-height)+10px)] z-40 w-[calc(100vw-24px)] overflow-y-auto rounded-[var(--panel-radius)] animate-slide-in-left lg:left-4 lg:w-[380px] xl:w-[420px]">
      <div className="border-b border-slate-200/70 px-5 pb-5 pt-5">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl" style={{ background: `linear-gradient(135deg, ${categoryMeta.tint}, #ffffff)` }}>
              <categoryMeta.icon size={20} style={{ color: categoryMeta.color }} />
            </div>
            <div>
              <p className="text-overline text-slate-500">{brief.badge}</p>
              <h1 className="max-w-[13rem] text-[1.06rem] font-bold leading-6 text-slate-950">{brief.title}</h1>
              <p className="mt-2 max-w-[15rem] text-sm leading-5 text-slate-600">{brief.summary}</p>
            </div>
          </div>
          <button onClick={onClose} className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-500 transition hover:text-slate-900">
            <X size={17} />
          </button>
        </div>

        <div className="relative overflow-hidden rounded-[24px] p-5 text-white shadow-sm" style={{ background: `linear-gradient(135deg, ${categoryMeta.color}, ${categoryMeta.color}DD, ${categoryMeta.color}99)` }}>
          <div className="relative z-10 flex flex-col gap-4">
            <div>
              <p className="text-[11px] uppercase tracking-widest text-white/80 font-bold mb-2">Active lens</p>
              <p className="truncate text-2xl font-extrabold leading-none tracking-tight shadow-sm mb-1">{
                activeLayer.replace(/-/g, " ").replace(/\b\w/g, (character) => character.toUpperCase())
              }</p>
              <p className="mt-3 text-[13px] leading-relaxed text-white/90 max-w-[17rem]">
                A pristine analytical layer designed for high-stakes investor discussions.
              </p>
            </div>
            <div className="self-start rounded-[18px] border border-white/20 bg-white/10 px-4 py-3 backdrop-blur-md shadow-sm">
              <div className="flex items-center gap-3">
                <span className="font-mono text-3xl font-extrabold leading-none tracking-tight">{projects.length}</span>
                <div className="flex flex-col">
                  <span className="text-[10px] text-white/90 font-bold uppercase tracking-wider mb-[2px]">Projects</span>
                  <span className="text-[10px] text-white/90 font-bold uppercase tracking-wider">Tracked</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-5 px-5 py-5">
        <section>
          <div className="grid grid-cols-1 gap-3">
            {storyCards.map((card) => (
              <div key={card.title} className="metric-card rounded-[22px] p-4">
                <p className="text-overline text-slate-500">{card.title}</p>
                <p className="mt-1 font-mono text-[1.8rem] font-bold leading-none text-slate-950">{card.value}</p>
                <p className="mt-2 max-w-[18rem] text-sm leading-5 text-slate-600">{card.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Executive snapshot</p>
              <h2 className="text-base font-semibold text-slate-950">Spatial KPIs</h2>
            </div>
            <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">Updated live</div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {highlightMetrics.map((metric) => (
              <MetricCard key={metric.label} metric={metric} accent={categoryMeta.color} />
            ))}
          </div>
        </section>

        <section className="metric-card rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Territory signal</p>
              <h3 className="text-base font-semibold text-slate-950">
                {activeCategory === "marketing"
                  ? "Sales concentration by city"
                  : activeCategory === "forecast"
                    ? "Forecast trajectory for Tunis"
                    : "Risk profile by governorate"}
              </h3>
            </div>
            <Sparkles size={16} style={{ color: categoryMeta.color }} />
          </div>

          <div className="min-w-0" style={{ width: "100%", minHeight: 220, height: 220 }}>
            <ResponsiveContainer width="99%" height={220} minWidth={280}>
              {activeCategory === "risk" ? (
                <BarChart data={zoneMetrics.slice(0, 7)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="governorate" tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: "#F8FAFC" }} contentStyle={{ borderRadius: 18, border: "1px solid #E2E8F0" }} />
                  <Bar dataKey="risk_score" radius={[10, 10, 0, 0]}>
                    {zoneMetrics.slice(0, 7).map((entry) => (
                      <Cell key={entry.governorate} fill={Number(entry.risk_score) > 60 ? "#DC2626" : "#F59E0B"} />
                    ))}
                  </Bar>
                </BarChart>
              ) : activeCategory === "forecast" ? (
                <AreaChart data={forecastTrend}>
                  <defs>
                    <linearGradient id="forecastGradient" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor={categoryMeta.color} stopOpacity={0.28} />
                      <stop offset="100%" stopColor={categoryMeta.color} stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ stroke: categoryMeta.color, strokeDasharray: "4 4" }} contentStyle={{ borderRadius: 18, border: "1px solid #E2E8F0" }} />
                  <Area type="monotone" dataKey="demand" stroke={categoryMeta.color} fill="url(#forecastGradient)" strokeWidth={3} />
                </AreaChart>
              ) : (
                <BarChart data={cityPerformance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="city" tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: "#F8FAFC" }} contentStyle={{ borderRadius: 18, border: "1px solid #E2E8F0" }} />
                  <Bar dataKey="sales" fill={categoryMeta.color} radius={[10, 10, 0, 0]} />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </section>

        <section className="metric-card rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Portfolio composition</p>
              <h3 className="text-base font-semibold text-slate-950">What the portfolio is selling</h3>
            </div>
            <Building2 size={16} className="text-slate-400" />
          </div>

          <div className="flex min-w-0 items-center gap-4">
            <div className="flex h-[126px] w-[126px] shrink-0 items-center justify-center">
              <PieChart width={126} height={126}>
                <Pie data={propertyMix} dataKey="value" innerRadius={34} outerRadius={52} paddingAngle={2}>
                  {propertyMix.map((slice, index) => (
                    <Cell key={slice.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </div>

            <div className="min-w-0 flex-1 space-y-2">
              {propertyMix.map((item, index) => (
                <div key={item.name} className="flex items-center gap-2 rounded-2xl bg-white/70 px-3 py-2">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ background: PIE_COLORS[index % PIE_COLORS.length] }} />
                  <span className="text-sm text-slate-600">{item.name}</span>
                  <span className="ml-auto text-sm font-semibold text-slate-900">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="metric-card rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">AI engine status</p>
              <h3 className="text-base font-semibold text-slate-950">Model confidence and anomaly watch</h3>
            </div>
            <Target size={16} style={{ color: categoryMeta.color }} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <EngineStat label="Price model" value={`${((mlMetrics?.accuracy.price_r2_score ?? 0) * 100).toFixed(1)}%`} caption={mlMetrics?.models.price_forecaster ?? "XGBoost"} accent={categoryMeta.color} />
            <EngineStat label="Demand model" value={`${((mlMetrics?.accuracy.demand_r2_score ?? 0) * 100).toFixed(1)}%`} caption={mlMetrics?.models.demand_forecaster ?? "XGBoost"} accent="#7C3AED" />
            <EngineStat label="Risk detector" value={`${mlMetrics?.anomalies_detected ?? 0}`} caption={mlMetrics?.models.risk_detector ?? "Isolation Forest"} accent="#DC2626" />
            <EngineStat label="Atlas depth" value={`${zoneMetrics.length}`} caption="Governorate features" accent="#1D9E75" />
          </div>
        </section>

        <section>
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Watchlist</p>
              <h3 className="text-base font-semibold text-slate-950">Projects worth discussing now</h3>
            </div>
          </div>

          <div className="space-y-3">
            {watchlist.map((project) => (
              <div key={project.id} className="metric-card rounded-[22px] p-4">
                <div className="mb-3 flex items-start gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl" style={{ background: categoryMeta.tint }}>
                    <MapPin size={16} style={{ color: categoryMeta.color }} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-950">{project.project_name}</p>
                        <p className="mt-1 text-sm text-slate-500">{project.city} . {project.neighborhood}</p>
                      </div>
                      <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{project.property_type}</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <WatchMetric label="Demand" value={`${project.demand_score}/100`} />
                  <WatchMetric label="Risk" value={`${project.risk_score}/100`} danger={Number(project.risk_score) > 45} />
                  <WatchMetric label="Velocity" value={`${Number(project.velocity).toFixed(0)}%`} />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="pb-2">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Zone leaders</p>
              <h3 className="text-base font-semibold text-slate-950">Geographies defining the narrative</h3>
            </div>
            <ShieldAlert size={16} className="text-slate-400" />
          </div>

          <div className="space-y-3">
            {zoneLeaders.map((zone) => (
              <div key={zone.governorate} className="metric-card rounded-[20px] p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-slate-950">{zone.governorate}</p>
                    <p className="mt-1 text-sm text-slate-500">Demand {zone.demand_score}/100 . Risk {zone.risk_score}/100</p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-lg font-bold text-slate-950">{Number(zone.avg_price_sqm).toLocaleString("en-US")}</p>
                    <p className="text-xs text-slate-500">DT/m2</p>
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

function MetricCard({ metric, accent }) {
  const toneColor = metric.tone === "positive" ? "var(--semantic-success)" : metric.tone === "negative" ? "var(--semantic-danger)" : "#64748B";

  return (
    <div className="metric-card rounded-[22px] p-4 shadow-sm border border-slate-100">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 mb-1">{metric.label}</p>
          <p className="font-mono text-2xl font-extrabold tracking-tight text-slate-900">{metric.value}</p>
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded-[12px] shadow-sm" style={{ background: `${accent}15`, color: accent }}>
          {metric.tone === "positive" ? <ArrowUpRight size={16} /> : metric.tone === "negative" ? <ArrowDownRight size={16} /> : <TrendingUp size={16} />}
        </div>
      </div>
      <p className="text-[12px] font-bold tracking-tight" style={{ color: toneColor }}>{metric.change}</p>
    </div>
  );
}

function EngineStat({ label, value, caption, accent }) {
  return (
    <div className="rounded-[20px] border border-slate-200 bg-white px-3 py-3">
      <p className="text-overline text-slate-500">{label}</p>
      <p className="mt-1 font-mono text-[1.3rem] font-bold text-slate-950">{value}</p>
      <p className="mt-1 text-xs font-medium" style={{ color: accent }}>{caption}</p>
    </div>
  );
}

function WatchMetric({ label, value, danger }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white px-3 py-2">
      <p className="text-[11px] font-medium text-slate-500">{label}</p>
      <p className={`mt-1 text-sm font-semibold ${danger ? "text-red-600" : "text-slate-900"}`}>{value}</p>
    </div>
  );
}
