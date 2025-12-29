"""
Module for managing SQLite database operations.
Stores and retrieves cryptocurrency price data.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class CryptoDatabase:
    """SQLite database manager for cryptocurrency price data."""

    def __init__(self, db_path: str = "data/crypto_prices.db"):
        """
        Initialize the database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Only create parent directory if a directory component exists (e.g. not ':memory:')
        dir_name = os.path.dirname(db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to the database and create tables if needed."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # Ensure foreign keys are enabled and create schema from canonical SQL when needed
        try:
            self.conn.execute("PRAGMA foreign_keys = ON")
        except Exception:
            pass
        self.create_tables()

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        # Use canonical SQL script to create the schema if `crypto_info` table is missing
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crypto_info'")
        exists = cursor.fetchone()
        if exists:
            return

        # Locate the create_schema.sql relative to this file
        base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
        schema_path = os.path.join(base_dir, 'scripts', 'create_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            # executescript runs the whole file in a single transaction
            self.conn.executescript(sql)
        else:
            raise RuntimeError(f"Schema file not found: {schema_path}; cannot create database schema")

    def add_cryptocurrency(self, symbol: str, name: str) -> int:
        """
        Add a cryptocurrency to the database.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
            name: Cryptocurrency name (e.g., 'Bitcoin')

        Returns:
            ID of the inserted cryptocurrency
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO cryptocurrencies (symbol, name)
                VALUES (?, ?)
            """, (symbol, name))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already exists

        cursor.execute("SELECT id FROM cryptocurrencies WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        return result[0] if result else None

    def insert_quote(self, symbol: str, quote_data: Dict) -> bool:
        """
        Insert a price quote for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol
            quote_data: Dictionary with quote information

        Returns:
            True if insertion was successful
        """
        cursor = self.conn.cursor()

        # Ensure cryptocurrency metadata exists (store symbol/name)
        self.add_cryptocurrency(symbol, quote_data.get("name", ""))

        try:
            # Normalize timestamp to date only (YYYY-MM-DD)
            ts = quote_data.get("timestamp", datetime.now())
            date_only = ts.date() if hasattr(ts, 'date') else ts

            cursor.execute("""
                INSERT INTO price_quotes (
                    crypto_id, close_eur, low_eur, high_eur, daily_returns, timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(crypto_id, timestamp)
                DO UPDATE SET
                    close_eur = excluded.close_eur,
                    low_eur = excluded.low_eur,
                    high_eur = excluded.high_eur,
                    daily_returns = excluded.daily_returns
                    -- created_at is NOT updated, preserves original insert time
            """, (
                symbol,
                quote_data.get("close_eur") or quote_data.get("price_eur"),  # Backward compatibility
                quote_data.get("low_eur"),
                quote_data.get("high_eur"),
                quote_data.get("daily_returns"),
                date_only
            ))
            self.conn.commit()

            return True
        except Exception as e:
            print(f"Error inserting quote for {symbol}: {e}")
            return False

    def insert_quotes_batch(self, quotes: List[Dict]) -> int:
        """
        Insert multiple quotes at once.

        Args:
            quotes: List of quote dictionaries

        Returns:
            Number of successfully inserted quotes
        """
        count = 0
        for quote in quotes:
            if self.insert_quote(quote.get("symbol"), quote):
                count += 1
        return count

    def get_quotes(self, symbol: str, days: Optional[int] = None) -> List[Dict]:
        """
        Get price quotes for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol
            days: Number of days to retrieve (None for all)

        Returns:
            List of quote dictionaries
        """
        cursor = self.conn.cursor()

        query = """
            SELECT pq.*, c.symbol, c.name
            FROM price_quotes pq
            JOIN cryptocurrencies c ON pq.crypto_id = c.symbol
            WHERE c.symbol = ?
        """

        params = [symbol]

        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query += " AND pq.timestamp >= ?"
            params.append(cutoff_date)

        query += " ORDER BY pq.timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_latest_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get the most recent quote for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            Quote dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pq.*, c.symbol, c.name
            FROM price_quotes pq
            JOIN cryptocurrencies c ON pq.crypto_id = c.symbol
            WHERE c.symbol = ?
            ORDER BY pq.timestamp DESC
            LIMIT 1
        """, (symbol,))

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_symbols(self) -> List[str]:
        """
        Get all cryptocurrencies in the database.

        Returns:
            List of cryptocurrency symbols
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT symbol FROM cryptocurrencies ORDER BY symbol")
        return [row[0] for row in cursor.fetchall()]

    def get_latest_timestamp(self, symbol: str) -> Optional[datetime]:
        """
        Get the most recent timestamp for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            Most recent datetime or None if no data exists
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MAX(pq.timestamp)
            FROM price_quotes pq
            JOIN cryptocurrencies c ON pq.crypto_id = c.symbol
            WHERE c.symbol = ?
        """, (symbol,))

        result = cursor.fetchone()
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        return None

    def get_oldest_timestamp(self, symbol: str) -> Optional[datetime]:
        """
        Get the oldest timestamp for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            Oldest datetime or None if no data exists
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MIN(pq.timestamp)
            FROM price_quotes pq
            JOIN cryptocurrencies c ON pq.crypto_id = c.symbol
            WHERE c.symbol = ?
        """, (symbol,))

        result = cursor.fetchone()
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        return None

    def insert_or_update_quote(self, symbol: str, quote_data: Dict) -> bool:
        """
        Insert a price quote or update if same timestamp exists.

        Args:
            symbol: Cryptocurrency symbol
            quote_data: Dictionary with quote information

        Returns:
            True if insertion/update was successful
        """
        cursor = self.conn.cursor()

        # Ensure cryptocurrency metadata exists (store symbol/name)
        self.add_cryptocurrency(symbol, quote_data.get("name", ""))

        try:
            # Normalize timestamp to date only (YYYY-MM-DD)
            ts = quote_data.get("timestamp", datetime.now())
            timestamp = ts.date() if hasattr(ts, 'date') else ts

            # Check if quote with same timestamp exists
            cursor.execute("""
                SELECT id FROM price_quotes
                WHERE crypto_id = ? AND timestamp = ?
            """, (symbol, timestamp))

            existing = cursor.fetchone()

            if existing:
                # Update existing quote
                cursor.execute("""
                    UPDATE price_quotes SET
                        close_eur = ?,
                        low_eur = ?,
                        high_eur = ?,
                        daily_returns = ?
                    WHERE id = ?
                """, (
                    quote_data.get("close_eur") or quote_data.get("price_eur"),  # Backward compatibility
                    quote_data.get("low_eur"),
                    quote_data.get("high_eur"),
                    quote_data.get("daily_returns"),
                    existing[0]
                ))
            else:
                # Insert new quote
                cursor.execute("""
                    INSERT INTO price_quotes (
                        crypto_id, close_eur, low_eur, high_eur, daily_returns, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    quote_data.get("close_eur") or quote_data.get("price_eur"),  # Backward compatibility
                    quote_data.get("low_eur"),
                    quote_data.get("high_eur"),
                    quote_data.get("daily_returns"),
                    timestamp
                ))

            self.conn.commit()
            self.conn.commit()

            return True
        except Exception as e:
            print(f"Error inserting/updating quote for {symbol}: {e}")
            return False

    def update_last_quote_date(self, symbol: str) -> bool:
        """
        Update the last_quote_date in crypto_info table for a symbol.
        Sets it to the most recent date from price_quotes.

        Args:
            symbol: Cryptocurrency symbol/code

        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        try:
            # Get the most recent quote date for this symbol
            cursor.execute("""
                SELECT MAX(timestamp) FROM price_quotes
                WHERE crypto_id = ?
            """, (symbol,))

            result = cursor.fetchone()
            last_date = result[0] if result and result[0] else None

            if last_date:
                # Update crypto_info with the last quote date
                cursor.execute("""
                    UPDATE crypto_info
                    SET last_quote_date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE code = ?
                """, (last_date, symbol))
                self.conn.commit()

            return True
        except Exception as e:
            print(f"Error updating last_quote_date for {symbol}: {e}")
            return False

    def get_last_quote_date_for_symbol(self, symbol: str) -> Optional[datetime]:
        """
        Get the last quote date for a symbol from crypto_info table.

        Args:
            symbol: Cryptocurrency symbol/code

        Returns:
            Last quote date or None if not available
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT last_quote_date FROM crypto_info
            WHERE code = ?
        """, (symbol,))

        result = cursor.fetchone()
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        return None

    def add_crypto_info(self, code: str, name: str, market_entry: Optional[datetime] = None,
                       market_cap: Optional[float] = None, favorite: Optional[str] = None) -> Optional[int]:
        """
        Add or update cryptocurrency information to crypto_info table.
        Uses UPSERT to update if code already exists.

        Args:
            code: Cryptocurrency code (e.g., 'BTC')
            name: Cryptocurrency name (e.g., 'Bitcoin')
            market_entry: Date when cryptocurrency entered the market
            market_cap: Market capitalization
            favorite: Favorite classification ('A', 'B', 'C', or None)

        Returns:
            ID of the inserted/existing cryptocurrency info
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO crypto_info (code, name, market_entry, market_cap, favorite)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(code)
                DO UPDATE SET
                    name = excluded.name,
                    market_entry = excluded.market_entry,
                    market_cap = excluded.market_cap,
                    favorite = excluded.favorite,
                    updated_at = CURRENT_TIMESTAMP
            """, (code, name, market_entry, market_cap, favorite))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding/updating crypto_info for {code}: {e}")
            return None

        cursor.execute("SELECT id FROM crypto_info WHERE code = ?", (code,))
        result = cursor.fetchone()
        return result[0] if result else None

    def update_crypto_info(self, code: str, name: Optional[str] = None,
                          market_entry: Optional[datetime] = None,
                          market_cap: Optional[float] = None,
                          favorite: Optional[str] = None) -> bool:
        """
        Update cryptocurrency information.

        Args:
            code: Cryptocurrency code
            name: Cryptocurrency name (optional)
            market_entry: Market entry date (optional)
            market_cap: Market cap (optional)
            favorite: Favorite classification ('A', 'B', 'C', or None) (optional)

        Returns:
            True if update was successful
        """
        cursor = self.conn.cursor()
        updates = ["updated_at = CURRENT_TIMESTAMP"]
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if market_entry is not None:
            updates.append("market_entry = ?")
            params.append(market_entry)
        if market_cap is not None:
            updates.append("market_cap = ?")
            params.append(market_cap)
        if favorite is not None:
            updates.append("favorite = ?")
            params.append(favorite)

        params.append(code)

        try:
            cursor.execute(f"""
                UPDATE crypto_info SET {', '.join(updates)}
                WHERE code = ?
            """, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating crypto_info for {code}: {e}")
            return False

    def get_crypto_info(self, code: str) -> Optional[Dict]:
        """
        Get cryptocurrency information.

        Args:
            code: Cryptocurrency code

        Returns:
            Dictionary with crypto info or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM crypto_info WHERE code = ?
        """, (code,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_crypto_info(self, favorites_only: bool = False, favorite_class: Optional[str] = None) -> List[Dict]:
        """
        Get all cryptocurrency information.

        Args:
            favorites_only: If True, return only favorite cryptocurrencies (any class)
            favorite_class: If specified, return only cryptocurrencies with this class ('A', 'B', or 'C')

        Returns:
            List of cryptocurrency info dictionaries
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM crypto_info"

        if favorite_class:
            query += f" WHERE favorite = '{favorite_class}'"
        elif favorites_only:
            query += " WHERE favorite IS NOT NULL AND favorite != ''"

        query += " ORDER BY code"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def set_favorite_class(self, code: str, favorite_class: Optional[str]) -> bool:
        """
        Set or unset a cryptocurrency favorite class.

        Args:
            code: Cryptocurrency code
            favorite_class: 'A', 'B', 'C' to set class, None to unmark

        Returns:
            True if successful
        """
        if favorite_class and favorite_class not in ['A', 'B', 'C']:
            raise ValueError("favorite_class must be 'A', 'B', 'C', or None")

        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE crypto_info
                SET favorite = ?, updated_at = CURRENT_TIMESTAMP
                WHERE code = ?
            """, (favorite_class, code))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error setting favorite class for {code}: {e}")
            return False

    def set_favorite(self, code: str, is_favorite: bool) -> bool:
        """
        Legacy method for backwards compatibility.
        Set or unset a cryptocurrency as favorite (class A).

        Args:
            code: Cryptocurrency code
            is_favorite: True to mark as favorite (class A), False to unmark

        Returns:
            True if successful
        """
        return self.set_favorite_class(code, 'A' if is_favorite else None)

    def delete_crypto_info(self, code: str) -> bool:
        """
        Delete cryptocurrency information.

        Args:
            code: Cryptocurrency code

        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM crypto_info WHERE code = ?", (code,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting crypto_info for {code}: {e}")
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
