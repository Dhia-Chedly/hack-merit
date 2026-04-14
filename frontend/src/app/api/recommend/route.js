import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

const GROQ_API_KEY = process.env.GROQ_API_KEY;

// ─── Sector-specific expert personas per category + layer ───
const SECTOR_PROMPTS = {
  "marketing|zone-pricing": {
    role: "Senior Real Estate Pricing Strategist for the Tunisian market",
    focus: "Analyze zone pricing dynamics, price-per-m² positioning, and price tier competitiveness. Focus on how the project or zone's pricing compares to neighboring areas and what adjustment would maximize absorption while protecting margins.",
  },
  "marketing|price-trend": {
    role: "Real Estate Market Analyst specializing in price momentum signals in MENA",
    focus: "Analyze price trends and momentum. Identify whether the zone is in an acceleration, peak, or correction phase. Provide timing advice for campaign spend and pricing adjustments based on the trend direction.",
  },
  "marketing|lead-density": {
    role: "Digital Marketing & Lead Generation Expert for real estate campaigns",
    focus: "Analyze lead density patterns and campaign source effectiveness. Identify which geographic zones generate the highest quality leads and recommend budget reallocation for Meta, Google, Mubawab, and broker channels.",
  },
  "marketing|buyer-origin": {
    role: "Buyer Catchment Intelligence Analyst — the core expertise of TerraLens AI",
    focus: "Decode where real buyers physically live vs where campaigns are targeted. Identify catchment gaps (high spend, zero conversions) and recommend geographic budget shifts based on actual buyer origin data.",
  },
  "marketing|attribution": {
    role: "Campaign Attribution & ROI Optimization Specialist",
    focus: "Analyze campaign-to-reservation funnel by source and zone. Identify which campaign types (Meta, Google, broker, listing) work best in which neighborhoods. Recommend source-level budget reallocation.",
  },
  "forecast|demand": {
    role: "Real Estate Demand Forecasting Analyst with ML expertise",
    focus: "Analyze the demand forecast index and its key drivers. Explain what factors are pushing demand up or down in this zone. Provide a 30-60-90 day demand outlook with confidence bands and recommended actions.",
  },
  "forecast|velocity": {
    role: "Sales Velocity & Inventory Analyst for real estate developers",
    focus: "Analyze sales velocity trends and predict weekly reservation rates. Flag projects showing velocity decline before it becomes visible in raw numbers. Recommend launch timing and inventory management actions.",
  },
  "forecast|absorption": {
    role: "Inventory Absorption & Market Timing Expert",
    focus: "Analyze time-to-sell for remaining inventory. Identify projects at risk of stagnation. Recommend pricing, incentive, and channel strategies to accelerate absorption before it becomes a financial problem.",
  },
  "risk|risk-grid": {
    role: "Portfolio Risk Analyst for real estate investment and development",
    focus: "Analyze the 6-dimension composite risk score: low demand, oversupply, slow velocity, pricing mismatch, low lead quality, and market cooling. Identify the top 2 risk drivers and recommend specific mitigation actions.",
  },
  "risk|competitors": {
    role: "Competitive Intelligence Analyst for Tunisian real estate",
    focus: "Analyze competitor pressure from Tecnocasa, Century 21, RE/MAX, and independent agencies. Identify catchment overlap and market share threats. Recommend differentiation and positioning strategies.",
  },
  "risk|oversupply": {
    role: "Supply-Demand Balance Analyst for real estate markets",
    focus: "Analyze supply/demand ratios and new pipeline inventory. Identify zones approaching saturation. Recommend launch timing adjustments and pricing protections to avoid oversupply traps.",
  },
  "risk|infrastructure": {
    role: "Infrastructure Risk & Urban Development Analyst",
    focus: "Analyze infrastructure risks (flooding, seismic, construction disruption, coastal erosion). Assess impact on property values and accessibility. Recommend risk-adjusted pricing and timeline adjustments.",
  },
};

