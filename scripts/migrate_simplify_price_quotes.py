"""
Migration script to simplify price_quotes table structure.
Removes statistical fields (market_cap, volume, percent_change) keeping only date and price.
Creates backup before migration.
"""

import sqlite3
import shutil
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path for database imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def migrate_price_quotes(db_path: str, backup: bool = True):
    """
    Migrate price_quotes table to simplified structure.
    
    Args:
        db_path: Path to database file
        backup: Whether to create backup before migration
    """
    print(f"Migrating database: {db_path}")
    
    # Create backup if requested
    if backup:
        backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Creating backup: {backup_path}")
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check if old structure exists
        cursor.execute("PRAGMA table_info(price_quotes)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'market_cap_eur' not in columns:
            print("Table already migrated or doesn't need migration.")
            return
        
        print("Migrating price_quotes table...")
        
        # Create new simplified table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_quotes_new (
                id INTEGER PRIMARY KEY,
                crypto_id TEXT NOT NULL,
                price_eur REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(crypto_id, timestamp)
            )
        """)
        
        # Copy essential data from old table
        cursor.execute("""
            INSERT INTO price_quotes_new (id, crypto_id, price_eur, timestamp, created_at)
            SELECT id, crypto_id, price_eur, timestamp, created_at
            FROM price_quotes
        """)
        
        row_count = cursor.rowcount
        print(f"Copied {row_count} rows to new table")
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE price_quotes")
        cursor.execute("ALTER TABLE price_quotes_new RENAME TO price_quotes")
        
        # Recreate index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crypto_timestamp 
            ON price_quotes(crypto_id, timestamp)
        """)
        
        conn.commit()
        print("Migration completed successfully!")
        print(f"Total rows migrated: {row_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate price_quotes table to simplified structure'
    )
    parser.add_argument(
        '--db-path',
        default='data/crypto_prices.db',
        help='Path to database file (default: data/crypto_prices.db)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup before migration'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db_path):
        print(f"Error: Database file not found: {args.db_path}")
        sys.exit(1)
    
    migrate_price_quotes(args.db_path, backup=not args.no_backup)

if __name__ == '__main__':
    main()
