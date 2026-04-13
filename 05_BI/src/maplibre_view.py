from __future__ import annotations

import datetime as dt
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit.components.v1 as components


def _coerce_json_value(value: Any) -> Any:
    """Convert pandas/numpy values to JSON-safe primitives."""
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return value.total_seconds()
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, dt.timedelta):
        return value.total_seconds()
    if isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        try:
            return _coerce_json_value(value.item())
        except Exception:
            return str(value)
    return value


def _to_projects_geojson(df: pd.DataFrame) -> dict[str, Any]:
    """Build a lightweight project point FeatureCollection for MapLibre."""
    features: list[dict[str, Any]] = []
    for record in df.to_dict(orient="records"):
        latitude = _coerce_json_value(record.get("latitude"))
        longitude = _coerce_json_value(record.get("longitude"))
        if latitude is None or longitude is None:
            continue

        properties = {key: _coerce_json_value(value) for key, value in record.items()}
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)],
                },
                "properties": properties,
            }
        )

    return {"type": "FeatureCollection", "features": features}


@lru_cache(maxsize=1)
def _load_vendor_maplibre_assets() -> tuple[str, str]:
    """Load vendored MapLibre JS/CSS to avoid external CDN runtime dependencies."""
    vendor_dir = Path(__file__).resolve().parent / "vendor"
    js_path = vendor_dir / "maplibre-gl.js"
    css_path = vendor_dir / "maplibre-gl.css"

    if not js_path.exists() or not css_path.exists():
        raise FileNotFoundError(
            "MapLibre vendor assets are missing. Expected files:\n"
            f"- {js_path}\n"
            f"- {css_path}"
        )

    js_content = js_path.read_text(encoding="utf-8")
    css_content = css_path.read_text(encoding="utf-8")
    return js_content, css_content


