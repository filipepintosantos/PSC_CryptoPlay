#!/usr/bin/env python3
"""Apply schema version 1.0.0 to all SQLite DBs under data/ by ensuring
`schema_info` exists and contains the correct version value.

Usage: python scripts/apply_schema_version.py [--dir data] [--version 1.0.0]
"""
import sqlite3
import glob
import os
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--dir", default="data", help="Directory with .db files")
parser.add_argument("--version", default="1.0.0", help="Schema version to apply")
args = parser.parse_args()

def apply_version(db_path: str, version: str) -> bool:
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # Ensure schema_info table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_info (
                version TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # If no row exists, insert; else update to new version
        cur.execute("SELECT version FROM schema_info LIMIT 1")
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO schema_info (version) VALUES (?)", (version,))
        else:
            cur.execute("UPDATE schema_info SET version = ?, applied_at = CURRENT_TIMESTAMP", (version,))
        # Also set the numeric PRAGMA user_version derived from the textual version
        try:
            parts = [int(p) for p in version.split('.')]
            # compute numeric as x*10000 + y*100 + z
            while len(parts) < 3:
                parts.append(0)
            numeric = parts[0]*10000 + parts[1]*100 + parts[2]
            cur.execute(f"PRAGMA user_version = {numeric}")
        except Exception:
            # If parsing fails, don't block the update; leave PRAGMA unchanged
            numeric = None
        conn.commit()
        # Read back for verification
        cur.execute("SELECT version, applied_at FROM schema_info LIMIT 1")
        new = cur.fetchone()
        conn.close()
        if numeric is not None:
            print(f"{os.path.basename(db_path)} -> version={new[0]}, applied_at={new[1]}, user_version={numeric}")
        else:
            print(f"{os.path.basename(db_path)} -> version={new[0]}, applied_at={new[1]}")
        return True
    except Exception as e:
        print(f"Failed to update {db_path}: {e}")
        return False

pattern = os.path.join(args.dir, "*.db")
dbs = glob.glob(pattern)
if not dbs:
    print(f"No .db files found in {args.dir}")
else:
    for db in dbs:
        apply_version(db, args.version)
