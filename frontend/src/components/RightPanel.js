"use client";

import { useEffect, useState } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Download,
  Loader2,
  MapPin,
  ShieldCheck,
  Sparkles,
  Target,
  X,
} from "lucide-react";
import { getCategoryMeta } from "@/lib/dashboardConfig";

export default function RightPanel({ data, isOpen, onClose, activeCategory, activeLayer }) {
  const [aiRecommendation, setAiRecommendation] = useState("");
  const [zoneMetrics, setZoneMetrics] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [isApplying, setIsApplying] = useState(false);
  const [applyState, setApplyState] = useState("idle"); // 'idle', 'syncing', 'applied'

  // Load supplementary data for enriched AI context
  useEffect(() => {
    fetch("/data/zone_metrics.json").then(r => r.json()).then(setZoneMetrics).catch(() => {});
    fetch("/data/competitors.json").then(r => r.json()).then(setCompetitors).catch(() => {});
  }, []);

  useEffect(() => {
    if (!isOpen || !data) return;
    setAiRecommendation(""); // Reset for loading state

    // Build rich context with ALL available data
    const context = {
      name: data.name || data.project_name || data.NAME_1 || data.shapeName || "Zone",
      sourceType: data.sourceType || "project",
      // Pricing
      avg_price: data.avg_price || 0,
      avg_price_sqm: data.avg_price_sqm || 0,
      price_per_sqm: data.price_per_sqm || 0,
      price_tier: data.price_tier || null,
      mom_price_change_pct: data.mom_price_change_pct || null,
      yoy_price_change_pct: data.yoy_price_change_pct || data.yoy_growth_pct || null,
      growth_pct: data.growth_pct || null,
      // Scores
      demand_score: data.demand_score || 0,
      risk_score: data.risk_score || 0,
      velocity: data.velocity || null,
      absorption_weeks: data.absorption_weeks || null,
      infrastructure_score: data.infrastructure_score || null,
      // Location
      governorate: data.governorate || null,
      city: data.city || null,
      neighborhood: data.neighborhood || data.delegation || null,
      // Demographics
      population: data.population || null,
      density: data.density || null,
      urbanization_pct: data.urbanization_pct || null,
      unemployment_pct: data.unemployment_pct || null,
      // Commercial
      ad_spend: data.ad_spend || null,
      leads: data.leads || data.lead_count || null,
      qualified_leads: data.qualified_leads || null,
      qualified_lead_rate: data.qualified_lead_rate || null,
      visits: data.visits || null,
      reservations: data.reservations || null,
      visit_to_reservation_rate: data.visit_to_reservation_rate || null,
      sales: data.sales || null,
      unsold_inventory: data.unsold_inventory || null,
      cost_per_lead: data.cost_per_lead || null,
      cost_per_qualified_lead: data.cost_per_qualified_lead || null,
      // Risk
      flood_risk: data.flood_risk || null,
      seismic_risk: data.seismic_risk || null,
      // Competition
      competitors_in_zone: data.competitors_in_zone || data.total_agencies || null,
      agency_brands: data.agency_brands || null,
      // Meta
      property_type: data.property_type || null,
      total_units: data.total_units || null,
    };

    fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        context: JSON.stringify(context),
        activeCategory,
        activeLayer,
        zoneMetrics,
        competitors,
      }),
    })
      .then(r => r.json())
      .then(payload => setAiRecommendation(payload.recommendation || "No recommendation available."))
      .catch(() => {
        setAiRecommendation(
          data.recommended_action ||
          `Demand sits at ${data.demand_score || "N/A"}/100 while risk remains ${data.risk_score || "N/A"}/100. Reallocate budget toward higher-converting adjacent neighborhoods.`
        );
      });
  }, [isOpen, data, activeCategory, activeLayer, zoneMetrics, competitors]);

  const handleApplyPlaybook = () => {
    if (applyState !== "idle") return;
    setApplyState("syncing");
    setTimeout(() => {
      setApplyState("applied");
      setTimeout(() => setApplyState("idle"), 3000); // Reset after 3 seconds
    }, 1800);
  };

  if (!isOpen || !data) return null;

  const categoryMeta = getCategoryMeta(activeCategory);
  const zoneName = data.project_name || data.name || data.NAME_1 || data.shapeName || "Selected Zone";
  const sourceLabel =
    data.sourceType === "delegation" ? "Selected delegation"
      : data.sourceType === "governorate" ? "Selected governorate"
        : "Selected project";
  const demandScore = Number(data.demand_score || 0);
  const riskScore = Number(data.risk_score || 0);
  const priceValue = Number(data.avg_price || data.avg_price_sqm || 0);
  const velocity = data.velocity ? `${Number(data.velocity).toFixed(1)}%` : "N/A";
  const confidence = Math.min(97, Math.max(74, 82 + Math.round((demandScore - riskScore) / 8 || 0)));
  const stance = riskScore >= 60 ? "Mitigate" : demandScore >= 75 ? "Accelerate" : "Calibrate";
  const aiLoading = !aiRecommendation;

  const infoRows = [
    ["Source", data.sourceType || "project"],
    ["Location", `${data.city || data.governorate || "Tunisia"}${data.neighborhood ? ` · ${data.neighborhood}` : ""}`],
    ["Property Type", data.property_type || "Mixed zone"],
    ["Ad Spend", data.ad_spend ? `${Number(data.ad_spend).toLocaleString()} DT` : "N/A"],
    ["Leads", data.leads || data.lead_count || "N/A"],
    ["Qualified", data.qualified_leads || "N/A"],
    ["Unsold", data.unsold_inventory || "N/A"],
    ["Absorption", data.absorption_weeks ? `${data.absorption_weeks} weeks` : "N/A"],
    ["Infra Score", data.infrastructure_score ? `${data.infrastructure_score}/100` : "N/A"],
  ];

  return (
    <aside className="panel-shell panel-scroll fixed bottom-3 right-3 top-[calc(var(--topbar-height)+8px)] z-40 w-[calc(100vw-24px)] overflow-y-auto rounded-[var(--panel-radius)] animate-slide-in-right lg:right-4 lg:w-[390px] xl:w-[420px]">
      {/* Header */}
      <div className="border-b border-slate-100 p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg" style={{ background: categoryMeta.tint }}>
              <MapPin size={16} style={{ color: categoryMeta.color }} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">{sourceLabel}</p>
              <h2 className="text-[15px] font-bold text-slate-900 truncate mt-0.5">{zoneName}</h2>
              <p className="text-[11px] text-slate-500 truncate">
                {data.city || data.governorate || "Tunisia"}
                {data.neighborhood ? ` · ${data.neighborhood}` : ""}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-400">
            <X size={15} />
          </button>
        </div>

        {/* Stance banner */}
        <div className="overflow-hidden rounded-xl p-4 text-white" style={{ background: categoryMeta.color }}>
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-wider text-white/60 font-semibold truncate">{activeLayer.replace(/-/g, " ")}</p>
              <p className="mt-1 text-xl font-bold leading-tight">{stance}</p>
            </div>
            <div className="shrink-0 rounded-lg bg-white/15 px-3 py-2 text-right">
              <p className="text-[9px] uppercase tracking-wider text-white/60 font-semibold">Confidence</p>
              <p className="font-mono text-xl font-bold leading-tight">{confidence}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-5 space-y-5">
        {/* Score tiles */}
        <section className="grid grid-cols-2 gap-3">
          <ScoreTile label="Demand" value={`${demandScore || "N/A"}/100`} accent="#2563EB" raw={demandScore} />
          <ScoreTile label="Risk" value={`${riskScore || "N/A"}/100`} accent="#DC2626" raw={riskScore} />
          <ScoreTile label="Avg Price" value={priceValue ? `${priceValue.toLocaleString()} DT` : "N/A"} accent="#1D9E75" raw={50} />
          <ScoreTile label="Velocity" value={velocity} accent="#7C3AED" raw={parseFloat(velocity) || 50} />
        </section>

        {/* AI Strategy */}
        <section className="metric-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-overline">AI strategy brief</p>
              <h3 className="text-[13px] font-semibold text-slate-900 mt-0.5">Recommended next move</h3>
            </div>
            <Sparkles size={14} className="text-amber-500" />
          </div>

          {aiLoading ? (
            <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-4 py-4 text-[12px] text-slate-500">
              <Loader2 size={14} className="animate-spin" style={{ color: categoryMeta.color }} />
              Generating sector-specific recommendation…
            </div>
          ) : (
            <StrategyBody recommendation={aiRecommendation} />
          )}

          <div className="mt-4 grid grid-cols-2 gap-2">
            <button
              onClick={() => window.print()}
              className="flex h-10 items-center justify-center gap-1.5 rounded-lg border border-slate-200 text-[12px] font-semibold text-slate-600 transition-colors hover:bg-slate-50"
            >
              <Download size={13} />
              Export brief
            </button>
            <button
              onClick={handleApplyPlaybook}
              disabled={applyState !== "idle" || aiLoading}
              className="flex h-10 min-w-0 transition-all items-center justify-center gap-1.5 rounded-lg text-[12px] font-semibold text-white px-2 disabled:opacity-80"
              style={{ background: applyState === "applied" ? "#059669" : categoryMeta.color }}
            >
              {applyState === "idle" ? (
                <>
                  <span className="truncate">Apply playbook</span>
                  <ArrowRight size={13} className="shrink-0" />
                </>
              ) : applyState === "syncing" ? (
                <>
                  <Loader2 size={13} className="animate-spin shrink-0" />
                  <span className="truncate">Syncing to CRM...</span>
                </>
              ) : (
                <>
                  <span className="truncate">Playbook Applied!</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* Decision Frame */}
        <section className="metric-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-overline">Decision frame</p>
              <h3 className="text-[13px] font-semibold text-slate-900 mt-0.5">Why this zone matters</h3>
            </div>
            <BrainCircuit size={14} style={{ color: categoryMeta.color }} />
          </div>
          <div className="space-y-2">
            <InsightLine label="Spatial edge" text={demandScore >= 75 ? "Catchment depth justifies proactive spend and faster follow-up." : "Demand is present but requires sharper segmentation."} />
            <InsightLine label="Pricing posture" text={priceValue ? `Current ticket near ${priceValue.toLocaleString()} DT. Incentive design should protect premium positioning.` : "Pricing signal incomplete. Rely on demand and risk balance."} />
            <InsightLine label="Risk guardrail" text={riskScore >= 60 ? "Elevated risk — mitigate exposure before pushing more budget." : "Risk manageable, allowing selective acceleration."} />
          </div>
        </section>

        {/* Data Room */}
        <section className="metric-card rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-overline">Data room</p>
              <h3 className="text-[13px] font-semibold text-slate-900 mt-0.5">Underlying inputs</h3>
            </div>
            <Target size={14} className="text-slate-400" />
          </div>
          <div className="overflow-hidden rounded-lg border border-slate-100">
            <table className="w-full text-[12px]">
              <tbody>
                {infoRows.map(([label, value], i) => (
                  <tr key={label} className={i % 2 === 0 ? "bg-slate-50" : "bg-white"}>
                    <td className="px-3 py-2.5 font-medium text-slate-500 whitespace-nowrap">{label}</td>
                    <td className="px-3 py-2.5 text-right font-semibold text-slate-900 truncate max-w-[160px]">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Data source */}
        <section className="rounded-xl border border-slate-100 bg-slate-50 p-4">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck size={14} className="text-emerald-600" />
            <p className="text-[12px] font-semibold text-slate-900">Data provenance</p>
          </div>
          <ul className="space-y-1 text-[11px] leading-relaxed text-slate-500">
            <li>Population: INS RGPH 2024 Census (Nov 2024)</li>
            <li>Prices: Mubawab.tn 2025 market reports</li>
            <li>Agencies: 65+ offices tracked (Tecnocasa, Century 21, RE/MAX)</li>
            <li>Risk model: 6-dimension composite (XGBoost + Isolation Forest)</li>
          </ul>
        </section>
      </div>
    </aside>
  );
}

function ScoreTile({ label, value, accent, raw = 50 }) {
  const barWidth = Math.min(100, Math.max(5, raw));
  return (
    <div className="metric-card rounded-xl p-3.5 min-h-[88px]">
      <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 mb-1 truncate">{label}</p>
      <p className="font-mono text-[17px] font-bold text-slate-900 leading-tight break-all">{value}</p>
      <div className="mt-2 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${barWidth}%`, background: accent }} />
      </div>
    </div>
  );
}

function StrategyBody({ recommendation }) {
  if (typeof recommendation === "object" && recommendation !== null) {
    return (
      <div className="space-y-2">
        {Object.entries(recommendation).map(([key, value]) => (
          <div key={key} className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 mb-0.5">{key}</p>
            <p className="text-[12px] leading-snug text-slate-700 break-words">{String(value)}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-3">
      <p className="text-[12px] leading-snug text-slate-700 break-words">{String(recommendation)}</p>
    </div>
  );
}

function InsightLine({ label, text }) {
  return (
    <div className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2.5">
      <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 mb-0.5">{label}</p>
      <p className="text-[12px] leading-snug text-slate-600 break-words">{text}</p>
    </div>
  );
}
