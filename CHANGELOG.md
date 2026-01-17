# [5.3.0] - 2026-01-17

### Added
- **11 new tests for database FIFO wallet functionality** (`tests/test_database_fifo.py`)
  - Tests for `rebuild_binance_wallet()` covering single/multiple entries, FIFO consumption, oversell scenarios
  - Tests for `_load_wallet_ops_config()` verifying config.ini loading
  - Edge case tests: empty transactions, full consumption, multiple coins, clearing old data
  
- **5 new tests for main.py reporting functionality** (`tests/test_main.py`)
  - Tests for `_add_volatility_to_reports()` with success, errors, and missing periods
  - Tests for `generate_report()` covering success and no-valid-data scenarios
  - Increased main.py coverage from 51% to 63%

### Improved
- **Test coverage** increased from 80% to 81% overall
  - 158 tests → 163 tests total (+5 tests)
  - main.py: 51% → 63% coverage (-38 uncovered statements)
  - database.py FIFO methods now fully tested
  
- **Code quality** improvements
  - Better test organization for wallet operations
  - More comprehensive edge case coverage
  - Improved validation of configuration loading

### Documentation
- Updated COVERAGE_ANALYSIS.md with new test implementations

# [5.2.1] - 2026-01-17

### Added
- **FIFO Wallet UI menu** in Binance section
  - View binance_wallet lots with interactive filters
  - Filter by crypto_id and amount_remaining status
  - Rebuild wallet from transactions with confirmation dialog
  - Summary row showing balances per coin
  - Calls rebuild_binance_wallet() with config.ini rules

### Fixed
- FIFO Wallet filter error when database connection was closed
- Summary label visibility on initial load
- GitHub Actions workflow to use unittest instead of pytest
- Coverage report generation for SonarCloud analysis

### Changed
- Workflow now generates coverage.xml for SonarQube metrics
- Database connection lifecycle improved for UI operations

# [5.2.0] - 2026-01-17

### Added
- **Binance Wallet (FIFO) tracking** (`binance_wallet` table)
  - Manages cryptocurrency holdings using FIFO (First In, First Out) method
  - Tracks individual lots: `amount_total`, `price_eur`, `amount_remaining`
  - Automatically rebuilds after each CSV import via `rebuild_binance_wallet()`
  - Configurable via `[wallet]` section in `config/config.ini`
  - Entries: Buy, Sell, Convert, Deposit, Redemption, Airdrop, Interest (configurable)
  - Exits: Buy, Sell, Convert, Subscription (configurable)
  - Symmetric handling of Buy/Sell operations tracks both crypto and fiat flows
  - Can be manually rebuilt anytime using database API

### Changed
- **Schema updated to v1.3.0**: Added `binance_wallet` table with FIFO lot tracking
- **Import process**: CSV import now automatically rebuilds wallet after importing transactions

# [5.1.1] - 2026-01-17

### Optimized
- **Binance CSV import**: Added cache for missing/invalid trading pairs
  - First API error for each invalid pair (e.g., USDCEUR, EURIEUR) is logged once
  - Subsequent occurrences skip the failed pair and jump directly to fallback conversions
  - Significantly reduces redundant API calls and error log noise during bulk imports

# [5.1.0] - 2026-01-03

### Added
- **New menu entry "Analisar Transações"** in Binance menu
  - Advanced filtering interface for Binance transactions analysis
  - Filter by: Coins (multi-select), Operations (multi-select), Date range (from/to)
  - Additional filters:
    - Sign filter: All / Only Positive / Only Negative values (based on change column)
    - "Group without Operation" option to aggregate by coin and account only
  - Quick select buttons: "All" / "None" for each filter group
  - Compact filter area (max 40% of screen, with scrolling)
  - Results table with dynamic columns:
    - With operation: Coin, Operation, Account, # Rows, Total Change, Total Value EUR
    - Without operation: Coin, Account, # Rows, Total Change, Total Value EUR
  - Summary statistics: Total transactions, Total Change, Total Value EUR
  - Right-aligned numeric values for better readability

### Changed
- **Menu reorganization**:
  - Moved "Consultar Transações" from Binance menu to "Consultar Base de Dados" menu
  - Renamed to "Transações Binance" for consistency
  - Binance menu now focused on data operations: Import and Analysis
- **Database schema update** (`scripts/create_schema.sql`):
  - Changed `binance_timestamp` column type from INTEGER to TEXT (ISO 8601 format)
  - Improved timestamp readability in database queries

### Fixed
- Fixed "Cannot operate on a closed database" error in transaction analysis
  - Database connection now maintained for filter operations
  - Proper connection lifecycle management
- Corrected ORDER BY clause when grouping without operation
- Fixed column alignment and visibility when toggling operation grouping

# [5.0.3] - 2026-01-03

### Added
- **CLI helper script for Binance CSV import** (`scripts/import_binance_csv_cli.py`)
  - Standalone importer for batch processing Binance transaction exports
  - Same price-fetching logic as UI (fallback conversions + caching)

### Fixed
- Binance CSV import now supports headers with underscores (User_ID, UTC_Time)
- Added explicit header row detection to prevent accidental insertion
- Price lookup with fallback conversions:
  - Primary: coin/EUR direct pair
  - Fallback 1: coin/USDT × (1/EUR/USDT)
  - Fallback 2: coin/USDC × (1/EUR/USDC)
  - If all fail: insert with NULL price_eur/value_eur
- Added caching for API calls by (coin, datetime) to reduce redundant requests
- **Fixed `change` column storage**: now correctly stores numeric values (REAL) instead of formatted strings
  - Scientific notation (e.g., "2E-8") is parsed to float and stored as-is
  - Duplicate detection now uses numeric value comparison
- **Converted `binance_timestamp` to ISO 8601 format** (TEXT column)
  - Millisecond timestamp converted to readable date/time format (e.g., "2023-01-03T09:00:00+00:00")
  - Implemented `timestamp_ms_to_iso()` function in both UI and CLI

### Changed
- Binance import now allows NULL prices instead of skipping rows without price data

# [5.0.2] - 2026-01-03

### Added
- **Binance API client** (`src/api_binance.py`)
  - Função `get_price_at_second()` usando klines de 1s
  - Helper `get_klines()` com limites protegidos e tratamento de erros
  - 11 testes unitários em `tests/test_api_binance.py`

