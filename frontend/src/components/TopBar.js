"use client";

import Image from "next/image";
import {
  Bell,
  ChevronRight,
  Layers3,
  PanelLeft,
  PanelRight,
  Search,
  ShieldCheck,
} from "lucide-react";
import { CATEGORIES, SUBCATEGORIES, getCategoryMeta } from "@/lib/dashboardConfig";

export default function TopBar({
  activeCategory,
  setActiveCategory,
  activeLayer,
  setActiveLayer,
  onToggleLeft,
  onToggleRight,
  selectedData,
}) {
  const categoryMeta = getCategoryMeta(activeCategory);
  const subcategories = SUBCATEGORIES[activeCategory] || [];

  return (
    <header className="pointer-events-none fixed inset-x-0 top-0 z-50 px-4 pt-4">
      <div className="glass pointer-events-auto rounded-[24px] px-5 py-3 shadow-[0_12px_32px_rgba(15,23,42,0.08)] bg-white/80 backdrop-blur-xl border border-white/90">
        <div className="flex items-center justify-between">
          {/* LEFT: Branding */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white shadow-sm border border-slate-100">
              <Image
                src="/terralens_logo.png"
                alt="TerraLens AI"
                width={28}
                height={28}
                className="h-6 w-6 object-contain"
                priority
              />
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center gap-2">
                <p className="text-[14px] font-bold tracking-tight text-slate-900">TERRALENS</p>
                <span className="rounded-[6px] bg-sky-100/80 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-sky-700">
                  AI
                </span>
              </div>
            </div>
            
            <button
              onClick={onToggleLeft}
              className="ml-2 flex h-9 w-9 items-center justify-center rounded-xl bg-slate-50 border border-slate-200/60 text-slate-500 transition hover:bg-white hover:text-slate-900 shadow-sm"
            >
              <PanelLeft size={16} />
            </button>
          </div>

          {/* CENTER: Main Category Tabs */}
          <div className="flex items-center justify-center bg-slate-100/60 p-1.5 rounded-[22px] border border-slate-200/50 my-1">
            {CATEGORIES.map((category) => {
              const Icon = category.icon;
              const isActive = activeCategory === category.id;

              return (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className="group flex h-11 min-w-[160px] items-center justify-center gap-2.5 rounded-[18px] px-4 text-sm font-bold transition-all duration-300 relative mx-0.5"
                  style={
                    isActive
                      ? {
                          background: category.color,
                          color: "#FFFFFF",
                          boxShadow: `0 4px 14px ${category.glow}`,
                        }
                      : {
                          background: "transparent",
                          color: "#64748B",
                        }
                  }
                >
                  <Icon size={16} />
                  <span>{category.label}</span>
                </button>
              );
            })}
          </div>

          {/* RIGHT: Global Actions & Subtabs */}
          <div className="flex items-center justify-end gap-3 min-w-[340px]">
            {/* Contextual Sub-layers */}
            <div className="hidden xl:flex items-center gap-1.5 bg-slate-50/80 rounded-full p-1 border border-slate-200/60 mr-2">
              {subcategories.map((sub) => {
                const Icon = sub.icon;
                const isActive = activeLayer === sub.id;

                return (
                  <button
                    key={sub.id}
                    onClick={() => setActiveLayer(sub.id)}
                    className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold transition-colors duration-200 ${isActive ? 'bg-white shadow border-slate-100 text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}
                  >
                    <Icon size={14} style={{ color: isActive ? categoryMeta.color : '' }} />
                    <span className="whitespace-nowrap">{sub.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="h-8 w-[1px] bg-slate-200 mx-1 hidden lg:block" />

            <div className="hidden lg:flex items-center gap-2 rounded-[16px] border border-slate-200 bg-white px-3 py-2 shadow-sm min-w-[140px]">
              <Search size={14} className="text-slate-400" />
              <span className="text-[12px] text-slate-400">Search zones...</span>
            </div>

            <button
              onClick={onToggleRight}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-50 border border-slate-200/60 text-slate-500 transition hover:bg-white hover:text-slate-900 shadow-sm"
            >
              <PanelRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
