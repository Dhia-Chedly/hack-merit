import "./globals.css";

export const metadata = {
  title: "TuniDomicile - Real Estate Intelligence Platform",
  description:
    "Map-first real estate intelligence dashboard for Tunisia. AI-powered market analysis, demand forecasting, and risk assessment.",
  keywords: "real estate, Tunisia, AI, market intelligence, GeoAI, mapping",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      style={{
        "--font-inter": '"Inter", "Segoe UI", system-ui, sans-serif',
        "--font-mono": '"JetBrains Mono", "SFMono-Regular", Consolas, monospace',
      }}
    >
      <body>{children}</body>
    </html>
  );
}