### Changed
- Importação de transações Binance no UI passa a abrir por defeito em `external/in`

# [5.0.1] - 2026-01-03

### Added
- **Nova funcionalidade: CSV Reader module** (`src/csv_reader.py`)
  - Módulo robusto para leitura de ficheiros CSV com suporte a múltiplos formatos
  - Auto-detecção de formatos de data (ISO, DD-MM-YYYY, etc.)
  - Parsing inteligente de preços com símbolos de moeda (€, $, £, ¥)
  - Configuração flexível via classe `CSVConfig`
  - Classe `CSVReader` para processamento de ficheiros CSV
  - Função `import_crypto_data()` para importação directa
  - 18 testes unitários cobrindo parsing, I/O de ficheiros e validação
- **Script CLI para importação CSV** (`scripts/import_from_csv.py`)
  - Interface amigável para importação de dados de preços
  - Suporte para delimitadores customizados, encodings e formatos de data
  - Modo dry-run para validação sem importar
  - Help detalhado com exemplos de uso
- **Documentação CSV** (`CSV_READER.md`)
  - Guia completo de uso do módulo CSV Reader
  - Exemplos de ficheiros CSV em diferentes formatos
  - API completa e descrição de todas as opções
- **Ficheiro de exemplo CSV** (`reports/BTC_sample.csv`)
  - Dados de exemplo para testes do importador CSV

### Changed
- Melhoradas funcionalidades de importação de dados CSV com novo módulo dedicado

# [5.0.0] - 2026-01-03

### Added
- **Nova funcionalidade: CSV Reader module** (`src/csv_reader.py`)
  - Módulo robusto para leitura de ficheiros CSV com suporte a múltiplos formatos
  - Auto-detecção de formatos de data (ISO, DD-MM-YYYY, etc.)
  - Parsing inteligente de preços com símbolos de moeda (€, $, £, ¥)
  - Configuração flexível via classe `CSVConfig`
  - Classe `CSVReader` para processamento de ficheiros CSV
  - Função `import_crypto_data()` para importação directa
  - 18 testes unitários cobrindo parsing, I/O de ficheiros e validação
- **Script CLI para importação CSV** (`scripts/import_from_csv.py`)
  - Interface amigável para importação de dados de preços
  - Suporte para delimitadores customizados, encodings e formatos de data
  - Modo dry-run para validação sem importar
  - Help detalhado com exemplos de uso
- **Documentação CSV** (`CSV_READER.md`)
  - Guia completo de uso do módulo CSV Reader
  - Exemplos de ficheiros CSV em diferentes formatos
  - API completa e descrição de todas as opções
- **Refactoring de schema**: Versão bumped para 1.2.0
  - Removida tabela redundante `cryptocurrencies`
  - Consolidação completa de metadados em `crypto_info`
  - Atualizado `PRAGMA user_version` para 10200
  - Remoção de método deprecado `add_cryptocurrency()`

### Changed
- Versão major 5.0.0: introduzida a nova tabela `binance_transactions`. Esta tabela marca o início de uma nova linha de funcionalidades relacionadas com transacções e análises adicionais; ver `scripts/apply_migration_binance.py` e `scripts/create_schema.sql` para detalhes da migração.

# [Schema 1.1.0] - 2026-01-03

### Added
- Adicionada tabela `binance_transactions` ao esquema de base de dados; incrementado `PRAGMA user_version` para `10100` (versão legível `1.1.0`).

# [4.3.15] - 2026-01-02

### Fixed
- Corrected report period statistics that were identical across periods due to a database join mismatch: some `price_quotes.crypto_id` values were stored as symbol text while queries expected numeric `crypto_info.id`. Updated query matching in `src/database.py` to accept either `ci.code` or `CAST(ci.id AS TEXT)`, regenerated the full historical data and the Excel report.
- Hardened data parsing and statistics in `src/analysis.py` (coerce numeric fields, drop invalid rows) and fixed an indentation bug affecting calculations.
- Minor Excel reporter fixes in `src/excel_reporter.py` (auto-filter range and Score column alignment).
- Regenerated `reports/AnaliseCrypto.xlsx` and ran unit tests to validate the fixes.

# [4.3.14] - 2026-01-01

### Fixed
- Resolved FOREIGN KEY failures when inserting `price_quotes` by using the numeric `id` from `crypto_info` as `crypto_id` and ensuring `crypto_info` rows are created when missing.
- Fixed leakage of `include_today` state in `main.py` so auto-range updates per-symbol behave correctly when `last_quote_date == today`.
- Ensured `update_last_quote_date` and related helpers consistently use `crypto_info.id` and derive fallback dates from `price_quotes` when needed.

### Changed
- Improved robustness of database inserts and joins; added `get_or_create_crypto_info_id()` helper in `src/database.py`.
- Added automatic cleanup of test DB files in `run_tests.cmd`.
- Minor UI startup fix: provide a minimal `ICON_MAP` fallback in `src/ui_main.py`.


### Testing
- Executed full update and unit tests locally; updated report generated at `reports/AnaliseCrypto.xlsx`.

# [4.3.13] - 2025-12-29

# [4.3.9] - 2025-12-29

# [4.3.8] - 2025-12-29

# [4.3.7] - 2025-12-29

### Changed
- Atualização da versão para 4.3.7 em toda a documentação e código.
- Adicionada coluna `first_quote_date` na tabela `crypto_info` para registrar a data da cotação mais antiga de cada moeda (EUR), preenchida automaticamente a partir de `price_quotes`.
- Criação de triggers SQLite para manter o campo `last_quote_date` sempre sincronizado com a data mais recente de cotação de cada moeda.


# [4.3.5] - 2025-12-23

### Added
- Entrada "Ferramentas" no menu lateral, com submenus "Configurações" e "Ajuda" (mostra README.md).
- "Atualização Diária" executa update_quotes.cmd e mostra o output na área de trabalho.

# [4.3.2] - 2025-12-23

### Changed
- Reduzida a indentação dos submenus do menu lateral para metade do valor padrão.
- Atualização da data da versão para 2025-12-23 em src/__init__.py.
- Sincronização da versão em sonar-project.properties para 4.3.2.

### Added
- Submenu "Gráficos" com novas opções: Candlestick, Linha, OHLC, Volume, Volatilidade (%), Média móvel (SMA/EMA), RSI, MACD, Bollinger Bands, Comparativo entre ativos (apenas entradas no menu, sem implementação).

