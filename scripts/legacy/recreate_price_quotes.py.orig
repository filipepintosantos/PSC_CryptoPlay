"""
Recreate price_quotes table with DATE-only timestamp.
Creates backup before modification.
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

db_path = 'data/crypto_prices.db'

# Create backup
backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(db_path, backup_path)
print(f"✓ Backup created: {backup_path}")

# Recreate table
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop old table
cursor.execute("DROP TABLE IF EXISTS price_quotes")
print("✓ Old table dropped")

# Create new table with DATE timestamp
cursor.execute("""
    CREATE TABLE price_quotes (
        id INTEGER PRIMARY KEY,
        crypto_id TEXT NOT NULL,
        price_eur REAL NOT NULL,
        timestamp DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(crypto_id, timestamp)
    )
""")
print("✓ New table created with DATE timestamp")

# Recreate index
cursor.execute("""
    CREATE INDEX idx_crypto_timestamp 
    ON price_quotes(crypto_id, timestamp)
""")
print("✓ Index created")

conn.commit()
conn.close()

print("\n✓ Database ready for import!")
print("  - timestamp is now DATE only (YYYY-MM-DD)")
print("  - Run: python scripts\\import_coinmarketcap_csv.py")
