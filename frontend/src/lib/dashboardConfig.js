import {
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  Building2,
  LocateFixed,
  Radar,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Waves,
} from "lucide-react";

export const CATEGORIES = [
  {
    id: "marketing",
    label: "Marketing Intelligence",
    shortLabel: "Marketing",
    color: "#2563EB",
    tint: "#EFF6FF",
    glow: "rgba(37, 99, 235, 0.18)",
    icon: BarChart3,
    eyebrow: "Campaign Intelligence",
    headline: "Decode where real buyers originate and which zones deserve budget now.",
  },
  {
    id: "forecast",
    label: "Prediction & Planning",
    shortLabel: "Prediction",
    color: "#7C3AED",
    tint: "#F5F3FF",
    glow: "rgba(124, 58, 237, 0.18)",
    icon: TrendingUp,
    eyebrow: "Forward Signals",
    headline: "Surface the next pockets of demand before campaign spend shifts there.",
  },
  {
    id: "risk",
    label: "Risk & Mitigation",
    shortLabel: "Risk",
    color: "#DC2626",
    tint: "#FEF2F2",
    glow: "rgba(220, 38, 38, 0.18)",
    icon: ShieldAlert,
    eyebrow: "Portfolio Defense",
    headline: "See oversupply, infrastructure pressure, and competitive threats before they compound.",
  },
];

export const SUBCATEGORIES = {
  marketing: [
    { id: "zone-pricing", label: "Zone Pricing", icon: Building2, description: "Price-led demand map" },
    { id: "price-trend", label: "Price Rise %", icon: TrendingUp, description: "Momentum by governorate" },
    { id: "lead-density", label: "Lead Density", icon: Radar, description: "Traffic heat surface" },
    { id: "buyer-origin", label: "Buyer Origin", icon: LocateFixed, description: "Catchment clusters" },
    { id: "attribution", label: "Attribution", icon: Sparkles, description: "Source efficiency split" },
  ],
  forecast: [
    { id: "demand", label: "Demand Forecast", icon: BrainCircuit, description: "12-month demand outlook" },
    { id: "velocity", label: "Sales Velocity", icon: TrendingUp, description: "Inventory movement speed" },
    { id: "absorption", label: "Absorption Rate", icon: Waves, description: "Sell-through horizon" },
  ],
  risk: [
    { id: "risk-grid", label: "Risk Grid", icon: ShieldAlert, description: "Composite zone risk" },
    { id: "competitors", label: "Competitor Pressure", icon: Building2, description: "Nearby market crowding" },
    { id: "oversupply", label: "Oversupply", icon: AlertTriangle, description: "Inventory imbalance" },
    { id: "infrastructure", label: "Infrastructure Risk", icon: Radar, description: "External disruption zones" },
  ],
};

export function getCategoryMeta(categoryId) {
  return CATEGORIES.find((category) => category.id === categoryId) ?? CATEGORIES[0];
}
