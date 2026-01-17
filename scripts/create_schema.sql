-- Schema de criação para PSC_CryptoPlay
-- Gerado a partir de src/database.py

-- Schema version variables (update here for new releases)
-- SCHEMA_VERSION = '1.4.0'
-- SCHEMA_VERSION_NUMBER = 10400  -- integer representation (x*10000 + y*100 + z)

PRAGMA user_version = 10400;

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
    source TEXT,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Carteira Binance (FIFO): controla lotes comprados e remanescentes
CREATE TABLE IF NOT EXISTS binance_wallet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crypto_id TEXT NOT NULL,        -- Ex: 'ADA', 'BTC'
    utc_time TEXT NOT NULL,         -- ISO 8601: '2024-01-15T10:32:00'
    amount_total REAL NOT NULL,     -- Quantidade comprada no lote
    price_eur REAL NOT NULL,        -- Preço unitário em EUR no momento da compra
    amount_remaining REAL NOT NULL, -- Quantidade ainda disponível para FIFO
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice auxiliar para buscas FIFO por moeda e tempo
CREATE INDEX IF NOT EXISTS idx_binance_wallet_crypto_time ON binance_wallet(crypto_id, utc_time);

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

-- Triggers para atualizar `update_date` em binance_transactions
CREATE TRIGGER IF NOT EXISTS trg_binance_transactions_update_date_insert
AFTER INSERT ON binance_transactions
BEGIN
    UPDATE binance_transactions
    SET update_date = CURRENT_TIMESTAMP
    WHERE id = NEW.id AND update_date IS NULL;
END;

CREATE TRIGGER IF NOT EXISTS trg_binance_transactions_update_date_update
AFTER UPDATE ON binance_transactions
BEGIN
    UPDATE binance_transactions
    SET update_date = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
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

-- Triggers para atualizar `update_date` em binance_wallet
CREATE TRIGGER IF NOT EXISTS trg_binance_wallet_update_date_insert
AFTER INSERT ON binance_wallet
BEGIN
    UPDATE binance_wallet
    SET update_date = CURRENT_TIMESTAMP
    WHERE id = NEW.id AND update_date IS NULL;
END;

CREATE TRIGGER IF NOT EXISTS trg_binance_wallet_update_date_update
AFTER UPDATE ON binance_wallet
BEGIN
    UPDATE binance_wallet
    SET update_date = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
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

-- Set initial schema version (format: x.y.z). Current schema version: 1.4.0
-- NOTE: keep the numeric version in sync with the PRAGMA user_version above.
-- The SQL below formats an integer version (x*10000 + y*100 + z) into 'x.y.z'.
WITH sv(v) AS (VALUES(10300))
INSERT INTO schema_info (version)
SELECT printf('%d.%d.%d', 
              CAST(v/10000 AS INTEGER), 
              CAST((v/100)%100 AS INTEGER), 
              CAST(v%100 AS INTEGER))
FROM sv
WHERE NOT EXISTS (SELECT 1 FROM schema_info);
