

# TerraLens AI — Design Reference Guide

## Light Theme Dashboard

---

## 1. Brand Identity

### Logo

The TerraLens AI logo features a **map pin icon** containing a compass rose with a globe grid overlay and a green directional arrow, paired with the wordmark "TERRALENS" in dark navy and "·AI" in green. The logo communicates geospatial intelligence, navigation, and precision.

**Logo URL:** `https://www.genspark.ai/api/files/s/Wdpdf6m9`

**Usage rules:**
- Minimum clear space around the logo equals the height of the "·AI" text on all sides.
- On light backgrounds, use the full-color version as shown.
- Never place the logo on visually busy map areas without a frosted-glass backdrop.
- Minimum display width: 140px (horizontal lockup).

---

## 2. Color System

### 2.1 Primary Palette

| Token | Hex | RGB | Usage |
|---|---|---|---|
| `--brand-navy` | `#0C2461` | 12, 36, 97 | Primary text, logo wordmark, headings |
| `--brand-teal` | `#1D9E75` | 29, 158, 117 | Logo accent, "·AI" text, success states, buyer origin dots |
| `--brand-cyan` | `#2EC4D6` | 46, 196, 214 | Logo compass elements, secondary accents, icon highlights |
| `--brand-cyan-light` | `#7AE3EC` | 122, 227, 236 | Logo grid fill, hover glows, active tab underlines |

### 2.2 Category Colors

Each of the three core product categories owns a color that persists across buttons, panel headers, chart accents, and layer legends.

| Category | Token | Hex | Tailwind Class | Usage |
|---|---|---|---|---|
| Marketing Intelligence | `--cat-marketing` | `#2563EB` | `blue-600` | Category pill, sidebar header, choropleth legend frame |
| Prediction & Planning | `--cat-forecast` | `#7C3AED` | `violet-600` | Category pill, forecast charts, demand hex color anchor |
| Risk & Mitigation | `--cat-risk` | `#DC2626` | `red-600` | Category pill, risk grid legend, alert badges |

**Category tint surfaces** (used for panel backgrounds when a category is active):

| Category | Token | Hex | Usage |
|---|---|---|---|
| Marketing tint | `--cat-marketing-tint` | `#EFF6FF` | Left sidebar background in Marketing mode |
| Forecast tint | `--cat-forecast-tint` | `#F5F3FF` | Left sidebar background in Forecast mode |
| Risk tint | `--cat-risk-tint` | `#FEF2F2` | Left sidebar background in Risk mode |

### 2.3 Neutral / UI Palette

| Token | Hex | Usage |
|---|---|---|
| `--surface-primary` | `#FFFFFF` | Card backgrounds, panels, modals |
| `--surface-secondary` | `#F8FAFC` | Page canvas behind map, table row alternation |
| `--surface-tertiary` | `#F1F5F9` | Disabled inputs, skeleton loading blocks |
| `--border-default` | `#E2E8F0` | Card borders, dividers, input outlines |
| `--border-strong` | `#CBD5E1` | Active input borders, focused elements |
| `--text-primary` | `#0F172A` | Headings, primary body text |
| `--text-secondary` | `#475569` | Descriptions, secondary labels |
| `--text-tertiary` | `#94A3B8` | Placeholders, timestamps, disabled text |
| `--text-inverse` | `#FFFFFF` | Text on filled buttons or dark overlays |

### 2.4 Semantic Colors

| Token | Hex | Usage |
|---|---|---|
| `--semantic-success` | `#059669` | Positive KPI change, rising zones, accelerating projects |
| `--semantic-success-bg` | `#ECFDF5` | Success badge background |
| `--semantic-warning` | `#D97706` | Monitor-level alerts, amber risk tier, caution cards |
| `--semantic-warning-bg` | `#FFFBEB` | Warning badge background |
| `--semantic-danger` | `#DC2626` | Critical risk, urgent actions, declining velocity |
| `--semantic-danger-bg` | `#FEF2F2` | Danger badge background |
| `--semantic-info` | `#2563EB` | Informational tooltips, neutral notifications |
| `--semantic-info-bg` | `#EFF6FF` | Info badge background |

