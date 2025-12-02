# Changelog

## [2.1.0] - 2025-12-02

### Added
- **Auto-discovery de criptomoedas**: Script `seed_large_cryptos_yfinance.py` que busca automaticamente todas as criptomoedas com market cap > $250M USD via CoinGecko API
- **Validação de dados EUR**: Só inclui moedas com quotações EUR disponíveis no Yahoo Finance
- **Opção `--all-from-db`**: Busca automaticamente todas as moedas da tabela `crypto_info`
- **Script `update_quotes.bat`**: Atualização rápida de todas as moedas com últimos 3 dias de dados
- **Tabela `crypto_info`**: Nova tabela para metadados de criptomoedas (market cap, data de entrada, favoritas)
- **Ordenação por market cap**: Relatórios Excel ordenados por capitalização de mercado
- **Colunas de percentagem**: Desvios expressos em percentagem além de valores absolutos
- **Freeze panes**: Linha 5 e coluna B fixas no relatório Excel
- **Última cotação em coluna B**: Aparece apenas uma vez, destacada

### Changed
- **Migração para yfinance**: Substituído CoinMarketCap API por Yahoo Finance (gratuito, sem API key)
- **Market cap mínimo**: Reduzido de $1B para $250M USD
- **Formato de relatório**: Simplificado para mostrar apenas diferenças percentuais
- **Largura de colunas**: Ajustada para 70 pixels (10 unidades Excel)
- **Número de decimais**: Última cotação com 2 decimais, outras métricas com 2 decimais

### Removed
- **Dependência de API key**: Não é mais necessário configurar chave API
- **Arquivo `.env`**: Removida necessidade de configuração de credenciais
- **Colunas de diferença absoluta**: Mantidas apenas as percentagens
- **Moedas sem dados EUR**: 53 criptomoedas removidas por não terem par EUR no Yahoo Finance

### Fixed
- **Erro ao gerar relatório**: Corrigido erro com moedas sem `market_cap` definido
- **Duplicação de quotações**: UPSERT garante que não há duplicados na tabela `price_quotes`

## [2.0.0] - 2024-11-XX

### Added
- Migração inicial para yfinance
- Suporte a DATE-only timestamps
- UPSERT handling para quotações duplicadas
- Modo incremental de fetch

### Changed
- API principal mudou de CoinMarketCap para Yahoo Finance
- Schema de timestamp simplificado para DATE

## [1.0.0] - 2024-XX-XX

### Added
- Versão inicial com CoinMarketCap API
- Análise estatística multi-período
- Relatórios Excel
- Importação CSV