# [4.2.4] - 2025-12-22

### Changed
- Ajuste de versão para 4.2.4

# [4.2.2] - 2025-12-22

### Changed
- Ajuste de versão para 4.2.2 após fusão de workflows CI

# [4.2.1] - 2025-12-22

### Changed
- Atualização de versão para 4.2.1


# [4.2.0] - 2025-12-22

### Changed
- Atualização de versão para 4.2.0
- Todas as referências ao relatório Excel agora usam `AnaliseCrypto.xlsx`.

# [4.0.0] - 2025-12-22


### Added
- **🖥️ Interface Gráfica PyQt6**: Nova interface desktop com barra lateral, área de gráficos e integração futura para atualização de dados, relatórios e consultas.
  - Arquivo principal: `src/ui_main.py`
  - Script de arranque: `run_ui.cmd`
  - Estrutura pronta para expansão de funcionalidades.

### Breaking
- Mudança de versão major para 4.0.0 devido à introdução da interface gráfica desktop.

# Changelog



### Fixed
  - `create_volatility_detail_sheet` (excel_reporter.py): extração de helpers para reduzir complexidade
  - Parâmetro não usado removido de `generate_report`

## [3.8.1] - 2025-12-21

# [4.3.3] - 2025-12-23

### Added
- Novas opções no menu **Atualizar Dados**: "Atualização Diária", "Reavaliar Moedas" e "Forçar Atualização" (apenas entradas no menu, sem implementação).

### Changed
- Atualização da versão para 4.3.3 em src/__init__.py, setup.py e sonar-project.properties.
### Fixed
- **🐛 Cálculo de Volatilidade**: Corrigido query SQL em `calculate_daily_volatility()`
  - Bug: JOIN com `crypto_info` falhava porque `price_quotes.crypto_id` guarda símbolo (texto) não ID numérico
  - Fix: Query agora usa `WHERE crypto_id = ?` diretamente com símbolo
  - Resultado: Coluna Vol% agora mostra volatilidade anualizada para cada período
  - Confirmado: Cálculo diferenciado por período (365, 180, 90, 30 dias)

## [3.8.0] - 2025-12-21

### Added
- **📊 Volatilidade Anualizada no Relatório**: Nova coluna V com cálculo de volatilidade baseado em daily_returns
  - Cálculo: σ(daily_returns) × √365 (desvio padrão anualizado)
  - Método `calculate_daily_volatility()` em VolatilityAnalyzer
  - Permite comparar risco entre diferentes criptomoedas
  - Volatilidade calculada para cada período (12M, 6M, 3M, 1M)

### Changed
- **📈 Estrutura do Relatório Excel**: Coluna V agora mostra Vol% (antes ±5%)
  - Coluna V: Vol% (volatilidade anualizada)
  - Colunas W-Z: ±5%, ±10%, ±15%, ±20% (deslocadas uma posição)
  - Coluna AA: Score/M (anteriormente coluna Z)
  - Header atualizado: "Vol%" adicionado

### Technical
- `volatility_analysis.py`: Novo método `calculate_daily_volatility(symbol, period_days)`
- `excel_reporter.py`: Headers e colunas ajustadas (V-AA)
- `get_period_stats()`: Retorna `daily_volatility` no dicionário de resultados

## [3.7.0] - 2025-12-21

### Added
- **📊 Estrutura OHLC na Tabela price_quotes**: Suporte completo para dados OHLC (Open/High/Low/Close)
  - Nova coluna `close_eur`: Renomeação de `price_eur` (preço de fecho)
  - Nova coluna `low_eur`: Preço mínimo do dia (NULL para dados antigos)
  - Nova coluna `high_eur`: Preço máximo do dia (NULL para dados antigos)
  - Nova coluna `daily_returns`: Retornos diários calculados (% variação)
  - API Yahoo Finance atualizada para capturar Low/High/Close
  - Cálculo automático de returns percentuais dia-a-dia
  - Retrocompatibilidade mantida com `price_eur` em CSV imports

### Changed
- **🔄 Migration Script**: Novo script `migrate_to_ohlc_schema.py`
  - Migração automática de bases existentes: `price_eur` → `close_eur`
  - Cálculo de `daily_returns` para dados históricos
  - Suporta `--dry-run` para preview
  - Preserva IDs e timestamps originais

### Technical
- Módulos atualizados: `database.py`, `api_yfinance.py`, `analysis.py`, `volatility_analysis.py`, `main.py`
- DataFrame references: `price_eur` → `close_eur`
- Backward compatibility: CSV imports aceitam ambos formatos

## [3.6.2] - 2025-12-21

### Changed
- **📊 Relatório Excel - Formato de Volatilidade**: Colunas de volatilidade agora mostram "subidas:descidas"
  - Colunas V-Y (±5%, ±10%, ±15%, ±20%): Formato alterado de soma total para "positivas:negativas"
  - Exemplo: "8:11" em vez de "19"
  - Facilita visualização de tendência (mais subidas vs descidas)
  - Score/Mês (coluna Z) mantido inalterado

## [3.6.1] - 2025-12-21

### Changed
- **📚 Consolidação de Documentação**: Reduzido de 11 para 5 arquivos .md essenciais
  - Removidos: LAST_QUOTE_DATE_UPDATE.md, PROJECT_COMPLETE.md, DEVELOPMENT.md, SONARQUBE.md
  - FAVORITES_CLASSIFICATION.md incorporado em CONFIGURATION.md
  - COLUMN_STRUCTURE.md incorporado em TECHNICAL.md
  - Documentação mais concisa: -55% linhas mantendo informação essencial
  - Arquivos mantidos: README, QUICKSTART, CHANGELOG, CONFIGURATION, TECHNICAL

## [3.6.0] - 2025-12-21

### Added
- **📅 Coluna last_quote_date na Tabela crypto_info**: Nova coluna para rastrear data da última cotação
  - Tabela `crypto_info`: Nova coluna `last_quote_date` (tipo DATE)
  - Armazena automaticamente a data mais recente de cotação para cada criptomoeda
  - Atualizada automaticamente após cada inserção/atualização de cotação
  - Permite otimização do processo de atualização