### 2.5 Map-Specific Color Scales

**Zone Pricing Choropleth (Marketing 7.1.1):**

| Tier | Label | Hex | DT/m² Range |
|---|---|---|---|
| 1 | Affordable | `#F0F9FF` | < 1,500 |
| 2 | Moderate | `#BAE6FD` | 1,500–2,500 |
| 3 | Mid-range | `#38BDF8` | 2,500–3,500 |
| 4 | Premium | `#1D4ED8` | 3,500–5,000 |
| 5 | Luxury | `#0C2461` | > 5,000 |

**Price Rise Diverging (Marketing 7.1.2):**

| Direction | Hex | Meaning |
|---|---|---|
| Strong decline | `#7F1D1D` | ≤ –5% MoM |
| Mild decline | `#F87171` | –5% to –1% |
| Neutral | `#E2E8F0` | –1% to +1% |
| Mild rise | `#34D399` | +1% to +5% |
| Strong rise | `#065F46` | ≥ +5% |

**Lead Density Heatmap (Marketing 7.1.3):**
Gradient stops: `#FEF9C3` → `#FB923C` → `#DC2626`

**Risk Composite Grid (Risk 9.2.1):**

| Class | Label | Hex | Score |
|---|---|---|---|
| 1 | Very Low | `#D1FAE5` | 0–20 |
| 2 | Low | `#A7F3D0` | 20–40 |
| 3 | Moderate | `#FEF3C7` | 40–60 |
| 4 | High | `#FBBF24` | 60–80 |
| 5 | Critical | `#7F1D1D` | 80–100 |

**Demand Forecast Hex (Forecast 8.2.1):**
Sequential: `#DBEAFE` (low) → `#3B82F6` (mid) → `#F59E0B` (high)

---

## 3. Typography

### 3.1 Font Stack

| Role | Font | Fallback | Weight | Reason |
|---|---|---|---|---|
| Headings | **Inter** | `system-ui, -apple-system, sans-serif` | 600, 700 | Clean geometric proportions; excellent for dashboards |
| Body | **Inter** | `system-ui, -apple-system, sans-serif` | 400, 500 | Same family for cohesion |
| Monospace / Data | **JetBrains Mono** | `ui-monospace, Menlo, monospace` | 400 | KPI values, coordinates, code |
| Arabic (Phase 4) | **IBM Plex Sans Arabic** | `Segoe UI, Tahoma, sans-serif` | 400, 600 | Designed for bilingual UI, RTL-ready |

### 3.2 Type Scale

| Token | Size | Line Height | Weight | Usage |
|---|---|---|---|---|
| `--text-display` | 28px / 1.75rem | 36px | 700 | Dashboard title (rare) |
| `--text-h1` | 22px / 1.375rem | 28px | 700 | Panel header, e.g., "Marketing Intelligence" |
| `--text-h2` | 18px / 1.125rem | 24px | 600 | Section title inside panels |
| `--text-h3` | 15px / 0.9375rem | 20px | 600 | Card title, zone name in tooltip |
| `--text-body` | 14px / 0.875rem | 20px | 400 | Default body text, descriptions |
| `--text-body-strong` | 14px / 0.875rem | 20px | 500 | Emphasized body, table headers |
| `--text-caption` | 12px / 0.75rem | 16px | 400 | Labels, timestamps, axis ticks |
| `--text-overline` | 11px / 0.6875rem | 16px | 600 | Uppercased category labels, badge text |
| `--text-kpi` | 32px / 2rem | 36px | 700 | Hero KPI numbers (JetBrains Mono) |
| `--text-kpi-small` | 20px / 1.25rem | 24px | 600 | Secondary KPI values (JetBrains Mono) |

### 3.3 Typography Rules

- All headings use `letter-spacing: -0.01em` for tightness.
- Overline text uses `letter-spacing: 0.06em; text-transform: uppercase`.
- KPI values always use `font-variant-numeric: tabular-nums` for column alignment.
- Maximum body text line length: 65 characters (≈ 520px at 14px).
- Paragraph spacing: 12px (`mb-3`).

---

## 4. Spacing & Layout

### 4.1 Spacing Scale

