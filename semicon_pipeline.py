from dagster import asset, Definitions, get_dagster_logger
import duckdb
from datetime import datetime

logger = get_dagster_logger()

@asset
def live_threat_scan():
    """Simulates or fetches the 2-hour SITREP threat data."""
    logger.info("Scanning global feeds for emerging threats...")
    
    return {
        "threat_level": "ELEVATED",
        "headline": "Supply Chain Reroute: Taiwan Strait Friction",
        "summary": "Maritime traffic adjustments observed affecting OSAT logistics out of Taipei.",
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@asset
def inject_to_local_db(live_threat_scan):
    """Pushes the scanned threat into a secure local DuckDB database."""
    logger.info("Connecting to Local Secure Database...")
    
    # Connects to a local file on your Mac instead of the cloud!
    con = duckdb.connect('local_intel.duckdb')
    
    # Create the table if it doesn't exist yet
    con.execute("""
    CREATE TABLE IF NOT EXISTS live_threats (
        threat_level VARCHAR,
        headline VARCHAR,
        summary VARCHAR,
        detected_at VARCHAR
    );
    """)
    
    logger.info("Injecting threat data into local tables...")
    query = f"""
    INSERT INTO live_threats (threat_level, headline, summary, detected_at)
    VALUES (
        '{live_threat_scan['threat_level']}',
        '{live_threat_scan['headline']}',
        '{live_threat_scan['summary']}',
        '{live_threat_scan['detected_at']}'
    );
    """
    con.execute(query)
    
    # Read the data back out to prove it worked!
    result = con.execute("SELECT headline FROM live_threats").fetchall()
    logger.info(f"✅ Successfully wrote intelligence! Current database records: {result}")
    
    con.close()
    return "Local Injection Complete"

defs = Definitions(
    assets=[live_threat_scan, inject_to_local_db],
)