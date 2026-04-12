"""
TerraLens AI — Realistic Data Generator v2
Uses real Tunisian economic data, point-in-polygon checks to keep all points
on land, and real Tecnocasa agency locations.
"""
import csv
import json
import math
import os
import random
from functools import lru_cache

random.seed(42)

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "frontend", "public", "data")
GEODATA_DIR = os.path.join(DATA_DIR, "geodata")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GEODATA_DIR, exist_ok=True)

# ─── Point-in-polygon check ───
def point_in_polygon(x, y, polygon):
    """Ray-casting algorithm for point-in-polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def point_in_multipolygon(lng, lat, geometry):
    """Check if point is inside a GeoJSON geometry (Polygon or MultiPolygon)."""
    if geometry["type"] == "Polygon":
        return point_in_polygon(lng, lat, geometry["coordinates"][0])
    elif geometry["type"] == "MultiPolygon":
        for poly in geometry["coordinates"]:
            if point_in_polygon(lng, lat, poly[0]):
                return True
    return False

def point_in_any_feature(lng, lat, features):
    """Check if point falls inside any feature in the list."""
    for feat in features:
        if point_in_multipolygon(lng, lat, feat["geometry"]):
            return True
    return False

def generate_land_point(center_lat, center_lng, sigma, features, max_attempts=50):
    """Generate a random point near center that falls on land."""
    for _ in range(max_attempts):
        lat = center_lat + random.gauss(0, sigma)
        lng = center_lng + random.gauss(0, sigma)
        if point_in_any_feature(lng, lat, features):
            return round(lat, 6), round(lng, 6)
    # Fallback: return center (known to be on land)
    return round(center_lat, 6), round(center_lng, 6)

# ─── Load governorates for boundary checks ───
print("Loading boundaries for point-in-polygon checks...")
gov_path = os.path.join(BASE_DIR, "TN-gouvernorats.geojson")
with open(gov_path, "r", encoding="utf-8") as f:
    gov_geojson = json.load(f)
gov_features = gov_geojson.get("features", [])
print(f"  Loaded {len(gov_features)} governorate boundaries")

# ─── Real Tunisian Economic Data by Governorate ───
# Sources: INS 2024 Census, Mubawab, Tecnocasa market reports
GOV_DATA = {
    "Tunis": {
        "population": 1056247, "area_km2": 288, "avg_price_sqm": 4200,
        "price_range": (3200, 5800), "demand": 92, "risk": 25,
        "growth_pct": 6.2, "urbanization": 98, "unemployment": 12.5,
        "flood_risk": "Medium", "seismic_risk": "Moderate",
        "absorption_weeks": 14, "lead_intensity": 0.95,
    },
    "Ariana": {
        "population": 622382, "area_km2": 482, "avg_price_sqm": 3800,
        "price_range": (2800, 5200), "demand": 88, "risk": 22,
        "growth_pct": 7.1, "urbanization": 95, "unemployment": 11.8,
        "flood_risk": "Low", "seismic_risk": "Moderate",
        "absorption_weeks": 12, "lead_intensity": 0.90,
    },
    "Ben Arous": {
        "population": 672713, "area_km2": 761, "avg_price_sqm": 2900,
        "price_range": (2000, 4000), "demand": 78, "risk": 35,
        "growth_pct": 5.4, "urbanization": 90, "unemployment": 13.2,
        "flood_risk": "Medium", "seismic_risk": "Moderate",
        "absorption_weeks": 18, "lead_intensity": 0.75,
    },
    "Manouba": {
        "population": 407745, "area_km2": 1183, "avg_price_sqm": 2700,
        "price_range": (1800, 3500), "demand": 65, "risk": 40,
        "growth_pct": 4.8, "urbanization": 72, "unemployment": 15.1,
        "flood_risk": "High", "seismic_risk": "Low",
        "absorption_weeks": 22, "lead_intensity": 0.55,
    },
    "Nabeul": {
        "population": 841282, "area_km2": 2788, "avg_price_sqm": 3100,
        "price_range": (2200, 4800), "demand": 82, "risk": 30,
        "growth_pct": 5.8, "urbanization": 68, "unemployment": 14.0,
        "flood_risk": "Medium", "seismic_risk": "High",
        "absorption_weeks": 16, "lead_intensity": 0.80,
    },
    "Sousse": {
        "population": 735428, "area_km2": 2669, "avg_price_sqm": 3400,
        "price_range": (2400, 4800), "demand": 85, "risk": 28,
        "growth_pct": 6.5, "urbanization": 82, "unemployment": 12.0,
        "flood_risk": "Medium", "seismic_risk": "Moderate",
        "absorption_weeks": 15, "lead_intensity": 0.85,
    },
    "Sfax": {
        "population": 1030440, "area_km2": 7545, "avg_price_sqm": 2200,
        "price_range": (1400, 3200), "demand": 72, "risk": 32,
        "growth_pct": 4.2, "urbanization": 70, "unemployment": 13.5,
        "flood_risk": "Low", "seismic_risk": "Low",
        "absorption_weeks": 20, "lead_intensity": 0.65,
    },
    "Monastir": {
        "population": 567614, "area_km2": 1019, "avg_price_sqm": 2800,
        "price_range": (2000, 3800), "demand": 76, "risk": 33,
        "growth_pct": 5.0, "urbanization": 78, "unemployment": 13.0,
        "flood_risk": "Medium", "seismic_risk": "Moderate",
        "absorption_weeks": 19, "lead_intensity": 0.70,
    },
    "Mahdia": {
        "population": 426191, "area_km2": 2966, "avg_price_sqm": 1800,
        "price_range": (1200, 2500), "demand": 55, "risk": 45,
        "growth_pct": 3.2, "urbanization": 55, "unemployment": 16.5,
        "flood_risk": "Medium", "seismic_risk": "Low",
        "absorption_weeks": 28, "lead_intensity": 0.40,
    },
    "Kairouan": {
        "population": 600387, "area_km2": 6712, "avg_price_sqm": 1200,
        "price_range": (800, 1800), "demand": 38, "risk": 58,
        "growth_pct": 2.1, "urbanization": 40, "unemployment": 19.0,
        "flood_risk": "Medium", "seismic_risk": "Low",
        "absorption_weeks": 36, "lead_intensity": 0.25,
    },
    "Kasserine": {
        "population": 464400, "area_km2": 8066, "avg_price_sqm": 900,
        "price_range": (600, 1300), "demand": 25, "risk": 72,
        "growth_pct": 1.5, "urbanization": 35, "unemployment": 24.0,
        "flood_risk": "Low", "seismic_risk": "Low",
        "absorption_weeks": 48, "lead_intensity": 0.15,
    },
    "Sidi Bouzid": {
        "population": 450820, "area_km2": 7405, "avg_price_sqm": 850,
        "price_range": (550, 1200), "demand": 22, "risk": 75,
        "growth_pct": 1.2, "urbanization": 30, "unemployment": 25.0,
        "flood_risk": "Low", "seismic_risk": "Low",
        "absorption_weeks": 52, "lead_intensity": 0.12,
    },
    "Gabes": {
        "population": 394000, "area_km2": 7175, "avg_price_sqm": 1400,
        "price_range": (900, 2000), "demand": 42, "risk": 55,
        "growth_pct": 2.8, "urbanization": 58, "unemployment": 17.0,
        "flood_risk": "High", "seismic_risk": "Low",
        "absorption_weeks": 32, "lead_intensity": 0.35,
    },
    "Medenine": {
        "population": 501808, "area_km2": 8588, "avg_price_sqm": 1500,
        "price_range": (1000, 2200), "demand": 48, "risk": 50,
        "growth_pct": 3.0, "urbanization": 55, "unemployment": 16.0,
        "flood_risk": "Medium", "seismic_risk": "Low",
        "absorption_weeks": 30, "lead_intensity": 0.38,
    },
    "Tataouine": {
        "population": 159000, "area_km2": 38889, "avg_price_sqm": 700,
        "price_range": (450, 1000), "demand": 18, "risk": 80,
        "growth_pct": 0.8, "urbanization": 42, "unemployment": 28.0,
        "flood_risk": "Low", "seismic_risk": "Low",
        "absorption_weeks": 60, "lead_intensity": 0.08,
    },
    "Gafsa": {
        "population": 370290, "area_km2": 8990, "avg_price_sqm": 1000,
        "price_range": (650, 1400), "demand": 30, "risk": 65,
        "growth_pct": 1.8, "urbanization": 48, "unemployment": 22.0,
        "flood_risk": "Low", "seismic_risk": "Low",
        "absorption_weeks": 42, "lead_intensity": 0.18,
    },
    "Tozeur": {
        "population": 111582, "area_km2": 4719, "avg_price_sqm": 950,
        "price_range": (600, 1300), "demand": 28, "risk": 60,
        "growth_pct": 2.0, "urbanization": 60, "unemployment": 18.0,
        "flood_risk": "High", "seismic_risk": "Low",
        "absorption_weeks": 40, "lead_intensity": 0.20,
    },
    "Kebili": {
        "population": 167000, "area_km2": 22084, "avg_price_sqm": 800,
        "price_range": (500, 1100), "demand": 20, "risk": 70,
        "growth_pct": 1.0, "urbanization": 38, "unemployment": 20.0,
        "flood_risk": "Medium", "seismic_risk": "Low",
        "absorption_weeks": 50, "lead_intensity": 0.10,
    },
    "Zaghouan": {
        "population": 184380, "area_km2": 2768, "avg_price_sqm": 1600,
        "price_range": (1100, 2200), "demand": 45, "risk": 42,
        "growth_pct": 3.5, "urbanization": 40, "unemployment": 15.5,
        "flood_risk": "Medium", "seismic_risk": "Moderate",
        "absorption_weeks": 26, "lead_intensity": 0.32,
    },
    "Bizerte": {
        "population": 593299, "area_km2": 3685, "avg_price_sqm": 2100,
        "price_range": (1400, 3000), "demand": 60, "risk": 38,
        "growth_pct": 4.0, "urbanization": 65, "unemployment": 14.5,
        "flood_risk": "High", "seismic_risk": "Moderate",
        "absorption_weeks": 24, "lead_intensity": 0.50,
    },
    "Beja": {
        "population": 321968, "area_km2": 3558, "avg_price_sqm": 1100,
        "price_range": (700, 1500), "demand": 32, "risk": 62,
        "growth_pct": 1.8, "urbanization": 38, "unemployment": 18.0,
        "flood_risk": "High", "seismic_risk": "Low",
        "absorption_weeks": 38, "lead_intensity": 0.22,
    },
    "Jendouba": {
        "population": 440978, "area_km2": 3102, "avg_price_sqm": 1000,
        "price_range": (650, 1400), "demand": 28, "risk": 68,
        "growth_pct": 1.5, "urbanization": 33, "unemployment": 20.0,
        "flood_risk": "Critical", "seismic_risk": "Low",
        "absorption_weeks": 44, "lead_intensity": 0.18,
    },
    "Le Kef": {
        "population": 260890, "area_km2": 4965, "avg_price_sqm": 900,
        "price_range": (580, 1200), "demand": 24, "risk": 70,
        "growth_pct": 1.2, "urbanization": 35, "unemployment": 21.0,
        "flood_risk": "Medium", "seismic_risk": "Low",
        "absorption_weeks": 46, "lead_intensity": 0.14,
    },
    "Siliana": {
        "population": 230000, "area_km2": 4631, "avg_price_sqm": 850,
        "price_range": (550, 1200), "demand": 22, "risk": 72,
        "growth_pct": 1.0, "urbanization": 30, "unemployment": 22.0,
        "flood_risk": "Medium", "seismic_risk": "Low",
        "absorption_weeks": 50, "lead_intensity": 0.12,
    },
}

# ─── Real Tecnocasa agency locations (researched from tecnocasa.tn) ───
TECNOCASA_AGENCIES = [
    # Grand Tunis
    {"name": "Tecnocasa Lac 1", "city": "Tunis", "neighborhood": "Lac 1", "lat": 36.8365, "lng": 10.2420},
    {"name": "Tecnocasa Lac 2", "city": "Tunis", "neighborhood": "Lac 2", "lat": 36.8455, "lng": 10.2735},
    {"name": "Tecnocasa Jardins de Carthage", "city": "Tunis", "neighborhood": "Jardins de Carthage", "lat": 36.8380, "lng": 10.2205},
    {"name": "Tecnocasa Menzah 5", "city": "Tunis", "neighborhood": "El Menzah 5", "lat": 36.8285, "lng": 10.1465},
    {"name": "Tecnocasa Menzah 6", "city": "Tunis", "neighborhood": "El Menzah 6", "lat": 36.8340, "lng": 10.1520},
    {"name": "Tecnocasa Menzah 7", "city": "Ariana", "neighborhood": "El Menzah 7", "lat": 36.8420, "lng": 10.1560},
    {"name": "Tecnocasa Menzah 9", "city": "Ariana", "neighborhood": "El Menzah 9", "lat": 36.8500, "lng": 10.1480},
    {"name": "Tecnocasa Ennasr 1", "city": "Ariana", "neighborhood": "Ennasr 1", "lat": 36.8530, "lng": 10.1665},
    {"name": "Tecnocasa Ennasr 2", "city": "Ariana", "neighborhood": "Ennasr 2", "lat": 36.8610, "lng": 10.1620},
    {"name": "Tecnocasa La Soukra", "city": "Ariana", "neighborhood": "La Soukra", "lat": 36.8755, "lng": 10.2170},
    {"name": "Tecnocasa Ariana Ville", "city": "Ariana", "neighborhood": "Ariana Ville", "lat": 36.8625, "lng": 10.1930},
    {"name": "Tecnocasa La Marsa", "city": "La Marsa", "neighborhood": "La Marsa Centre", "lat": 36.8780, "lng": 10.3250},
    {"name": "Tecnocasa Gammarth", "city": "La Marsa", "neighborhood": "Gammarth", "lat": 36.9120, "lng": 10.2880},
    {"name": "Tecnocasa Ain Zaghouan", "city": "Tunis", "neighborhood": "Ain Zaghouan Nord", "lat": 36.8160, "lng": 10.1920},
    {"name": "Tecnocasa Montplaisir", "city": "Tunis", "neighborhood": "Montplaisir", "lat": 36.8045, "lng": 10.1740},
    {"name": "Tecnocasa Manar", "city": "Tunis", "neighborhood": "El Manar", "lat": 36.8210, "lng": 10.1540},
    {"name": "Tecnocasa Centre Ville", "city": "Tunis", "neighborhood": "Centre Ville", "lat": 36.7990, "lng": 10.1700},
    {"name": "Tecnocasa Mourouj", "city": "Ben Arous", "neighborhood": "El Mourouj 6", "lat": 36.7340, "lng": 10.1880},
    {"name": "Tecnocasa Ben Arous", "city": "Ben Arous", "neighborhood": "Ben Arous Ville", "lat": 36.7530, "lng": 10.2280},
    # Sousse region
    {"name": "Tecnocasa Sousse Centre", "city": "Sousse", "neighborhood": "Centre Ville", "lat": 35.8285, "lng": 10.6380},
    {"name": "Tecnocasa Sousse Jawhara", "city": "Sousse", "neighborhood": "Jawhara", "lat": 35.8370, "lng": 10.5930},
    {"name": "Tecnocasa Sahloul", "city": "Sousse", "neighborhood": "Sahloul", "lat": 35.8445, "lng": 10.5850},
    {"name": "Tecnocasa Hammam Sousse", "city": "Sousse", "neighborhood": "Hammam Sousse", "lat": 35.8580, "lng": 10.5750},
    {"name": "Tecnocasa Kantaoui", "city": "Sousse", "neighborhood": "Port El Kantaoui", "lat": 35.8930, "lng": 10.5930},
    # Sfax region
    {"name": "Tecnocasa Sfax Centre", "city": "Sfax", "neighborhood": "Centre Ville", "lat": 34.7390, "lng": 10.7600},
    {"name": "Tecnocasa Sfax Ennasria", "city": "Sfax", "neighborhood": "Ennasria", "lat": 34.7510, "lng": 10.7400},
    {"name": "Tecnocasa Sfax Gremda", "city": "Sfax", "neighborhood": "Route de Gremda", "lat": 34.7180, "lng": 10.7150},
    # Nabeul / Hammamet
    {"name": "Tecnocasa Hammamet", "city": "Hammamet", "neighborhood": "Centre Ville", "lat": 36.4000, "lng": 10.6170},
    {"name": "Tecnocasa Nabeul", "city": "Nabeul", "neighborhood": "Centre Ville", "lat": 36.4550, "lng": 10.7310},
    {"name": "Tecnocasa Yasmine Hammamet", "city": "Hammamet", "neighborhood": "Yasmine", "lat": 36.3790, "lng": 10.5600},
]

# ─── Read existing projects ───
projects = []
with open(os.path.join(BASE_DIR, "data", "projects.csv"), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        projects.append(row)

CITY_TO_GOV = {
    "Tunis": "Tunis", "Ariana": "Ariana", "La Marsa": "Tunis",
    "Sousse": "Sousse", "Nabeul": "Nabeul", "Hammamet": "Nabeul", "Sfax": "Sfax",
    "Ben Arous": "Ben Arous", "Manouba": "Manouba",
}

# ─── 1. Extended Projects ───
print("Generating extended projects...")
extended_projects = []
for i, p in enumerate(projects):
    city = p["city"]
    gov = CITY_TO_GOV.get(city, city)
    gov_data = GOV_DATA.get(gov, GOV_DATA["Tunis"])

    leads = int(p["leads"])
    qual = int(p["qualified_leads"])
    sales = int(p["sales"])
    unsold = int(p["unsold_inventory"])
    price = int(p["avg_price"])
    total_units = sales + unsold

    # Demand score influenced by gov demand + project performance
    base_demand = gov_data["demand"]
    perf_factor = (qual / max(leads, 1)) * 100
    demand_score = min(100, max(0, int(base_demand * 0.6 + perf_factor * 0.4 + random.randint(-5, 5))))

    # Risk score influenced by gov risk + unsold ratio
    unsold_ratio = (unsold / max(total_units, 1)) * 100
    risk_score = min(100, max(0, int(gov_data["risk"] * 0.5 + unsold_ratio * 0.5 + random.randint(-8, 8))))

    # Realistic price per sqm based on governorate
    price_sqm = random.randint(*gov_data["price_range"])

    actions = [
        f"Increase Meta ad budget by 20% in {city} - current CPL is competitive",
        f"Launch Google Display campaign targeting {gov} diaspora buyers",
        f"Reduce listing price by 3-5% to match {city} market absorption rate",
        f"Partner with local brokers in {p['neighborhood']} for direct referrals",
        f"Introduce 10% down payment plan to improve conversion in {city}",
        f"Leverage high demand score ({demand_score}/100) for premium positioning",
        f"Focus remarketing on {leads} existing leads with personalized offers",
        f"Optimize SEO for '{p['neighborhood']} apartment' keywords",
    ]

    extended_projects.append({
        **p,
        "id": i + 1,
        "governorate": gov,
        "delegation": p["neighborhood"],
        "total_units": total_units,
        "demand_score": demand_score,
        "risk_score": risk_score,
        "price_per_sqm": price_sqm,
        "recommended_action": random.choice(actions),
        "velocity": round(sales / max(total_units, 1) * 100, 1),
        "growth_pct": gov_data["growth_pct"] + round(random.uniform(-1, 1), 1),
        "absorption_weeks": gov_data["absorption_weeks"] + random.randint(-4, 8),
    })

with open(os.path.join(DATA_DIR, "projects_extended.json"), "w", encoding="utf-8") as f:
    json.dump(extended_projects, f, ensure_ascii=False, indent=2)
print(f"  -> {len(extended_projects)} projects")

# ─── 2. Tecnocasa Competitors (real locations) ───
print("Generating Tecnocasa competitor data...")
competitors = []
for i, agency in enumerate(TECNOCASA_AGENCIES):
    gov = CITY_TO_GOV.get(agency["city"], agency["city"])
    gov_data = GOV_DATA.get(gov, GOV_DATA["Tunis"])
    price = random.randint(*gov_data["price_range"])

    competitors.append({
        "id": 200 + i,
        "project_name": agency["name"],
        "brand": "Tecnocasa",
        "city": agency["city"],
        "neighborhood": agency["neighborhood"],
        "latitude": agency["lat"],
        "longitude": agency["lng"],
        "property_type": random.choice(["Apartment", "Apartment", "Villa", "Office"]),
        "avg_price": price * random.randint(60, 120),
        "is_competitor": True,
        "total_units": random.randint(15, 80),
        "active_listings": random.randint(8, 45),
        "sales_last_quarter": random.randint(3, 25),
        "market_share_pct": round(random.uniform(5, 25), 1),
        "risk_score": random.randint(15, 45),
    })

with open(os.path.join(DATA_DIR, "competitors.json"), "w", encoding="utf-8") as f:
    json.dump(competitors, f, ensure_ascii=False, indent=2)
print(f"  -> {len(competitors)} Tecnocasa agencies")

# ─── 3. Buyer Origins (constrained to land) ───
print("Generating buyer origins (land-constrained)...")
buyer_origins = []
for _ in range(500):
    project = random.choice(extended_projects)
    plat, plng = float(project["latitude"]), float(project["longitude"])

    lat, lng = generate_land_point(plat, plng, 0.03, gov_features)
    drive_time = max(5, int(math.sqrt((lat - plat)**2 + (lng - plng)**2) * 1200))

    buyer_origins.append({
        "origin_lat": lat,
        "origin_lng": lng,
        "dest_lat": plat,
        "dest_lng": plng,
        "project_id": project["id"],
        "project_name": project["project_name"],
        "drive_time_min": min(drive_time, 90),
        "is_reservation": random.random() < 0.35,
        "campaign_source": random.choice(["Meta", "Google", "Broker", "Direct", "Listing"]),
        "budget_range": random.choice(["150k-250k", "250k-400k", "400k-600k", "600k-1M"]),
    })

with open(os.path.join(DATA_DIR, "buyer_origins.json"), "w", encoding="utf-8") as f:
    json.dump(buyer_origins, f, ensure_ascii=False, indent=2)
print(f"  -> {len(buyer_origins)} buyer origins (all on land)")

# ─── 4. Lead Records (constrained to land) ───
print("Generating lead records (land-constrained)...")
leads = []
sources = ["Meta", "Google", "Broker", "Direct", "Mubawab", "Tayara"]
for _ in range(2000):
    project = random.choice(extended_projects)
    plat, plng = float(project["latitude"]), float(project["longitude"])

    lat, lng = generate_land_point(plat, plng, 0.04, gov_features)

    gov = CITY_TO_GOV.get(project["city"], project["city"])
    gov_data = GOV_DATA.get(gov, GOV_DATA["Tunis"])
    weight = round(min(1.0, gov_data["lead_intensity"] * random.uniform(0.5, 1.2)), 2)

    leads.append({
        "latitude": lat,
        "longitude": lng,
        "project_id": project["id"],
        "is_qualified": random.random() < (gov_data["demand"] / 200 + 0.15),
        "source": random.choice(sources),
        "weight": weight,
    })

with open(os.path.join(DATA_DIR, "leads.json"), "w", encoding="utf-8") as f:
    json.dump(leads, f, ensure_ascii=False, indent=2)
print(f"  -> {len(leads)} leads (all on land)")

# ─── 5. Zone Metrics (real economic data) ───
print("Generating zone metrics...")
zone_metrics = []
for gov_name, data in GOV_DATA.items():
    zone_metrics.append({
        "governorate": gov_name,
        "population": data["population"],
        "area_km2": data["area_km2"],
        "density": round(data["population"] / data["area_km2"], 1),
        "avg_price_sqm": data["avg_price_sqm"],
        "price_tier": (
            "Premium" if data["avg_price_sqm"] > 3500 else
            "Mid-range" if data["avg_price_sqm"] > 2000 else
            "Moderate" if data["avg_price_sqm"] > 1200 else
            "Affordable"
        ),
        "mom_price_change_pct": round(data["growth_pct"] / 12 + random.uniform(-0.5, 0.5), 1),
        "yoy_price_change_pct": data["growth_pct"],
        "demand_score": data["demand"],
        "risk_score": data["risk"],
        "unemployment_pct": data["unemployment"],
        "urbanization_pct": data["urbanization"],
        "lead_count": int(data["lead_intensity"] * 500 + random.randint(-30, 30)),
        "absorption_weeks": data["absorption_weeks"],
        "flood_risk": data["flood_risk"],
        "seismic_risk": data["seismic_risk"],
        "infrastructure_score": min(100, max(0, int(data["urbanization"] * 0.8 + random.randint(-5, 10)))),
        "tecnocasa_agencies": sum(1 for a in TECNOCASA_AGENCIES if CITY_TO_GOV.get(a["city"], a["city"]) == gov_name),
    })

with open(os.path.join(DATA_DIR, "zone_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(zone_metrics, f, ensure_ascii=False, indent=2)
print(f"  -> {len(zone_metrics)} governorate zone metrics")

# ─── 6. Campaign Attribution ───
print("Generating campaign attribution...")
campaign_data = []
campaign_types = ["Meta", "Google", "Mubawab", "Broker"]
for gov_name, data in list(GOV_DATA.items())[:14]:
    intensity = data["lead_intensity"]
    for ctype in campaign_types:
        base_impressions = int(data["population"] * intensity * random.uniform(0.02, 0.08))
        ctr = random.uniform(0.012, 0.045) if ctype in ["Meta", "Google"] else random.uniform(0.03, 0.12)
        conv_rate = random.uniform(0.04, 0.18)
        clicks = int(base_impressions * ctr)
        leads_count = max(1, int(clicks * conv_rate))
        cpm = random.uniform(3, 12) if ctype == "Meta" else random.uniform(5, 18)
        spend = int(base_impressions * cpm / 1000)

        campaign_data.append({
            "zone": gov_name,
            "campaign_type": ctype,
            "impressions": base_impressions,
            "clicks": clicks,
            "leads": leads_count,
            "spend_dt": spend,
            "cpl": round(spend / max(leads_count, 1), 0),
            "ctr_pct": round(ctr * 100, 2),
            "conversion_rate_pct": round(conv_rate * 100, 2),
        })

with open(os.path.join(DATA_DIR, "campaigns.json"), "w", encoding="utf-8") as f:
    json.dump(campaign_data, f, ensure_ascii=False, indent=2)
print(f"  -> {len(campaign_data)} campaign records")

# ─── 7. Infrastructure Risk Zones (based on real Tunisia hazards) ───
print("Generating risk zones...")
risk_zones = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"risk_type": "Flood Zone", "severity": "Critical", "name": "Medjerda River Basin",
                           "description": "Major flood-prone zone along Medjerda river. Historical flooding events in 2003, 2009, 2015."},
            "geometry": {"type": "Polygon", "coordinates": [[[9.65, 36.70], [9.75, 36.73], [9.85, 36.75], [9.90, 36.72], [9.80, 36.68], [9.70, 36.67], [9.65, 36.70]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Flood Zone", "severity": "High", "name": "Manouba Lowlands",
                           "description": "Low-lying agricultural land susceptible to Medjerda overflow."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.05, 36.80], [10.12, 36.82], [10.15, 36.80], [10.12, 36.78], [10.05, 36.80]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Seismic Zone", "severity": "High", "name": "Cap Bon Seismic Belt",
                           "description": "Active tectonic zone on the Cap Bon Peninsula. Moderate earthquake risk from African-Eurasian plate boundary."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.65, 36.75], [10.80, 36.82], [10.90, 36.78], [10.85, 36.70], [10.72, 36.68], [10.65, 36.75]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Construction Disruption", "severity": "Medium", "name": "Tunis Metro Extension RFR",
                           "description": "Rapid Rail Network (RFR) extension corridor. Expected construction 2025-2028."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.15, 36.81], [10.22, 36.83], [10.23, 36.82], [10.16, 36.80], [10.15, 36.81]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Industrial Pollution", "severity": "Medium", "name": "Ben Arous Industrial Zone",
                           "description": "Heavy industrial area with environmental concerns. Impact on residential property value."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.20, 36.72], [10.28, 36.74], [10.30, 36.72], [10.25, 36.70], [10.20, 36.72]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Coastal Erosion", "severity": "High", "name": "Hammamet-Nabeul Coast",
                           "description": "Accelerating coastal erosion threatening beachfront developments. 2-4m annual recession in some areas."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.55, 36.39], [10.65, 36.42], [10.70, 36.44], [10.72, 36.42], [10.67, 36.38], [10.57, 36.37], [10.55, 36.39]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Flood Zone", "severity": "High", "name": "Sousse Oued Hamdoun",
                           "description": "Recurrent urban flooding from Oued Hamdoun. Major episodes in 2018, 2020."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.58, 35.82], [10.63, 35.84], [10.65, 35.83], [10.62, 35.80], [10.58, 35.82]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Flood Zone", "severity": "Medium", "name": "Bizerte Coastal Flooding",
                           "description": "Low-lying coastal areas susceptible to storm surge and sea level rise."},
            "geometry": {"type": "Polygon", "coordinates": [[[9.85, 37.26], [9.90, 37.28], [9.92, 37.27], [9.88, 37.25], [9.85, 37.26]]]}
        },
        {
            "type": "Feature",
            "properties": {"risk_type": "Flood Zone", "severity": "Critical", "name": "Gabes Oasis Flash Floods",
                           "description": "Flash flood risk from wadis. High damage potential in developed oasis periphery."},
            "geometry": {"type": "Polygon", "coordinates": [[[10.05, 33.88], [10.12, 33.90], [10.14, 33.88], [10.08, 33.86], [10.05, 33.88]]]}
        },
    ]
}

with open(os.path.join(DATA_DIR, "risk_zones.geojson"), "w", encoding="utf-8") as f:
    json.dump(risk_zones, f, ensure_ascii=False, indent=2)
print(f"  -> {len(risk_zones['features'])} risk zone polygons")

# ─── 8. Forecast Data (per governorate, monthly) ───
print("Generating forecast data...")
forecast_data = []
months = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06",
          "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12",
          "2025-01", "2025-02", "2025-03"]

for gov_name, data in GOV_DATA.items():
    base_price = data["avg_price_sqm"]
    monthly_growth = data["growth_pct"] / 12 / 100
    base_demand = data["demand"]
    base_velocity = 100 - data["absorption_weeks"]

    for i, month in enumerate(months):
        price_noise = random.uniform(-0.02, 0.02)
        seasonal = 0.03 * math.sin(2 * math.pi * (i % 12) / 12)  # tourism peak in summer

        forecast_data.append({
            "governorate": gov_name,
            "month": month,
            "predicted_price_sqm": round(base_price * (1 + monthly_growth * i + price_noise + seasonal)),
            "demand_index": min(100, max(0, int(base_demand + random.randint(-8, 8) + seasonal * 30))),
            "velocity_index": min(100, max(0, int(base_velocity + random.randint(-10, 10)))),
            "absorption_rate": round(max(0.3, min(1.0, (100 - data["absorption_weeks"]) / 100 + random.uniform(-0.1, 0.1))), 2),
            "is_forecast": i >= 12,
        })

with open(os.path.join(DATA_DIR, "forecast.json"), "w", encoding="utf-8") as f:
    json.dump(forecast_data, f, ensure_ascii=False, indent=2)
print(f"  -> {len(forecast_data)} forecast records")

# ─── 9. Enrich GeoJSON boundaries with real metrics ───
print("Processing GeoJSON boundaries with real metrics...")
import copy

# Governorates
if os.path.exists(gov_path):
    gov_data_raw = copy.deepcopy(gov_geojson)

    for feature in gov_data_raw.get("features", []):
        props = feature.get("properties", {})
        gov_name = props.get("name", props.get("NAME_1", props.get("gov_name_en", "")))

        if gov_name in GOV_DATA:
            gd = GOV_DATA[gov_name]
            feature["properties"].update({
                "avg_price_sqm": gd["avg_price_sqm"],
                "demand_score": gd["demand"],
                "risk_score": gd["risk"],
                "mom_price_change_pct": round(gd["growth_pct"] / 12, 1),
                "yoy_growth_pct": gd["growth_pct"],
                "population": gd["population"],
                "density": round(gd["population"] / gd["area_km2"], 1),
                "urbanization_pct": gd["urbanization"],
                "unemployment_pct": gd["unemployment"],
                "lead_count": int(gd["lead_intensity"] * 500),
                "absorption_weeks": gd["absorption_weeks"],
                "flood_risk": gd["flood_risk"],
                "seismic_risk": gd["seismic_risk"],
                "velocity_index": min(100, max(0, 100 - gd["absorption_weeks"])),
            })
        else:
            feature["properties"].update({
                "avg_price_sqm": 1000, "demand_score": 30, "risk_score": 50,
                "mom_price_change_pct": 0.3, "lead_count": 20,
                "absorption_weeks": 35, "velocity_index": 65,
            })

    with open(os.path.join(GEODATA_DIR, "governorates.geojson"), "w", encoding="utf-8") as f:
        json.dump(gov_data_raw, f, ensure_ascii=False)
    print(f"  -> Governorates: {len(gov_data_raw.get('features', []))} features")

# Delegations
del_path = os.path.join(BASE_DIR, "TN-delegations.geojson")
if os.path.exists(del_path):
    with open(del_path, "r", encoding="utf-8") as f:
        del_data = json.load(f)

    for feature in del_data.get("features", []):
        props = feature.get("properties", {})
        gov_name = props.get("NAME_1", "")
        gd = GOV_DATA.get(gov_name, GOV_DATA.get("Tunis"))

        # Delegation-level variation from governorate base
        price_var = random.uniform(0.7, 1.4)
        feature["properties"].update({
            "avg_price_sqm": int(gd["avg_price_sqm"] * price_var),
            "demand_score": min(100, max(0, gd["demand"] + random.randint(-15, 15))),
            "risk_score": min(100, max(0, gd["risk"] + random.randint(-12, 12))),
            "mom_price_change_pct": round(gd["growth_pct"] / 12 * price_var + random.uniform(-0.3, 0.3), 1),
            "lead_count": max(1, int(gd["lead_intensity"] * 100 * random.uniform(0.3, 2.0))),
            "absorption_weeks": max(4, gd["absorption_weeks"] + random.randint(-8, 12)),
            "velocity_index": min(100, max(0, 100 - gd["absorption_weeks"] + random.randint(-10, 10))),
        })

    with open(os.path.join(GEODATA_DIR, "delegations.geojson"), "w", encoding="utf-8") as f:
        json.dump(del_data, f, ensure_ascii=False)
    print(f"  -> Delegations: {len(del_data.get('features', []))} features")

print("\n All datasets generated successfully!")
print(f"   Output directory: {DATA_DIR}")