Based on a 4px base unit, following Tailwind defaults:

| Token | Value | Usage |
|---|---|---|
| `--space-1` | 4px | Tight internal padding (badge text padding) |
| `--space-2` | 8px | Icon-to-text gaps, compact list items |
| `--space-3` | 12px | Default gap between inline elements |
| `--space-4` | 16px | Card internal padding, standard gap |
| `--space-5` | 20px | Section spacing within a panel |
| `--space-6` | 24px | Panel internal padding |
| `--space-8` | 32px | Section dividers, panel header bottom margin |
| `--space-10` | 40px | Between major layout sections |
| `--space-12` | 48px | Top bar height |

### 4.2 Master Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  TOP BAR (h: 48px, fixed, z-50)                                │
│  [Logo]   [Marketing] [Prediction] [Risk]    [Search] [Avatar] │
│           ┌─────────────────────────────┐                       │
│           │ subcategory pills (h: 36px) │                       │
│           └─────────────────────────────┘                       │
├────────────────┬────────────────────────────────┬───────────────┤
│                │                                │               │
│  LEFT PANEL    │       MAP SURFACE              │  RIGHT PANEL  │
│  (w: 380px)    │       (100vw × 100vh)          │  (w: 400px)   │
│  collapsible   │       MapLibre GL JS           │  contextual   │
│  slides in     │       + Deck.gl layers         │  on click     │
│  z-40          │       z-0                      │  z-40         │
│                │                                │               │
│                │                                │               │
│                │                                │               │
│                │                                │               │
│                ├────────────────────────────────┤               │
│                │ BOTTOM BAR (optional, h: 64px) │               │
│                │ Time slider + Compare toggle   │               │
└────────────────┴────────────────────────────────┴───────────────┘
```

### 4.3 Breakpoints

| Token | Width | Behavior |
|---|---|---|
| `sm` | 640px | Stack panels vertically, bottom sheet navigation |
| `md` | 768px | Left panel as collapsible drawer, right panel as bottom sheet |
| `lg` | 1024px | Left panel visible, right panel overlay |
| `xl` | 1280px | Full layout — both panels + map at designed widths |
| `2xl` | 1536px | Expanded map surface, wider panels (420px) |

---

## 5. Component Specifications

### 5.1 Top Bar

| Property | Value |
|---|---|
| Height | 48px |
| Background | `#FFFFFF` with `border-bottom: 1px solid var(--border-default)` |
| Shadow | `0 1px 3px rgba(0, 0, 0, 0.06)` |
| Z-index | 50 |
| Logo placement | Left-aligned, 16px from left edge, vertically centered, max-height 32px |
| Category buttons | Center-aligned group, 8px gap between buttons |
| Right section | Search icon + user avatar, 16px from right edge |

### 5.2 Category Buttons

| State | Background | Border | Text Color | Shadow |
|---|---|---|---|---|
| Default | `#FFFFFF` | `1px solid {category color at 30% opacity}` | `{category color}` | none |
| Hover | `{category color at 5% opacity}` | `1px solid {category color at 50% opacity}` | `{category color}` | none |
| Active | `{category color}` | none | `#FFFFFF` | `0 1px 3px {category color at 25% opacity}` |

**Dimensions:** height 36px, padding 0 20px, border-radius 18px (full pill), font `--text-body-strong`.

### 5.3 Subcategory Pills

| Property | Value |
|---|---|
| Height | 28px |
| Padding | 0 14px |
| Border-radius | 14px (full pill) |
| Font | `--text-caption`, weight 500 |
| Default state | `background: var(--surface-secondary)`, `color: var(--text-secondary)` |
| Active state | `background: {category color at 12% opacity}`, `color: {category color}`, `border: 1px solid {category color at 30% opacity}` |
| Container | Horizontal row, 6px gap, centered below active category button |
| Overflow | Horizontally scrollable on small screens, no visible scrollbar |

### 5.4 Left Sidebar Panel

