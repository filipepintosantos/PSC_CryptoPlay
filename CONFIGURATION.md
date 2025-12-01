# Guia de Configuração - PSC CryptoPlay

## Arquivo config.ini

O arquivo `config/config.ini` permite personalizar o comportamento da aplicação sem alterar o código.

### Seção [symbols]

Define as listas de criptomoedas a rastrear.

```ini
[symbols]
# Lista completa de criptomoedas (use com --all-symbols)
all = BTC,ETH,ADA,XRP,SOL,DOGE,LTC,BNB,CARDANO,POLKADOT

# Lista de favoritos (padrão quando executa sem flags)
favorites = BTC,ETH,ADA,XRP,SOL
```

**Uso:**
- `python main.py` → usa `favorites`
- `python main.py --favorites` → usa `favorites`
- `python main.py --all-symbols` → usa `all`
- `python main.py --symbols BTC,ETH` → ignora config e usa BTC,ETH

### Seção [fetch]

Controla como os dados são recolhidos.

```ini
[fetch]
# Modo: 'incremental' ou 'full'
mode = incremental

# Se True, atualiza valores quando há duplicatas de timestamp
upsert_duplicates = true
```

**Modos:**

- **incremental**: Continua a partir da última data registada na base de dados
  - Mais eficiente (menos dados transferidos)
  - Ideal para execução diária/horária
  - Não recolhe dados antigos

- **full**: Recolhe desde a data mais antiga disponível
  - Recolhe histórico completo
  - Usa `upsert_duplicates=true` para atualizar dados existentes
  - Ideal para primeira execução ou atualização completa

### Seção [database]

Configuração da base de dados SQLite.

```ini
[database]
# Caminho do ficheiro de base de dados
path = data/crypto_prices.db

# Timeout para operações (segundos)
timeout = 10
```

### Seção [report]

Configuração de relatórios.

```ini
[report]
# Caminho de saída do ficheiro Excel
output_path = reports/crypto_analysis.xlsx

# Incluir sheets detalhadas por criptomoeda
include_detailed_sheets = true
```

### Seção [analysis]

Configuração da análise estatística.

```ini
[analysis]
# Períodos a analisar (não editar diretamente - está hardcoded no código)
periods = ["12_months", "6_months", "3_months", "1_month"]

# Moeda de referência
currency = EUR
```

## Arquivo .env

Configuração de segurança e variáveis de ambiente.

```bash
# Chave de API do CoinMarketCap
CMC_API_KEY=your_actual_api_key_here

# Opcional: Log level
LOG_LEVEL=INFO
```

## Exemplos de Configuração

### Setup Mínimo (Produção)

```ini
[symbols]
all = BTC,ETH,ADA
favorites = BTC,ETH

[fetch]
mode = incremental
upsert_duplicates = true

[database]
path = C:\data\crypto_prices.db
timeout = 30

[report]
output_path = C:\reports\crypto_analysis.xlsx
```

### Setup Desenvolvimento

```ini
[symbols]
all = BTC,ETH,ADA,XRP,SOL,DOGE
favorites = BTC,ETH

[fetch]
mode = full
upsert_duplicates = true

[database]
path = data/test_crypto.db
timeout = 10

[report]
output_path = reports/test_analysis.xlsx
```

### Setup Monitoramento (Múltiplas Moedas)

```ini
[symbols]
all = BTC,ETH,ADA,XRP,SOL,DOGE,LTC,BNB,POLKADOT,CARDANO,MATIC,AVAX
favorites = BTC,ETH,ADA

[fetch]
mode = incremental
upsert_duplicates = false

[database]
path = data/production_crypto.db
timeout = 60
```

## Workflow Recomendado

### 1. Primeira Execução

```bash
# Edite config/config.ini
# Define suas criptomoedas em [symbols]

# Execute em modo full para recolher histórico
python main.py --all-symbols --fetch-mode full

# Isto criará:
# - Banco de dados com histórico
# - Relatório Excel completo
```

### 2. Execuções Diárias

```bash
# Use modo incremental (padrão)
python main.py --fetch-mode incremental

# Ou mais simples (usa favorites)
python main.py
```

### 3. Atualização Completa Periódica

```bash
# Uma vez por semana/mês, recolha tudo novamente
python main.py --all-symbols --fetch-mode full
```

## Troubleshooting

### Erro: "No such file or directory: 'config/config.ini'"

- Certifique-se de que o ficheiro existe em `config/config.ini`
- Se não existir, crie-o baseado no exemplo acima

### Símbolos não aparecem no relatório

- Verifique se o símbolo está correto (ex: `BTC`, não `bitcoin`)
- Certifique-se de que tem dados nesse símbolo na base de dados
- Use `--report-only` para ver dados existentes

### Modo incremental não funciona como esperado

- Verifique se já tem dados na base de dados: `dir data\crypto_prices.db`
- Use `--fetch-mode full` para forçar recolha completa
- Verifique permissões de ficheiro

### Performance lenta

- Aumente `timeout` em `[database]` seção
- Use `--fetch-only` em hora de pico, `--report-only` depois
- Reduza número de símbolos em análise

---

**Última atualização**: Dezembro 2024
