-- Schema de criação para PSC_CryptoPlay
-- Gerado a partir de src/database.py

-- Schema version variables (update here for new releases)
-- SCHEMA_VERSION = '1.2.0'
-- SCHEMA_VERSION_NUMBER = 10200  -- integer representation (x*10000 + y*100 + z)

PRAGMA user_version = 10200;

PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

-- Informações adicionais sobre as criptomoedas
CREATE TABLE IF NOT EXISTS crypto_info (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    market_entry TIMESTAMP,
    market_cap REAL,
    favorite TEXT DEFAULT NULL,
    last_quote_date DATE DEFAULT NULL,
    first_quote_date DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de cotações (OHLC simplificado por dia)
CREATE TABLE IF NOT EXISTS price_quotes (
    id INTEGER PRIMARY KEY,
    crypto_id TEXT NOT NULL,
    close_eur REAL NOT NULL,
    low_eur REAL,
    high_eur REAL,
    daily_returns REAL,
    timestamp DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crypto_id, timestamp)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_crypto_timestamp ON price_quotes(crypto_id, timestamp);

-- Tabela de transações da Binance
CREATE TABLE IF NOT EXISTS binance_transactions (
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
);

COMMIT;

PRAGMA foreign_keys = ON;

-- Triggers para manter `last_quote_date` sincronizado em `crypto_info`
-- (original: scripts/create_last_quote_date_triggers.sql)
CREATE TRIGGER IF NOT EXISTS trg_update_last_quote_date_after_insert
AFTER INSERT ON price_quotes
BEGIN
    UPDATE crypto_info
    SET last_quote_date = (
        SELECT MAX(timestamp) FROM price_quotes WHERE crypto_id = NEW.crypto_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE code = NEW.crypto_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_update_last_quote_date_after_update
AFTER UPDATE ON price_quotes
BEGIN
    UPDATE crypto_info
    SET last_quote_date = (
        SELECT MAX(timestamp) FROM price_quotes WHERE crypto_id = NEW.crypto_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE code = NEW.crypto_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_update_last_quote_date_after_delete
AFTER DELETE ON price_quotes
BEGIN
    UPDATE crypto_info
    SET last_quote_date = (
        SELECT MAX(timestamp) FROM price_quotes WHERE crypto_id = OLD.crypto_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE code = OLD.crypto_id;
END;

-- Schema versioning: single-row table with applied schema version
CREATE TABLE IF NOT EXISTS schema_info (
    version TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Set initial schema version (format: x.y.z). Current schema version: 1.2.0
-- NOTE: keep the numeric version in sync with the PRAGMA user_version above.
-- The SQL below formats an integer version (x*10000 + y*100 + z) into 'x.y.z'.
WITH sv(v) AS (VALUES(10200))
INSERT INTO schema_info (version)
SELECT printf('%d.%d.%d', 
              CAST(v/10000 AS INTEGER), 
              CAST((v/100)%100 AS INTEGER), 
              CAST(v%100 AS INTEGER))
FROM sv
WHERE NOT EXISTS (SELECT 1 FROM schema_info);
