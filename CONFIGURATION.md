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

## Sistema de Favoritos (Classes A, B, C)

### Classificação por Prioridade

O sistema permite classificar criptomoedas em 3 níveis:

- **Classe A**: Prioridade máxima (top priority)
- **Classe B**: Prioridade secundária
- **Classe C**: Prioridade terciária

### Configuração no config.ini

```ini
[symbols]
# Classe A: Top priority
favorites_a = BTC,ETH,SOL,ADA,LINK,ATOM,XTZ

# Classe B: Secondary priority
favorites_b = XRP,BNB,TRX,DOGE,DOT,AVAX

# Classe C: Tertiary priority
favorites_c = BCH,XMR,XLM,LTC,AAVE
```

### Funções de Base de Dados

```python
# Definir classe
db.set_favorite_class(code, 'A')  # A, B, C ou None

# Buscar por classe
db.get_all_crypto_info(favorite_class='A')      # Apenas A
db.get_all_crypto_info(favorites_only=True)     # Todas as classes
```

### Visualização no Excel

- Classe A: 🟡 Dourado
- Classe B: 🟠 Laranja
- Classe C: 🔵 Azul Claro

### Scripts

```bash
# Adicionar com classificação
python scripts/add_symbols.py MATIC ALGO --class B

# Ver favoritos atuais
python scripts/mark_favorites.py
```

## Workflow Recomendado

### 1. Primeira Execução

```bash
# Configure config/config.ini
python main.py --all-symbols --fetch-mode full
```

### 2. Execuções Diárias

```bash
# Atualização inteligente (auto-range)
update_quotes.cmd

# Ou manual
python main.py
```

### 3. Atualização Completa Periódica

```bash
# Semanal/mensal
python main.py --all-symbols --fetch-mode full
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| "No such file config.ini" | Crie o arquivo baseado no exemplo |
| Símbolos não aparecem | Verifique nome correto (BTC, não bitcoin) |
| Modo incremental não funciona | Use `--fetch-mode full` |
| Performance lenta | Reduza número de símbolos |

---

**PSC CryptoPlay © 2025**