const DEFAULT_PROMPT = {
  role: "Senior Real Estate Market Intelligence Advisor for Tunisia",
  focus: "Provide a comprehensive analysis of this zone or project, covering pricing, demand, risk, and competitive dynamics. Recommend specific, actionable next steps.",
};

const CATEGORY_SCHEMAS = {
  marketing: `{
  "Verdict": "A 2-sentence executive summary of the marketing or pricing opportunity. Connect the numbers to the strategy.",
  "Campaign Strategy": "Specific, actionable recommendation for digital marketing channels (Meta, Google, broker) targeting the right buyers.",
  "Budget Reallocation": "Where to shift ad spend geographically based on lead density and catchment gaps.",
  "Lead Quality Warning": "A caution regarding lead conversion rates, competitor noise, or audience targeting issues."
}`,
  forecast: `{
  "Verdict": "A 2-sentence executive summary of the demand index and velocity trends. Are we accelerating or cooling?",
  "Absorption Forecast": "Predicted time-to-sell for remaining inventory based on current sales velocity and lead volume.",
  "Launch Timing": "When to release new units or start pre-sales phases, grounded in the demand and price momentum data.",
  "Pricing Adjustment": "Specific pricing changes (e.g., +5% or defensive holds) referencing competitor pricing or MoM trends."
}`,
  risk: `{
  "Verdict": "A 2-sentence executive summary of the overall 6-dimension risk score and its primary drivers.",
  "Critical Vulnerability": "The main risk driver in this zone (e.g., oversupply, slow sales, low lead quality, or infrastructure).",
  "Competitor Threat": "How competitor agencies (Tecnocasa, Century 21, etc.) are positioned in the catchment and the threat they pose.",
  "Mitigation Playbook": "Specific operational, pricing, or product steps the developer must take to minimize financial exposure."
}`
};