- **🚀 Modo Auto-Range de Atualização**: Atualização inteligente de cotações
  - Novo argumento `--auto-range` para buscar apenas dados novos
  - Verifica `last_quote_date` e busca desde essa data até ontem
  - Reduz tráfego de API buscando apenas cotações faltantes
  - Fallback para 365 dias se não houver dados prévios
  - Script `update_quotes.cmd` agora usa modo auto-range por padrão

- **🔧 Novos Métodos no CryptoDatabase**:
  - `update_last_quote_date(symbol)`: Atualiza data da última cotação na crypto_info
  - `get_last_quote_date_for_symbol(symbol)`: Consulta data da última cotação
  - Chamados automaticamente pelo `insert_or_update_quote()`

- **🔄 API Estendida com start_date**: yfinance API mais flexível
  - `fetch_historical_range()`: Novo parâmetro opcional `start_date`
  - Permite buscar dados desde uma data específica até ontem
  - Mantém compatibilidade com parâmetro `days` existente

- **📦 Script de Migração**: Ferramenta para bases de dados existentes
  - `scripts/add_last_quote_date_column.py`: Adiciona coluna em BDs existentes
  - Popula automaticamente com datas das cotações mais recentes
  - Idempotente (pode ser executado múltiplas vezes)
  - Uso: `python scripts/add_last_quote_date_column.py [--db-path PATH]`

- **📖 Nova Documentação**:
  - `LAST_QUOTE_DATE_UPDATE.md`: Guia completo da nova funcionalidade
  - Exemplos de uso e casos de migração
  - Benefícios e notas técnicas detalhadas

### Changed
- **⚡ Otimização do update_quotes.cmd**: Agora usa modo auto-range
  - Antes: `--days 3` (sempre busca 3 dias para todas as moedas)
  - Agora: `--auto-range` (busca apenas dados novos desde última cotação)
  - Reduz chamadas à API e tempo de execução

### Technical
- `database.py`: Modificado `create_tables()` para incluir coluna `last_quote_date`
- `database.py`: `insert_or_update_quote()` atualiza `last_quote_date` automaticamente
- `main.py`: Função `fetch_historical_range()` aceita parâmetro `auto_range`
- `main.py`: Argumentos CLI incluem `--auto-range` 
- `main.py`: Função `_fetch_price_data()` usa auto-range por padrão quando `--days` não especificado
- `api_yfinance.py`: `fetch_historical_range()` aceita `start_date` opcional

## [3.5.3] - 2025-12-15

### Fixed
- **🎨 Correção da Lógica de Cores nas Colunas de Diferenças**: Cores agora seguem convenção financeira padrão
  - Verde (C6EFCE): Valores positivos (≥ 0) - preço acima da média/mediana
  - Vermelho (FFC7CE): Valores negativos (< 0) - preço abaixo da média/mediana
  - Aplica-se a todas as 8 colunas de diferenças (K, L, M, N, R, S, T, U)
  - `_write_single_deviation_cell()`: Lógica de cores corrigida
  - Removida linha duplicada que reaplicava cor desnecessariamente na célula U

- **🔧 Cálculo Correto de Desvios da Mediana**: Adicionados cálculos específicos para mediana/MAD
  - `_analyze_period_data()`: Novos cálculos de desvios da mediana e MAD
  - Variáveis adicionadas: `latest_deviation_from_median_pct`, `latest_deviation_from_median_minus_mad_pct`
  - Variáveis adicionadas: `second_deviation_from_median_pct`, `second_deviation_from_median_minus_mad_pct`
  - Colunas R, S, T, U agora usam valores corretos da mediana (anteriormente usavam valores da média)
  - `_write_deviation_formulas()`: Corrigido para usar variáveis específicas da mediana

- **🔧 Correção do Bug no update_quotes.cmd**: Script agora executa completamente
  - `generate_report()`: Adicionado parâmetro `config` na assinatura da função
  - `validate_and_update_favorites()`: Agora recebe o parâmetro `config` corretamente
  - Script update_quotes.cmd agora gera o relatório Excel após atualizar cotações

## [3.5.2] - 2025-12-14

### Changed
- **🔄 Atualização Automática de Favoritos**: Favoritos agora são atualizados automaticamente
  - `generate_report()`: Chama `validate_and_update_favorites()` antes de gerar relatórios
  - Garante sincronização com `config.ini` sempre que um relatório é gerado
  - Remove necessidade de executar manualmente `scripts/mark_favorites.py`
  - `generate_report.cmd`: Atualizado para incluir atualização de favoritos

- **⚖️ Ponderação Suavizada do Score de Volatilidade**: Nova escala reduz impacto excessivo
  - Anterior: 5%×1, 10%×2, 15%×3, 20%×4
  - Atual: 5%×1.0, 10%×1.5, 15%×2.0, 20%×2.5
  - Mantém 5% como base (peso 1.0) com incrementos de 0.5
  - Scores mais proporcionais e menos agressivos
  - Comentários e testes atualizados com nova fórmula

## [3.5.1] - 2025-12-14

### Fixed
- **🔧 Correção de Contagem Duplicada de Eventos de Volatilidade**:
  - `_analyze_window()`: Agora processa thresholds do maior para o menor (20% → 15% → 10% → 5%)
  - Quando detecta evento de threshold maior (ex: 15%), marca o período como "usado"
  - Eventos menores (10%, 5%) não são contados se já houver um maior no mesmo período
  - Previne sobreposição marcando índices vizinhos (±window_days) como usados
  - Exemplo: variação de 15% em 72h conta apenas 1x (não conta como 10% ou 5%)
  
- **🔧 Eliminação de Sobreposição entre Janelas**:
  - `get_summary_stats()` e `get_period_stats()` agora usam apenas janela de 7d
  - Anteriormente somava 24h + 72h + 7d (contagem triplicada)
  - Janela de 7d é a mais abrangente e já captura movimentos significativos
  - Reduz drasticamente os valores de volatilidade para refletir eventos únicos reais

## [3.5.0] - 2025-12-13

