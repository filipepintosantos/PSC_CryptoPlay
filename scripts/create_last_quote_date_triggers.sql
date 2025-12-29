-- Trigger para atualizar last_quote_date na tabela crypto_info após INSERT em price_quotes
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

-- Trigger para atualizar last_quote_date na tabela crypto_info após UPDATE em price_quotes
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

-- Trigger para atualizar last_quote_date na tabela crypto_info após DELETE em price_quotes
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
