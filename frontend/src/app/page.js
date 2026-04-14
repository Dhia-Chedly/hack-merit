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
  const [searchQuery, setSearchQuery] = useState("");

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
        searchQuery={searchQuery}
      />

      <TopBar
        activeCategory={activeCategory}
        setActiveCategory={handleCategoryChange}
        activeLayer={activeLayer}
        setActiveLayer={setActiveLayer}
        onToggleLeft={() => setLeftPanelOpen((value) => !value)}
        onToggleRight={() => setRightPanelOpen((value) => !value)}
        selectedData={selectedData}
        onSearch={setSearchQuery}
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

      <MapLegend activeCategory={activeCategory} activeLayer={activeLayer} leftPanelOpen={leftPanelOpen} />

      {!leftPanelOpen && (
        <button
          onClick={() => setLeftPanelOpen(true)}
          className="floating-chip fixed left-4 top-[calc(var(--topbar-height)+8px)] z-40 flex h-10 w-10 items-center justify-center rounded-lg"
          aria-label="Open intelligence panel"
        >
          <PanelLeftClose size={16} className="text-slate-500" />
        </button>
      )}

      {!rightPanelOpen && selectedData && (
        <button
          onClick={() => setRightPanelOpen(true)}
          className="floating-chip fixed right-4 top-[calc(var(--topbar-height)+8px)] z-40 flex h-10 items-center gap-2 rounded-lg px-3"
        >
          <PanelRightClose size={16} className="text-slate-500" />
          <span className="text-[12px] font-semibold text-slate-600">Open insight</span>
        </button>
      )}

      <div className="pointer-events-none fixed bottom-4 right-4 z-30 hidden md:block">
        <div className="floating-chip pointer-events-auto max-w-[340px] rounded-lg px-3 py-2.5">
          <div className="flex items-center gap-2">
            <Target size={12} style={{ color: categoryMeta.color }} />
            <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">{activeLayerMeta?.label || categoryMeta.shortLabel}</p>
          </div>
          <p className="mt-1 text-[12px] font-medium text-slate-600 leading-snug">{categoryMeta.headline}</p>
        </div>
      </div>
    </main>
  );
}