def render_maplibre_projects(
    projects_df: pd.DataFrame,
    *,
    height: int,
    center_lat: float,
    center_lon: float,
    zoom: float,
    map_style: str,
) -> None:
    """Render a MapLibre project map with popup details and fly-to click behavior."""
    vendor_js, vendor_css = _load_vendor_maplibre_assets()
    vendor_js = vendor_js.replace("</script>", "<\\/script>")
    vendor_css = vendor_css.replace("</style>", "<\\/style>")

    projects_geojson = _to_projects_geojson(projects_df)
    projects_json = json.dumps(projects_geojson, ensure_ascii=True)
    preferred_vector_style_json = json.dumps(map_style)

    primary_style = {
        "version": 8,
        "name": "Carto Light Raster",
        "sources": {
            "carto_raster": {
                "type": "raster",
                "tiles": [
                    "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                    "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                    "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                ],
                "tileSize": 256,
                "attribution": "&copy; CARTO, &copy; OpenStreetMap contributors",
            }
        },
        "layers": [
            {
                "id": "carto_raster",
                "type": "raster",
                "source": "carto_raster",
            }
        ],
    }

    fallback_style = {
        "version": 8,
        "name": "OSM Raster Fallback",
        "sources": {
            "osm": {
                "type": "raster",
                "tiles": [
                    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                ],
                "tileSize": 256,
                "attribution": "&copy; OpenStreetMap contributors",
            }
        },
        "layers": [
            {
                "id": "osm",
                "type": "raster",
                "source": "osm",
            }
        ],
    }

    primary_style_json = json.dumps(primary_style, ensure_ascii=True)
    fallback_style_json = json.dumps(fallback_style, ensure_ascii=True)

    html = f"""
<style>
{vendor_css}
</style>
<style>
  html, body {{
    margin: 0;
    padding: 0;
    background: transparent;
  }}
  #maplibre-root {{
    position: relative;
    width: 100%;
    height: {height}px;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(18, 26, 42, 0.24);
    background: #0b1220;
  }}
  #maplibre-status {{
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 30;
    padding: 6px 10px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: rgba(15, 23, 42, 0.78);
    color: #e2e8f0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.01em;
  }}
  #maplibre-status.error {{
    border-color: rgba(248, 113, 113, 0.45);
    color: #fecaca;
  }}
  .maplibregl-ctrl-group {{
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
  }}
  .maplibregl-ctrl-group button {{
    width: 30px;
    height: 30px;
  }}
  .maplibregl-popup-content {{
    border-radius: 12px;
    padding: 0 !important;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.22);
    background: linear-gradient(180deg, #ffffff, #f7fafc);
  }}
  .maplibregl-popup-tip {{
    border-top-color: #ffffff !important;
    border-bottom-color: #ffffff !important;
  }}
  .popup-wrap {{
    padding: 14px 14px 12px;
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    color: #13253f;
    min-width: 230px;
  }}
  .popup-title {{
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 8px;
    color: #0f172a;
  }}
  .popup-meta {{
    font-size: 11px;
    color: #475569;
    margin-bottom: 10px;
  }}
  .popup-row {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
    font-size: 11px;
    margin-bottom: 4px;
  }}
  .popup-label {{
    color: #64748b;
    font-weight: 600;
  }}
  .popup-value {{
    color: #0f172a;
    font-weight: 700;
    text-align: right;
  }}
</style>

<div id="maplibre-root">
  <div id="maplibre-status">Loading map engine...</div>
</div>

<script>
{vendor_js}
</script>
<script>
  const PROJECTS = {projects_json};
  const PREFERRED_VECTOR_STYLE = {preferred_vector_style_json};
  const PRIMARY_STYLE = {primary_style_json};
  const FALLBACK_STYLE = {fallback_style_json};
  const DEFAULT_CENTER = [{center_lon}, {center_lat}];
  const DEFAULT_ZOOM = {zoom};

  const statusNode = document.getElementById("maplibre-status");

  const setStatus = (message, isError = false) => {{
    if (!statusNode) return;
    statusNode.textContent = message || "";
    statusNode.classList.toggle("error", Boolean(isError));
  }};

  const formatInt = (value) => {{
    const number = Number(value);
    return Number.isFinite(number)
      ? number.toLocaleString("en-US", {{ maximumFractionDigits: 0 }})
      : "N/A";
  }};

  const formatFloat = (value, decimals) => {{
    const number = Number(value);
    return Number.isFinite(number)
      ? number.toLocaleString("en-US", {{ minimumFractionDigits: decimals, maximumFractionDigits: decimals }})
      : "N/A";
  }};

  const formatMoney = (value) => {{
    const number = Number(value);
    return Number.isFinite(number)
      ? number.toLocaleString("en-US", {{ maximumFractionDigits: 0 }}) + " TND"
      : "N/A";
  }};

  const htmlEscape = (value) => {{
    if (value === null || value === undefined) return "N/A";
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }};

  const popupMarkup = (props) => (
    '<div class="popup-wrap">' +
      '<div class="popup-title">' + htmlEscape(props.project_name) + '</div>' +
      '<div class="popup-meta">' + htmlEscape(props.city) + ' . ' + htmlEscape(props.neighborhood) + ' . ' + htmlEscape(props.property_type) + '</div>' +
      '<div class="popup-row"><span class="popup-label">Leads</span><span class="popup-value">' + formatInt(props.leads) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Qualified Leads</span><span class="popup-value">' + formatInt(props.qualified_leads) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Visits</span><span class="popup-value">' + formatInt(props.visits) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Reservations</span><span class="popup-value">' + formatInt(props.reservations) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Sales</span><span class="popup-value">' + formatInt(props.sales) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Unsold Inventory</span><span class="popup-value">' + formatInt(props.unsold_inventory) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Average Price</span><span class="popup-value">' + formatMoney(props.avg_price) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Risk Score</span><span class="popup-value">' + formatFloat(props.risk_score, 1) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Risk Level</span><span class="popup-value">' + htmlEscape(props.risk_level) + '</span></div>' +
      '<div class="popup-row"><span class="popup-label">Recommended Action</span><span class="popup-value">' + htmlEscape(props.recommended_action) + '</span></div>' +
    '</div>'
  );

  const addProjectLayers = (map) => {{
    if (map.getLayer("project-markers")) map.removeLayer("project-markers");
    if (map.getLayer("project-glow")) map.removeLayer("project-glow");
    if (map.getSource("projects")) map.removeSource("projects");

    map.addSource("projects", {{ type: "geojson", data: PROJECTS }});

    map.addLayer({{
      id: "project-glow",
      type: "circle",
      source: "projects",
      paint: {{
        "circle-radius": ["interpolate", ["linear"], ["coalesce", ["get", "leads"], 0], 0, 12, 800, 24, 2200, 34],
        "circle-color": "rgba(45, 212, 191, 0.25)",
        "circle-blur": 1.05,
        "circle-opacity": 0.36,
      }},
    }});

    map.addLayer({{
      id: "project-markers",
      type: "circle",
      source: "projects",
      paint: {{
        "circle-radius": ["interpolate", ["linear"], ["coalesce", ["get", "leads"], 0], 0, 5, 800, 9, 2200, 14],
        "circle-color": [
          "interpolate", ["linear"], ["coalesce", ["get", "risk_score"], 50],
          0, "#1D9E75",
          40, "#2EC4D6",
          60, "#F59E0B",
          80, "#DC2626"
        ],
        "circle-stroke-color": "#FFFFFF",
        "circle-stroke-width": 2.1,
        "circle-opacity": 0.93,
      }},
    }});

    const features = PROJECTS.features || [];
    if (features.length === 1) {{
      map.flyTo({{ center: features[0].geometry.coordinates, zoom: 11.6, pitch: 30, duration: 450 }});
    }} else if (features.length > 1) {{
      const bounds = new maplibregl.LngLatBounds();
      for (const feature of features) bounds.extend(feature.geometry.coordinates);
      map.fitBounds(bounds, {{ padding: 46, maxZoom: 11.2, duration: 0 }});
    }}

    setStatus(String(features.length) + " projects loaded");
  }};

  const wireInteractions = (map) => {{
    const popup = new maplibregl.Popup({{ closeButton: false, closeOnClick: false, maxWidth: "320px", offset: 10 }});

    map.on("mouseenter", "project-markers", (event) => {{
      map.getCanvas().style.cursor = "pointer";
      const feature = event.features && event.features[0];
      if (!feature) return;
      popup.setLngLat(event.lngLat).setHTML(popupMarkup(feature.properties || {{}})).addTo(map);
    }});

    map.on("mousemove", "project-markers", (event) => {{
      const feature = event.features && event.features[0];
      if (!feature) return;
      popup.setLngLat(event.lngLat).setHTML(popupMarkup(feature.properties || {{}})).addTo(map);
    }});

    map.on("mouseleave", "project-markers", () => {{
      map.getCanvas().style.cursor = "";
      popup.remove();
    }});

    map.on("click", "project-markers", (event) => {{
      const feature = event.features && event.features[0];
      if (!feature) return;
      map.flyTo({{ center: event.lngLat, zoom: Math.max(map.getZoom(), 12.6), pitch: 32, duration: 700 }});
      popup.setLngLat(event.lngLat).setHTML(popupMarkup(feature.properties || {{}})).addTo(map);
    }});
  }};

  const initMap = () => {{
    if (!window.maplibregl) {{
      setStatus("Map engine failed to load from CDN.", true);
      return;
    }}

    if (!maplibregl.supported()) {{
      setStatus("WebGL unavailable. Enable hardware acceleration in the browser.", true);
      return;
    }}

    setStatus("Creating map...");
    let fallbackApplied = false;
    let interactionsBound = false;

    const map = new maplibregl.Map({{
      container: "maplibre-root",
      style: PRIMARY_STYLE,
      center: DEFAULT_CENTER,
      zoom: DEFAULT_ZOOM,
      pitch: 22,
      bearing: 0,
      antialias: true,
    }});

    map.addControl(new maplibregl.NavigationControl({{ visualizePitch: true }}), "bottom-right");
    map.addControl(new maplibregl.AttributionControl({{ compact: true }}), "bottom-right");

    // Streamlit iframe mounts can need a post-render resize to paint tiles.
    window.setTimeout(() => map.resize(), 300);
    window.setTimeout(() => map.resize(), 1200);

    let styleLoaded = false;
    window.setTimeout(() => {{
      if (!styleLoaded && !fallbackApplied) {{
        fallbackApplied = true;
        setStatus("Primary basemap timeout. Switching fallback...");
        map.setStyle(FALLBACK_STYLE);
      }}
    }}, 7000);

    map.on("style.load", () => {{
      styleLoaded = true;
      try {{
        addProjectLayers(map);
        if (!interactionsBound) {{
          wireInteractions(map);
          interactionsBound = true;
        }}
      }} catch (error) {{
        console.error("Failed to build project layers", error);
        setStatus("Map loaded but project layers failed.", true);
      }}
    }});

    map.on("error", (event) => {{
      console.error("Map rendering error", event && event.error ? event.error : event);
      if (!fallbackApplied) {{
        fallbackApplied = true;
        setStatus("Primary basemap failed. Switching fallback...");
        map.setStyle(FALLBACK_STYLE);
        return;
      }}
      setStatus("Map rendering failed. Check network/CDN and browser WebGL.", true);
    }});
  }};

  const waitForEngine = (attempt = 0) => {{
    if (window.maplibregl) {{
      initMap();
      return;
    }}
    if (attempt > 240) {{
      setStatus("Map engine script did not initialize.", true);
      return;
    }}
    window.setTimeout(() => waitForEngine(attempt + 1), 50);
  }};

  waitForEngine();
</script>
"""

    components.html(html, height=height)
