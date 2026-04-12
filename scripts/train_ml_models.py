import json
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

FRONTEND_DATA_DIR = os.path.join("frontend", "public", "data")
ZONE_METRICS_PATH = os.path.join(FRONTEND_DATA_DIR, "zone_metrics.json")
FORECAST_PATH = os.path.join(FRONTEND_DATA_DIR, "forecast.json")
ML_METRICS_PATH = os.path.join(FRONTEND_DATA_DIR, "ml_metrics.json")

def load_data():
    with open(ZONE_METRICS_PATH, "r") as f:
        zones = json.load(f)
    return zones

def generate_synthetic_historical_data(zones_data):
    """
    Since we don't have 10-year historical real estate data for Tunisia,
    we simulate a high-quality historical dataset based on the INS 2024 baselines
    to train our XGBoost model.
    """
    print("Generating synthetic historical records for ML training...")
    records = []
    
    # Simulate 36 months of history for each of the 24 governorates
    for zone in zones_data:
        base_price = zone.get("avg_price_sqm", 2000.0)
        
        for t in range(-36, 0): # t=0 is present
            # Introduce realistic market noise and macroeconomic cycles
            # Prices inflate slowly, demand fluctuates seasonally
            market_cycle = np.sin(t / 6.0) * 0.05 # 5% macro cycle
            seasonal = np.sin((t % 12) / 12.0 * np.pi) * 0.1 # seasonal peaks in summer
            
            # Historical features
            hist_price = base_price * (1 + (t * 0.005) + market_cycle) # 0.5% monthly inflation historically
            hist_demand = np.clip(zone["demand_score"] + (seasonal * 50) + np.random.normal(0, 5), 10, 100)
            
            records.append({
                "governorate": zone["governorate"],
                "month_num": (t % 12) + 1,
                "population_density": zone["density"],
                "urbanization_pct": zone["urbanization_pct"],
                "unemployment_pct": zone["unemployment_pct"],
                "base_price": hist_price,
                # Target variable 1: Price next month
                "target_future_price": hist_price * (1 + min(max(np.random.normal(0.005, 0.01), -0.05), 0.05)),
                # Target variable 2: Demand next month
                "target_future_demand": hist_demand + np.random.normal(0, 3)
            })
            
    df = pd.DataFrame(records)
    print(f"Generated {len(df)} historical records.")
    return df

def train_xgboost(df):
    """
    Train XGBoost Regressors on the historical data.
    """
    print("Training XGBoost Models for Price and Demand Forecasting...")
    features = ["month_num", "population_density", "urbanization_pct", "unemployment_pct", "base_price"]
    
    X = df[features]
    y_price = df["target_future_price"]
    y_demand = df["target_future_demand"]
    
    # Price Model
    X_train, X_test, yp_train, yp_test = train_test_split(X, y_price, test_size=0.2, random_state=42)
    xgb_price = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    xgb_price.fit(X_train, yp_train)
    r2_price = r2_score(yp_test, xgb_price.predict(X_test))
    
    # Demand Model
    X_train, X_test, yd_train, yd_test = train_test_split(X, y_demand, test_size=0.2, random_state=42)
    xgb_demand = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    xgb_demand.fit(X_train, yd_train)
    r2_demand = r2_score(yd_test, xgb_demand.predict(X_test))
    
    # Feature importances
    price_importances = {features[i]: float(xgb_price.feature_importances_[i]) for i in range(len(features))}
    
    return xgb_price, xgb_demand, r2_price, r2_demand, price_importances, features

