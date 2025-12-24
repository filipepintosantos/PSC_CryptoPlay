
# Documentação Técnica - PSC CryptoPlay


## Novidades v4.3.6
- Menu lateral: nova entrada "Consultar Base de Dados" com submenus:
    - Lista de Moedas: mostra tabela crypto_info
    - Cotações: mostra tabela price_quotes
- Menu "Ferramentas" com submenus "Configurações" e "Ajuda" (mostra README.md na área de trabalho)
- "Atualização Diária" executa update_quotes.cmd e mostra o output na área de trabalho

## Arquitetura do Sistema

```
┌─────────────────┐
│   main.py       │  Orquestrador principal
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────────┐
    │          │          │              │
    v          v          v              v
┌──────┐   ┌────────┐ ┌────────┐    ┌────────────┐
│ API  │   │Database│ │Analysis│    │ExcelReporter
│      │   │        │ │        │    │            │
└──────┘   └────────┘ └────────┘    └────────────┘
    │          │          │              │
    └─────────►│◄─────────┴──────────────┘
               │
         ┌─────▼─────┐
         │  SQLite   │
         │  DB       │
         └───────────┘
```

## Módulos

### 1. api.py - CoinMarketCapAPI

**Responsabilidades:**
- Conectar à API do CoinMarketCap
- Recuperar quotações em EUR
- Parsear dados de resposta

**Classes principais:**
- `CoinMarketCapAPI`: Gerencia conexão e requisições

**Métodos principais:**
- `get_latest_quotes(symbols)`: Busca quotações mais recentes
- `parse_quotes(data, symbols)`: Extrai dados relevantes
- `fetch_and_parse(symbols)`: Integra fetch + parse

**Dados Capturados:**
```python
{
    "symbol": "BTC",
    "name": "Bitcoin",
    "price_eur": 45000.50,
    "market_cap_eur": 900000000.00,
    "volume_24h_eur": 25000000.00,
    "percent_change_24h": 2.50,
    "percent_change_7d": -1.20,
    "percent_change_30d": 15.00,
    "timestamp": datetime.now()
}
```

### 2. database.py - CryptoDatabase

**Responsabilidades:**
- Gerenciar conexão SQLite
- Criar e manter tabelas
- Inserir e recuperar dados

**Classes principais:**
- `CryptoDatabase`: Gerenciador SQLite

**Tabelas:**

#### cryptocurrencies
```sql
id INTEGER PRIMARY KEY
symbol TEXT UNIQUE NOT NULL
name TEXT NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### price_quotes
```sql
id INTEGER PRIMARY KEY
crypto_id INTEGER (FK)
price_eur REAL
market_cap_eur REAL
volume_24h_eur REAL
percent_change_24h REAL
percent_change_7d REAL
percent_change_30d REAL
timestamp TIMESTAMP NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Métodos principais:**
- `add_cryptocurrency(symbol, name)`: Adiciona criptomoeda
- `insert_quote(symbol, quote_data)`: Insere quotação
- `insert_quotes_batch(quotes)`: Insere múltiplas quotações
- `get_quotes(symbol, days)`: Recupera quotações por período
- `get_latest_quote(symbol)`: Obtém quotação mais recente
- `get_all_symbols()`: Lista todas as criptomoedas

### 3. analysis.py - StatisticalAnalyzer

**Responsabilidades:**
- Calcular estatísticas dos preços
- Analisar períodos rolantes
- Gerar relatórios

**Classes principais:**
- `StatisticalAnalyzer`: Análise estatística

**Períodos Análisados:**
- 12_months: 365 dias
- 6_months: 182 dias
- 3_months: 91 dias
- 1_month: 30 dias

**Métricas Calculadas:**
```python
{
    "min": float,              # Preço mínimo
    "max": float,              # Preço máximo
    "mean": float,             # Média
    "std": float,              # Desvio padrão
    "mean_minus_std": float,   # Média - Desvio Padrão
    "count": int               # Número de pontos de dados
}
```

**Métodos principais:**
- `calculate_statistics(prices)`: Calcula estatísticas
- `analyze_rolling_periods(df)`: Análise por períodos
- `prepare_dataframe_from_quotes(quotes)`: Prepara DataFrame
- `generate_report(symbol, quotes)`: Gera relatório completo
- `batch_generate_reports(symbols, func)`: Múltiplos relatórios

**Resultado da Análise:**
```python
{
    "symbol": "BTC",
    "data_points": 100,
    "date_range": {
        "start": "2024-01-01T00:00:00",
        "end": "2024-12-01T00:00:00"
    },
    "periods": {
        "12_months": {
            "stats": {...},
            "latest_quote": 45000.50,
            "latest_deviation_from_mean": 1500.25,
            "latest_deviation_from_mean_minus_std": 2000.75
        },
        ...
    }
}
```

### 4. excel_reporter.py - ExcelReporter

**Responsabilidades:**
- Criar workbooks Excel
- Formatar sheets com estilos
- Exportar relatórios

**Classes principais:**
- `ExcelReporter`: Gerador de Excel

