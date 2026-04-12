"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const MAPTILER_KEY = "2rJz6kffNiHH881P3PE2";
const MAP_STYLE = `https://api.maptiler.com/maps/dataviz-light/style.json?key=${MAPTILER_KEY}`;

export default function MapView({ activeCategory, activeLayer, onZoneClick }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const popup = useRef(null);
  const [layersLoaded, setLayersLoaded] = useState(false);

  const setPopupMarkup = useCallback((markup) => {
    if (!popup.current) {
      return;
    }

    popup.current.setHTML(`
      <div style="padding:16px 16px 14px;background:linear-gradient(180deg,#ffffff,#f8fafc);font-family:Inter,system-ui,sans-serif;">
        ${markup}
      </div>
    `);
  }, []);

  const normalizeGovernorateName = useCallback((value) => {
    if (!value) {
      return "";
    }

    const normalized = String(value).trim().toLowerCase();
    const aliases = {
      mannouba: "Manouba",
      manouba: "Manouba",
      "ben arous": "Ben Arous",
      tunis: "Tunis",
      ariana: "Ariana",
      nabeul: "Nabeul",
      sousse: "Sousse",
      sfax: "Sfax",
      bizerte: "Bizerte",
      zaghouan: "Zaghouan",
      kairouan: "Kairouan",
      mahdia: "Mahdia",
    };

    return aliases[normalized] || String(value).trim();
  }, []);

  const normalizeSelection = useCallback((properties, type) => {
    const governorate = normalizeGovernorateName(
      properties.governorate || properties.gouv_fr || properties.name || properties.NAME_1
    );
    const delegation = properties.delegation || properties.del_fr || null;
    const name = delegation || governorate || properties.project_name || "Selected Zone";

    return {
      ...properties,
      governorate,
      delegation,
      name,
      sourceType: type,
      shapeName: name,
    };
  }, [normalizeGovernorateName]);

  const applyActiveStyles = useCallback(() => {
    if (!map.current) {
      return;
    }

    const currentMap = map.current;
    const hasLayer = (id) => Boolean(currentMap.getLayer(id));
    const setPaint = (id, property, value) => {
      if (!hasLayer(id)) {
        return;
      }
      currentMap.setPaintProperty(id, property, value);
    };

    if (!hasLayer("gov-fill")) {
      return;
    }

    setPaint("gov-fill", "fill-opacity", 0.52);
    setPaint("gov-outline", "line-opacity", 1);
    setPaint("del-fill", "fill-opacity", 0.48);
    setPaint("del-outline", "line-opacity", 0.3);
    setPaint("lead-heat", "heatmap-opacity", 0);
    setPaint("buyer-scatter", "circle-opacity", 0);
    setPaint("risk-fill", "fill-opacity", 0);
    setPaint("risk-outline", "line-opacity", 0);
    setPaint("project-markers", "circle-opacity", 0.92);
    setPaint("project-glow", "circle-opacity", 0.34);
    setPaint("competitor-markers", "circle-opacity", 0.78);
    setPaint("competitor-markers", "circle-radius", 7);
    if (hasLayer("competitor-labels")) {
      currentMap.setPaintProperty("competitor-labels", "text-opacity", 0);
    }

    if (activeCategory === "marketing") {
      if (activeLayer === "zone-pricing" || activeLayer === "") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "avg_price_sqm"], 800, "#F0F9FF", 1500, "#BAE6FD", 2500, "#38BDF8", 3500, "#1D4ED8", 5000, "#0C2461"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "avg_price_sqm"], 800, "#F0F9FF", 1500, "#BAE6FD", 2500, "#38BDF8", 3500, "#1D4ED8", 5000, "#0C2461"]);
      } else if (activeLayer === "price-trend") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "mom_price_change_pct"], -1, "#7F1D1D", -0.2, "#F87171", 0, "#E2E8F0", 0.3, "#34D399", 0.8, "#065F46"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "mom_price_change_pct"], -1, "#7F1D1D", -0.2, "#F87171", 0, "#E2E8F0", 0.3, "#34D399", 0.8, "#065F46"]);
      } else if (activeLayer === "lead-density") {
        setPaint("lead-heat", "heatmap-opacity", 0.78);
        setPaint("gov-fill", "fill-opacity", 0.12);
        setPaint("del-fill", "fill-opacity", 0.12);
        setPaint("project-markers", "circle-opacity", 0.2);
      } else if (activeLayer === "buyer-origin") {
        setPaint("buyer-scatter", "circle-opacity", 0.76);
        setPaint("gov-fill", "fill-opacity", 0.12);
        setPaint("del-fill", "fill-opacity", 0.12);
        setPaint("project-markers", "circle-opacity", 0.38);
      } else if (activeLayer === "attribution") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "lead_count"], 20, "#F0F9FF", 100, "#BAE6FD", 250, "#3B82F6", 500, "#1E40AF"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "lead_count"], 20, "#F0F9FF", 100, "#BAE6FD", 250, "#3B82F6", 500, "#1E40AF"]);
      }
    } else if (activeCategory === "forecast") {
      setPaint("del-fill", "fill-opacity", 0.32);
      setPaint("del-outline", "line-opacity", 0.6);

      if (activeLayer === "demand" || activeLayer === "") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "demand_score"], 18, "#DBEAFE", 40, "#3B82F6", 70, "#7C3AED", 95, "#F59E0B"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "demand_score"], 15, "#DBEAFE", 40, "#818CF8", 70, "#7C3AED", 95, "#F59E0B"]);
      } else if (activeLayer === "velocity") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "velocity_index"], 30, "#FEE2E2", 50, "#FCA5A5", 70, "#A78BFA", 90, "#1D9E75"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "velocity_index"], 30, "#FEE2E2", 50, "#FCA5A5", 70, "#A78BFA", 90, "#1D9E75"]);
      } else if (activeLayer === "absorption") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "absorption_weeks"], 8, "#1D9E75", 20, "#FDE68A", 35, "#F59E0B", 52, "#DC2626"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "absorption_weeks"], 4, "#1D9E75", 15, "#FDE68A", 30, "#F59E0B", 60, "#DC2626"]);
      }
    } else if (activeCategory === "risk") {
      if (activeLayer === "risk-grid" || activeLayer === "") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "risk_score"], 10, "#D1FAE5", 25, "#A7F3D0", 40, "#FEF3C7", 60, "#FBBF24", 80, "#7F1D1D"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "risk_score"], 10, "#D1FAE5", 25, "#A7F3D0", 40, "#FEF3C7", 60, "#FBBF24", 80, "#7F1D1D"]);
        setPaint("risk-fill", "fill-opacity", 0.22);
        setPaint("risk-outline", "line-opacity", 0.64);
      } else if (activeLayer === "competitors") {
        setPaint("gov-fill", "fill-opacity", 0.12);
        setPaint("del-fill", "fill-opacity", 0.12);
        setPaint("project-markers", "circle-opacity", 0.56);
        setPaint("competitor-markers", "circle-radius", 10);
        setPaint("competitor-markers", "circle-opacity", 1);
        if (hasLayer("competitor-labels")) {
          currentMap.setPaintProperty("competitor-labels", "text-opacity", 1);
        }
      } else if (activeLayer === "oversupply") {
        setPaint("gov-fill", "fill-color", ["interpolate", ["linear"], ["get", "absorption_weeks"], 8, "#1D9E75", 25, "#FEF3C7", 40, "#F59E0B", 52, "#DC2626"]);
        setPaint("del-fill", "fill-color", ["interpolate", ["linear"], ["get", "absorption_weeks"], 8, "#1D9E75", 25, "#FEF3C7", 40, "#F59E0B", 52, "#DC2626"]);
        setPaint("del-outline", "line-opacity", 0.4);
      } else if (activeLayer === "infrastructure") {
        setPaint("gov-fill", "fill-opacity", 0.14);
        setPaint("del-fill", "fill-opacity", 0.14);
        setPaint("project-markers", "circle-opacity", 0.48);
        setPaint("risk-fill", "fill-opacity", 0.4);
        setPaint("risk-outline", "line-opacity", 0.82);
      }
    }
  }, [activeCategory, activeLayer]);

  const loadGeoJsonLayers = useCallback(async () => {
    if (!map.current) {
      return;
    }

    const currentMap = map.current;

    try {
      const [governorates, delegations, projects, competitors, leads, buyers, riskZones, zoneMetrics] = await Promise.all([
        fetch("/data/geodata/governorates.geojson").then((response) => response.json()),
        fetch("/data/geodata/delegations.geojson").then((response) => response.json()),
        fetch("/data/projects_extended.json").then((response) => response.json()),
        fetch("/data/competitors.json").then((response) => response.json()),
        fetch("/data/leads.json").then((response) => response.json()),
        fetch("/data/buyer_origins.json").then((response) => response.json()),
        fetch("/data/risk_zones.geojson").then((response) => response.json()),
        fetch("/data/zone_metrics.json").then((response) => response.json()),
      ]);

      const zoneMetricsByGovernorate = new Map(
        zoneMetrics.map((zone) => [normalizeGovernorateName(zone.governorate), zone])
      );

      governorates.features = governorates.features.map((feature) => {
        const governorateName = normalizeGovernorateName(feature.properties.gouv_fr || feature.properties.name || feature.properties.NAME_1);
        const metrics = zoneMetricsByGovernorate.get(governorateName);

        return {
          ...feature,
          properties: {
            ...feature.properties,
            ...metrics,
            governorate: governorateName,
            name: governorateName,
          },
        };
      });

      delegations.features = delegations.features.map((feature) => {
        const governorateName = normalizeGovernorateName(feature.properties.gouv_fr);
        return {
          ...feature,
          properties: {
            ...feature.properties,
            governorate: governorateName,
            delegation: feature.properties.del_fr,
            name: feature.properties.del_fr,
          },
        };
      });

      currentMap.addSource("governorates", { type: "geojson", data: governorates });
      currentMap.addSource("delegations", { type: "geojson", data: delegations });
      currentMap.addSource("projects", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: projects.map((project) => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [Number(project.longitude), Number(project.latitude)] },
            properties: { ...project },
          })),
        },
      });
      currentMap.addSource("competitors", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: competitors.map((competitor) => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [Number(competitor.longitude), Number(competitor.latitude)] },
            properties: { ...competitor },
          })),
        },
      });
      currentMap.addSource("leads", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: leads.map((lead) => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [Number(lead.longitude), Number(lead.latitude)] },
            properties: { ...lead },
          })),
        },
      });
      currentMap.addSource("buyers", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: buyers.map((buyer) => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [Number(buyer.origin_lng), Number(buyer.origin_lat)] },
            properties: { ...buyer },
          })),
        },
      });
      currentMap.addSource("risk-zones", { type: "geojson", data: riskZones });

      currentMap.addLayer({
        id: "gov-fill",
        type: "fill",
        source: "governorates",
        paint: { "fill-color": "#DCEAFE", "fill-opacity": 0.46 },
      });

      currentMap.addLayer({
        id: "gov-outline",
        type: "line",
        source: "governorates",
        paint: { "line-color": "rgba(12, 36, 97, 0.22)", "line-width": 1.2 },
      });

      currentMap.addLayer({
        id: "del-fill",
        type: "fill",
        source: "delegations",
        paint: { "fill-color": "#C4B5FD", "fill-opacity": 0 },
        minzoom: 9,
      });

      currentMap.addLayer({
        id: "del-outline",
        type: "line",
        source: "delegations",
        paint: { "line-color": "rgba(124, 58, 237, 0.30)", "line-width": 0.9, "line-opacity": 0 },
        minzoom: 9,
      });

      currentMap.addLayer({
        id: "project-glow",
        type: "circle",
        source: "projects",
        paint: {
          "circle-radius": 22,
          "circle-color": "rgba(29, 158, 117, 0.20)",
          "circle-blur": 1.1,
          "circle-opacity": 0.35,
        },
      });

      currentMap.addLayer({
        id: "project-markers",
        type: "circle",
        source: "projects",
        paint: {
          "circle-radius": ["interpolate", ["linear"], ["get", "demand_score"], 0, 6, 50, 9, 100, 14],
          "circle-color": ["interpolate", ["linear"], ["get", "risk_score"], 0, "#1D9E75", 45, "#2EC4D6", 65, "#F59E0B", 80, "#DC2626"],
          "circle-stroke-color": "#FFFFFF",
          "circle-stroke-width": 2.6,
          "circle-opacity": 0.92,
        },
      });

      currentMap.addLayer({
        id: "competitor-markers",
        type: "circle",
        source: "competitors",
        paint: {
          "circle-radius": 7,
          "circle-color": "#FBBF24",
          "circle-stroke-color": "#FFFFFF",
          "circle-stroke-width": 2,
          "circle-opacity": 0.78,
        },
      });

      currentMap.addLayer({
        id: "competitor-labels",
        type: "symbol",
        source: "competitors",
        layout: {
          "text-field": ["get", "project_name"],
          "text-size": 10,
          "text-offset": [0, 1.5],
          "text-anchor": "top",
        },
        paint: { "text-color": "#8A5A00", "text-halo-color": "#FFFFFF", "text-halo-width": 1.2, "text-opacity": 0 },
      });

      currentMap.addLayer({
        id: "lead-heat",
        type: "heatmap",
        source: "leads",
        paint: {
          "heatmap-weight": ["get", "weight"],
          "heatmap-intensity": 1.15,
          "heatmap-radius": 28,
          "heatmap-color": ["interpolate", ["linear"], ["heatmap-density"], 0, "rgba(0,0,0,0)", 0.2, "#FEF9C3", 0.45, "#FB923C", 0.7, "#EF4444", 1, "#B91C1C"],
          "heatmap-opacity": 0,
        },
      });

      currentMap.addLayer({
        id: "buyer-scatter",
        type: "circle",
        source: "buyers",
        paint: {
          "circle-radius": 4.5,
          "circle-color": ["case", ["get", "is_reservation"], "#1D9E75", "#2EC4D6"],
          "circle-opacity": 0,
          "circle-stroke-width": 1,
          "circle-stroke-color": "#FFFFFF",
        },
      });

      currentMap.addLayer({
        id: "risk-fill",
        type: "fill",
        source: "risk-zones",
        paint: {
          "fill-color": ["match", ["get", "severity"], "Critical", "#7F1D1D", "High", "#DC2626", "Medium", "#F59E0B", "#FEF3C7"],
          "fill-opacity": 0,
        },
      });

      currentMap.addLayer({
        id: "risk-outline",
        type: "line",
        source: "risk-zones",
        paint: { "line-color": "#DC2626", "line-width": 2, "line-dasharray": [4, 2], "line-opacity": 0 },
      });

      currentMap.on("click", "project-markers", (event) => {
        const feature = event.features?.[0];
        if (feature && onZoneClick) {
          onZoneClick(feature.properties);
        }
        currentMap.flyTo({ center: event.lngLat, zoom: 13.2, pitch: 32, duration: 700 });
      });

      currentMap.on("click", "competitor-markers", (event) => {
        const feature = event.features?.[0];
        if (feature && onZoneClick) {
          onZoneClick(feature.properties);
        }
      });

      currentMap.on("click", "gov-fill", (event) => {
        const feature = event.features?.[0];
        if (feature && onZoneClick) {
          onZoneClick(normalizeSelection(feature.properties, "governorate"));
        }
      });

      currentMap.on("click", "del-fill", (event) => {
        const feature = event.features?.[0];
        if (feature && onZoneClick) {
          onZoneClick(normalizeSelection(feature.properties, "delegation"));
        }
      });

      currentMap.on("mouseenter", "project-markers", (event) => {
        currentMap.getCanvas().style.cursor = "pointer";
        const properties = event.features?.[0]?.properties;
        if (!properties) {
          return;
        }
        setPopupMarkup(`
          <p style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#64748B;font-weight:700;">Project</p>
          <p style="margin-top:6px;font-size:16px;font-weight:700;color:#0F172A;">${properties.project_name}</p>
          <p style="margin-top:4px;font-size:13px;color:#64748B;">${properties.city} . ${properties.neighborhood}</p>
          <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;">
            <span style="padding:6px 10px;border-radius:999px;background:#ECFDF5;color:#047857;font-size:12px;font-weight:600;">Demand ${properties.demand_score}/100</span>
            <span style="padding:6px 10px;border-radius:999px;background:#EFF6FF;color:#1D4ED8;font-size:12px;font-weight:600;">${Number(properties.avg_price).toLocaleString("en-US")} DT</span>
          </div>
        `);
        popup.current.setLngLat(event.lngLat).addTo(currentMap);
      });

      currentMap.on("mouseleave", "project-markers", () => {
        currentMap.getCanvas().style.cursor = "";
        popup.current.remove();
      });

      currentMap.on("mouseenter", "competitor-markers", (event) => {
        currentMap.getCanvas().style.cursor = "pointer";
        const properties = event.features?.[0]?.properties;
        if (!properties) {
          return;
        }
        setPopupMarkup(`
          <p style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#64748B;font-weight:700;">Competitor</p>
          <p style="margin-top:6px;font-size:15px;font-weight:700;color:#0F172A;">${properties.project_name}</p>
          <p style="margin-top:4px;font-size:13px;color:#64748B;">${properties.neighborhood || ""}</p>
          <p style="margin-top:10px;font-size:13px;color:#8A5A00;font-weight:600;">${properties.active_listings || "N/A"} active listings</p>
        `);
        popup.current.setLngLat(event.lngLat).addTo(currentMap);
      });

      currentMap.on("mouseleave", "competitor-markers", () => {
        currentMap.getCanvas().style.cursor = "";
        popup.current.remove();
      });

      currentMap.on("mouseenter", "gov-fill", (event) => {
        currentMap.getCanvas().style.cursor = "pointer";
        const properties = event.features?.[0]?.properties;
        if (!properties) {
          return;
        }
        const zoneName = properties.name || properties.gouv_fr || properties.NAME_1 || "Governorate";
        setPopupMarkup(`
          <p style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#64748B;font-weight:700;">Governorate</p>
          <p style="margin-top:6px;font-size:16px;font-weight:700;color:#0F172A;">${zoneName}</p>
          <div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="border-radius:14px;background:#EFF6FF;padding:10px;">
              <p style="font-size:11px;color:#64748B;">Avg price</p>
              <p style="margin-top:4px;font-size:14px;font-weight:700;color:#1D4ED8;">${Number(properties.avg_price_sqm || 0).toLocaleString("en-US")} DT/m2</p>
            </div>
            <div style="border-radius:14px;background:#F8FAFC;padding:10px;">
              <p style="font-size:11px;color:#64748B;">Demand</p>
              <p style="margin-top:4px;font-size:14px;font-weight:700;color:#0F172A;">${properties.demand_score || "N/A"}/100</p>
            </div>
          </div>
        `);
        popup.current.setLngLat(event.lngLat).addTo(currentMap);
      });

      currentMap.on("mouseleave", "gov-fill", () => {
        currentMap.getCanvas().style.cursor = "";
        popup.current.remove();
      });

      currentMap.on("mouseenter", "del-fill", (event) => {
        currentMap.getCanvas().style.cursor = "pointer";
        const properties = event.features?.[0]?.properties;
        if (!properties) {
          return;
        }
        setPopupMarkup(`
          <p style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#64748B;font-weight:700;">Delegation</p>
          <p style="margin-top:6px;font-size:16px;font-weight:700;color:#0F172A;">${properties.del_fr || properties.name}</p>
          <p style="margin-top:4px;font-size:13px;color:#64748B;">${properties.gouv_fr || properties.governorate || ""}</p>
          <div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="border-radius:14px;background:#EFF6FF;padding:10px;">
              <p style="font-size:11px;color:#64748B;">Avg price</p>
              <p style="margin-top:4px;font-size:14px;font-weight:700;color:#1D4ED8;">${Number(properties.avg_price_sqm || 0).toLocaleString("en-US")} DT/m2</p>
            </div>
            <div style="border-radius:14px;background:#F8FAFC;padding:10px;">
              <p style="font-size:11px;color:#64748B;">Demand</p>
              <p style="margin-top:4px;font-size:14px;font-weight:700;color:#0F172A;">${properties.demand_score || "N/A"}/100</p>
            </div>
          </div>
        `);
        popup.current.setLngLat(event.lngLat).addTo(currentMap);
      });

      currentMap.on("mouseleave", "del-fill", () => {
        currentMap.getCanvas().style.cursor = "";
        popup.current.remove();
      });

      currentMap.on("mouseenter", "risk-fill", (event) => {
        currentMap.getCanvas().style.cursor = "pointer";
        const properties = event.features?.[0]?.properties;
        if (!properties) {
          return;
        }
        setPopupMarkup(`
          <p style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#991B1B;font-weight:700;">Risk zone</p>
          <p style="margin-top:6px;font-size:16px;font-weight:700;color:#0F172A;">${properties.name}</p>
          <p style="margin-top:4px;font-size:13px;color:#64748B;">${properties.risk_type} . ${properties.severity}</p>
          <p style="margin-top:10px;font-size:13px;line-height:1.5;color:#475569;">${properties.description || ""}</p>
        `);
        popup.current.setLngLat(event.lngLat).addTo(currentMap);
      });

      currentMap.on("mouseleave", "risk-fill", () => {
        currentMap.getCanvas().style.cursor = "";
        popup.current.remove();
      });

      setLayersLoaded(true);
      requestAnimationFrame(() => {
        applyActiveStyles();
      });
    } catch (error) {
      console.error("Error loading GeoJSON layers:", error);
    }
  }, [applyActiveStyles, normalizeGovernorateName, normalizeSelection, onZoneClick, setPopupMarkup]);

  useEffect(() => {
    if (map.current) {
      return;
    }

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: MAP_STYLE,
      center: [10.1815, 36.8065],
      zoom: 10,
      minZoom: 6,
      maxZoom: 17,
      pitch: 18,
      bearing: -8,
      attributionControl: false,
    });

    map.current.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");
    map.current.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");

    popup.current = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      offset: 18,
      maxWidth: "300px",
    });

    map.current.on("load", () => {
      loadGeoJsonLayers();
    });

    map.current.on("styledata", () => {
      if (layersLoaded) {
        requestAnimationFrame(() => {
          applyActiveStyles();
        });
      }
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [applyActiveStyles, layersLoaded, loadGeoJsonLayers]);

  useEffect(() => {
    if (!map.current || !layersLoaded) {
      return;
    }
    requestAnimationFrame(() => {
      applyActiveStyles();
    });
  }, [applyActiveStyles, layersLoaded]);

  return (
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, width: "100%", height: "100%", zIndex: 0 }}>
      <div ref={mapContainer} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