def train_isolation_forest(zones_data):
    """
    Use Isolation Forest to detect anomalous "danger zones" based on 
    macro-economic fragility and oversupply signals.
    """
    print("Training Isolation Forest for Risk/Anomaly Detection...")
    df = pd.DataFrame(zones_data)
    
    features = ['density', 'unemployment_pct', 'demand_score', 'avg_price_sqm']
    X = df[features]
    
    # Train Isolation Forest (contamination=0.15 means we expect ~15% of zones to be highly risky anomalies)
    iso = IsolationForest(contamination=0.15, random_state=42)
    df['anomaly_label'] = iso.fit_predict(X) 
    
    # Score samples (lower score = more anomalous)
    # We invert it so higher score = higher risk (0-100 scale)
    anomaly_scores = iso.decision_function(X)
    df['raw_risk'] = -anomaly_scores 
    
    # MinMax Scale to 0-100
    r_min, r_max = df['raw_risk'].min(), df['raw_risk'].max()
    df['ml_risk_score'] = ((df['raw_risk'] - r_min) / (r_max - r_min)) * 100
    
    # Map back to zones
    risk_mapping = df.set_index('governorate')['ml_risk_score'].to_dict()
    anomaly_mapping = df.set_index('governorate')['anomaly_label'].to_dict()
    
    for zone in zones_data:
        zone['risk_score'] = int(risk_mapping[zone['governorate']])
        zone['is_ml_anomaly'] = int(anomaly_mapping[zone['governorate']] == -1)
        
    return zones_data

def generate_forecast(zones_data, xgb_price, xgb_demand, features):
    """
    Generate 15 months of forecast (12 past, 3 future) using the trained XGBoost models.
    """
    print("Generating ML-driven forecast...")
    forecast_data = []
    
    from datetime import datetime
    import calendar
    
    # Start January 2024
    dates = []
    for m in range(1, 13): dates.append(f"2024-{m:02d}")
    for m in range(1, 4): dates.append(f"2025-{m:02d}")
    
    for zone in zones_data:
        current_price = zone.get("avg_price_sqm", 2000.0)
        
        for i, dt_str in enumerate(dates):
            month_num = int(dt_str.split('-')[1])
            is_future = dt_str.startswith('2025')
            
            # Predict
            X_pred = pd.DataFrame([{
                "month_num": month_num,
                "population_density": zone["density"],
                "urbanization_pct": zone["urbanization_pct"],
                "unemployment_pct": zone["unemployment_pct"],
                "base_price": current_price
            }])
            
            p_price = float(xgb_price.predict(X_pred)[0])
            p_demand = float(xgb_demand.predict(X_pred)[0])
            
            # Derive velocity/absorption loosely based on demand vs price
            velocity = int(np.clip((p_demand / 100.0) * (5000 / p_price) * 100, 10, 95))
            absorption = round(104 - velocity, 2)
            
            forecast_data.append({
                "governorate": zone["governorate"],
                "month": dt_str,
                "predicted_price_sqm": int(p_price),
                "demand_index": int(np.clip(p_demand, 10, 99)),
                "velocity_index": velocity,
                "absorption_rate": absorption,
                "is_forecast": is_future
            })
            
            # carry price forward for auto-regressive effect
            current_price = p_price
            
    return forecast_data

def main():
    np.random.seed(42)
    os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)
    
    zones = load_data()
    
    # 1. Generate Historical Data
    df_hist = generate_synthetic_historical_data(zones)
    
    # 2. Train XGBoost Forecast Models
    xgb_price, xgb_demand, r2_price, r2_demand, importances, features = train_xgboost(df_hist)
    
    # 3. Train Isolation Forest Risk Model
    zones = train_isolation_forest(zones)
    
    # 4. Generate ML Forecasts
    forecast_data = generate_forecast(zones, xgb_price, xgb_demand, features)
    
    # 5. Export ML Metrics
    metrics = {
        "models": {
            "price_forecaster": "XGBoost Regressor",
            "demand_forecaster": "XGBoost Regressor",
            "risk_detector": "Isolation Forest"
        },
        "accuracy": {
            "price_r2_score": round(r2_price, 4),
            "demand_r2_score": round(r2_demand, 4)
        },
        "feature_importances": importances,
        "anomalies_detected": sum(1 for z in zones if z.get('is_ml_anomaly', False))
    }
    
    # Save files
    with open(ML_METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
        
    with open(ZONE_METRICS_PATH, "w") as f:
        json.dump(zones, f, indent=2)
        
    with open(FORECAST_PATH, "w") as f:
        json.dump(forecast_data, f, indent=2)
        
    print("ML Training complete.")
    print(f"Price Model R\u00b2: {r2_price:.4f} | Demand Model R\u00b2: {r2_demand:.4f}")
    print(f"Total Anomalies (High Risk Zones): {metrics['anomalies_detected']}")
    
if __name__ == "__main__":
    main()
