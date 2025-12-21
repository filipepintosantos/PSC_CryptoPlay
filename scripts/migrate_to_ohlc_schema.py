"""
Migration script to update price_quotes table structure for OHLC data.

Changes:
- Renames price_eur column to close_eur
- Adds low_eur column
- Adds high_eur column
- Adds daily_returns column

Author: PSC_CryptoPlay
Date: 2024
"""

import sqlite3
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def migrate_database(db_path: str = 'data/crypto_prices.db'):
    """
    Migrate existing database to OHLC schema.
    
    Args:
        db_path: Path to the SQLite database file
    """
    print(f"Starting migration of {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(price_quotes)")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        if 'close_eur' in columns:
            print("Database already migrated to OHLC schema.")
            return
        
        if 'price_eur' not in columns:
            print("ERROR: price_quotes table doesn't have expected structure!")
            return
        
        print("Creating new price_quotes table with OHLC structure...")
        
        # Create new table with updated schema
        cursor.execute("""
            CREATE TABLE price_quotes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crypto_id INTEGER NOT NULL,
                close_eur REAL NOT NULL,
                low_eur REAL,
                high_eur REAL,
                daily_returns REAL,
                timestamp DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (crypto_id) REFERENCES crypto_info (id),
                UNIQUE(crypto_id, timestamp)
            )
        """)
        
        print("Migrating data from old table...")
        
        # Copy data from old table, using price_eur as close_eur
        cursor.execute("""
            INSERT INTO price_quotes_new (id, crypto_id, close_eur, timestamp, created_at)
            SELECT id, crypto_id, price_eur, timestamp, created_at
            FROM price_quotes
        """)
        
        rows_migrated = cursor.rowcount
        print(f"Migrated {rows_migrated} rows.")
        
        # Calculate daily_returns based on migrated data
        print("Calculating daily returns...")
        
        cursor.execute("""
            SELECT DISTINCT crypto_id FROM price_quotes_new ORDER BY crypto_id
        """)
        crypto_ids = [row[0] for row in cursor.fetchall()]
        
        for crypto_id in crypto_ids:
            # Get all quotes for this crypto, ordered by date
            cursor.execute("""
                SELECT id, close_eur, timestamp
                FROM price_quotes_new
                WHERE crypto_id = ?
                ORDER BY timestamp ASC
            """, (crypto_id,))
            
            quotes = cursor.fetchall()
            
            # Calculate returns for each quote (except first)
            for i in range(1, len(quotes)):
                current_id, current_close, _ = quotes[i]
                _, prev_close, _ = quotes[i-1]
                
                if prev_close > 0:
                    daily_return = ((current_close - prev_close) / prev_close) * 100
                    cursor.execute("""
                        UPDATE price_quotes_new
                        SET daily_returns = ?
                        WHERE id = ?
                    """, (daily_return, current_id))
        
        print(f"Calculated daily returns for {len(crypto_ids)} cryptocurrencies.")
        
        # Drop old table and rename new one
        print("Replacing old table with new structure...")
        cursor.execute("DROP TABLE price_quotes")
        cursor.execute("ALTER TABLE price_quotes_new RENAME TO price_quotes")
        
        # Recreate indexes if they existed
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_quotes_crypto_id 
            ON price_quotes(crypto_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_quotes_timestamp 
            ON price_quotes(timestamp)
        """)
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("Database now supports OHLC data (close_eur, low_eur, high_eur, daily_returns)")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    
    finally:
        conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate price_quotes table to OHLC schema'
    )
    parser.add_argument(
        '--db-path',
        default='data/crypto_prices.db',
        help='Path to the SQLite database file (default: data/crypto_prices.db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print(f"Would migrate database at: {args.db_path}")
        print("Changes:")
        print("  - Rename price_eur → close_eur")
        print("  - Add low_eur column (NULL for existing data)")
        print("  - Add high_eur column (NULL for existing data)")
        print("  - Add daily_returns column (calculated from historical close prices)")
    else:
        migrate_database(args.db_path)
