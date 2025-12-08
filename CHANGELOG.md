# Changelog

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
