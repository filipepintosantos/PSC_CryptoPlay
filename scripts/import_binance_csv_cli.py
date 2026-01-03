from __future__ import annotations

import sys
import csv
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import CryptoDatabase
from src.api_binance import get_price_at_second


def pick(row_dict, *names: str) -> str:
    for name in names:
        if name in row_dict and row_dict[name] != "":
            return row_dict.get(name, "")
    return ""


def import_csv(csv_path: Path, db_path: Path) -> tuple[int, int]:
    db = CryptoDatabase(db_path)
    cursor = db.conn.cursor()
    count = 0
    skipped = 0
    cache: dict[tuple[str, datetime], tuple[float, int | None]] = {}

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user_id = pick(row, "User ID", "User_ID").strip()
                utc_time_str = pick(row, "UTC Time", "UTC_Time").strip()
                account = pick(row, "Account").strip()
                operation = pick(row, "Operation").strip()
                coin = pick(row, "Coin").strip().upper()
                remark = pick(row, "Remark").strip()
                change_val = float(pick(row, "Change") or 0)

                if not utc_time_str:
                    print("Skip: UTC Time vazio")
                    skipped += 1
                    continue

                try:
                    dt = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    dt_utc = dt.astimezone(timezone.utc)
                except Exception:
                    print(f"Skip: invalid UTC Time {utc_time_str!r}")
                    skipped += 1
                    continue

                cache_key = (coin, dt_utc.replace(microsecond=0))
                if coin == "EUR":
                    price_eur = 1.0
                    ts_open = int(dt_utc.timestamp() * 1000)
                elif cache_key in cache:
                    price_eur, ts_open = cache[cache_key]
                else:
                    symbol_pair = f"{coin}EUR"
                    try:
                        price_eur, ts_open = get_price_at_second(symbol_pair, dt_utc)
                    except Exception as e:  # noqa: BLE001
                        print(f"Skip: API error for {symbol_pair} @ {utc_time_str}: {e}")
                        price_eur = None
                        ts_open = None
                    if price_eur is None:
                        # Fallback 1: coin/USDT * USDT/EUR
                        try:
                            price_coin_usdt, ts_coin = get_price_at_second(f"{coin}USDT", dt_utc)
                            price_eur_usdt, ts_usdt = get_price_at_second("EURUSDT", dt_utc)
                            if (
                                price_coin_usdt is not None
                                and price_eur_usdt is not None
                                and price_eur_usdt != 0
                            ):
                                price_usdt_eur = 1 / price_eur_usdt
                                ts_open = ts_coin if ts_coin is not None else ts_usdt
                                price_eur = price_coin_usdt * price_usdt_eur
                        except Exception as e:  # noqa: BLE001
                            print(f"Fallback1 error for {coin} @ {utc_time_str}: {e}")
                    if price_eur is None:
                        # Fallback 2: coin/USDC * USDC/EUR
                        try:
                            price_coin_usdc, ts_coin = get_price_at_second(f"{coin}USDC", dt_utc)
                            price_eur_usdc, ts_usdc = get_price_at_second("EURUSDC", dt_utc)
                            if (
                                price_coin_usdc is not None
                                and price_eur_usdc is not None
                                and price_eur_usdc != 0
                            ):
                                price_usdc_eur = 1 / price_eur_usdc
                                ts_open = ts_coin if ts_coin is not None else ts_usdc
                                price_eur = price_coin_usdc * price_usdc_eur
                        except Exception as e:  # noqa: BLE001
                            print(f"Fallback2 error for {coin} @ {utc_time_str}: {e}")
                    cache[cache_key] = (price_eur, ts_open)

                binance_ts = ts_open if ts_open is not None else int(dt_utc.timestamp() * 1000)
                value_eur = price_eur * change_val

                cursor.execute(
                    """SELECT 1 FROM binance_transactions
                           WHERE user_id = ? AND utc_time = ? AND account = ? AND operation = ?
                                 AND coin = ? AND change = ? AND remark = ?""",
                    (user_id, utc_time_str, account, operation, coin, change_val, remark),
                )
                if cursor.fetchone():
                    skipped += 1
                    continue

                cursor.execute(
                    """INSERT INTO binance_transactions
                    (user_id, utc_time, account, operation, coin, change, remark,
                     price_eur, value_eur, binance_timestamp, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id,
                        utc_time_str,
                        account,
                        operation,
                        coin,
                        change_val,
                        remark,
                        price_eur,
                        value_eur,
                        binance_ts,
                        "BinanceCSV",
                    ),
                )
                count += 1
            except Exception as e:  # noqa: BLE001
                print(f"Skip: row error {e}")
                skipped += 1

    db.conn.commit()
    db.close()
    return count, skipped


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: import_binance_csv_cli.py <csv_path> [db_path]")
        return 1
    csv_path = Path(argv[1]).expanduser().resolve()
    db_path = Path(argv[2]).expanduser().resolve() if len(argv) > 2 else Path(__file__).resolve().parent.parent / "data" / "crypto_prices.db"
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return 1
    print(f"CSV: {csv_path}")
    print(f"DB:  {db_path}")
    count, skipped = import_csv(csv_path, db_path)
    print(f"Inserted: {count}, skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