| Property | Value |
|---|---|
| Width | 380px (xl), 340px (lg), full-width drawer (md and below) |
| Background | `#FFFFFF` |
| Border | `border-right: 1px solid var(--border-default)` |
| Shadow | `4px 0 16px rgba(0, 0, 0, 0.06)` |
| Border-radius | 0 (flush to viewport edge) |
| Z-index | 40 |
| Top offset | 48px (below top bar) |
| Height | `calc(100vh - 48px)` |
| Overflow | `overflow-y: auto` with custom thin scrollbar |
| Animation | Slide-in from left, 250ms ease-out |
| Internal padding | 24px |
| Header | Category icon + title (h1), tinted background strip (16px tall, category-tint color) |
| Close button | 24×24px icon button, top-right corner of panel, `--text-tertiary` color |

### 5.5 Right Context Panel

| Property | Value |
|---|---|
| Width | 400px (xl), 360px (lg), bottom sheet (md and below) |
| Background | `#FFFFFF` |
| Border | `border-left: 1px solid var(--border-default)` |
| Shadow | `-4px 0 16px rgba(0, 0, 0, 0.06)` |
| Border-radius | 12px top-left and bottom-left corners |
| Z-index | 40 |
| Top offset | 60px (below top bar + subcategory row) |
| Height | `calc(100vh - 76px)` |
| Animation | Slide-in from right, 200ms ease-out |
| Trigger | Zone click or project marker click |
| Dismiss | Click on empty map area, or close button |

### 5.6 Hover Tooltip (HoverPanel)

| Property | Value |
|---|---|
| Max width | 280px |
| Background | `#FFFFFF` |
| Border | `1px solid var(--border-default)` |
| Border-radius | 10px |
| Shadow | `0 4px 20px rgba(0, 0, 0, 0.12)` |
| Padding | 14px |
| Z-index | 45 |
| Offset from cursor | 16px right, 16px below (flips near edges) |
| Animation | Fade in 150ms ease-in, fade out 100ms ease-out |
| Pointer events | `none` (does not capture mouse) |

**Internal layout:**

```
┌──────────────────────────────┐
│  Zone Name            ▲ +3% │  ← --text-h3, trend badge
│  Primary Metric: 2,450 DT   │  ← --text-kpi-small (JetBrains Mono)
│  ┌────────────────────────┐  │
│  │   Mini Sparkline       │  │  ← 90px height, Recharts TrendLine
│  └────────────────────────┘  │
│  Leads: 142    Conv: 4.2%   │  ← --text-caption, two-column stats
└──────────────────────────────┘
```

### 5.7 AI Recommendation Card

| Property | Value |
|---|---|
| Location | Inside right panel, pinned to top |
| Background | White with a 3px left border in semantic color (green/amber/red) |
| Border-radius | 10px |
| Padding | 20px |
| Shadow | `0 2px 8px rgba(0, 0, 0, 0.06)` |

**Internal layout:**

```
┌─ ● AI Recommendation ──────────────────────┐
│                                             │
│  ACTION HEADING                    85% ✓    │  ← --text-h3 + confidence badge
│                                             │
│  Increase Meta budget in La Marsa by 40%.   │
│  Buyer origin data shows 23% of             │  ← --text-body, 2 sentences
│  reservations from this zone but only 8%    │
│  of current spend.                          │
│                                             │
│  Projected impact: +12 reservations/month   │  ← --text-body-strong, semantic green
│                                             │
│  [ Export PDF ]  [ Apply to Campaign ]      │  ← secondary + primary buttons
└─────────────────────────────────────────────┘
```

### 5.8 KPI Cards (Left Panel)

Used inside the left sidebar to display key metrics for the active category.

| Property | Value |
|---|---|
| Background | `#FFFFFF` |
| Border | `1px solid var(--border-default)` |
| Border-radius | 10px |
| Padding | 16px |
| Margin-bottom | 12px |
| Shadow | `0 1px 3px rgba(0, 0, 0, 0.04)` |

**Internal layout:**

```
┌────────────────────────────────┐
│  KPI Label          ▲ +12.5%  │  ← --text-caption + trend badge
│  2,847                        │  ← --text-kpi (JetBrains Mono)
│  vs 2,531 last month          │  ← --text-caption, --text-tertiary
└────────────────────────────────┘
```

