"use client";

import { getCategoryMeta } from "@/lib/dashboardConfig";

const LEGENDS = {
  marketing: {
    "zone-pricing": {
      title: "Zone Price (DT/m2)",
      type: "gradient",
      colors: ["#F0F9FF", "#BAE6FD", "#38BDF8", "#1D4ED8", "#0C2461"],
      labels: ["<1.5k", "2.5k", "3.5k", "5k+"],
    },
    "price-trend": {
      title: "Price Change (MoM)",
      type: "gradient",
      colors: ["#7F1D1D", "#F87171", "#E2E8F0", "#34D399", "#065F46"],
      labels: ["Decline", "Flat", "Rise", "Strong rise"],
    },
    "lead-density": {
      title: "Lead Density",
      type: "gradient",
      colors: ["#FEF9C3", "#FBBF24", "#FB923C", "#EF4444", "#DC2626"],
      labels: ["Low", "Medium", "High", "Peak"],
    },
    "buyer-origin": {
      title: "Buyer Origin",
      type: "dots",
      items: [
        { color: "#1D9E75", label: "Reservation" },
        { color: "#2EC4D6", label: "Lead only" },
      ],
    },
    attribution: {
      title: "Source Mix",
      type: "dots",
      items: [
        { color: "#2563EB", label: "Meta" },
        { color: "#F59E0B", label: "Google" },
        { color: "#7C3AED", label: "Broker" },
        { color: "#1D9E75", label: "Direct" },
      ],
    },
  },
  forecast: {
    demand: {
      title: "Demand Index",
      type: "gradient",
      colors: ["#DBEAFE", "#3B82F6", "#7C3AED", "#F59E0B"],
      labels: ["Low", "Medium", "High", "Premium"],
    },
    velocity: {
      title: "Sales Velocity",
      type: "gradient",
      colors: ["#FEE2E2", "#F87171", "#7C3AED", "#1D9E75"],
      labels: ["Slow", "Mixed", "Fast", "Very fast"],
    },
    absorption: {
      title: "Absorption Horizon",
      type: "gradient",
      colors: ["#1D9E75", "#FDE68A", "#F59E0B", "#DC2626"],
      labels: ["Short", "Balanced", "Long", "Stalled"],
    },
  },
  risk: {
    "risk-grid": {
      title: "Composite Risk",
      type: "gradient",
      colors: ["#D1FAE5", "#A7F3D0", "#FEF3C7", "#FBBF24", "#7F1D1D"],
      labels: ["Low", "Guarded", "Moderate", "Critical"],
    },
    competitors: {
      title: "Competitor Presence",
      type: "dots",
      items: [
        { color: "#FBBF24", label: "Competitor" },
        { color: "#1D9E75", label: "TerraLens project" },
      ],
    },
    oversupply: {
      title: "Supply Balance",
      type: "gradient",
      colors: ["#1D9E75", "#FEF3C7", "#F59E0B", "#DC2626"],
      labels: ["Tight", "Balanced", "Heavy", "Oversupplied"],
    },
    infrastructure: {
      title: "Infrastructure Risk",
      type: "dots",
      items: [
        { color: "#7F1D1D", label: "Critical" },
        { color: "#DC2626", label: "High" },
        { color: "#F59E0B", label: "Medium" },
      ],
    },
  },
};

export default function MapLegend({ activeCategory, activeLayer, leftPanelOpen }) {
  const legend = LEGENDS[activeCategory]?.[activeLayer];
  const categoryMeta = getCategoryMeta(activeCategory);

  if (!legend) {
    return null;
  }

  const positionClasses = leftPanelOpen
    ? "left-4 lg:left-[410px] xl:left-[440px] transition-all duration-300"
    : "left-4 md:left-6 transition-all duration-300";

  return (
    <div className={`pointer-events-none fixed bottom-28 z-30 xl:bottom-36 ${positionClasses}`}>
      <div className="floating-chip pointer-events-auto w-[210px] rounded-lg px-3 py-3 animate-fade-in">
        <div className="mb-3 flex items-center justify-between">
          <div>
          <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">{categoryMeta.shortLabel}</p>
            <p className="text-[12px] font-semibold text-slate-900 mt-0.5">{legend.title}</p>
          </div>
          <div
            className="h-7 w-7 rounded-lg"
            style={{ background: categoryMeta.tint }}
          />
        </div>

        {(legend.type === "gradient" || legend.type === "diverging") && (
          <>
            <div
              className="h-3 rounded-full"
              style={{ background: `linear-gradient(90deg, ${legend.colors.join(", ")})` }}
            />
            <div className="mt-2 grid grid-cols-4 gap-2">
              {legend.labels.map((label) => (
                <span key={label} className="text-[10px] leading-4 text-slate-500">
                  {label}
                </span>
              ))}
            </div>
          </>
        )}

        {legend.type === "dots" && (
          <div className="space-y-2">
            {legend.items.map((item) => (
              <div key={item.label} className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full" style={{ background: item.color }} />
                <span className="text-xs text-slate-600">{item.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
