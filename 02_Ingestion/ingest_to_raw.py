import duckdb
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    
    source_path = root / "01_Source" / "projects.csv"
    db_path = root / "03_Storage_Raw" / "lakehouse.duckdb"
    
    if not source_path.exists():
        print(f"Error: Source file {source_path} not found.")
        return

    print("Connecting to DuckDB Lakehouse...")
    conn = duckdb.connect(str(db_path))
    
    print(f"Ingesting {source_path.name} into Raw Storage...")
    
    # Drop table if exists to ensure idempotency
    conn.execute("DROP TABLE IF EXISTS raw_projects;")
    
    # Create and load natively using DuckDB's CSV reader
    query = f"""
    CREATE TABLE raw_projects AS 
    SELECT * FROM read_csv_auto('{source_path}', normalize_names=True);
    """
    
    conn.execute(query)
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM raw_projects;").fetchone()[0]
    print(f"Successfully ingested {count} rows into table 'raw_projects'.")
    
    conn.close()

if __name__ == "__main__":
    main()
