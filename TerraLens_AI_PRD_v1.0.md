**PRODUCT REQUIREMENTS DOCUMENT**

**TerraLens AI**

Buyer Catchment Intelligence for MENA Real Estate

|             |                           |
|-------------|---------------------------|
| **Version** | 1.0 --- MVP Phase         |
| **Date**    | April 2026                |
| **Status**  | Draft --- Hackathon Build |
| **Market**  | Tunisia → MENA            |

**Table of Contents**

**1. Executive Summary**

TerraLens AI is a map-first, AI-powered decision intelligence platform for real estate developers, marketers, and agencies operating in the MENA region. It transforms fragmented campaign data, lead records, and geographic signals into three unified views: Marketing Intelligence, Prediction and Planning, and Risk and Mitigation --- all anchored on an interactive map.

|                                                                                                                                                                                                                                                                                                                                            |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Core Innovation:** The core innovation is Buyer Catchment Intelligence: the system decodes where a developer\'s actual buyers physically live, builds a spatial catchment model for each project and neighborhood, and tells campaign teams exactly which geographic zones to target this week --- and why the answer changes over time. |

The platform is built for real estate marketing agencies as its primary customer --- the 20--30 boutique firms in Tunisia managing campaigns for 5--10 developer clients each. Agencies feel the campaign ROI pain daily and can sign in 2--4 weeks, bringing multiple developer datasets with them immediately.

|                                              |                                                                                |
|----------------------------------------------|--------------------------------------------------------------------------------|
| **Key Product Metrics (Target at 6 Months)** |                                                                                |
| **Primary Users**                            | Real estate marketing agencies (20--30 in Tunisia)                             |
| **Revenue Model**                            | SaaS subscription per agency --- tiered by number of developer projects        |
| **Data Flywheel**                            | Each campaign analyzed improves buyer origin atlas accuracy for all users      |
| **Market Entry**                             | Tunisia first, MENA expansion from month 9                                     |
| **Tech Differentiator**                      | Geospatially causal AI --- remove location layer, model is wrong by definition |
| **Migration**                                | From Streamlit MVP to Next.js 15 + MapLibre GL JS + Python Flask API           |

**2. Problem Statement**

**2.1 The Core Pain**

Real estate developers and their marketing agencies in Tunisia spend 30,000--80,000 DT per campaign quarter on Meta and Google ads, listing platforms, and broker networks. They receive aggregate performance reports showing impressions, clicks, leads, and reservations --- but they have no way to understand the spatial relationship between:

- Where their campaigns were targeted geographically

- Where the leads who actually converted into reservations physically live and work

- What spatial signals --- competitor activity, infrastructure events, neighborhood demographics --- explain the difference

|                                                                                                                                                                                                                                                                        |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **The Consequence:** The result: the same campaign targeting mistake is repeated every quarter. Budget is wasted in zones that generate clicks but no buyers. High-intent zones are systematically under-targeted because they are invisible without spatial analysis. |

**2.2 What Existing Tools Cannot Do**

|                         |                                              |                                                                                   |
|-------------------------|----------------------------------------------|-----------------------------------------------------------------------------------|
| **Tool**                | **What it does**                             | **What it cannot do**                                                             |
| HouseCanary / Reonomy   | Investor-facing property valuation and data  | Developer campaign attribution or buyer origin decoding                           |
| Realiste (MENA)         | Neighborhood price forecasting for investors | Operational campaign geo-targeting for developers                                 |
| Power BI / Tableau      | Generic BI dashboards with basic map widgets | Spatially causal analysis --- isochrones, catchment modeling, spillover detection |
| Meta / Google Analytics | Campaign performance by ad set               | Where buyers physically live or why geographic zones convert differently          |
| CRM Platforms           | Lead tracking and pipeline management        | Geographic attribution of lead quality or buyer origin clustering                 |

**2.3 The Opportunity**

No product in Tunisia or the broader MENA market combines campaign attribution data with spatial buyer origin modeling for the developer operations use case. The first platform to do this owns the Tunisian buyer origin atlas --- a dataset that becomes more accurate with every campaign analyzed and every reservation logged, creating a data moat that is impossible to replicate without 12+ months of real deal data.

**3. Product Vision and Goals**

**3.1 Vision Statement**

|                                                                                                                                                                                 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TerraLens AI is the operating system for spatial real estate intelligence in MENA --- the platform that makes geographic data causally actionable, not decoratively visualized. |

**3.2 Product Goals**

- Decode buyer origin: show developers exactly which neighborhoods their real buyers come from, not where campaigns were targeted

- Predict catchment shifts: forecast where buyer demand will come from next quarter as demographics, infrastructure, and competitor activity evolve

- Recommend campaign geography: output specific zone-level budget allocation recommendations with confidence scores

- Build the atlas: accumulate a Tunisia-wide buyer origin dataset that improves model accuracy with every new data point

- Enable MENA scale: establish a replicable methodology that works in Cairo, Casablanca, and Riyadh with the same mechanics

**3.3 Success Metrics**

|                               |                       |                       |
|-------------------------------|-----------------------|-----------------------|
| **Metric**                    | **Target (3 months)** | **Target (6 months)** |
| Agencies onboarded            | 3                     | 8                     |
| Developer projects in atlas   | 15                    | 45                    |
| Buyer origin accuracy (MAE)   | \< 3.2km median error | \< 2.0km median error |
| Campaign ROI improvement      | Demonstrated 1.5×     | Avg 2.3× documented   |
| NPS (agency clients)          | \> 40                 | \> 60                 |
| Reservations tracked in atlas | 200+                  | 800+                  |

**4. Users and Personas**

**4.1 Primary Persona --- The Agency Strategist**

