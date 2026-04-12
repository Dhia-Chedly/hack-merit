"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { ArrowRight, PanelLeftClose, PanelRightClose, Target } from "lucide-react";
import TopBar from "@/components/TopBar";
import LeftPanel from "@/components/LeftPanel";
import RightPanel from "@/components/RightPanel";
import MapLegend from "@/components/MapLegend";
import { SUBCATEGORIES, getCategoryMeta } from "@/lib/dashboardConfig";

const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

export default function Dashboard() {
  const [activeCategory, setActiveCategory] = useState("marketing");
  const [activeLayer, setActiveLayer] = useState("zone-pricing");
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  const [selectedData, setSelectedData] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const syncViewport = () => {
      const mobile = window.innerWidth < 1280;
      setIsMobile(mobile);
      if (mobile) {
        setLeftPanelOpen(false);
      } else {
        setLeftPanelOpen(true);
      }
    };

    syncViewport();
    window.addEventListener("resize", syncViewport);
    return () => window.removeEventListener("resize", syncViewport);
  }, []);

  const categoryMeta = getCategoryMeta(activeCategory);
  const activeLayerMeta = (SUBCATEGORIES[activeCategory] || []).find((layer) => layer.id === activeLayer);

  const handleCategoryChange = (categoryId) => {
    const defaultLayer = SUBCATEGORIES[categoryId]?.[0]?.id || "";
    setActiveCategory(categoryId);
    setActiveLayer(defaultLayer);
  };

  const handleZoneClick = (data) => {
    setSelectedData(data);
    setRightPanelOpen(true);
  };

  return (
    <main className="relative h-[100dvh] w-screen overflow-hidden bg-slate-50 isolate">
      <MapView
        activeCategory={activeCategory}
        activeLayer={activeLayer}
        onZoneClick={handleZoneClick}
      />

      <TopBar
        activeCategory={activeCategory}
        setActiveCategory={handleCategoryChange}
        activeLayer={activeLayer}
        setActiveLayer={setActiveLayer}
        onToggleLeft={() => setLeftPanelOpen((value) => !value)}
        onToggleRight={() => setRightPanelOpen((value) => !value)}
        selectedData={selectedData}
      />

      <LeftPanel
        activeCategory={activeCategory}
        activeLayer={activeLayer}
        isOpen={leftPanelOpen}
        onClose={() => setLeftPanelOpen(false)}
      />

      <RightPanel
        key={`${activeCategory}-${activeLayer}-${selectedData?.id || selectedData?.project_name || selectedData?.name || selectedData?.NAME_1 || "none"}`}
        data={selectedData}
        isOpen={rightPanelOpen}
        onClose={() => {
          setRightPanelOpen(false);
          if (isMobile) {
            setSelectedData(null);
          }
        }}
        activeCategory={activeCategory}
        activeLayer={activeLayer}
      />

      <MapLegend activeCategory={activeCategory} activeLayer={activeLayer} />

      {!leftPanelOpen && (
        <button
          onClick={() => setLeftPanelOpen(true)}
          className="floating-chip fixed left-4 top-[calc(var(--topbar-height)+18px)] z-40 flex h-12 w-12 items-center justify-center rounded-2xl transition-transform hover:scale-[1.03]"
          aria-label="Open intelligence panel"
        >
          <PanelLeftClose size={18} className="text-slate-700" />
        </button>
      )}

      {!rightPanelOpen && selectedData && (
        <button
          onClick={() => setRightPanelOpen(true)}
          className="floating-chip fixed right-4 top-[calc(var(--topbar-height)+18px)] z-40 flex h-12 items-center gap-2 rounded-2xl px-4 transition-transform hover:scale-[1.02]"
        >
          <PanelRightClose size={18} className="text-slate-700" />
          <span className="text-sm font-semibold text-slate-800">
            Open insight
          </span>
        </button>
      )}

      <div className="pointer-events-none fixed bottom-4 right-4 z-30 hidden md:block">
        <div className="floating-chip pointer-events-auto max-w-[360px] rounded-2xl px-4 py-3">
          <div className="mb-1 flex items-center gap-2">
            <Target size={14} style={{ color: categoryMeta.color }} />
            <p className="text-overline text-slate-500">{activeLayerMeta?.label || categoryMeta.shortLabel}</p>
          </div>
          <div className="mt-1 flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-900">{categoryMeta.headline}</span>
            <ArrowRight size={15} className="text-slate-500" />
          </div>
        </div>
      </div>
    </main>
  );
}
