#!/usr/bin/env python3
"""Apply migration: create `binance_transactions` table if missing."""
import argparse
import sqlite3
import os
import sys


DDL = '''
CREATE TABLE IF NOT EXISTS binance_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    utc_time TEXT,
    account TEXT,
    operation TEXT,
    coin TEXT,
    change REAL,
    remark TEXT,
    price_eur REAL,
    value_eur REAL,
    binance_timestamp INTEGER,
    source TEXT
);
'''


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=os.path.join("data", "crypto_prices.db"))
    p.add_argument("--yes", action="store_true")
    return p.parse_args()


def list_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def main():
    args = parse_args()
    db = args.db
    if not os.path.exists(db):
        print(f"Database not found: {db}")
        sys.exit(2)

    if not args.yes:
        resp = input(f"Apply migration to create 'binance_transactions' in '{db}'? Type YES to confirm: ")
        if resp.strip() != 'YES':
            print('Aborted')
            return

    conn = sqlite3.connect(db)
    try:
        cur = conn.cursor()
        cur.executescript(DDL)
        conn.commit()
        print("Migration applied: 'binance_transactions' ensured.")
        tbls = list_tables(conn)
        print('\nTables in DB:')
        for t in tbls:
            print(t)
    except Exception as e:
        print(f"Error applying migration: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
