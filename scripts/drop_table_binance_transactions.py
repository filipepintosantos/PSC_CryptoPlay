#!/usr/bin/env python3
"""Drop the `binance_transactions` table from the SQLite database.

Usage:
  python scripts/drop_table_binance_transactions.py [--db PATH] [--yes]

By default the database path is `data/crypto_prices.db`.
"""
import argparse
import sqlite3
import sys
import os


def parse_args():
    p = argparse.ArgumentParser(description="Drop binance_transactions table from SQLite DB")
    p.add_argument("--db", default=os.path.join("data", "crypto_prices.db"), help="Path to SQLite database file")
    p.add_argument("--yes", action="store_true", help="Do not prompt for confirmation")
    return p.parse_args()


def table_exists(conn, table_name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cur.fetchone() is not None


def drop_table(conn, table_name: str) -> None:
    cur = conn.cursor()
    cur.execute(f"DROP TABLE {table_name}")
    conn.commit()


def main():
    args = parse_args()
    db_path = args.db

    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        sys.exit(2)

    conn = sqlite3.connect(db_path)

    tbl = "binance_transactions"
    if not table_exists(conn, tbl):
        print(f"Table '{tbl}' does not exist in {db_path}. Nothing to do.")
        conn.close()
        return

    if not args.yes:
        resp = input(f"Are you sure you want to DROP table '{tbl}' from '{db_path}'? Type YES to confirm: ")
        if resp.strip() != "YES":
            print("Aborted by user.")
            conn.close()
            return

    try:
        drop_table(conn, tbl)
        print(f"Table '{tbl}' dropped successfully from {db_path}.")
    except Exception as e:
        print(f"Error dropping table '{tbl}': {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
