#!/usr/bin/env python3
"""Drop binance_transactions table from the given SQLite DB."""
import argparse
import sqlite3
import os
import sys


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=os.path.join("data", "crypto_prices.db"))
    return p.parse_args()


def main():
    args = parse_args()
    db = args.db
    if not os.path.exists(db):
        print(f"Database not found: {db}")
        sys.exit(2)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS binance_transactions")
    conn.commit()
    print("Dropped table 'binance_transactions' (if existed)")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for r in cur.fetchall():
        print(r[0])
    conn.close()


if __name__ == '__main__':
    main()
