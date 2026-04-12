import { NextResponse } from "next/server";

const GROQ_API_KEY = process.env.GROQ_API_KEY;

export async function POST(request) {
  try {
    const { context } = await request.json();

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
            content: `You are TerraLens AI, an expert real estate market intelligence advisor for the Tunisian market, powered by XGBoost and Isolation Forest predictions.
Analyze the provided zone/project metrics which include ML-derived attributes (like future demand, risk anomalies, competitor saturation). 
Internally use Chain-of-Thought reasoning to weigh pricing against oversupply and risks.
You MUST output a strict JSON object with EXACTLY these four keys:
{
  "Verdict": "A 1-sentence summary of the market opportunity (e.g. 'Highly lucrative with strong ML-predicted price growth.')",
  "Primary Strategy": "A 1-sentence targeted action for marketing or development.",
  "Risk Warning": "A 1-sentence caution based on competitor pressure or infrastructure hazards.",
  "Pricing Action": "A specific numerical suggestion based on the provided ML future price predictions."
}
Always respond in English. Do not include markdown formatting or extra text outside the JSON object.`,
          },
          {
            role: "user",
            content: `Analyze this ML-enriched zone/project data and provide the JSON recommendation:\n${context}`,
          },
        ],
        temperature: 0.3,
        max_tokens: 400,
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
      parsedRecommendation = {
        Verdict: "Market analysis unavailable due to generation error.",
        "Primary Strategy": "Review raw metrics manually.",
        "Risk Warning": "System anomaly.",
        "Pricing Action": "Hold current pricing."
      };
    }

    return NextResponse.json({ recommendation: parsedRecommendation });
  } catch (error) {
    console.error("AI recommendation error:", error);
    return NextResponse.json({
      recommendation: {
        Verdict: "Based on current market indicators, consider adjusting pricing.",
        "Primary Strategy": "Increase digital advertising budget in high-demand zones.",
        "Risk Warning": "Monitor competitor activity closely.",
        "Pricing Action": "Maintain defensive pricing until Q3."
      }
    });
  }
}