**Sheets Criadas:**
1. **Resumo**: Todas as criptomoedas em uma tabela
2. **Detalhado**: Uma sheet por criptomoeda

**Formatação:**
- Headers azuis com texto branco
- Sub-headers cinzas
- Números com 8 casas decimais
- Bordas em todas as células
- Cores de highlight para desvios (verde/vermelho)
- Colunas redimensionadas automaticamente

**Métodos principais:**
- `create_summary_sheet(reports)`: Sheet de resumo
- `create_detailed_sheet(symbol, report)`: Sheet detalhada
- `save()`: Salva workbook
- `generate_report(reports)`: Gera relatório completo

### 5. main.py - Orquestrador

**Fluxo Principal:**
1. Parse de argumentos CLI
2. Inicializa banco de dados
3. Fetch de quotações (se não --report-only)
4. Insere dados no banco
5. Gera análise estatística
6. Cria relatório Excel
7. Exibe resumo

**Argumentos:**
- `--symbols`: Lista de criptomoedas (padrão: BTC,ETH,ADA,XRP,SOL)
- `--api-key`: Chave CoinMarketCap
- `--db-path`: Caminho do banco SQLite
- `--report-path`: Caminho do Excel
- `--fetch-only`: Apenas buscar dados
- `--report-only`: Apenas gerar relatório

## Fluxo de Dados

```
CoinMarketCap API
        │
        ▼
  api.py fetch_and_parse()
        │
        ├─ get_latest_quotes()  ──► HTTP Request
        │
        └─ parse_quotes()  ──────► Dict com dados
               │
               ▼
  main.py insert_quotes_batch()
               │
               ▼
  database.py insert_quote()  ──► SQLite INSERT
               │
               ▼
  analysis.py batch_generate_reports()
               │
               ├─ get_quotes()  ────► SQLite SELECT
               │
               └─ generate_report()  ──► Stats calculadas
                      │
                      ▼
  excel_reporter.py generate_report()
                      │
                      ├─ create_summary_sheet()
                      │
                      ├─ create_detailed_sheet()  (×N)
                      │
                      └─ save()  ──► XLSX File
```

## Dependências Externas

- **requests**: HTTP library para API calls
- **pandas**: DataFrames para análise de dados
- **openpyxl**: Criação de arquivos Excel
- **python-dotenv**: Carregamento de variáveis de ambiente

## Tratamento de Erros

### API
- Validação de chave de API
- Tratamento de timeouts
- Parsing de erros de resposta

### Database
- Verificação de permissões de arquivo
- Tratamento de duplicatas
- Criação automática de diretórios

### Analysis
- Validação de dados vazios
- Tratamento de NaN/infinity
- Logging de erros

### Excel
- Criação automática de diretórios
- Tratamento de caracteres especiais
- Limpeza de worksheets existentes

## Performance

- **In-memory SQLite**: Opção para testes
- **Indexed Queries**: Índice em (crypto_id, timestamp)
- **Batch Operations**: Inserção múltipla de quotações
- **DataFrame Optimization**: Uso de pandas para análise

## Segurança

- **API Key**: Armazenada em .env (não commitada)
- **Input Validation**: Sanitização de símbolos
- **SQL Injection Prevention**: Uso de prepared statements
- **File Permissions**: Criação com permissões padrão

## Estrutura de Colunas do Relatório Excel (21 colunas: A-U)

### Colunas Base (A-E)
- **A**: Favorito (A, B, C ou vazio)
- **B**: Símbolo (BTC, ETH, etc.)
- **C**: Última Cotação
- **D**: Penúltima Cotação
- **E**: Período (12M, 6M, 3M, 1M)

### Estatísticas Baseadas em Média (F-J)
- **F**: Mínimo | **G**: Máximo | **H**: Média
- **I**: Desvio Padrão | **J**: Média-Desvio (H-I)

### Comparações com Média (K-N)
- **K**: Last-AVG% = (C-H)/H
- **L**: Last-A-S% = (C-J)/J
- **M**: 2nd-AVG% = (D-H)/H
- **N**: 2nd-A-S% = (D-J)/J

### Estatísticas Baseadas em Mediana (O-Q)
- **O**: MEDIAN | **P**: MAD | **Q**: MED-MAD (O-P)

### Comparações com Mediana (R-U)
- **R**: Last-MED% = (C-O)/O
- **S**: Last-M-M% = (C-Q)/Q
- **T**: 2nd-MED% = (D-O)/O
- **U**: 2nd-M-M% = (D-Q)/Q

## Extensibilidade

**Adicionar criptomoedas:**
```bash
python main.py --symbols BTC,ETH,NEW
```

**Adicionar métricas:**
Estender `calculate_statistics()` em `analysis.py`

**Modificar relatório:**
Alterar `ExcelReporter` em `excel_reporter.py`

## Testes

```bash
# Executar testes
run_tests.cmd

# Com cobertura
pytest --cov=src --cov-report=html
```

**101 testes** cobrindo: database, análise estatística, API, volatilidade.

---

**PSC CryptoPlay © 2025**
