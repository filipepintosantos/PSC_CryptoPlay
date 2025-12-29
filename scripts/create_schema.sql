-- Schema de criação para PSC_CryptoPlay
-- Gerado a partir de src/database.py

PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

-- Tabela de metadados das criptomoedas
CREATE TABLE IF NOT EXISTS cryptocurrencies (
    id INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
