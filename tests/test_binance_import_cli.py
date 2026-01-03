"""Tests for Binance CSV import CLI script."""

import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.import_binance_csv_cli import (
    pick,
    parse_float_scientific,
    timestamp_ms_to_iso,
)


class TestImportBinanceHelpers(unittest.TestCase):
    """Test helper functions for Binance import."""

    def test_pick_first_available(self):
        """Test pick returns first available value."""
        row = {"User ID": "123", "user_id": "456", "other": "789"}
        result = pick(row, "User ID", "user_id")
        self.assertEqual(result, "123")

    def test_pick_second_if_first_empty(self):
        """Test pick returns second value if first is empty."""
        row = {"User ID": "", "user_id": "456"}
        result = pick(row, "User ID", "user_id")
        self.assertEqual(result, "456")

    def test_pick_returns_empty_if_none_found(self):
        """Test pick returns empty string if no values found."""
        row = {"other": "value"}
        result = pick(row, "User ID", "user_id")
        self.assertEqual(result, "")

    def test_parse_float_scientific_normal(self):
        """Test parsing normal float values."""
        self.assertEqual(parse_float_scientific("123.45"), 123.45)
        self.assertEqual(parse_float_scientific("0.001"), 0.001)
        self.assertEqual(parse_float_scientific("-50.0"), -50.0)

    def test_parse_float_scientific_notation(self):
        """Test parsing scientific notation."""
        self.assertEqual(parse_float_scientific("2E-8"), 2e-08)
        self.assertEqual(parse_float_scientific("1.5E-7"), 1.5e-07)
        self.assertEqual(parse_float_scientific("3.14E+2"), 314.0)

    def test_parse_float_scientific_edge_cases(self):
        """Test parsing edge cases."""
        self.assertEqual(parse_float_scientific(""), 0.0)
        self.assertEqual(parse_float_scientific("   "), 0.0)
        self.assertEqual(parse_float_scientific("invalid"), 0.0)
        self.assertEqual(parse_float_scientific("0"), 0.0)

    def test_timestamp_ms_to_iso_valid(self):
        """Test timestamp conversion with valid values."""
        # 2023-01-03 09:00:00 UTC
        ts = 1672736400000
        result = timestamp_ms_to_iso(ts)
        self.assertIn("2023-01-03", result)
        self.assertIn("09:00:00", result)
        self.assertIn("+00:00", result)

    def test_timestamp_ms_to_iso_zero(self):
        """Test timestamp conversion with zero."""
        result = timestamp_ms_to_iso(0)
        self.assertEqual(result, "")

    def test_timestamp_ms_to_iso_none(self):
        """Test timestamp conversion with None."""
        result = timestamp_ms_to_iso(None)
        self.assertEqual(result, "")

    def test_timestamp_ms_to_iso_epoch(self):
        """Test timestamp conversion at Unix epoch."""
        ts = 1000  # 1970-01-01 00:00:01 UTC
        result = timestamp_ms_to_iso(ts)
        self.assertIn("1970-01-01", result)


class TestBinanceImportIntegration(unittest.TestCase):
    """Integration tests for Binance CSV import."""

    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_path = Path(self.temp_db.name)
        self.temp_db.close()

        # Create database schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE binance_transactions (
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
                binance_timestamp TEXT,
                source TEXT
            )
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up test database."""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_database_schema_created(self):
        """Test that database schema is correctly created."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='binance_transactions'")
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "binance_transactions")

    def test_database_columns(self):
        """Test that all expected columns exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(binance_transactions)")
        columns = cursor.fetchall()
        conn.close()

        column_names = [col[1] for col in columns]
        expected_columns = [
            "id", "user_id", "utc_time", "account", "operation",
            "coin", "change", "remark", "price_eur", "value_eur",
            "binance_timestamp", "source"
        ]

        for expected in expected_columns:
            self.assertIn(expected, column_names, f"Column {expected} not found")


if __name__ == "__main__":
    unittest.main()
