"""
Additional tests for database helper functions added during recent fixes.
"""
import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import CryptoDatabase


class TestDatabaseExtra(unittest.TestCase):
    def setUp(self):
        self.db = CryptoDatabase(":memory:")

    def tearDown(self):
        if self.db:
            self.db.close()

    def test_get_or_create_crypto_info_id(self):
        # Create new crypto_info row
        id1 = self.db.get_or_create_crypto_info_id("TESTCOIN", "Test Coin")
        self.assertIsNotNone(id1)
        # Calling again returns same id
        id2 = self.db.get_or_create_crypto_info_id("TESTCOIN", "Test Coin")
        self.assertEqual(id1, id2)

    def test_insert_or_update_quote_upsert(self):
        # Insert a quote and then upsert with new close price
        base_date = datetime.now()
        quote = {
            "symbol": "UPT",
            "name": "UpsertTest",
            "close_eur": 10.0,
            "timestamp": base_date
        }
        ok = self.db.insert_or_update_quote("UPT", quote)
        self.assertTrue(ok)

        # Upsert same date with new price
        quote2 = quote.copy()
        quote2["close_eur"] = 12.5
        ok2 = self.db.insert_or_update_quote("UPT", quote2)
        self.assertTrue(ok2)

        quotes = self.db.get_quotes("UPT")
        self.assertEqual(len(quotes), 1)
        self.assertAlmostEqual(quotes[0]["close_eur"], 12.5)


if __name__ == "__main__":
    unittest.main()
