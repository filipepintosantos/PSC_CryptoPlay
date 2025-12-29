#!/usr/bin/env python
"""Functional test for last_quote_date triggers and cleanup of test DB files."""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
import glob


def run_trigger_test(db_path: str) -> int:
    print(f"Testing triggers on {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure BTC exists
    cur.execute("SELECT code, last_quote_date FROM crypto_info WHERE code = 'BTC'")
    row = cur.fetchone()
    if not row:
        print("ERROR: BTC not found in crypto_info")
        conn.close()
        return 2

    before = row[1]
    print(f"Before last_quote_date: {before}")

    # Determine a new unique date (max existing + 1 day)
    cur.execute("SELECT MAX(timestamp) FROM price_quotes WHERE crypto_id = ?", ('BTC',))
    max_ts = cur.fetchone()[0]
    if max_ts:
        try:
            max_date = datetime.fromisoformat(max_ts).date()
        except Exception:
            max_date = datetime.today().date()
        new_date = (max_date + timedelta(days=1)).isoformat()
    else:
        new_date = datetime.today().date().isoformat()

    # Insert a new quote (will trigger the AFTER INSERT trigger)
    try:
        cur.execute(
            "INSERT INTO price_quotes (crypto_id, close_eur, timestamp, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            ('BTC', 1.23, new_date),
        )
        conn.commit()
    except Exception as e:
        print(f"ERROR inserting quote: {e}")
        conn.close()
        return 3

    # Read updated last_quote_date
    cur.execute("SELECT last_quote_date FROM crypto_info WHERE code = 'BTC'")
    updated = cur.fetchone()[0]
    conn.close()

    print(f"After last_quote_date: {updated}")
    if updated == new_date:
        print("Trigger updated last_quote_date successfully.")
        return 0
    else:
        print("Trigger did NOT update last_quote_date as expected.")
        return 4


def cleanup_test_dbs(pattern: str = 'data/test*.db') -> int:
    files = glob.glob(pattern)
    if not files:
        print("No test DB files to remove.")
        return 0
    removed = 0
    for f in files:
        try:
            os.remove(f)
            print(f"Removed test DB: {f}")
            removed += 1
        except Exception as e:
            print(f"Failed to remove {f}: {e}")
    return 0 if removed else 2


if __name__ == '__main__':
    db = sys.argv[1] if len(sys.argv) > 1 else 'data/test_schema_triggers.db'
    rc = run_trigger_test(db)
    # Always attempt cleanup of test DBs regardless of rc
    cleanup_test_dbs('data/test*.db')
    sys.exit(rc)
