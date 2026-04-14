"use client";

import Image from "next/image";
import {
  Layers3,
  PanelLeft,
  PanelRight,
  Search,
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
  onSearch,
}) {
  const categoryMeta = getCategoryMeta(activeCategory);
  const subcategories = SUBCATEGORIES[activeCategory] || [];

  return (
    <header className="pointer-events-none fixed inset-x-0 top-0 z-50 px-4 pt-3">
      <div className="pointer-events-auto rounded-[12px] bg-white border border-slate-200 px-4 py-2.5 shadow-sm">
        <div className="flex items-center justify-between">
          {/* LEFT: Branding */}
          <div className="flex items-center gap-3">
            <button
              onClick={onToggleLeft}
              className="ml-1 flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 text-slate-500"
            >
              <PanelLeft size={15} />
            </button>
          </div>

          {/* CENTER: Category Tabs */}
          <div className="flex items-center gap-1 bg-slate-50 p-1 rounded-lg border border-slate-100">
            {CATEGORIES.map((category) => {
              const Icon = category.icon;
              const isActive = activeCategory === category.id;

              return (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className="flex h-9 items-center gap-2 rounded-md px-4 text-[13px] font-semibold transition-colors"
                  style={
                    isActive
                      ? { background: category.color, color: "#FFFFFF" }
                      : { background: "transparent", color: "#64748B" }
                  }
                >
                  <Icon size={14} />
                  <span className="hidden md:inline">{category.label}</span>
                </button>
              );
            })}
          </div>

          {/* RIGHT: Sub-layers + Actions */}
          <div className="flex items-center gap-2">
            <div className="hidden xl:flex items-center gap-0.5 bg-slate-50 rounded-lg p-1 border border-slate-100">
              {subcategories.map((sub) => {
                const Icon = sub.icon;
                const isActive = activeLayer === sub.id;

                return (
                  <button
                    key={sub.id}
                    onClick={() => setActiveLayer(sub.id)}
                    className={`flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-[11px] font-semibold ${isActive ? "bg-white border border-slate-200 text-slate-800" : "text-slate-500"}`}
                  >
                    <Icon size={12} style={{ color: isActive ? categoryMeta.color : "" }} />
                    <span className="whitespace-nowrap">{sub.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="hidden lg:flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5">
              <Search size={13} className="text-slate-400" />
              <select
                onChange={(e) => {
                  if(onSearch) onSearch(e.target.value);
                }}
                className="text-[11px] text-slate-800 outline-none w-[120px] bg-transparent cursor-pointer font-semibold"
                defaultValue=""
              >
                <option value="" disabled>Select Zone…</option>
                <optgroup label="Grand Tunis">
                  <option value="Tunis">Tunis</option>
                  <option value="Ariana">Ariana</option>
                  <option value="Ben Arous">Ben Arous</option>
                  <option value="Manouba">Manouba</option>
                </optgroup>
                <optgroup label="Cap Bon & Region">
                  <option value="Nabeul">Nabeul</option>
                  <option value="Sousse">Sousse</option>
                </optgroup>
                <optgroup label="South">
                  <option value="Sfax">Sfax</option>
                </optgroup>
              </select>
            </div>

            <button
              onClick={onToggleRight}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500"
            >
              <PanelRight size={15} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