|                                                    |                                                                                                  |
|----------------------------------------------------|--------------------------------------------------------------------------------------------------|
| **Sami --- Real Estate Marketing Agency Director** |                                                                                                  |
| **Role**                                           | Manages campaigns for 5--8 developer clients across Tunis                                        |
| **Pain**                                           | Cannot explain spatially why campaigns underperform. Clients demand ROI proof he cannot produce. |
| **Goal**                                           | Show clients a map that proves where their buyers came from and why next budget should shift.    |
| **Frequency**                                      | Opens TerraLens every Monday morning to review the previous week and plan the coming one.        |
| **Tech comfort**                                   | Comfortable with Google Analytics and Meta Business Manager. Not a data scientist.               |
| **Decision power**                                 | Full authority to sign SaaS contracts under 2,000 DT/month without board approval.               |

**4.2 Secondary Persona --- The Developer Sales Director**

|                                                   |                                                                                                         |
|---------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| **Yasmine --- Real Estate Developer VP of Sales** |                                                                                                         |
| **Role**                                          | Oversees sales and marketing for 2--4 active projects in Greater Tunis                                  |
| **Pain**                                          | Spends 60K DT per quarter on campaigns with no visibility into why some projects sell and others stall. |
| **Goal**                                          | Understand which neighborhoods her project should be marketed in and when to reposition pricing.        |
| **Frequency**                                     | Weekly review of project-level KPIs. Monthly strategic planning with her agency.                        |
| **Tech comfort**                                  | Uses Excel and PowerPoint. Expects clean, exportable visuals.                                           |
| **Decision power**                                | Controls marketing budget but requires CFO approval for contracts above 5,000 DT/month.                 |

**4.3 Tertiary Persona --- The Data Analyst**

|                                                    |                                                                                                 |
|----------------------------------------------------|-------------------------------------------------------------------------------------------------|
| **Mehdi --- Agency or Developer In-House Analyst** |                                                                                                 |
| **Role**                                           | Produces weekly performance reports and ad-hoc analysis for leadership                          |
| **Pain**                                           | Spends 3--4 hours per week manually merging CRM exports, ad platform reports, and spreadsheets. |
| **Goal**                                           | One platform that replaces the manual merge and adds spatial context he cannot produce himself. |
| **Frequency**                                      | Daily user. Builds custom segments, exports reports, and monitors new lead quality.             |
| **Tech comfort**                                   | High. Comfortable with SQL, Python basics, and BI tools.                                        |
| **Decision power**                                 | Recommends tools. Does not sign contracts.                                                      |

**5. System Architecture**

**5.1 High-Level Stack**

|                  |                                      |                                                                |
|------------------|--------------------------------------|----------------------------------------------------------------|
| **Layer**        | **Technology**                       | **Responsibility**                                             |
| Frontend         | Next.js 15 + Tailwind CSS            | UI, routing, server-side rendering, component library          |
| Map Engine       | MapLibre GL JS                       | Base map rendering, layer management, interaction events       |
| Advanced Geo Viz | Deck.gl / Kepler.gl                  | HexagonLayer, HeatmapLayer, GeoJsonLayer, ScatterplotLayer     |
| Backend API      | Python Flask + Flask-CORS            | Data processing, ML inference, KPI computation, geo operations |
| Geo Processing   | GeoPandas + Shapely + H3             | Spatial joins, isochrone computation, hexagonal grid indexing  |
| ML / AI          | scikit-learn + XGBoost + statsmodels | Demand forecasting, risk scoring, catchment modeling           |
| Database         | PostgreSQL + PostGIS                 | Spatial queries, project data, buyer origin records            |
| Cache            | Redis                                | API response caching, ML prediction cache                      |
| Map Tiles        | MapTiler (OpenStreetMap base)        | Basemap tiles for MapLibre GL JS                               |

**5.2 Migration from Streamlit MVP**

|                                                                                                                                                                                                                                                                                                   |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Migration Note:** The existing Streamlit MVP (app.py + src/data_loader.py + src/kpis.py) provides the data model and KPI logic. The migration preserves all KPI computation logic and the projects.csv data schema, refactoring them into Flask API endpoints consumed by the Next.js frontend. |

- data_loader.py → Flask /api/projects endpoint with pagination and filtering

- kpis.py → Flask /api/kpis/{project_id} endpoint returning JSON metrics

- Streamlit map components → Deck.gl layers managed by Next.js MapLibre wrapper

- Streamlit filters → Next.js sidebar component with URL-persisted state

**5.3 Frontend Directory Structure**

> terragens/
>
> frontend/ \# Next.js 15 application
>
> app/ \# App router
>
> (dashboard)/ \# Authenticated routes
>
> page.tsx \# Main map dashboard
>
> projects/\[id\]/page.tsx \# Project deep-dive
>
> components/
>
> map/
>
> MapContainer.tsx \# MapLibre GL JS wrapper
>
> DeckGLOverlay.tsx \# Deck.gl integration layer
>
> LayerControls.tsx \# Category + subcategory buttons
>
> HoverPanel.tsx \# On-hover tooltip with charts
>
> MapLegend.tsx \# Dynamic color scale legend
>
> panels/
>
> MarketingPanel.tsx \# Marketing intelligence sidebar
>
> ForecastPanel.tsx \# Prediction sidebar
>
> RiskPanel.tsx \# Risk sidebar
>
> charts/
>
> MiniBarChart.tsx \# Recharts bar (hover popup)
>
> TrendLine.tsx \# Sparkline time series
>
> RadarChart.tsx \# Risk radar
>
> lib/
>
> api.ts \# Typed fetch wrappers
>
> mapLayers.ts \# Deck.gl layer factory functions
>
> colorScales.ts \# D3 color interpolation

**5.4 Backend Directory Structure**

