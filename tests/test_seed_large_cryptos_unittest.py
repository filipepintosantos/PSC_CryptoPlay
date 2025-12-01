import os
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta, timezone

from unittest.mock import patch, MagicMock

from scripts.seed_large_cryptos import seed_large_cryptos
from src.database import CryptoDatabase


def make_fake_response(items):
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"data": items}
    return mock


class TestSeedLargeCryptos(unittest.TestCase):
    def test_inserts_only_large_old_coins(self):
        tmpdir = tempfile.mkdtemp()
        try:
            db_path = os.path.join(tmpdir, "test_seed.db")

            past_date = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()

            large_coin = {
                "symbol": "BIG",
                "name": "BigCoin",
                "date_added": past_date,
                "quote": {"USD": {"market_cap": 2_000_000_000}}
            }

            small_coin = {
                "symbol": "SMALL",
                "name": "SmallCoin",
                "date_added": past_date,
                "quote": {"USD": {"market_cap": 100_000_000}}
            }

            recent_coin = {
                "symbol": "NEW",
                "name": "NewCoin",
                "date_added": datetime.now(timezone.utc).isoformat(),
                "quote": {"USD": {"market_cap": 5_000_000_000}}
            }

            items = [large_coin, small_coin, recent_coin]

            fake_resp = make_fake_response(items)

            with patch("requests.get", return_value=fake_resp):
                # Ensure API key check passes in test environment
                os.environ["COINMARKETCAP_API_KEY"] = "DUMMY_TEST_KEY"
                try:
                    seed_large_cryptos(db_path=db_path, dry_run=False, limit=100, max_pages=1)
                finally:
                    del os.environ["COINMARKETCAP_API_KEY"]

            db = CryptoDatabase(db_path=db_path)
            rows = db.get_all_crypto_info()
            codes = [r["code"] for r in rows]

            self.assertIn("BIG", codes)
            self.assertNotIn("SMALL", codes)
            self.assertNotIn("NEW", codes)

            db.close()
        finally:
            try:
                shutil.rmtree(tmpdir)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
