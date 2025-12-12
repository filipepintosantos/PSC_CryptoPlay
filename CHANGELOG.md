# Changelog

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