> backend/ \# Flask application
>
> app.py \# Flask app factory
>
> api/
>
> routes/
>
> marketing.py \# /api/marketing/\* endpoints
>
> forecast.py \# /api/forecast/\* endpoints
>
> risk.py \# /api/risk/\* endpoints
>
> projects.py \# /api/projects/\* endpoints
>
> src/ \# Migrated from Streamlit MVP
>
> data_loader.py \# CSV + DB ingestion (preserved)
>
> kpis.py \# KPI computation (preserved)
>
> geo/
>
> catchment.py \# Isochrone + buyer origin modeling
>
> h3_grid.py \# Hexagonal grid operations
>
> spillover.py \# Competitor sellout demand diffusion
>
> ml/
>
> demand_forecast.py \# Time-series demand model
>
> risk_scorer.py \# Multi-factor risk computation
>
> buyer_origin.py \# Catchment decoder
>
> data/
>
> projects.csv \# Existing MVP dataset (preserved)
>
> geodata/ \# GeoJSON for governorates, delegations

**6. Map Interface --- Core Design Principles**

**6.1 Layout**

The application is a full-viewport map dashboard. The map occupies 100% of the screen. All controls and panels float over it without reducing the map area.

|                            |                                        |                                                          |
|----------------------------|----------------------------------------|----------------------------------------------------------|
| **Zone**                   | **Component**                          | **Behavior**                                             |
| Top bar (full width)       | Category buttons + subcategory pills   | Fixed overlay, always visible, z-index highest           |
| Left sidebar (collapsible) | Context panel with BI charts and stats | Slides in on category selection, can be dismissed        |
| Right side (auto)          | AI recommendation card                 | Appears when a zone or project is clicked                |
| Bottom bar (optional)      | Time slider + comparison toggle        | Slides up when temporal analysis is active               |
| Map surface                | All Deck.gl layers                     | Responds to hover, click, zoom, and pan                  |
| Hover tooltip              | MiniBarChart + key stats               | Appears on pointer proximity to a zone or project marker |

**6.2 Category Buttons --- Top Bar Design**

Three primary category buttons sit at the top center of the map. Each button activates a mode that changes all visible layers simultaneously. The active category button is visually elevated. Subcategory pills appear directly below the active button.

|                            |                                                                           |
|----------------------------|---------------------------------------------------------------------------|
| **Category Button States** |                                                                           |
| **Default state**          | Pill shape, white background, colored border, muted text                  |
| **Active state**           | Filled background (category color), white text, subtle elevation          |
| **Subcategory pills**      | Smaller pills in a horizontal row, same color family, togglable           |
| **Multiple subcategories** | Multiple subcategory pills can be active simultaneously in Marketing mode |
| **Single subcategory**     | Only one subcategory active at a time in Forecast and Risk modes          |

**6.3 Map Layer Technology**

- Base map: MapLibre GL JS with MapTiler OpenStreetMap tiles (dark and light themes)

- Governorate / delegation boundaries: GeoJsonLayer from Deck.gl, filled with choropleth color scales

- Hexagonal demand grid: HexagonLayer or H3HexagonLayer from Deck.gl, extruded in 3D for density visualization

- Project markers: ScatterplotLayer from Deck.gl with size encoding for project volume

- Buyer origin heatmap: HeatmapLayer from Deck.gl, showing density of confirmed buyer home addresses

- Catchment boundaries: GeoJsonLayer rendering isochrone polygons from 5-minute to 30-minute drive-time zones

- Risk grid: GeoJsonLayer with sequential red color scale encoding composite risk scores

**6.4 Hover and Click Behavior**

|                          |                                   |                                                                               |
|--------------------------|-----------------------------------|-------------------------------------------------------------------------------|
| **Trigger**              | **Element hovered / clicked**     | **Response**                                                                  |
| Hover --- zone           | Governorate or delegation polygon | Tooltip with zone name, active metric value, sparkline trend, and top 2 stats |
| Hover --- project marker | ScatterplotLayer point            | Popup with project name, KPIs, and AI recommendation badge                    |
| Hover --- hexagonal cell | H3 hex tile                       | Tooltip showing cell-level density value and percentile rank                  |
| Click --- zone           | Any polygon                       | Right panel opens with full zone analytics and AI recommendation              |
| Click --- project        | Marker point                      | Right panel opens with project deep-dive: all KPIs, forecasts, risk breakdown |
| Click --- map (empty)    | No element                        | All panels close, map returns to overview state                               |

**7. Category 1 --- Marketing Intelligence**

|                                                                                                                                                                  |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Category Goal:** This category answers: Where is buyer interest coming from, what is converting, and which zones need a different campaign strategy this week? |

**7.1 Subcategories and Map Layers**

**7.1.1 --- Zone Pricing Categories**

Shows average price per square meter by governorate and delegation, color-coded into 5 tiers from affordable to luxury. This layer answers the fundamental market positioning question: where does this project\'s price point fit geographically?

- Layer type: GeoJsonLayer (choropleth) over delegation boundaries

