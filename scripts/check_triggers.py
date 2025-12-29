#!/usr/bin/env python
"""Check and print triggers in a SQLite database file."""

import sqlite3
import sys

def list_triggers(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print('No triggers found')
        return 1
    for name, sql in rows:
        print(f"{name}: {sql}")
    return 0

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/test_schema_triggers.db'
    sys.exit(list_triggers(path))
