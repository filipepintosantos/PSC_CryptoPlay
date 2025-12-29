-- Adiciona a coluna first_quote_date na tabela crypto_info, se não existir
ALTER TABLE crypto_info ADD COLUMN first_quote_date DATE;

-- Atualiza o valor de first_quote_date para cada moeda com base na menor data (timestamp) em price_quotes
UPDATE crypto_info
SET first_quote_date = (
    SELECT MIN(timestamp) FROM price_quotes WHERE crypto_id = code
);
