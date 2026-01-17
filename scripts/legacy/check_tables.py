#!/usr/bin/env python3
"""List tables in the given SQLite database (default: data/crypto_prices.db)."""
import argparse
import sqlite3
import os


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=os.path.join("data", "crypto_prices.db"))
    return p.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.db):
        print(f"Database not found: {args.db}")
        return
    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    rows = cur.fetchall()
    for r in rows:
        print(r[0])
    conn.close()


if __name__ == '__main__':
    main()
