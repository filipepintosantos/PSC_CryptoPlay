import os
import sqlite3
import tempfile
import subprocess
import sys
from pathlib import Path


def test_apply_schema_version_sets_user_version_and_schema_info():
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "test_schema.db"

    # create an empty sqlite db
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS dummy(id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    # run the script using the same Python interpreter
    res = subprocess.run([sys.executable, "scripts/apply_schema_version.py", "--dir", tmpdir.name, "--version", "1.0.0"], capture_output=True, text=True)
    assert res.returncode == 0, f"Script failed: {res.stderr}"

    # verify PRAGMA and schema_info
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA user_version")
    user_version = cur.fetchone()[0]
    assert user_version == 10000, f"expected 10000, got {user_version}"

    cur.execute("SELECT version FROM schema_info LIMIT 1")
    row = cur.fetchone()
    assert row is not None and row[0] == "1.0.0"
    conn.close()
    tmpdir.cleanup()