### Added
- **⭐ Sistema de Classificação de Favoritos A/B/C**: Favoritos agora têm três níveis de prioridade
  - 🥇 Classe A (⭐⭐⭐): Top priority - Dourado (#FFD700)
  - 🥈 Classe B (⭐⭐): Secondary priority - Laranja (#FFA500)
  - 🥉 Classe C (⭐): Tertiary priority - Azul claro (#87CEEB)
  - 📝 Configuração em `config.ini`: `favorites_a`, `favorites_b`, `favorites_c`
  - 🔄 Validação automática das classificações ao executar `main.py`
  - 📊 Relatórios Excel mostram classe (A/B/C) com cores diferentes
  - 🛠️ Novo módulo `favorites_helper.py` com funções utilitárias
  - 📜 Script `add_symbols.py` para adicionar símbolos com classificação
  - 🔧 Script `migrate_to_favorite_classes.py` para migrar bases existentes

### Changed
- **Database Schema**: Coluna `favorite` agora aceita TEXT ('A', 'B', 'C', NULL) em vez de BOOLEAN
  - Migração automática de valores antigos: 1 → 'A', 0 → NULL
  - Mantida compatibilidade com `set_favorite(code, bool)` (converte para Classe A)
- **Excel Report**: Coluna de favoritos mostra A/B/C em vez de X
  - Coluna B (Symbol): largura 46 pixels
  - Colunas K-N e R-U (Percentagens): largura 55 pixels
  - Colunas V-Z (Volatilidade): largura 37 pixels
- **Script `mark_favorites.py`**: Atualizado para marcar todas as três classes
  - Mostra resumo por classe com emojis diferentes
  - Lista todos os favoritos organizados por classificação

### Documentation
- 📚 Novo arquivo `FAVORITES_CLASSIFICATION.md` com guia completo do sistema
  - Instruções de uso e migração
  - Exemplos de configuração
  - Referência das funções da API

## [3.4.0] - 2025-12-13

### Enhanced
- **📊 Score Normalizado por Mês**: Adicionada métrica Score/Mês para comparação justa entre períodos
  - 🔢 Nova coluna "Score/M" divide score ponderado pelo número de meses do período
  - 📈 Permite comparar volatilidade entre 1M, 3M, 6M e 12M de forma normalizada
  - 🎨 Formatação colorida: laranja >25, dourado >15
  - ✅ Exibido tanto na folha Resumo quanto Volatility Detail

### Changed
- **Folha Resumo - Colunas de Volatilidade Simplificadas**:
  - Removidas: Vol+15%, Vol+20%, Vol-15%, Vol-20%, VolScore
  - Mantidas: Vol+5%, Vol+10%, Vol-5%, Vol-10%, Vol/M
  - Foco nas métricas mais relevantes e score normalizado
  
- **Folha Volatility Detail**:
  - Removida coluna "Simple" (score sem ponderação)
  - Renomeadas: "Weighted" → "Score", adicionada "Score/M"
  - 17 colunas total: Fav, Symbol, Period, 12 thresholds, Score, Score/M
  - Ordenação por market cap (igual à folha Resumo)
  - Colunas soma adicionadas: ±5%, ±10%, ±15%, ±20% (fundo cinza)

### Fixed
- **🐛 Bug Crítico - Weighted Scoring**: Corrigido cálculo de score ponderado
  - `get_period_stats()` não estava agregando thresholds ±15% e ±20%
  - Score weighted era igual ao simple por falta de ponderação
  - Agora calcula corretamente: (±5%×1) + (±10%×2) + (±15%×3) + (±20%×4)
  - Exemplo BTC 12M: Simple=214, Weighted=251, Score/M=20.9

### Technical
- Novo parâmetro `period` em `_write_volatility_stats()` para cálculo de Score/M
- Atualizado `get_period_stats()` com todas as agregações de thresholds
- Teste adicionado: `test_weighted_score_calculation()`
- 81 testes passando, 85% coverage

## [3.3.0] - 2025-12-13

### Enhanced
- **📊 Volatility Detail Sheet Improvements**: Reorganizada a folha de detalhe de volatilidade
  - ✨ Adicionada coluna "Fav" para marcar favoritos com "X" e fundo dourado
  - 📅 Adicionada coluna "Period" mostrando período de análise (12M, 6M, 3M, 1M)
  - 📋 Dados organizados por símbolo e ordenados por market cap
  - ◀️ Cabeçalhos alinhados à esquerda para melhor legibilidade
  - 🎨 Score de volatilidade com destaque colorido (laranja >100, dourado >50)
  - 📊 Estrutura completa: todos os thresholds exibidos
  - 🔄 Colunas ordenadas por variação absoluta

### Technical
- Refatorado `_write_volatility_row` → `_write_volatility_detail_row`
- Método `create_volatility_detail_sheet` recebe `market_caps` para ordenação
- Loop reorganizado com ordenação por market cap descendente

## [3.2.2] - 2025-12-13

### Fixed
- **🔧 SonarQube Code Quality**: Resolvidos todos os avisos de complexidade cognitiva e code smells
  - Removido comentário inline no código (excel_reporter.py linha 48)
  - Convertido f-string sem interpolação para string normal (main.py linha 263)
  - Reduzida complexidade cognitiva de funções críticas:
    * `_write_deviation_formulas`: 16→7 (extraída `_write_single_deviation_cell`)
    * `create_volatility_detail_sheet`: 16→5 (extraída `_write_volatility_row`)
    * `import_csv_data`: 21→8 (extraídas `_get_column_indices`, `_parse_csv_date`)
    * `generate_report`: 18→12 (extraída `_add_volatility_to_reports`)
    * `main`: 27→15 (extraídas `_setup_argument_parser`, `_handle_csv_import`, `_fetch_price_data`)

### Changed
- **Refatoração para melhor manutenibilidade**:
  - Funções divididas em métodos auxiliares menores e focados
  - Código mais legível e testável
  - Separação de responsabilidades melhorada
  - Funções auxiliares privadas (prefixo `_`) para clareza

### Technical
- Todas as funções agora com complexidade cognitiva ≤ 15 (limite SonarQube)
- Nenhum code smell ou bug reportado
- 80 testes passando sem erros
- Código mais limpo e organizado

## [3.2.1] - 2025-12-13

### Fixed
- **🎯 Volatility Analysis - Correção Conceitual Importante**: 
  - **ANTES (errado)**: Períodos 1M, 3M, 6M eram usados como JANELAS ROLANTES longas
  - **AGORA (correto)**: Períodos 1M, 3M, 6M são PERÍODOS DE ANÁLISE (quantos dados históricos usar)
  - Janelas rolantes são apenas **períodos curtos**: 24h, 72h, 7d
  
- **Interpretação correta**:
  - Análise de **12 meses**: Conta oscilações em 365 dias usando janelas de 24h, 72h, 7d
  - Análise de **6 meses**: Conta oscilações em 180 dias usando janelas de 24h, 72h, 7d
  - Análise de **3 meses**: Conta oscilações em 90 dias usando janelas de 24h, 72h, 7d
  - Análise de **1 mês**: Conta oscilações em 30 dias usando janelas de 24h, 72h, 7d

### Changed
- `VolatilityAnalyzer.WINDOWS`: Removidas janelas longas (1M, 3M, 6M) - agora apenas 24h, 72h, 7d
- `VolatilityAnalyzer.get_period_stats()`: Simplificado para usar sempre janelas curtas
- `ExcelReporter.create_volatility_detail_sheet()`: Agora mostra apenas 3 janelas (24h, 72h, 7d)
- Folha "Volatility Detail" reduzida mas mais precisa

### Benefits
- **Comparação correta entre períodos**: 
  - Pode comparar volatilidade recente (1M) vs. histórica (12M)
  - Exemplo: BTC teve 50 oscilações de +5% no último mês vs. 200 no último ano
- **Análise consistente**: Mesmas janelas (24h, 72h, 7d) para todos os períodos
- **Interpretação clara**: Períodos = horizonte temporal, Janelas = frequência de oscilação

## [3.2.0] - 2025-12-13

### Enhanced
- **📊 Volatility Detail as Excel Sheet**: Dados detalhados de volatilidade agora numa folha "Volatility Detail" dentro do Excel
  - Elimina necessidade de ficheiro CSV separado
  - Tudo num único ficheiro Excel para melhor organização
  - Folha formatada com headers, borders, freeze panes e auto-filter
  - Contém todas as 6 janelas (24h, 72h, 7d, 1M, 3M, 6M) e 8 limiares (±5%, ±10%, ±15%, ±20%)

### Changed
- `ExcelReporter.generate_report()`: Aceita agora parâmetro `volatility_results` (opcional)
- `ExcelReporter.create_volatility_detail_sheet()`: Novo método para criar folha de volatilidade detalhada
- `main.py`: Remove exportação CSV, dados incluídos diretamente no Excel
- Console output atualizado: "Volatility details: See 'Volatility Detail' sheet in Excel"

### Removed
- Exportação automática para CSV `reports/volatility_analysis.csv`
- Método `VolatilityAnalyzer.export_to_csv()` ainda disponível mas não usado por padrão

### Benefits
- **Ficheiro único**: Tudo no Excel (Resumo + Detalhes + Volatilidade)
- **Melhor organização**: Não precisa gerir múltiplos ficheiros
- **Fácil navegação**: Troca entre folhas no mesmo Excel
- **Formatação profissional**: Headers coloridos, borders, filtros

## [3.1.0] - 2025-12-13

### Enhanced
- **🎯 Volatility Analysis - Period-Specific Stats**: Agora cada período (12M, 6M, 3M, 1M) tem suas próprias estatísticas de volatilidade
  - Adicionadas janelas de análise: **1M (30 dias), 3M (90 dias), 6M (180 dias)**
  - CSV expandido com 6 janelas: 24h, 72h, 7d, 1M, 3M, 6M
  - Excel agora mostra volatilidade **específica para cada período** em vez de agregado total
  - Períodos longos (12M, 6M) usam janelas longas (7d, 1M, 3M)
  - Períodos médios (3M) usam janelas médias (72h, 7d, 1M)
  - Períodos curtos (1M) usam janelas curtas (24h, 72h, 7d)

- **📊 Excel Report - Volatility per Period**: 
  - Cada linha de período mostra suas próprias estatísticas Vol+5%, Vol+10%, Vol-5%, Vol-10%, VolScore
  - Permite comparação direta de volatilidade entre períodos de 12M, 6M, 3M e 1M
  - Facilita identificação de mudanças de padrão de volatilidade ao longo do tempo

### Changed
- `VolatilityAnalyzer.WINDOWS`: Expandido de 3 para 6 janelas (adicionadas 1M, 3M, 6M)
- `VolatilityAnalyzer.get_period_stats()`: Novo método para estatísticas específicas de período
- `main.py`: Agora calcula volatilidade por período em vez de agregado global
- `excel_reporter.py._write_volatility_stats()`: Agora escreve volatilidade em cada linha de período

### Technical
- CSV exportado inclui todas as 6 janelas para análise detalhada
- Excel mostra resumos apropriados para cada período de análise
- Seleção inteligente de janelas baseada no período: períodos mais longos usam janelas mais longas

### Documentation
- A volatilidade por período permite:
  - Identificar se a moeda está mais volátil recentemente (1M) vs. historicamente (12M)
  - Comparar padrões de oscilação entre diferentes horizontes temporais
  - Detectar mudanças de comportamento do mercado

## [3.0.0] - 2025-12-13

### Added
- **🎯 Volatility Analysis Module**: New comprehensive volatility analysis system
  - Created `volatility_analysis.py` module with `VolatilityAnalyzer` class
  - Rolling window analysis for 24h (1 day), 72h (3 days), and 7 days periods
  - Tracks price oscillations at multiple thresholds: ±5%, ±10%, ±15%, ±20%
  - Counts positive and negative oscillation events across all windows
  - Calculates composite volatility score (sum of all oscillation events)

- **📊 Excel Report - 5 New Volatility Columns** (V-Z):
  - Column V: **Vol+5%** - Count of positive oscillations ≥ +5%
  - Column W: **Vol+10%** - Count of positive oscillations ≥ +10%
  - Column X: **Vol-5%** - Count of negative oscillations ≤ -5%
  - Column Y: **Vol-10%** - Count of negative oscillations ≤ -10%
  - Column Z: **VolScore** - Total volatility score with conditional formatting:
    * Orange (FFA500) if score > 100 (very high volatility)
    * Gold (FFD700) if score > 50 (high volatility)
  - Volatility data displayed once per symbol (merged across 4 period rows)

- **📄 CSV Export**: Detailed volatility analysis exported to `reports/volatility_analysis.csv`
  - Columns: Symbol, Window, +5%, +10%, +15%, +20%, -5%, -10%, -15%, -20%
  - Shows granular data for each rolling window and threshold
  - Useful for in-depth volatility pattern analysis

- **🧪 Unit Tests**: Created `test_volatility_analysis.py` with 6 tests
  - Tests oscillation calculation structure
  - Validates threshold counting
  - Tests summary statistics aggregation
  - Tests batch symbol analysis
  - Tests CSV export functionality
  - Tests empty/missing symbol handling

### Changed
- **Excel Report Structure**: Expanded from 21 to 26 columns (A-Z)
  - Previous columns A-U remain unchanged
  - New columns V-Z added for volatility metrics
  - Auto-filter range extended: A4:U{row} → A4:Z{row}
  - Title merge extended: A1:U1 → A1:Z1

- **main.py Integration**: Enhanced `generate_report()` function
  - Creates `VolatilityAnalyzer` instance
  - Analyzes all symbols with `analyze_all_symbols()`
  - Exports detailed CSV: `reports/volatility_analysis.csv`
  - Adds volatility summary to reports dictionary
  - Console output includes volatility CSV path

### Technical
- **Dependencies**: Uses existing pandas library for rolling window calculations
- **Performance**: Analyzes 365 days of data by default
- **Data Flow**: Database → VolatilityAnalyzer → CSV + Excel summary
- **Testing**: 80 total tests passing (was 74, added 6 new)

### Documentation
- Volatility metrics help identify:
  - Price stability/instability patterns
  - Risk levels for trading strategies
  - Comparative volatility between cryptocurrencies
  - Frequency of significant price movements

## [2.9.2] - 2025-12-12

### Fixed
- **Column Order Correction**: Moved MEDIAN before MAD for better logical grouping
  - Previous: K=MEDIAN, L-O=Comparisons, P=MAD, Q=MED-MAD, R-U=Comparisons
  - Current: K-N=Mean Comparisons, O=MEDIAN, P=MAD, Q=MED-MAD, R-U=Median Comparisons
  - Now follows sequence: Statistics → Comparisons → Robust Statistics → Robust Comparisons
  
### Changed
- Updated all formula references to use correct column positions
  - MEDIAN: K → O
  - MED-MAD formula: `=K-P` → `=O-P`
  - Median comparison formulas now reference column O instead of K
  
- Updated COLUMN_STRUCTURE.md with correct column mapping

## [2.9.1] - 2025-12-12

### Changed
- **Column Width Optimization**: Reduced column widths for more compact display
  - Favorite column: 3.29 → 3
  - Symbol column: 8.29 → 7
  - Quote columns: 10 → 9
  - Statistics columns: 10 → 8.5
  
- **Header Alignment**: Aligned headers to top of cells with `vertical='top'`
  - Allows for more compact row height while maintaining readability
  - Header row height set to 30 for optimal display with wrapped text
  
### Result
- More data visible on screen without scrolling
- Maintains readability with 9pt font and top alignment

## [2.9.0] - 2025-12-12

### Changed
- **Column Headers**: Replaced Portuguese headers with English abbreviations for compactness
  - Símbolo → Symbol
  - Última/Penúltima Cotação → Last/2nd Last
  - Período → Period
  - Mínimo/Máximo → MIN/MAX
  - Média/Desvio → AVG/STD
  - Média-Desvio → AVG-STD
  - Mediana → MEDIAN
  - Mediana-MAD → MED-MAD
  - Percentage columns use abbreviated format (Last-AVG%, Last-A-S%, 2nd-AVG%, 2nd-A-S%, etc.)

- **Font Size**: Reduced font size for all numeric data to 9pt for better density
  - Applies to: quotes (columns C, D), statistics (F-K, P-Q), and all percentage columns (L-O, R-U)
  - Headers and symbol remain at default size
  - Period column reduced to 9pt

### Technical
- All numeric cells now use `Font(size=9)` for consistency
- Bold quotes maintain size=9 for uniformity

## [2.8.0] - 2025-12-12

### Changed
- **Column Reorganization**: Complete restructure of Excel report columns for better logical grouping
  - Grouped mean-based statistics together (F-J): Min, Max, Média, Desvio, Média-Desvio
  - Placed Mediana separately (K) as central robust statistic
  - Grouped mean comparisons (L-O): Últ-Média %, Últ-Méd-STD %, Penúlt-Média %, Penúlt-Méd-STD %
  - Grouped median-based statistics (P-Q): MAD, Mediana-MAD
  - Grouped median comparisons (R-U): Últ-Mediana %, Últ-Med-MAD %, Penúlt-Mediana %, Penúlt-Med-MAD %
  - Total: 21 columns (A-U)

### Added
- **COLUMN_STRUCTURE.md**: Comprehensive documentation of column structure and formula validation

### Fixed
- **Column Names**: Updated all column headers to match formulas accurately
  - "Méd-STD" instead of "M-D" for clarity (Mean minus Standard Deviation)
  - "Med-MAD" for Median minus MAD consistency

## [2.7.0] - 2025-12-12

### Added
- **Median-MAD Deviation Columns**: Added 2 new columns for robust deviation analysis
  - Column R: Últ. Dif. Med-MAD % - Latest quote deviation from Median-MAD baseline
  - Column S: Penúlt. Dif. Med-MAD % - Second latest quote deviation from Median-MAD baseline
  - Provides outlier-resistant alternative to Mean-Std deviations
  - Same conditional formatting (green/red) as other deviation columns

### Changed
- **Report Structure**: Expanded from 17 to 19 columns (A-S)
  - Auto-filter updated to cover all 19 columns
  - Title merge adjusted to column S
  - All tests passing

## [2.6.0] - 2025-12-12

### Added
- **Median and MAD Statistics**: Enhanced report with robust statistical measures
  - Median (column I): Central tendency measure less sensitive to outliers than mean
  - MAD (column K): Median Absolute Deviation - robust dispersion measure
  - Median-MAD (column M): Formula-based calculation (Median - MAD)
  - These provide alternative statistical baselines for price analysis
  
### Changed
- **Report Structure**: Expanded from 14 to 17 columns (A-Q)
  - Column layout: Fav, Símbolo, Última, Penúltima, Período, Mínimo, Máximo, Média, **Mediana**, Desvio, **MAD**, Média-Desvio, **Mediana-MAD**, Últ.Dif.Média%, Últ.Dif.M-D%, Penúlt.Dif.Média%, Penúlt.Dif.M-D%
  - Deviation columns shifted: N-Q (previously K-N)
  - Auto-filter and title merge updated to column Q
  
### Technical
- Updated `StatisticalAnalyzer.calculate_statistics()` to include median and MAD
- Enhanced `_write_period_stats()` with new column writes
- Adjusted all column references in deviation formulas
- All 75 tests passing

## [2.5.5] - 2025-12-09

### Fixed
- **Report Layout Corrections**: Fixed column alignment issues from v2.5.4
  - Última Cotação correctly placed in column C
  - Penúltima Cotação correctly placed in column D
  - Período moved to column E (after quotes)
  - All deviation formulas (columns K-N) now reference correct quote columns
  - Removed duplicate and incomplete code

### Changed
- **Period Order**: Inverted to descending order - 12M → 6M → 3M → 1M (12 months first)
- **Data Repetition**: Favorite marker and Symbol now filled in all 4 rows per cryptocurrency
  - Enables proper filtering without cell merging
  - Maintains Excel auto-filter functionality
- **Title Formatting**: 
  - Title merge adjusted to match report width (A1:N1)
  - Row heights adjusted: title row = 25, date row = 18

### Removed
- Cell merging for columns A and B (broke auto-filter functionality)

## [2.5.4] - 2025-12-09

### Changed
- **Excel Report Layout**: Redesigned summary sheet to display 4 analysis periods (1M, 3M, 6M, 12M) in separate rows per cryptocurrency instead of columns
  - Each cryptocurrency now occupies 4 consecutive rows, one for each time period
  - Period column added to identify the analysis timeframe (1M, 3M, 6M, 12M)
  - Simplified horizontal structure: 14 columns instead of 40+
  - Improved readability: Direct vertical comparison of periods
  - Symbol and favorite marker only displayed on first row (1M period) to reduce visual clutter
  - Maintained all statistical metrics: Min, Max, Mean, Std Dev, Mean-Std, and deviation percentages
  - Auto-filter and freeze panes adjusted for new layout
  - Period order changed to ascending: 1 month → 3 months → 6 months → 12 months

### Benefits
- More direct observation and comparison of different time periods
- Easier to spot trends across periods for a single cryptocurrency
- Better use of screen width, reduced horizontal scrolling
- More compact and organized presentation

## [2.5.3] - 2025-12-08

### Added
- Git support in virtual environment activation scripts (both PowerShell and CMD)
  - Modified `venv\Scripts\Activate.ps1` to include Git in PATH
  - Modified `venv\Scripts\activate.bat` to include Git in PATH
  - Git now available automatically when activating venv

### Removed
- Cleaned up redundant documentation files:
  - `VENV_GUIDE.md` (covered by setup.cmd and README)
  - `VENV_SETUP.md` (covered by setup.cmd and README)
  - `START_HERE.md` (covered by QUICKSTART.md)
  - `IMPROVEMENTS.md` (covered by CHANGELOG.md)
  - `INDEX.md` (README serves as entry point)
  - `migrate_to_yfinance.cmd` (migration completed long ago)
  - `import_btc_history.cmd` (file was already deleted)

### Fixed
- Restored project to last GitHub commit state (removed incomplete Binance integration)
- Git PATH configuration for Windows environment

## [2.5.2] - 2025-12-08

### Changed
- Reorganized Excel report headers: moved main column headers (Fav, Símbolo, Última Cotação, Penúltima Cotação) from row 4 to row 5
- Unified header formatting: both header rows (4 and 5) now use consistent blue background (4472C4) with white text
- Applied auto_filter to row 5 for better data filtering

### Fixed
- Fixed mean calculation to use actual computed values instead of Excel formula `=(MIN+MAX)/2`
- Reduced header font size from 9 to 8 for better readability
- Added borders to merged period header cells

## [2.5.1] - 2025-12-06

### Changed
- Renamed Excel report from `crypto_analysis.xlsx` to `AnaliseCrypto.xlsx`

### Fixed
- Fixed missing `NUMBER_FORMAT_DECIMAL` constant in ExcelReporter class
- Fixed method name typo: `create_detailed_sheet` → `create_detail_sheet`

### Added
- Comprehensive test suite for ExcelReporter (7 new tests)
- Tests now validate class constants, method names, and actual report generation
- All 22 tests pass in ~7s

## [2.5.0] - 2025-12-06

### Added
- **SonarLint integration**: Configured SonarLint with Java 25 for real-time code analysis
- **Code quality constants**: Added NUMBER_FORMAT_DECIMAL and DEFAULT_SYMBOLS to reduce duplication

### Changed
- **Code quality improvements**: Fixed all SonarQube warnings for duplicated literals, unused variables, and deprecated methods
- **Timezone handling**: Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
- **API cleanup**: Removed unused `close_of_day` parameter from `fetch_and_parse` method

### Fixed
- **SonarQube issues**: Resolved 15+ code quality issues including:
  - Duplicate string literals replaced with constants
  - Unused local variables removed
  - Unnecessary f-strings corrected
  - Identical branches consolidated
  - Deprecated datetime methods updated

## [2.4.0] - 2025-12-04

### Added
- **Expanded coverage**: Market cap threshold reduced to $100M (from $250M), adding 31 new cryptocurrencies
- **Favorites column**: New column A in reports with "X" marker and gold highlighting for favorite cryptos
- **Excel formulas**: Dynamic formulas for Mean, Mean-StdDev, and all deviation calculations
- **Test coverage**: Added pytest support and coverage reporting for SonarQube integration
- **Shell integration**: VS Code settings configured for improved terminal command detection

### Changed
- **Report structure**: Adjusted column widths (A=23px, B=58px) and header font size to 9
- **Column reduction**: Removed variation columns (Var. Dif. Média %, Var. Dif. M-D %) to simplify reports
- **Version bump**: Updated to 2.4.0 across all files

### Removed
- **CoinMarketCap legacy code**: Deleted obsolete `src/api.py` and related scripts
- **Unused imports**: Removed import_coinmarketcap_csv.py, import_csv.py, old seed_large_cryptos.py
- **Documentation cleanup**: Removed all CMC_API_KEY references from README, TECHNICAL, START_HERE, VENV_SETUP
- **Test cleanup**: Removed CoinMarketCap-related test code

### Fixed
- **SonarQube coverage**: Added Python test execution to GitHub Actions workflow for proper coverage reporting
- **Test suite**: Updated `test_seed_large_cryptos_unittest.py` to match refactored yfinance-based seeding
- **README accuracy**: Updated dependencies, version numbers, and market cap thresholds

## [2.3.0] - 2025-12-03

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
