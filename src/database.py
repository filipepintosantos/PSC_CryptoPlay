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
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Table for cryptocurrency metadata with additional fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cryptocurrencies (
                id INTEGER PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for cryptocurrency information (code, name, marketEntry, marketCap, favorite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_info (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                market_entry TIMESTAMP,
                market_cap REAL,
                favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for price quotes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_quotes (
                id INTEGER PRIMARY KEY,
                crypto_id TEXT NOT NULL,
                price_eur REAL NOT NULL,
                market_cap_eur REAL,
                volume_24h_eur REAL,
                percent_change_24h REAL,
                percent_change_7d REAL,
                percent_change_30d REAL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                -- crypto_id stores the cryptocurrency code (symbol), e.g. 'BTC'
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crypto_timestamp 
            ON price_quotes(crypto_id, timestamp)
        """)
        
        self.conn.commit()
    
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
            cursor.execute("""
                INSERT INTO price_quotes (
                    crypto_id, price_eur, market_cap_eur, volume_24h_eur,
                    percent_change_24h, percent_change_7d, percent_change_30d,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                quote_data.get("price_eur"),
                quote_data.get("market_cap_eur"),
                quote_data.get("volume_24h_eur"),
                quote_data.get("percent_change_24h"),
                quote_data.get("percent_change_7d"),
                quote_data.get("percent_change_30d"),
                quote_data.get("timestamp", datetime.now())
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
            timestamp = quote_data.get("timestamp", datetime.now())
            
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
                        price_eur = ?,
                        market_cap_eur = ?,
                        volume_24h_eur = ?,
                        percent_change_24h = ?,
                        percent_change_7d = ?,
                        percent_change_30d = ?
                    WHERE id = ?
                """, (
                    quote_data.get("price_eur"),
                    quote_data.get("market_cap_eur"),
                    quote_data.get("volume_24h_eur"),
                    quote_data.get("percent_change_24h"),
                    quote_data.get("percent_change_7d"),
                    quote_data.get("percent_change_30d"),
                    existing[0]
                ))
            else:
                # Insert new quote
                cursor.execute("""
                    INSERT INTO price_quotes (
                        crypto_id, price_eur, market_cap_eur, volume_24h_eur,
                        percent_change_24h, percent_change_7d, percent_change_30d,
                        timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    quote_data.get("price_eur"),
                    quote_data.get("market_cap_eur"),
                    quote_data.get("volume_24h_eur"),
                    quote_data.get("percent_change_24h"),
                    quote_data.get("percent_change_7d"),
                    quote_data.get("percent_change_30d"),
                    timestamp
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting/updating quote for {symbol}: {e}")
            return False
    
    def add_crypto_info(self, code: str, name: str, market_entry: Optional[datetime] = None, 
                       market_cap: Optional[float] = None, favorite: bool = False) -> Optional[int]:
        """
        Add cryptocurrency information to crypto_info table.
        
        Args:
            code: Cryptocurrency code (e.g., 'BTC')
            name: Cryptocurrency name (e.g., 'Bitcoin')
            market_entry: Date when cryptocurrency entered the market
            market_cap: Market capitalization
            favorite: Whether this is a favorite cryptocurrency
        
        Returns:
            ID of the inserted/existing cryptocurrency info
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO crypto_info (code, name, market_entry, market_cap, favorite)
                VALUES (?, ?, ?, ?, ?)
            """, (code, name, market_entry, market_cap, favorite))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already exists
        
        cursor.execute("SELECT id FROM crypto_info WHERE code = ?", (code,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def update_crypto_info(self, code: str, name: Optional[str] = None, 
                          market_entry: Optional[datetime] = None, 
                          market_cap: Optional[float] = None, 
                          favorite: Optional[bool] = None) -> bool:
        """
        Update cryptocurrency information.
        
        Args:
            code: Cryptocurrency code
            name: Cryptocurrency name (optional)
            market_entry: Market entry date (optional)
            market_cap: Market cap (optional)
            favorite: Favorite flag (optional)
        
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
    
    def get_all_crypto_info(self, favorites_only: bool = False) -> List[Dict]:
        """
        Get all cryptocurrency information.
        
        Args:
            favorites_only: If True, return only favorite cryptocurrencies
        
        Returns:
            List of cryptocurrency info dictionaries
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM crypto_info"
        
        if favorites_only:
            query += " WHERE favorite = 1"
        
        query += " ORDER BY code"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def set_favorite(self, code: str, favorite: bool) -> bool:
        """
        Set or unset a cryptocurrency as favorite.
        
        Args:
            code: Cryptocurrency code
            favorite: True to mark as favorite, False to unmark
        
        Returns:
            True if successful
        """
        return self.update_crypto_info(code, favorite=favorite)
    
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
