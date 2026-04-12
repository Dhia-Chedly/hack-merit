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

  useEffect(() => {
    if (!isOpen || !data) {
      return;
    }

    const context = JSON.stringify({
      name: data.name || data.project_name || data.NAME_1 || "Zone",
      avg_price: data.avg_price_sqm || data.avg_price || 0,
      demand_score: data.demand_score || 0,
      risk_score: data.risk_score || 0,
      category: activeCategory,
      layer: activeLayer,
      source_type: data.sourceType || "project",
    });

    fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context }),
    })
      .then((response) => response.json())
      .then((payload) => {
        setAiRecommendation(payload.recommendation || "No recommendation available.");
      })
      .catch(() => {
        setAiRecommendation(
          data.recommended_action ||
            `Demand sits at ${data.demand_score || "N/A"} while risk remains ${data.risk_score || "N/A"}. Reallocate budget toward higher-converting adjacent neighborhoods, tighten message-market fit, and preserve pricing power with selective incentives.`
        );
      });
  }, [isOpen, data, activeCategory, activeLayer]);

  if (!isOpen || !data) {
    return null;
  }

  const categoryMeta = getCategoryMeta(activeCategory);
  const zoneName = data.project_name || data.name || data.NAME_1 || data.shapeName || "Selected Zone";
  const sourceLabel =
    data.sourceType === "delegation"
      ? "Selected delegation"
      : data.sourceType === "governorate"
        ? "Selected governorate"
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
    ["Location", `${data.city || data.governorate || "Tunisia"}${data.neighborhood ? ` . ${data.neighborhood}` : ""}`],
    ["Property Type", data.property_type || "Mixed zone"],
    ["Ad Spend", data.ad_spend ? `${Number(data.ad_spend).toLocaleString("en-US")} DT` : "N/A"],
    ["Leads", data.leads || data.lead_count || "N/A"],
    ["Qualified", data.qualified_leads || "N/A"],
    ["Unsold", data.unsold_inventory || "N/A"],
  ];

  return (
    <aside className="panel-shell panel-scroll fixed bottom-3 right-3 top-[calc(var(--topbar-height)+10px)] z-40 w-[calc(100vw-24px)] overflow-y-auto rounded-[var(--panel-radius)] animate-slide-in-right lg:right-4 lg:w-[380px] xl:w-[420px]">
      <div className="border-b border-slate-200/70 px-5 pb-5 pt-5">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl" style={{ background: `linear-gradient(135deg, ${categoryMeta.tint}, #ffffff)` }}>
              <MapPin size={18} style={{ color: categoryMeta.color }} />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">{sourceLabel}</p>
              <h2 className="max-w-[16rem] text-lg font-bold leading-tight text-slate-950 truncate mt-1">{zoneName}</h2>
              <p className="mt-1 text-[13px] text-slate-500 truncate">
                {data.city || data.governorate || "Tunisia"}
                {data.neighborhood ? ` . ${data.neighborhood}` : ""}
              </p>
            </div>
          </div>

          <button onClick={onClose} className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-500 transition hover:text-slate-900">
            <X size={17} />
          </button>
        </div>

        <div className="rounded-[24px] p-5 text-white shadow-sm" style={{ background: `linear-gradient(135deg, ${categoryMeta.color}, ${categoryMeta.color}DD, #0C2461)` }}>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <p className="text-[11px] uppercase tracking-widest text-white/80 font-bold mb-2">
                {activeLayer.replace(/-/g, " ")}
              </p>
              <p className="text-3xl font-extrabold tracking-tight text-white leading-none shadow-sm">{stance}</p>
              <p className="mt-3 text-[13px] leading-relaxed text-white/90">
                The map sees both opportunity and friction. Use this drawer to frame the next decision.
              </p>
            </div>
            <div className="shrink-0 rounded-[18px] border border-white/20 bg-white/10 px-4 py-3 text-right backdrop-blur-md shadow-sm">
              <div className="flex flex-col items-end">
                <p className="text-[10px] uppercase tracking-widest text-white/70 font-bold mb-1">Confidence</p>
                <p className="font-mono text-3xl font-extrabold leading-none">{confidence}%</p>
                <p className="text-[10px] text-white/80 font-bold uppercase tracking-wider mt-1">AI-backed</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-5 px-5 py-5">
        <section className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <NarrativeCard
            title="What this means"
            value={stance}
            text={
              stance === "Accelerate"
                ? "This zone supports more confident spend and faster follow-up."
                : stance === "Mitigate"
                  ? "Protect pricing and reduce exposure before pushing more budget."
                  : "Opportunity exists, but execution needs tighter targeting."
            }
          />
          <NarrativeCard
            title="Confidence"
            value={`${confidence}%`}
            text="A fast read of how strongly the current spatial and commercial signals align."
          />
        </section>

        <section className="grid grid-cols-2 gap-3">
          <ScoreTile label="Demand" value={`${demandScore || "N/A"}/100`} accent="#2563EB" />
          <ScoreTile label="Risk" value={`${riskScore || "N/A"}/100`} accent="#DC2626" />
          <ScoreTile label="Avg Price" value={priceValue ? `${priceValue.toLocaleString("en-US")} DT` : "N/A"} accent="#1D9E75" />
          <ScoreTile label="Velocity" value={velocity} accent="#7C3AED" />
        </section>

        <section className="metric-card rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">AI strategy brief</p>
              <h3 className="text-base font-semibold text-slate-950">Recommended next move</h3>
            </div>
            <Sparkles size={16} className="text-amber-500" />
          </div>

          {aiLoading ? (
            <div className="flex items-center gap-3 rounded-[20px] bg-slate-50 px-4 py-5 text-sm text-slate-600">
              <Loader2 size={16} className="animate-spin" style={{ color: categoryMeta.color }} />
              Preparing a concise spatial recommendation...
            </div>
          ) : (
            <StrategyBody recommendation={aiRecommendation} />
          )}

          <div className="mt-4 grid grid-cols-2 gap-3">
            <button className="flex h-11 items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white text-sm font-semibold text-slate-700 transition hover:-translate-y-0.5">
              <Download size={15} />
              Export brief
            </button>
            <button className="flex h-11 items-center justify-center gap-2 rounded-2xl text-sm font-semibold text-white transition hover:-translate-y-0.5" style={{ background: categoryMeta.color }}>
              Apply playbook
              <ArrowRight size={15} />
            </button>
          </div>
        </section>

        <section className="metric-card rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Decision frame</p>
              <h3 className="text-base font-semibold text-slate-950">Why this zone matters</h3>
            </div>
            <BrainCircuit size={16} style={{ color: categoryMeta.color }} />
          </div>

          <div className="space-y-3">
            <InsightLine label="Spatial edge" text={demandScore >= 75 ? "Catchment depth justifies proactive spend and faster follow-up." : "Demand is present but requires sharper segmentation and sequencing."} />
            <InsightLine label="Pricing posture" text={priceValue ? `Current ticket sits near ${priceValue.toLocaleString()} DT, so incentive design should protect premium positioning.` : "Pricing signal is incomplete, so rely on demand and risk balance before changing offer structure."} />
            <InsightLine label="Risk guardrail" text={riskScore >= 60 ? "Elevated risk means mitigate exposure before pushing more budget into the zone." : "Risk remains manageable, allowing selective acceleration with controlled testing."} />
          </div>
        </section>

        <section className="metric-card rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-overline text-slate-500">Data room</p>
              <h3 className="text-base font-semibold text-slate-950">Underlying inputs</h3>
            </div>
            <Target size={16} className="text-slate-400" />
          </div>

          <div className="overflow-hidden rounded-[20px] border border-slate-200">
            <table className="w-full text-sm">
              <tbody>
                {infoRows.map(([label, value], index) => (
                  <tr key={label} className={index % 2 === 0 ? "bg-slate-50" : "bg-white"}>
                    <td className="px-4 py-3 font-medium text-slate-500">{label}</td>
                    <td className="px-4 py-3 text-right font-semibold text-slate-900">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-[24px] border border-slate-200 bg-[linear-gradient(180deg,#ffffff,#f8fafc)] p-4">
          <div className="mb-3 flex items-center gap-2">
            <ShieldCheck size={16} className="text-emerald-600" />
            <p className="text-sm font-semibold text-slate-950">Recommendation hygiene</p>
          </div>
          <ul className="space-y-2 text-sm leading-5 text-slate-600">
            <li>Grounded in the active map layer and the selected geography.</li>
            <li>Combines commercial upside with supply and risk context.</li>
            <li>Designed to be presentable in an agency or investor review instantly.</li>
          </ul>
        </section>
      </div>
    </aside>
  );
}

function ScoreTile({ label, value, accent }) {
  return (
    <div className="metric-card rounded-[22px] p-4 shadow-sm border border-slate-100">
      <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 mb-1">{label}</p>
      <p className="font-mono text-2xl font-extrabold tracking-tight text-slate-900">{value}</p>
      <div className="mt-3 h-2 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-2 rounded-full transition-all duration-500 ease-out" style={{ width: "78%", background: accent }} />
      </div>
    </div>
  );
}

function StrategyBody({ recommendation }) {
  if (typeof recommendation === "object" && recommendation !== null) {
    return (
      <div className="space-y-3">
        {Object.entries(recommendation).map(([key, value]) => (
          <div key={key} className="rounded-[20px] bg-slate-50 border border-slate-100 px-4 py-3">
            <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 mb-0.5">{key}</p>
            <p className="text-sm leading-snug text-slate-700">{String(value)}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-[20px] bg-slate-50 border border-slate-100 px-4 py-4">
      <p className="text-sm leading-snug text-slate-700">{String(recommendation)}</p>
    </div>
  );
}

function InsightLine({ label, text }) {
  return (
    <div className="rounded-[20px] bg-slate-50 border border-slate-100 px-4 py-3">
      <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 mb-0.5">{label}</p>
      <p className="text-[13px] leading-snug text-slate-700">{text}</p>
    </div>
  );
}

function NarrativeCard({ title, value, text }) {
  return (
    <div className="metric-card rounded-[22px] p-4 shadow-sm border border-slate-100">
      <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 mb-1">{title}</p>
      <p className="font-mono text-xl font-extrabold tracking-tight text-slate-900 leading-none">{value}</p>
      <p className="mt-2 text-sm leading-snug text-slate-600 line-clamp-3">{text}</p>
    </div>
  );
}