export async function POST(request) {
  try {
    const body = await request.json();
    const { context, activeCategory, activeLayer, zoneMetrics, competitors } = body;

    // Parse the context data
    let contextData;
    try {
      contextData = typeof context === "string" ? JSON.parse(context) : context;
    } catch {
      contextData = { raw: context };
    }

    // Get the sector-specific prompt
    const promptKey = `${activeCategory || "marketing"}|${activeLayer || "zone-pricing"}`;
    const sectorPrompt = SECTOR_PROMPTS[promptKey] || DEFAULT_PROMPT;

    // Build rich context with all available data
    const enrichedContext = buildEnrichedContext(contextData, zoneMetrics, competitors, activeCategory, activeLayer);

    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        response_format: { type: "json_object" },
        messages: [
          {
            role: "system",
            content: `You are a ${sectorPrompt.role}, powering TerraLens AI — a map-first decision intelligence platform for real estate developers and marketing agencies in Tunisia.

YOUR EXPERTISE: ${sectorPrompt.focus}

CONTEXT: The user is viewing the "${activeLayer}" layer under the "${activeCategory}" category. They clicked on a specific zone or project to get your expert analysis.

DATA FOUNDATION:
- Population data: INS RGPH 2024 Census (November 2024)
- Price data: Mubawab.tn 2025 market reports
- Agency data: 65+ tracked agencies (Tecnocasa, Century 21, RE/MAX, independents)
- Risk models: 6-dimension composite scoring (XGBoost + Isolation Forest)

You MUST output a strict JSON object with EXACTLY these keys:
${CATEGORY_SCHEMAS[activeCategory || "marketing"] || CATEGORY_SCHEMAS.marketing}

RULES:
- Be as specific as a consultant briefing an agency director. No vague advice.
- Reference actual numbers from the data (prices, scores, rates, agency counts).
- Mention competitor dynamics when relevant (Tecnocasa, Century 21, RE/MAX presence).
- Your advice should be immediately actionable — the user should know exactly what to do Monday morning.
- Always respond in English.`,
          },
          {
            role: "user",
            content: `Analyze this zone/project and provide your expert ${sectorPrompt.role.toLowerCase()} recommendation:\n\n${enrichedContext}`,
          },
        ],
        temperature: 0.25,
        max_tokens: 600,
      }),
    });

    if (!response.ok) {
      throw new Error(`Groq API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || "{}";

    let parsedRecommendation;
    try {
      parsedRecommendation = JSON.parse(content);
    } catch (e) {
      console.error("Failed to parse Groq response as JSON:", content);
      parsedRecommendation = getFallback(activeCategory);
    }

    return NextResponse.json({ recommendation: parsedRecommendation });
  } catch (error) {
    console.error("AI recommendation error:", error);
    return NextResponse.json({ recommendation: getFallback(request.json?.activeCategory || "marketing") });
  }
}

function getFallback(category) {
  if (category === "forecast") {
    return {
      Verdict: "Demand remains robust, creating an opportunity for accelerated sales.",
      "Absorption Forecast": "Current inventory should absorb within 18-24 weeks at current velocity.",
      "Launch Timing": "Optimal window for next phase launch is early Q3.",
      "Pricing Adjustment": "Market supports a 3% price bump; hold firm against discounts."
    };
  } else if (category === "risk") {
    return {
      Verdict: "Zone shows manageable risk with some vulnerability to competitor saturation.",
      "Critical Vulnerability": "Slight oversupply building up due to new launches in adjacent areas.",
      "Competitor Threat": "Strong competitor agency presence demands differentiated product marketing.",
      "Mitigation Playbook": "Shift focus to highly qualified leads and offer flexible payment structures."
    };
  }
  return {
    Verdict: "Based on current market indicators, this zone shows mixed signals requiring careful positioning.",
    "Campaign Strategy": "Increase digital advertising budget targeting high-demand adjacent zones.",
    "Budget Reallocation": "Shift spend away from underperforming postal codes into proven catchment areas.",
    "Lead Quality Warning": "Monitor competitor activity closely — low qualified lead rates indicate poor targeting."
  };
}

function buildEnrichedContext(data, zoneMetrics, competitors, category, layer) {
  const lines = [];

  // Zone/Project identification
  const name = data.name || data.project_name || data.NAME_1 || data.shapeName || "Selected Area";
  const sourceType = data.sourceType || "project";
  lines.push(`=== ${sourceType.toUpperCase()}: ${name} ===`);
  lines.push(`Active View: ${category} > ${layer}`);
  lines.push("");

  // Core metrics
  lines.push("── CORE METRICS ──");
  if (data.avg_price_sqm || data.avg_price) {
    lines.push(`Price: ${(data.avg_price_sqm || data.avg_price || 0).toLocaleString()} ${data.avg_price_sqm ? "DT/m²" : "DT"}`);
  }
  if (data.price_per_sqm) lines.push(`Price per m²: ${data.price_per_sqm} DT/m²`);
  if (data.demand_score !== undefined) lines.push(`Demand Score: ${data.demand_score}/100`);
  if (data.risk_score !== undefined) lines.push(`Risk Score: ${data.risk_score}/100`);
  if (data.velocity !== undefined) lines.push(`Sales Velocity: ${data.velocity}%`);
  if (data.absorption_weeks) lines.push(`Absorption Horizon: ${data.absorption_weeks} weeks`);
  if (data.infrastructure_score) lines.push(`Infrastructure Score: ${data.infrastructure_score}/100`);

  // Location & demographics
  lines.push("");
  lines.push("── LOCATION & DEMOGRAPHICS ──");
  if (data.governorate) lines.push(`Governorate: ${data.governorate}`);
  if (data.city) lines.push(`City: ${data.city}`);
  if (data.neighborhood || data.delegation) lines.push(`Neighborhood: ${data.neighborhood || data.delegation}`);
  if (data.population) lines.push(`Population: ${Number(data.population).toLocaleString()} (INS 2024)`);
  if (data.density) lines.push(`Density: ${data.density} people/km²`);
  if (data.urbanization_pct) lines.push(`Urbanization: ${data.urbanization_pct}%`);
  if (data.unemployment_pct) lines.push(`Unemployment: ${data.unemployment_pct}%`);

  // Commercial metrics
  if (data.leads || data.qualified_leads || data.ad_spend) {
    lines.push("");
    lines.push("── COMMERCIAL PERFORMANCE ──");
    if (data.ad_spend) lines.push(`Ad Spend: ${Number(data.ad_spend).toLocaleString()} DT`);
    if (data.leads) lines.push(`Total Leads: ${data.leads}`);
    if (data.qualified_leads) lines.push(`Qualified Leads: ${data.qualified_leads}`);
    if (data.qualified_lead_rate) lines.push(`Qualified Rate: ${data.qualified_lead_rate}%`);
    if (data.visits) lines.push(`Site Visits: ${data.visits}`);
    if (data.reservations) lines.push(`Reservations: ${data.reservations}`);
    if (data.visit_to_reservation_rate) lines.push(`Visit-to-Reservation: ${data.visit_to_reservation_rate}%`);
    if (data.sales) lines.push(`Sales: ${data.sales}`);
    if (data.unsold_inventory) lines.push(`Unsold Inventory: ${data.unsold_inventory} units`);
    if (data.cost_per_lead) lines.push(`Cost Per Lead: ${data.cost_per_lead} DT`);
    if (data.cost_per_qualified_lead) lines.push(`Cost Per Qualified Lead: ${data.cost_per_qualified_lead} DT`);
  }

  // Price context
  lines.push("");
  lines.push("── PRICE CONTEXT ──");
  if (data.price_tier) lines.push(`Price Tier: ${data.price_tier}`);
  if (data.mom_price_change_pct !== undefined) lines.push(`Month-over-Month Change: ${data.mom_price_change_pct}%`);
  if (data.yoy_price_change_pct || data.yoy_growth_pct || data.growth_pct) {
    lines.push(`Year-over-Year Growth: ${data.yoy_price_change_pct || data.yoy_growth_pct || data.growth_pct}%`);
  }

  // Risk details
  if (data.flood_risk || data.seismic_risk) {
    lines.push("");
    lines.push("── RISK FACTORS ──");
    if (data.flood_risk) lines.push(`Flood Risk: ${data.flood_risk}`);
    if (data.seismic_risk) lines.push(`Seismic Risk: ${data.seismic_risk}`);
  }

  // Competitor landscape
  if (data.competitors_in_zone || data.total_agencies) {
    lines.push("");
    lines.push("── COMPETITIVE LANDSCAPE ──");
    lines.push(`Total Agencies in Zone: ${data.competitors_in_zone || data.total_agencies || "N/A"}`);
    if (data.agency_brands && typeof data.agency_brands === "object") {
      for (const [brand, count] of Object.entries(data.agency_brands)) {
        lines.push(`  ${brand}: ${count} office(s)`);
      }
    }
  }

  // Zone-level metrics if provided separately
  if (zoneMetrics && Array.isArray(zoneMetrics)) {
    const govName = data.governorate || data.name;
    const zoneMatch = zoneMetrics.find(z => z.governorate === govName);
    if (zoneMatch) {
      lines.push("");
      lines.push("── ZONE BENCHMARK (governorate level) ──");
      lines.push(`Zone Avg Price: ${zoneMatch.avg_price_sqm} DT/m²`);
      lines.push(`Zone Demand: ${zoneMatch.demand_score}/100`);
      lines.push(`Zone Risk: ${zoneMatch.risk_score}/100`);
      lines.push(`Zone Lead Volume: ${zoneMatch.lead_count}`);
      if (zoneMatch.total_agencies) lines.push(`Total Agencies: ${zoneMatch.total_agencies}`);
    }
  }

  // Nearby competitors if provided
  if (competitors && Array.isArray(competitors)) {
    const govName = data.governorate || data.city || data.name;
    const nearbyCompetitors = competitors
      .filter(c => c.governorate === govName || c.city === (data.city || govName))
      .slice(0, 5);
    if (nearbyCompetitors.length > 0) {
      lines.push("");
      lines.push("── NEARBY COMPETITORS ──");
      for (const c of nearbyCompetitors) {
        lines.push(`  ${c.project_name} (${c.brand}) — ${c.neighborhood}, ${c.active_listings} active listings`);
      }
    }
  }

  return lines.join("\n");
}
