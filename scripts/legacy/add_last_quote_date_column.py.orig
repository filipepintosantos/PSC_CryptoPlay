"""
Migration script to add last_quote_date column to crypto_info table.
This script adds the new column and populates it with the most recent quote date
for each cryptocurrency from the price_quotes table.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import CryptoDatabase


def add_last_quote_date_column(db_path: str = "data/crypto_prices.db"):
    """
    Add last_quote_date column to crypto_info table and populate it.
    
    Args:
        db_path: Path to the SQLite database
    """
    print(f"Migrating database: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(crypto_info)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'last_quote_date' in columns:
        print("✓ Column 'last_quote_date' already exists in crypto_info table")
    else:
        print("Adding column 'last_quote_date' to crypto_info table...")
        try:
            cursor.execute("""
                ALTER TABLE crypto_info 
                ADD COLUMN last_quote_date DATE DEFAULT NULL
            """)
            conn.commit()
            print("✓ Column added successfully")
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            conn.close()
            return 1
    
    # Populate the column with data from price_quotes
    print("\nPopulating last_quote_date for all cryptocurrencies...")
    cursor.execute("SELECT code FROM crypto_info")
    codes = [row[0] for row in cursor.fetchall()]
    
    updated_count = 0
    for code in codes:
        # Get the most recent quote date for this code
        cursor.execute("""
            SELECT MAX(timestamp) FROM price_quotes
            WHERE crypto_id = ?
        """, (code,))
        
        result = cursor.fetchone()
        last_date = result[0] if result and result[0] else None
        
        if last_date:
            cursor.execute("""
                UPDATE crypto_info 
                SET last_quote_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            """, (last_date, code))
            updated_count += 1
            print(f"  ✓ {code}: {last_date}")
        else:
            print(f"  ⚠ {code}: no quotes found")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'=' * 60}")
    print(f"Migration complete: {updated_count}/{len(codes)} cryptocurrencies updated")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add and populate last_quote_date column in crypto_info table"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/crypto_prices.db",
        help="Path to SQLite database (default: data/crypto_prices.db)"
    )
    
    args = parser.parse_args()
    sys.exit(add_last_quote_date_column(args.db_path))