- Color scale: Sequential blue --- white (#F0F9FF) to deep navy (#0C2461) across 5 price quintiles

- Hover tooltip: Zone name, avg price/m2, price tier label, YoY change percentage, number of active projects

- Click: Right panel shows price distribution histogram for the zone, comparison to city average, top 3 projects by price, and AI narrative

- Legend: 5-band color strip with DT/m2 values at each breakpoint

**API endpoint:** GET /api/marketing/pricing?level={governorate\|delegation}&period={month}

**Key fields:** zone_id, zone_name, avg_price_sqm, price_tier (1--5), yoy_change_pct, active_projects_count

**7.1.2 --- Price Rise % (Rising Zone Signal)**

Shows the month-over-month percentage price movement per zone. This is a leading indicator of emerging buyer demand and is used to identify zones where campaign spend should increase before competition does.

- Layer type: GeoJsonLayer (choropleth) with diverging color scale

- Color scale: Diverging --- red (#7F1D1D) for declining zones, gray neutral at 0%, green (#065F46) for rising zones

- Hover tooltip: Zone name, rise % this month, last 3 months trend (sparkline), and confidence level

- Click: Right panel shows 12-month price trend chart, correlation with lead volume, and AI recommendation

- Subcategory toggle: Switch between monthly, quarterly, and annual view

**API endpoint:** GET /api/marketing/price-trend?level={level}&period={monthly\|quarterly\|annual}

**Key fields:** zone_id, price_change_pct, trend_direction, 12m_history\[\], confidence_score

**7.1.3 --- Lead Density Heatmap**

Shows where inquiries and qualified leads are geographically clustered. This is the direct spatial output of campaign activity --- the raw signal of where buyer interest is currently concentrated.

- Layer type: HeatmapLayer (Deck.gl) over confirmed lead origin addresses

- Color: Yellow-orange-red heat gradient from low to high density

- Hover tooltip: Zone lead count, qualified lead rate, primary campaign source for this zone

- Click: Right panel shows lead source breakdown (Meta vs Google vs listing platforms), quality score by source, and campaign cost per qualified lead for the zone

- Filter: Toggle between all leads vs qualified leads only

**API endpoint:** GET /api/marketing/lead-density?project_id={id}&qualified_only={bool}

**Key fields:** lead_id, origin_lat, origin_lng, is_qualified, source, campaign_id, project_id

**7.1.4 --- Buyer Origin Decoder (Core Innovation)**

This is TerraLens\'s primary differentiator. It shows where confirmed buyers (leads that became reservations) physically lived at the time of purchase --- decoded from CRM address data and cross-referenced with spatial zones. This reveals the true catchment area of each project.

- Layer type: ScatterplotLayer for individual buyer origin points + HeatmapLayer for density

- Color: Teal (#1D9E75) dots for confirmed buyers, overlaid on campaign spend choropleth

- Isochrone overlay: Drive-time catchment zones (5, 10, 20, 30 minutes) rendered as GeoJsonLayer polygons

- Gap visualization: Areas of high campaign spend but zero buyer origins highlighted in amber --- the waste signal

- Hover tooltip: Zone buyer count, conversion rate from this zone, avg drive time to project

- Click: Right panel shows full catchment analysis with zone-by-zone conversion funnel and AI budget reallocation recommendation

**API endpoint:** GET /api/marketing/buyer-origin?project_id={id}

**Key fields:** buyer_id, origin_lat, origin_lng, zone_id, drive_time_min, reservation_date

**7.1.5 --- Campaign Attribution by Zone**

Maps the performance of each active campaign (Meta, Google, listing platforms, outdoor) broken down by geographic zone. Shows which campaign types work in which neighborhoods --- essential for budget reallocation decisions.

- Layer type: GeoJsonLayer with pattern fill encoding campaign mix (hatching for Meta-dominant zones, dots for Search-dominant zones)

- Hover tooltip: Zone campaign breakdown pie, cost per qualified lead by source, this zone vs city average

- Click: Right panel shows full attribution table with campaign-to-reservation funnel by source and zone

**API endpoint:** GET /api/marketing/attribution?project_id={id}&campaign_type={meta\|google\|listing\|all}

**Key fields:** zone_id, campaign_type, impressions, clicks, leads, qualified_leads, reservations, spend_dt, cpl

**7.1.6 --- Broker Activity Density**

Shows the geographic concentration of broker-sourced leads and reservations. Identifies which zones are broker-driven vs digital-driven, helping agencies allocate between broker commissions and digital ad spend.

- Layer type: ScatterplotLayer sized by broker deal count per zone

- Color: Purple scale (#F5F3FF to \#4C1D95) for broker density

- Hover tooltip: Zone broker count, broker-sourced reservation share, top 3 active brokers in this zone

**API endpoint:** GET /api/marketing/broker-density?zone_id={id}

**Key fields:** zone_id, broker_id, lead_count, reservation_count, active_period

**8. Category 2 --- Prediction and Planning**

|                                                                                                                                                                                      |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Category Goal:** This category answers: What is likely to happen in each zone and project over the next 30--90 days, and what strategy should we adopt based on those predictions? |

**8.1 ML Model Architecture**

The forecasting engine uses a two-stage approach: a spatial demand model capturing zone-level dynamics, and a project-level sales velocity model. Both models are trained on synthetic historical data in MVP phase and updated with real data as agencies onboard.

|                            |                                                              |                                                     |
|----------------------------|--------------------------------------------------------------|-----------------------------------------------------|
| **Model**                  | **Algorithm**                                                | **Output**                                          |
| Zone demand index          | XGBoost with spatial lag features (H3 neighbors)             | 30/60/90-day demand score per zone                  |
| Project sales velocity     | ARIMA + external regressors (seasonality, competitor events) | Expected reservations/week for each project         |
| Catchment shift prediction | Spatial regression with demographic trend inputs             | Zone-level buyer origin probability 1 quarter ahead |
| Price trend forecast       | Prophet (Facebook) with seasonality decomposition            | Price direction and confidence interval per zone    |
| Inventory absorption       | Gradient boosting classifier                                 | Estimated weeks to sell remaining inventory         |

**8.2 Subcategories and Map Layers**

**8.2.1 --- Demand Forecast Index**

A composite index predicting buyer demand activity in each zone over the next 30, 60, and 90 days. Incorporates historical sales velocity, price trend, competitor inventory, infrastructure events, and seasonal factors.

- Layer type: H3HexagonLayer extruded in 3D --- taller hexagons indicate higher predicted demand

- Color: Cool-to-warm scale --- blue (low demand predicted) through amber (high demand predicted)

- Time selector: Slider in bottom bar switches between 30-day, 60-day, and 90-day forecast horizon

- Hover tooltip: Zone name, demand index score (0--100), key driver list, confidence band

- Click: Right panel shows demand decomposition chart (which factors drive the score), 90-day trend, and comparison to same period last year

**API endpoint:** GET /api/forecast/demand?zone_id={id}&horizon={30\|60\|90}

**Key fields:** zone_id, demand_score, confidence_low, confidence_high, drivers\[\], horizon_days, as_of_date

**8.2.2 --- Sales Velocity Forecast**

Predicts the weekly reservation rate for each active project over the next 8 weeks. Flags projects with declining velocity before the slowdown is visible in raw numbers.

- Layer type: ScatterplotLayer --- project markers sized by predicted weekly reservations

- Velocity arrows: Small directional indicators on each marker showing rising, stable, or declining trend

- Color: Green markers for accelerating projects, gray for stable, orange for decelerating

- Hover tooltip: Project name, current weekly reservations, predicted next 4 weeks, key risk factor if declining

- Click: Right panel shows 8-week forecast chart with confidence bands, decomposed by buyer type (local vs diaspora), and AI recommendation

**API endpoint:** GET /api/forecast/velocity?project_id={id}&weeks=8

**Key fields:** project_id, week, predicted_reservations, confidence_low, confidence_high, trend_direction, key_risk

**8.2.3 --- Catchment Shift Prediction**

Predicts how the geographic buyer origin catchment for each project will shift over the next quarter. Identifies zones that will gain or lose buyer interest based on demographic shifts, infrastructure development, and competitor activity.

- Layer type: GeoJsonLayer with flow arrows overlaid (animated paths showing catchment expansion or contraction)

- Color: Gaining zones in teal, losing zones in coral, stable zones in gray

- Hover tooltip: Zone, current buyer contribution %, predicted change, driver (e.g., new metro, competitor project launch)

- Click: Right panel shows before/after catchment map, driver explanation, and recommended campaign adjustment

**API endpoint:** GET /api/forecast/catchment-shift?project_id={id}&quarter={Q}

**Key fields:** zone_id, current_contribution_pct, predicted_contribution_pct, delta_pct, primary_driver, driver_type

**8.2.4 --- AI Strategy Recommendations**

The recommendation engine synthesizes all forecast signals and outputs prioritized, actionable recommendations for each project and zone. Recommendations are spatially grounded --- every suggestion points at a specific zone, project, or budget shift.

- Displayed as: Card overlay on the right panel when any zone or project is in active state

- Recommendation types: Increase budget in zone X, reposition project Y to lower price segment, delay campaign in zone Z, activate broker outreach in emerging zone A

- Each recommendation includes: Projected impact (estimated additional reservations), confidence score (%), reasoning (2-sentence spatial explanation), and a \'Do it\' CTA linking to export

- AI engine: Claude API call with structured context (project KPIs, zone forecasts, competitor signals) generating JSON recommendation objects

**API endpoint:** POST /api/forecast/recommendations with body {project_id, zone_id, context_window}

**Response schema:** {action, zone_id, projected_impact, confidence, reasoning, urgency_level}

**8.2.5 --- Inventory Absorption Forecast**

Shows estimated time-to-sell for remaining inventory in each project, by unit type. Identifies projects at risk of inventory stagnation before it becomes a financial problem.

- Layer type: Project markers with a countdown clock indicator (color + label showing estimated weeks remaining)

- Color: Green (\>16 weeks comfortable), amber (8--16 weeks monitor), red (\<8 weeks urgent)

- Hover tooltip: Project name, units remaining, estimated weeks to sell, recommended action

**API endpoint:** GET /api/forecast/absorption?project_id={id}

**Key fields:** project_id, units_remaining, unit_type, predicted_weeks_to_sell, risk_level, recommended_action

**9. Category 3 --- Risk and Mitigation**

|                                                                                                                                                                              |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Category Goal:** This category answers: What are the geographic risk exposures for each project and zone, how severe are they, and what should the team do to reduce them? |

**9.1 Risk Model Architecture**

The risk engine computes a composite risk score for each zone and project using six independent risk dimensions. Each dimension is scored 0--100 and weighted by project type. The composite score triggers a three-tier alert system.

|                          |                                                               |                    |
|--------------------------|---------------------------------------------------------------|--------------------|
| **Risk Dimension**       | **Data Signal**                                               | **Default Weight** |
| Low demand risk          | Demand forecast index below threshold, declining lead volume  | 25%                |
| Oversupply risk          | Competitor inventory + new project launches in catchment zone | 20%                |
| Slow sales velocity risk | Reservation rate trend vs historical baseline                 | 20%                |
| Pricing mismatch risk    | Project price tier vs zone median buyer purchasing power      | 15%                |
| Low lead quality risk    | Qualified lead rate, visit-to-reservation ratio               | 10%                |
| Market cooling risk      | Price trend direction + transaction volume momentum           | 10%                |

**9.2 Subcategories and Map Layers**

**9.2.1 --- Composite Risk Grid**

The primary risk view. A classified grid divides the map into H3 hexagonal cells, each colored by composite risk score. This is the Monday morning view for an agency director checking portfolio health.

- Layer type: H3HexagonLayer with flat (non-extruded) fill colored by risk score

- Color scale: Sequential --- light green (#D1FAE5) for low risk through amber (#FEF3C7) to deep red (#7F1D1D) for critical risk

- Grid resolution: H3 resolution 7 (\~1.2km per hex diameter) for Tunis metro, resolution 6 for regional view

- Classification: 5 classes --- Very Low (0--20), Low (20--40), Moderate (40--60), High (60--80), Critical (80--100)

- Hover tooltip: Cell risk score, top 2 risk drivers, active projects in this cell, recommended action

- Click: Right panel shows risk radar chart (all 6 dimensions), driver breakdown, and mitigation recommendations

**API endpoint:** GET /api/risk/grid?resolution={6\|7}&project_ids={csv}

**Key fields:** h3_cell_id, risk_score, risk_class, drivers\[\], active_projects\[\], zone_name

**9.2.2 --- Competitor Pressure Map**

Shows the geographic distribution of competing projects, their inventory levels, recent price moves, and estimated sales velocity. Identifies where competitor activity is increasing risk for TerraLens client projects.

- Layer type: ScatterplotLayer for competitor project locations, sized by estimated remaining inventory

- Pressure zones: Buffered GeoJsonLayer showing the catchment overlap between client projects and competitors (overlap areas highlighted in amber)

- Hover tooltip: Competitor project name (or \'Unknown project\'), estimated units, recent price action, overlap with your project catchment

- Click: Right panel shows head-to-head comparison: client project vs top 3 competitors in same catchment zone

**API endpoint:** GET /api/risk/competitors?project_id={id}&radius_km={number}

**Key fields:** competitor_id, lat, lng, estimated_units, price_tier, launch_date, catchment_overlap_pct

**9.2.3 --- Oversupply Pressure Index**

A zone-level score combining total available inventory from all developers active in each zone with historical absorption rates. Identifies zones at risk of market saturation before price pressure becomes visible.

- Layer type: GeoJsonLayer (choropleth) over delegations

- Color: Blue-green for undersupplied zones (opportunity), neutral for balanced, red-orange for oversupplied

- Hover tooltip: Zone supply/demand ratio, total available units, absorption rate trend, months of supply remaining

- Click: Right panel shows supply pipeline chart (units launching in next 6 months vs predicted demand), and warning if project launch timing is at risk

**API endpoint:** GET /api/risk/oversupply?zone_id={id}

**Key fields:** zone_id, supply_demand_ratio, total_available_units, absorption_rate_monthly, months_of_supply, risk_level

**9.2.4 --- Infrastructure Risk Exposure**

Identifies geographic risks from infrastructure factors: flood zones, construction disruption corridors, road closure impacts, and utility zone instability. Relevant for projects currently launching or planning to launch.

- Layer type: GeoJsonLayer with hatching pattern fill encoding infrastructure risk areas

- Color: Semi-transparent red over flood zones, amber over construction corridors, gray over access disruption areas

- Hover tooltip: Risk type, severity level, estimated duration/permanence, impacted projects in zone

- Click: Right panel shows risk description, impact on project catchment accessibility, and recommended timeline adjustment

**API endpoint:** GET /api/risk/infrastructure?zone_id={id}

**Key fields:** zone_id, risk_type, severity, start_date, end_date, affected_radius_km, impacted_project_ids\[\]

**9.2.5 --- Portfolio Risk Dashboard (Below-Map View)**

When Risk mode is active, a summary bar appears below the map showing all client projects ranked by composite risk score. This gives an agency director an instant portfolio health check without navigating the map.

- Layout: Horizontal scrollable row of project cards, each showing project name, risk score badge, top risk driver, and one-line recommendation

- Sorting: Default by risk score descending (highest risk first)

- Filter: Filter by risk dimension (e.g., show only projects with high pricing risk)

- Action: Each card has a \'View on Map\' button that flies the map to the project location and opens the detail panel

**API endpoint:** GET /api/risk/portfolio?agency_id={id}

**Key fields:** project_id, project_name, risk_score, risk_class, top_driver, recommendation, lat, lng

**10. API Specification**

**10.1 Base Configuration**

**Base URL:** http://localhost:5000/api (development) \| https://api.terragens.tn/api (production)

**Auth:** JWT Bearer token in Authorization header

**CORS:** Flask-CORS configured for Next.js frontend origin

**Format:** All responses return JSON with envelope: {success, data, meta, error}

**Errors:** Standard HTTP codes: 400 validation, 401 auth, 404 not found, 422 geo error, 500 server

**10.2 Key Endpoints Summary**

|                                |            |                                                                     |
|--------------------------------|------------|---------------------------------------------------------------------|
| **Endpoint**                   | **Method** | **Description**                                                     |
| GET /projects                  | GET        | List all projects with pagination and filters (region, type, price) |
| GET /projects/{id}             | GET        | Full project detail including all KPIs from kpis.py                 |
| GET /marketing/pricing         | GET        | Zone price tiers by governorate or delegation                       |
| GET /marketing/price-trend     | GET        | Price change % with time period selection                           |
| GET /marketing/lead-density    | GET        | Lead origin coordinates for HeatmapLayer                            |
| GET /marketing/buyer-origin    | GET        | Confirmed buyer addresses + isochrone polygons                      |
| GET /marketing/attribution     | GET        | Campaign performance breakdown by zone and source                   |
| GET /marketing/broker-density  | GET        | Broker-sourced deal density by zone                                 |
| GET /forecast/demand           | GET        | Zone demand index with confidence bands                             |
| GET /forecast/velocity         | GET        | Project reservation rate forecast 8 weeks                           |
| GET /forecast/catchment-shift  | GET        | Predicted buyer origin shifts next quarter                          |
| POST /forecast/recommendations | POST       | AI-generated strategy recommendations via Claude API                |
| GET /forecast/absorption       | GET        | Inventory sell-through time prediction                              |
| GET /risk/grid                 | GET        | H3 hexagonal risk grid for composite score                          |
| GET /risk/competitors          | GET        | Competitor project locations and pressure analysis                  |
| GET /risk/oversupply           | GET        | Zone supply/demand balance index                                    |
| GET /risk/infrastructure       | GET        | Infrastructure risk zones (flood, construction, access)             |
| GET /risk/portfolio            | GET        | Full portfolio risk summary for an agency                           |

**11. Data Model**

**11.1 Core Tables**

The data model extends the existing Streamlit MVP dataset (projects.csv) with spatial and temporal dimensions. All geospatial fields use EPSG:4326 (WGS84) coordinates.

**projects table (extended from MVP)**

|                       |                 |                                          |
|-----------------------|-----------------|------------------------------------------|
| **Field**             | **Type**        | **Description**                          |
| project_id            | UUID PK         | Unique project identifier                |
| project_name          | VARCHAR         | Display name                             |
| developer_id          | UUID FK         | Owning developer                         |
| neighborhood          | VARCHAR         | Neighborhood name (from MVP)             |
| delegation            | VARCHAR         | Delegation administrative unit           |
| governorate           | VARCHAR         | Governorate administrative unit          |
| latitude              | DECIMAL(10,7)   | Project centroid latitude (WGS84)        |
| longitude             | DECIMAL(10,7)   | Project centroid longitude (WGS84)       |
| geom                  | GEOMETRY(Point) | PostGIS spatial index for geo queries    |
| property_type         | ENUM            | apartment \| villa \| commercial \| land |
| price_range           | VARCHAR         | Price tier label from MVP                |
| avg_price_sqm         | DECIMAL         | Current avg price per m2 in DT           |
| total_units           | INTEGER         | Total inventory units                    |
| unsold_inventory      | INTEGER         | Units remaining (from kpis.py)           |
| ad_spend              | DECIMAL         | Total campaign spend in DT (from MVP)    |
| leads                 | INTEGER         | Total leads (from MVP)                   |
| qualified_leads       | INTEGER         | Qualified leads (from kpis.py)           |
| visits                | INTEGER         | Site visits (from MVP)                   |
| reservations          | INTEGER         | Confirmed reservations (from MVP)        |
| sales                 | INTEGER         | Completed sales (from MVP)               |
| forecast_demand_score | DECIMAL         | ML demand score 0--100 (from MVP)        |
| risk_score            | DECIMAL         | Composite risk score 0--100 (from MVP)   |
| recommended_action    | TEXT            | AI recommendation text (from MVP)        |

**buyer_origins table (new)**

|                 |               |                                                 |
|-----------------|---------------|-------------------------------------------------|
| **Field**       | **Type**      | **Description**                                 |
| origin_id       | UUID PK       | Unique buyer origin record                      |
| project_id      | UUID FK       | Associated project                              |
| lead_id         | VARCHAR       | CRM lead reference (anonymized)                 |
| origin_lat      | DECIMAL(10,7) | Buyer home latitude                             |
| origin_lng      | DECIMAL(10,7) | Buyer home longitude                            |
| h3_cell_id      | VARCHAR       | H3 resolution-7 cell identifier                 |
| delegation_id   | VARCHAR       | Delegation of origin                            |
| drive_time_min  | INTEGER       | Drive time to project in minutes                |
| is_reservation  | BOOLEAN       | True if this lead became a reservation          |
| campaign_source | ENUM          | meta \| google \| listing \| broker \| referral |
| origin_date     | DATE          | Date lead was captured                          |

**zones table (new)**

|                      |                   |                                                 |
|----------------------|-------------------|-------------------------------------------------|
| **Field**            | **Type**          | **Description**                                 |
| zone_id              | VARCHAR PK        | Delegation or governorate code                  |
| zone_name            | VARCHAR           | Display name                                    |
| zone_type            | ENUM              | delegation \| governorate                       |
| geom                 | GEOMETRY(Polygon) | PostGIS boundary polygon                        |
| avg_price_sqm        | DECIMAL           | Current average price/m2                        |
| price_tier           | INTEGER           | 1--5 price quintile                             |
| demand_score_30d     | DECIMAL           | 30-day demand forecast                          |
| demand_score_60d     | DECIMAL           | 60-day demand forecast                          |
| demand_score_90d     | DECIMAL           | 90-day demand forecast                          |
| risk_score           | DECIMAL           | Composite risk score                            |
| risk_class           | ENUM              | very_low \| low \| moderate \| high \| critical |
| supply_demand_ratio  | DECIMAL           | Units available / monthly absorption            |
| yoy_price_change_pct | DECIMAL           | Year-over-year price change %                   |
| mom_price_change_pct | DECIMAL           | Month-over-month price change %                 |

**12. Frontend Component Specifications**

**12.1 LayerControls.tsx --- The Top Bar**

The most critical UI component. Controls which Deck.gl layers are visible and passes the active subcategory to the MapContainer for layer switching.

> interface LayerControlsProps {
>
> activeCategory: \'marketing\' \| \'forecast\' \| \'risk\'
>
> activeSubcategories: string\[\]
>
> onCategoryChange: (cat: string) =\> void
>
> onSubcategoryToggle: (sub: string) =\> void
>
> }

- Category buttons: Three pill buttons, evenly spaced, centered horizontally. Blue (#2563EB) for Marketing, Purple (#7C3AED) for Forecast, Red (#DC2626) for Risk.

- Subcategory pills: Render conditionally based on active category. Use a horizontal scrollable row for mobile compatibility.

- State persistence: Active category and subcategories stored in URL search params for shareable links.

**12.2 HoverPanel.tsx --- The Tooltip**

Appears on pointer proximity (within 20px) of any interactive layer element. Renders above all map layers. Contains a MiniBarChart or TrendLine and 2--3 key stats.

- Position: Follows cursor with 16px offset, flips to avoid viewport edge

- Content structure: Zone/project name (bold), primary metric value (large), trend indicator (arrow + %), mini chart (90px height), 2 key stats

- Animation: Fade in 150ms, fade out 100ms on pointer leave

- Dark mode: Semi-transparent dark background (#1E293B at 95% opacity) for map contrast

**12.3 MapLayers.ts --- Deck.gl Layer Factory**

A pure TypeScript module that exports a function for each subcategory layer configuration. Each function returns a configured Deck.gl layer object ready for injection into the DeckGLOverlay.

> export function getPricingChoroplethLayer(data: ZoneFeatureCollection, colorScale: D3Scale): GeoJsonLayer
>
> export function getLeadHeatmapLayer(leads: LeadPoint\[\]): HeatmapLayer
>
> export function getBuyerOriginScatterLayer(buyers: BuyerOrigin\[\]): ScatterplotLayer
>
> export function getRiskHexagonLayer(cells: H3Cell\[\]): H3HexagonLayer
>
> export function getDemandHexLayer(cells: H3Cell\[\], horizon: 30\|60\|90): H3HexagonLayer

**12.4 AI Recommendation Card**

Rendered in the right panel when a zone or project is clicked. Calls POST /api/forecast/recommendations with the current context and streams the response.

- Trigger: Zone or project click event from any category mode

- Loading state: Skeleton animation while awaiting Claude API response

- Content: Action heading (bold), projected impact metric, confidence badge (%), 2-sentence reasoning, and Export button

- Color coding: Green card for opportunity actions, amber for caution, red for urgent risk mitigation

**13. Build Phases and Roadmap**

**Phase 0 --- COMPLETE (Streamlit MVP)**

Status: Done. The Streamlit MVP provides the data model, KPI logic, and CSV infrastructure that all future phases build on.

- data_loader.py: CSV ingestion from data/projects.csv

- kpis.py: Qualified Lead Rate, Unsold Inventory, Visit to Reservation Rate

- app.py: Executive KPI dashboard + dataset preview

**Phase 1 --- Hackathon Build (48 hours)**

|                                                                                                                                                                                                          |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Phase Goal:** Goal: Working demo with live map, all 3 category buttons, synthetic data across 5 Tunisian zones, and one complete demo flow showing buyer origin decoder for a fictional agency client. |

- Flask API serving /api/projects and /api/kpis from existing CSV

- Next.js 15 app with MapLibre GL JS base map (MapTiler tiles)

- Deck.gl integration: GeoJsonLayer for governorate pricing choropleth

- Category button UI with Marketing / Forecast / Risk switcher

- 3 subcategory layers per category (minimum viable set)

- HoverPanel with zone name + 3 stats + mini chart

- Right panel with AI recommendation (using Claude API)

- Synthetic data: 5 Tunisian governorates, 8 mock projects, 200 mock buyer origin points

- Demo flow: Agency dashboard → Marketing → Buyer Origin → Click Lac district → See recommendation

**Phase 2 --- First Agency Pilot (Months 1--2)**

- PostgreSQL + PostGIS database replacing CSV

- Agency onboarding flow: connect Meta pixel, Google Analytics, CRM export

- Real buyer origin data pipeline from CRM address field

- H3 hexagonal risk grid with real composite scoring

- Isochrone computation using Mapbox or OSRM

- Multi-project portfolio view for agency clients

- User authentication + agency-scoped data isolation

**Phase 3 --- Forecasting Engine (Months 3--4)**

- ML demand forecast model trained on synthetic + first pilot data

- Sales velocity forecast with 8-week horizon

- Competitor project monitoring (manual entry + web scrape)

- Inventory absorption prediction

- AI recommendation engine with Claude API structured prompting

- Automated weekly insight email for agency clients

**Phase 4 --- Scale and MENA Expansion (Months 5--9)**

- Second city: Sfax or Sousse data extension

- Arabic language interface (RTL layout support in Tailwind)

- Cairo or Casablanca pilot with adapted data pipeline

- Buyer origin atlas API for third-party integrations

- Kepler.gl workflow export for advanced analyst users

- Series A positioning: documented ROI from pilot agencies

**14. Non-Functional Requirements**

|                 |                                    |                                                                        |
|-----------------|------------------------------------|------------------------------------------------------------------------|
| **Category**    | **Requirement**                    | **Target**                                                             |
| Performance     | Map layer render on layer switch   | \< 300ms for GeoJsonLayer, \< 500ms for HeatmapLayer                   |
| Performance     | API response time (most endpoints) | \< 800ms at p95                                                        |
| Performance     | AI recommendation response         | \< 4 seconds (streamed)                                                |
| Scalability     | Concurrent agency users (Phase 1)  | Up to 20 simultaneous                                                  |
| Scalability     | Buyer origin records               | Up to 50,000 records without pagination degradation                    |
| Data privacy    | Buyer origin data                  | Aggregated to H3 cell level before display --- no individual tracking  |
| Browser support | Desktop browsers                   | Chrome 110+, Firefox 115+, Safari 16+, Edge 110+                       |
| Mobile          | Agency director casual access      | Responsive at 768px+ --- full functionality at 1280px+                 |
| Uptime          | Development phase                  | No SLA --- local deployment                                            |
| Security        | API auth                           | JWT with 24h expiry, refresh token pattern                             |
| Licensing       | Map tiles                          | MapTiler free tier for development, OpenStreetMap attribution required |

**15. Glossary**

|                  |                                                                                                |                                                              |
|------------------|------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| **Term**         | **Definition**                                                                                 | **Context**                                                  |
| Buyer Origin     | The geographic home location of a lead at the time of their purchase or reservation            | Core data point of TerraLens --- decoded from CRM address    |
| Catchment Area   | The geographic zone from which a project draws its buyers, modeled using drive-time isochrones | Spatial basis for budget allocation recommendations          |
| Isochrone        | A polygon representing equal travel time from a central point (e.g., 15-minute drive zone)     | Computed by road network routing, not straight-line distance |
| H3 Grid          | Uber\'s hexagonal hierarchical spatial indexing system used for zone-level aggregation         | Used for demand and risk grid layers at resolution 7         |
| Demand Spillover | The geographic diffusion of buyer demand when a competing project sells out                    | Modeled using distance-decay function from sellout location  |
| Qualified Lead   | A lead that meets minimum criteria: valid phone, real inquiry, financial pre-screening         | KPI inherited from Streamlit MVP (kpis.py)                   |
| Atlas            | The accumulated buyer origin dataset built from all agency campaigns processed by TerraLens    | The core data flywheel and competitive moat                  |
| CORS             | Cross-Origin Resource Sharing --- configured in Flask to allow Next.js frontend requests       | Flask-CORS package required for local dev                    |
| CPL              | Cost Per Lead in DT --- campaign spend divided by lead count                                   | Marketing intelligence KPI                                   |
| CPQL             | Cost Per Qualified Lead in DT --- campaign spend divided by qualified lead count               | Higher-value marketing KPI from kpis.py                      |
| VTR              | Visit-to-Reservation Rate --- % of site visits that result in a reservation                    | Sales funnel KPI from kpis.py                                |

TerraLens AI --- Product Requirements Document --- v1.0

Confidential --- Internal use only --- April 2026
