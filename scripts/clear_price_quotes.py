"""Utility to safely clear the `price_quotes` table.

Usage examples (from project root):

    .\venv\Scripts\python.exe scripts\clear_price_quotes.py --db-path data\crypto_prices.db

Options:
    --db-path   Path to sqlite DB (default: data/crypto_prices.db)
    --no-backup Skip creating an automatic backup (not recommended)
    --vacuum    Run VACUUM after deletion to compact the DB
    --yes       Skip interactive confirmation

The script creates a timestamped backup by default and prints number of deleted rows.
"""

import argparse
import shutil
import os
import sqlite3
from datetime import datetime


def backup_db(db_path: str) -> str:
    dirname = os.path.dirname(db_path) or '.'
    base = os.path.basename(db_path)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak_name = f"{base}.bak.{ts}"
    bak_path = os.path.join(dirname, bak_name)
    shutil.copy2(db_path, bak_path)
    return bak_path


def clear_price_quotes(db_path: str, no_backup: bool = False, vacuum: bool = False) -> None:
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return

    if not no_backup:
        bak = backup_db(db_path)
        print(f"Backup created: {bak}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        cur.execute("SELECT COUNT(*) FROM price_quotes")
        row = cur.fetchone()
        total = row[0] if row else 0
    except sqlite3.OperationalError as e:
        print(f"Error reading table `price_quotes`: {e}")
        conn.close()
        return

    print(f"Found {total} rows in `price_quotes`")

    if total == 0:
        print("No rows to delete.")
        conn.close()
        return

    cur.execute("DELETE FROM price_quotes")
    conn.commit()

    print(f"Deleted {total} rows from `price_quotes`")

    if vacuum:
        print("Running VACUUM to compact database (may take time)...")
        cur.execute("VACUUM")
        conn.commit()
        print("VACUUM complete")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Safely clear the price_quotes table")
    parser.add_argument("--db-path", default="data/crypto_prices.db")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--vacuum", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    if not args.yes:
        confirm = input(f"This will DELETE ALL rows in `{args.db_path}`->`price_quotes`. Continue? [y/N]: ")
        if confirm.lower() not in ("y", "yes"):
            print("Aborted by user")
            return

    clear_price_quotes(args.db_path, no_backup=args.no_backup, vacuum=args.vacuum)


if __name__ == "__main__":
    main()
