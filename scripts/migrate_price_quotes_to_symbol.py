"""
Migration script: convert `price_quotes.crypto_id` from INTEGER (cryptocurrencies.id)
to TEXT (cryptocurrency symbol). This script will:

- Create a timestamped backup of the DB file (unless --no-backup)
- Create a new table `price_quotes_new` with `crypto_id TEXT`
- Copy rows from `price_quotes` mapping numeric crypto_id -> symbol via `cryptocurrencies` table
- If no symbol is found for a numeric id, the script stores `ID_<numeric>` as crypto_id and logs a warning
- Replace the old table with the new one and recreate the index

Usage (Windows cmd.exe):

  .\venv\Scripts\python.exe scripts\migrate_price_quotes_to_symbol.py --db-path data\crypto_prices.db

Options:
  --no-backup    : do not create a backup copy (NOT recommended)
  --vacuum       : run VACUUM after migration to reclaim space

Run this locally — do NOT paste your DB here. The script prints progress and warnings.
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import os
from datetime import datetime
from typing import Optional


def backup_db(db_path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.bak.{ts}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def get_crypto_symbol(conn: sqlite3.Connection, numeric_id: int) -> Optional[str]:
    cur = conn.cursor()
    cur.execute("SELECT symbol FROM cryptocurrencies WHERE id = ?", (numeric_id,))
    row = cur.fetchone()
    return row[0] if row else None


def migrate(db_path: str, do_backup: bool = True, vacuum: bool = False):
    if not os.path.exists(db_path):
        raise SystemExit(f"Database not found at: {db_path}")

    if do_backup:
        backup = backup_db(db_path)
        print(f"Backup created: {backup}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Check current column type
    cur.execute("PRAGMA table_info('price_quotes')")
    cols = cur.fetchall()
    crypto_col = None
    for c in cols:
        if c[1] == 'crypto_id':
            crypto_col = c
            break

    if crypto_col is None:
        conn.close()
        raise SystemExit("price_quotes table or crypto_id column not found")

    col_type = (crypto_col[2] or "").upper()
    if 'TEXT' in col_type:
        conn.close()
        print("price_quotes.crypto_id is already TEXT — nothing to do.")
        return

    print("Starting migration: converting price_quotes.crypto_id -> TEXT (symbol)")

    # Create new table
    cur.execute("BEGIN")
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_quotes_new (
                id INTEGER PRIMARY KEY,
                crypto_id TEXT NOT NULL,
                price_eur REAL NOT NULL,
                market_cap_eur REAL,
                volume_24h_eur REAL,
                percent_change_24h REAL,
                percent_change_7d REAL,
                percent_change_30d REAL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Copy rows, mapping numeric id -> symbol
        cur.execute("SELECT id, crypto_id, price_eur, market_cap_eur, volume_24h_eur, percent_change_24h, percent_change_7d, percent_change_30d, timestamp, created_at FROM price_quotes")
        rows = cur.fetchall()
        inserted = 0
        for r in rows:
            old_crypto_id = r['crypto_id']
            symbol = None
            try:
                # Try to interpret as integer id
                numeric = int(old_crypto_id)
                symbol = get_crypto_symbol(conn, numeric)
            except Exception:
                # old value may already be text; use as-is
                symbol = str(old_crypto_id) if old_crypto_id is not None else None

            if not symbol:
                # Preserve original numeric id information
                symbol = f"ID_{old_crypto_id}"
                print(f"WARNING: no symbol found for crypto_id={old_crypto_id}; storing as '{symbol}'")

            cur.execute("""
                INSERT INTO price_quotes_new (crypto_id, price_eur, market_cap_eur, volume_24h_eur, percent_change_24h, percent_change_7d, percent_change_30d, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                r['price_eur'],
                r['market_cap_eur'],
                r['volume_24h_eur'],
                r['percent_change_24h'],
                r['percent_change_7d'],
                r['percent_change_30d'],
                r['timestamp'],
                r['created_at']
            ))
            inserted += 1

        # Drop old table and rename
        cur.execute("DROP TABLE price_quotes")
        cur.execute("ALTER TABLE price_quotes_new RENAME TO price_quotes")

        # Recreate index
        cur.execute("CREATE INDEX IF NOT EXISTS idx_crypto_timestamp ON price_quotes(crypto_id, timestamp)")

        conn.commit()
        print(f"Migration finished: inserted {inserted} rows into new price_quotes table.")

        if vacuum:
            print("Running VACUUM to reclaim space...")
            cur.execute("VACUUM")

    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate price_quotes.crypto_id to store symbol (TEXT)")
    parser.add_argument("--db-path", default="data/crypto_prices.db", help="Path to SQLite DB file")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a backup copy")
    parser.add_argument("--vacuum", action="store_true", help="Run VACUUM after migration")

    args = parser.parse_args()
    migrate(args.db_path, do_backup=not args.no_backup, vacuum=args.vacuum)


if __name__ == '__main__':
    main()
