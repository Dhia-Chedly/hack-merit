import duckdb
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    
    db_path = root / "03_Storage_Raw" / "lakehouse.duckdb"
    curated_data_dir = root / "data" / "curated"
    curated_data_dir.mkdir(parents=True, exist_ok=True)

    legacy_bi_dir = root / "05_BI" / "data"
    legacy_bi_dir.mkdir(parents=True, exist_ok=True)

    output_path = curated_data_dir / "project_metrics.csv"
    legacy_output_path = legacy_bi_dir / "project_metrics.csv"
    
    if not db_path.exists():
        print(f"Error: Database {db_path} not found. Run 02_Ingestion first.")
        return

    print("Connecting to DuckDB Lakehouse for Transformation...")
    conn = duckdb.connect(str(db_path))
    
    # 1. Transform / Clean Logic via SQL
    # Since our raw source is already clean, this simulates a silver/gold transformation 
    # to enforce data quality rules natively in querying:
    query = """
    SELECT 
        project_id,
        project_name,
        city,
        neighborhood,
        latitude,
        longitude,
        property_type,
        quality_tier,
        CAST(launch_date AS DATE) AS launch_date,
        total_units,
        avg_price,
        total_leads,
        qualified_leads,
        qualified_lead_rate,
        visits,
        reservations,
        sales,
        spend,
        cpl,
        cpql,
        lead_to_visit_rate,
        visit_to_reservation_rate,
        reservation_to_sale_rate,
        revenue,
        avg_sale_price,
        GREATEST(0, total_units - sales) AS unsold_inventory,
        sell_through_rate
    FROM raw_projects
    WHERE avg_price > 0 -- Basic Data Quality Check
    """
    
    print("Executing ELT Transformation built on 'raw_projects' dataframe...")
    df = conn.execute(query).df()
    
    # 2. Output curated table and mirror to legacy BI path for backward compatibility.
    df.to_csv(legacy_output_path, index=False)
    df.to_csv(output_path, index=False)
    print(
        "Successfully transformed and exported "
        f"{len(df)} rows to:\n- {output_path}\n- {legacy_output_path}"
    )
    
    conn.close()

if __name__ == "__main__":
    main()