**Trend badge:**
- Positive: `background: var(--semantic-success-bg)`, `color: var(--semantic-success)`, up arrow
- Negative: `background: var(--semantic-danger-bg)`, `color: var(--semantic-danger)`, down arrow
- Neutral: `background: var(--surface-tertiary)`, `color: var(--text-tertiary)`, dash

### 5.9 Data Table

Used in right panel for attribution breakdowns, competitor comparisons, and portfolio risk lists.

| Property | Value |
|---|---|
| Header row bg | `var(--surface-secondary)` |
| Header text | `--text-caption`, weight 600, uppercase, `--text-tertiary` |
| Row height | 44px |
| Row border | `border-bottom: 1px solid var(--border-default)` |
| Row hover | `background: var(--surface-secondary)` |
| Cell padding | 12px horizontal |
| Numeric alignment | Right-aligned, `tabular-nums` |
| Border-radius | 10px (outer container), overflow hidden |

### 5.10 Buttons

**Primary Button:**

| Property | Value |
|---|---|
| Background | `var(--brand-navy)` (#0C2461) |
| Text | `#FFFFFF`, `--text-body-strong` |
| Height | 40px |
| Padding | 0 24px |
| Border-radius | 8px |
| Hover | `background: #0E2D74` (5% lighter) |
| Active | `background: #091C4A` (10% darker) |
| Shadow | `0 1px 2px rgba(0, 0, 0, 0.08)` |

**Secondary Button:**

| Property | Value |
|---|---|
| Background | `#FFFFFF` |
| Border | `1px solid var(--border-strong)` |
| Text | `var(--text-primary)`, `--text-body-strong` |
| Height | 40px |
| Padding | 0 20px |
| Border-radius | 8px |
| Hover | `background: var(--surface-secondary)` |

**Ghost Button (icon-only):**

| Property | Value |
|---|---|
| Background | transparent |
| Size | 36×36px |
| Border-radius | 8px |
| Icon color | `var(--text-secondary)` |
| Hover | `background: var(--surface-secondary)` |

### 5.11 Badge / Tag

| Property | Value |
|---|---|
| Height | 22px |
| Padding | 0 8px |
| Border-radius | 6px |
| Font | `--text-overline` (11px, 600, uppercase) |
| Variants | success, warning, danger, info, neutral (each uses its semantic bg + text color) |

### 5.12 Map Legend

Floats in the bottom-left corner of the map surface.

| Property | Value |
|---|---|
| Background | `rgba(255, 255, 255, 0.92)` with `backdrop-filter: blur(8px)` |
| Border | `1px solid var(--border-default)` |
| Border-radius | 10px |
| Padding | 14px |
| Max width | 220px |
| Z-index | 35 |
| Title | `--text-caption`, weight 600, `--text-secondary` |
| Color strip | 12px height, full width, rounded 4px, gradient or segmented |
| Labels | `--text-caption`, `--text-tertiary`, spaced below strip |
| Animation | Fade transition 200ms when layer switches |

### 5.13 Bottom Time Bar

| Property | Value |
|---|---|
| Height | 64px |
| Background | `rgba(255, 255, 255, 0.95)` with `backdrop-filter: blur(8px)` |
| Border-top | `1px solid var(--border-default)` |
| Z-index | 35 |
| Position | Fixed to bottom of map viewport, full width minus panel widths |
| Content | Time slider (range input), period label, comparison toggle switch |
| Slider track | 4px height, `var(--border-default)` |
| Slider thumb | 20px circle, `var(--brand-navy)` fill, white border |
| Animation | Slides up 250ms ease-out when temporal analysis is activated |

### 5.14 Portfolio Risk Bar (Below-Map, Risk Mode)

| Property | Value |
|---|---|
| Height | 140px |
| Background | `#FFFFFF` |
| Border-top | `1px solid var(--border-default)` |
| Shadow | `0 -2px 8px rgba(0, 0, 0, 0.06)` |
| Scroll | Horizontal, custom scrollbar |
| Card width | 260px per project card |
| Card gap | 12px |
| Card border-radius | 10px |
| Card border | `1px solid var(--border-default)` |
| Risk badge | Top-right corner, colored by risk class |

---

## 6. Iconography

### 6.1 Icon Set

Use **Lucide Icons** (open-source, MIT licensed, designed for 24×24px grid). Consistent stroke width of 1.5px.

### 6.2 Key Icon Assignments

| Context | Icon Name | Usage |
|---|---|---|
| Marketing category | `bar-chart-3` | Category button icon |
| Forecast category | `trending-up` | Category button icon |
| Risk category | `shield-alert` | Category button icon |
| Search | `search` | Top bar search trigger |
| User menu | `user-circle` | Top bar avatar fallback |
| Close panel | `x` | Panel dismiss buttons |
| Expand panel | `chevron-right` | Collapsed panel indicator |
| Export | `download` | Export PDF/CSV buttons |
| AI recommendation | `sparkles` | Recommendation card header |
| Rising trend | `arrow-up-right` | KPI trend badge |
| Falling trend | `arrow-down-right` | KPI trend badge |
| Stable | `minus` | KPI trend badge |
| Filter | `sliders-horizontal` | Filter controls |
| Layers | `layers` | Map layer toggle |
| Calendar | `calendar` | Time period selector |
| Map pin | `map-pin` | Project markers in lists |
| Warning | `alert-triangle` | Risk alerts |
| Info | `info` | Informational tooltips |
| Refresh | `refresh-cw` | Data reload |

### 6.3 Icon Sizing

| Context | Size | Stroke |
|---|---|---|
| Top bar / navigation | 20×20px | 1.5px |
| Inside buttons (with text) | 16×16px | 1.5px |
| KPI card decorators | 16×16px | 1.5px |
| Panel section headers | 18×18px | 1.5px |
| Tooltip / badge inline | 14×14px | 1.5px |

---

## 7. Charts & Data Visualization

### 7.1 Chart Library

**Recharts** for all panel-embedded charts (bar, line, area, radar, pie). Consistent styling tokens applied across all instances.

### 7.2 Chart Style Tokens

| Property | Value |
|---|---|
| Grid lines | `var(--border-default)` (#E2E8F0), 1px, dashed |
| Axis labels | `--text-caption`, `var(--text-tertiary)` |
| Axis lines | `var(--border-strong)` (#CBD5E1), 1px |
| Tooltip bg | `#FFFFFF`, `border: 1px solid var(--border-default)`, `border-radius: 8px`, `shadow: 0 4px 12px rgba(0,0,0,0.1)` |
| Bar border-radius | 4px top corners |
| Line stroke width | 2px |
| Area fill opacity | 0.12 |
| Confidence band fill | Category color at 8% opacity |
| Animation | 400ms ease-out on data transition |

### 7.3 Chart Types per Subcategory

| Subcategory | Chart in Left Panel | Chart in Hover Tooltip | Chart in Right Panel |
|---|---|---|---|
| Zone Pricing | Bar chart (price by tier) | Sparkline (12-month trend) | Histogram (price distribution) |
| Price Rise % | Area chart (trend over time) | Sparkline (3-month) | Line chart (12-month with annotation) |
| Lead Density | Stacked bar (source mix) | Mini bar (qualified vs total) | Funnel chart (lead → reservation) |
| Buyer Origin | Donut (zone contribution %) | Mini bar (conversion rate) | Sankey (origin zone → project flow) |
| Campaign Attribution | Grouped bar (by source) | Pie (source mix) | Table + bar (full breakdown) |
| Demand Forecast | Area chart with confidence band | Sparkline (demand trend) | Decomposition stacked area |
| Sales Velocity | Line chart with forecast band | Sparkline (8-week) | Multi-line (by buyer type) |
| Risk Composite | — | — | Radar chart (6 dimensions) |
| Inventory Absorption | Horizontal bar (weeks remaining) | Countdown number | Stacked bar (unit types) |

### 7.4 Mini Sparkline (Tooltip)

| Property | Value |
|---|---|
| Width | 100% of tooltip content area |
| Height | 48px |
| Stroke | Category color, 1.5px |
| Fill | Category color at 8% opacity |
| Dots | None (clean line only) |
| Axes | Hidden |
| Last-point dot | 4px circle, category color, visible |

---

## 8. Map Base Layer (Light Theme)

### 8.1 MapTiler Style

Use **MapTiler Positron** (or equivalent light OSM style) as the base layer for the light theme.

| Property | Value |
|---|---|
| Style URL | `https://api.maptiler.com/maps/positron/style.json?key={KEY}` |
| Land color | `#FAFAFA` |
| Water color | `#D4E6F1` |
| Roads | Light gray (#E0E0E0) |
| Labels | `--text-tertiary` (#94A3B8), Inter font |
| Building fill | `#EEEEEE` |
| Parks | `#E8F5E9` |

### 8.2 Overlay Opacity Guidelines

To maintain legibility of both the base map and data layers:

| Layer Type | Recommended Fill Opacity |
|---|---|
| Choropleth polygons | 0.55–0.70 |
| Heatmap | 0.60–0.80 (Deck.gl `intensity` control) |
| H3 hex grid | 0.65 (flat), 0.80 (extruded) |
| Isochrone zones | 0.15–0.25 (stroke at 0.8) |
| Risk hatching | 0.30 (pattern fill) |
| Catchment overlap | 0.20 (amber fill) |

### 8.3 Default Map View

| Property | Value |
|---|---|
| Center | `[10.1815, 36.8065]` (Tunis) |
| Zoom | 11 |
| Min zoom | 6 (Tunisia country view) |
| Max zoom | 17 (building-level) |
| Pitch | 0° (flat) for 2D modes; 45° for extruded hex layers |
| Bearing | 0° |

---

## 9. Motion & Animation

### 9.1 Transition Tokens

| Token | Duration | Easing | Usage |
|---|---|---|---|
| `--transition-fast` | 150ms | ease-in | Tooltip appear, button state change |
| `--transition-default` | 200ms | ease-out | Panel slide, layer fade, badge transitions |
| `--transition-medium` | 250ms | ease-out | Sidebar open/close, bottom bar slide |
| `--transition-slow` | 400ms | ease-in-out | Map fly-to, chart data transition |
| `--transition-layer` | 300ms | ease-out | Deck.gl layer opacity fade on category switch |

### 9.2 Map Transitions

| Action | Animation |
|---|---|
| Category switch | All current layers fade out (200ms), new layers fade in (300ms). No map position change. |
| Subcategory toggle | Active layer cross-fades (200ms). Map position preserved. |
| Zone click → fly-to | `map.flyTo()` with 600ms duration, zoom to 13, centered on zone centroid |
| Project click → fly-to | `map.flyTo()` with 500ms duration, zoom to 14, centered on project marker |
| "View on Map" from portfolio bar | `map.flyTo()` with 800ms duration, ease-in-out |
| Reset (click empty map) | All panels dismiss (200ms slide-out), map eases to default view (600ms) |

### 9.3 Skeleton Loading

When panels or charts are loading data:

| Property | Value |
|---|---|
| Background | `var(--surface-tertiary)` (#F1F5F9) |
| Shimmer gradient | `linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%)` |
| Animation | `background-position` sweep, 1.5s infinite |
| Border-radius | Matches the component being loaded |
| Text placeholders | Rounded rectangles at 60%, 80%, 40% width for visual variety |

---

## 10. Shadows & Elevation

| Level | Token | Value | Usage |
|---|---|---|---|
| 0 | `--shadow-none` | none | Flat elements, table rows |
| 1 | `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.04)` | KPI cards, table container |
| 2 | `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.06)` | Top bar, subcategory container |
| 3 | `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08)` | Floating panels, dropdowns |
| 4 | `--shadow-lg` | `0 4px 20px rgba(0,0,0,0.12)` | Hover tooltip, modals |
| 5 | `--shadow-xl` | `0 8px 30px rgba(0,0,0,0.16)` | Notification toast, critical alert overlay |

---

## 11. Scrollbar Styling

Custom thin scrollbar for all panel `overflow-y: auto` containers:

```css
.panel-scroll::-webkit-scrollbar {
  width: 6px;
}
.panel-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.panel-scroll::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: 3px;
}
.panel-scroll::-webkit-scrollbar-thumb:hover {
  background: var(--border-strong);
}
```

---

## 12. Accessibility

| Requirement | Implementation |
|---|---|
| Color contrast | All text meets WCAG 2.1 AA (4.5:1 for body, 3:1 for large text). Verified: `--text-primary` on `--surface-primary` = 15.4:1. `--text-secondary` on `--surface-primary` = 6.1:1. |
| Focus indicators | 2px solid `var(--brand-cyan)` outline with 2px offset on all interactive elements. |
| Keyboard navigation | Tab order follows visual hierarchy: top bar → left panel → map controls → right panel. Category buttons navigable with arrow keys. |
| Screen reader | All map layers have `aria-label` descriptions. Chart components include `role="img"` and `aria-label` summarizing the data. |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` disables all animations, uses instant transitions. |
| Map fallback | Non-sighted users receive a tabular summary of visible data via a toggle at the top of each panel. |
| Color-blind safety | All color scales verified against deuteranopia and protanopia simulations. Risk grid and diverging scales use luminance differentiation in addition to hue. |

---

## 13. Responsive Behavior Summary

### Desktop (≥ 1280px) — Primary Design Target

Full layout as described in Section 4.2. Both panels can be open simultaneously alongside the map. All features fully functional.

### Laptop (1024px–1279px)

Left panel width reduces to 340px. Right panel overlaps map (no side-by-side). Portfolio risk bar scrolls with narrower cards (220px).

### Tablet (768px–1023px)

Left panel becomes a drawer (slides over map, 85% width). Right panel becomes a bottom sheet (60% viewport height, draggable). Category buttons remain in top bar. Subcategory pills horizontally scroll. Bottom time bar hidden — time selection moves into left panel.

### Mobile (< 768px)

Single-panel mode. Top bar collapses to hamburger + category icon buttons. Tapping a category opens a full-screen panel. Map is accessed by dismissing all panels. Hover tooltips replaced by tap-to-reveal behavior. Portfolio risk bar becomes a vertical scrolling list.

---

## 14. Tailwind CSS Configuration Reference

```js
// tailwind.config.js (key extensions)
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          navy: '#0C2461',
          teal: '#1D9E75',
          cyan: '#2EC4D6',
          'cyan-light': '#7AE3EC',
        },
        cat: {
          marketing: '#2563EB',
          'marketing-tint': '#EFF6FF',
          forecast: '#7C3AED',
          'forecast-tint': '#F5F3FF',
          risk: '#DC2626',
          'risk-tint': '#FEF2F2',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'Menlo', 'monospace'],
        arabic: ['IBM Plex Sans Arabic', 'Segoe UI', 'Tahoma', 'sans-serif'],
      },
      width: {
        'panel-left': '380px',
        'panel-right': '400px',
      },
      zIndex: {
        map: '0',
        legend: '35',
        panel: '40',
        tooltip: '45',
        topbar: '50',
        modal: '60',
      },
      boxShadow: {
        'panel': '4px 0 16px rgba(0, 0, 0, 0.06)',
        'panel-right': '-4px 0 16px rgba(0, 0, 0, 0.06)',
        'tooltip': '0 4px 20px rgba(0, 0, 0, 0.12)',
        'topbar': '0 1px 3px rgba(0, 0, 0, 0.06)',
      },
      borderRadius: {
        'card': '10px',
        'pill': '9999px',
      },
    },
  },
}
```

---

## 15. File Naming & Asset Conventions

| Asset Type | Location | Naming Convention |
|---|---|---|
| Logo variants | `/public/brand/` | `terralens-logo-full.svg`, `terralens-logo-mark.svg`, `terralens-logo-mono.svg` |
| Category icons | `/public/icons/` | `icon-marketing.svg`, `icon-forecast.svg`, `icon-risk.svg` |
| GeoJSON boundaries | `/backend/data/geodata/` | `tunisia-governorates.geojson`, `tunisia-delegations.geojson` |
| Map style override | `/frontend/lib/` | `mapStyle.ts` |
| Color scale definitions | `/frontend/lib/` | `colorScales.ts` |
| Design tokens (CSS) | `/frontend/app/` | `globals.css` (CSS custom properties) |
| Component styles | Co-located | Tailwind classes inline, no separate CSS files |

---
