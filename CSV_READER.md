# CSV Reader Module

Módulo robusto para leitura e importação de dados de criptomoedas a partir de ficheiros CSV.

## Características

- 📖 **Leitura flexível**: Suporta diferentes formatos de CSV (delimitadores, codificação, headers)
- 📅 **Datas automáticas**: Auto-detecção de formatos de data comuns
- 💰 **Preços com símbolos**: Parsing inteligente com símbolos de moeda (€, $, £, ¥)
- 🗂️ **Mapeamento de colunas**: Funciona com índices numéricos ou nomes de coluna
- ⚙️ **Configuração flexível**: Classe `CSVConfig` para customização
- ✅ **Validação**: Tratamento robusto de erros e linhas inválidas

## Instalação

O módulo é parte do projeto PSC_CryptoPlay. Não requer instalação adicional além das dependências do projeto.

## Uso

### Forma 1: Via Script da Linha de Comando

```bash
# Uso básico
python scripts/import_from_csv.py BTC_prices.csv BTC

# Com opções customizadas
python scripts/import_from_csv.py prices.csv BTC \
    --date-col Date \
    --price-col Price \
    --date-format "%d-%m-%Y"

# Sem linha de cabeçalho
python scripts/import_from_csv.py prices.csv BTC --no-header

# Delimiter diferente
python scripts/import_from_csv.py prices.csv BTC --delimiter ";"

# Modo seco (validar sem importar)
python scripts/import_from_csv.py prices.csv BTC --dry-run
```

### Forma 2: Como Módulo Python

```python
from src.csv_reader import CSVReader, CSVConfig, import_crypto_data

# Configuração básica
config = CSVConfig(
    date_column='Date',
    price_column='Price',
    date_format='%Y-%m-%d'
)

# Ler ficheiro
reader = CSVReader(config)
rows = reader.read_file('data/BTC_prices.csv')

# Processar dados
for row in rows:
    print(f"{row['date']} → €{row['price']:.2f}")

# Importar para base de dados
from src.database import CryptoDatabase

db = CryptoDatabase('data/crypto_prices.db')
for row in rows:
    quote = {
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'close_eur': row['price'],
        'timestamp': row['date']
    }
    db.insert_or_update_quote('BTC', quote)
db.close()
```

### Forma 3: Função Convenience

```python
from src.csv_reader import import_crypto_data, CSVConfig

config = CSVConfig(date_column='Date', price_column='Price')
quotes = import_crypto_data('BTC_prices.csv', 'BTC', config)

# quotes é uma lista de dicts pronta para a base de dados
for quote in quotes:
    print(quote)
```

## Configuração (CSVConfig)

```python
from src.csv_reader import CSVConfig

config = CSVConfig(
    date_column='Date',           # Nome da coluna ou índice (0-based)
    price_column='Price',         # Nome da coluna ou índice
    has_header=True,              # CSV tem linha de cabeçalho?
    encoding='utf-8',             # Codificação do ficheiro
    delimiter=',',                # Separador de campos
    date_format='%Y-%m-%d',       # Formato de data, ou None para auto-detecção
    skip_rows=0                   # Linhas a ignorar no início
)
```

### Detecção Automática de Datas

Se `date_format=None`, o módulo tenta os seguintes formatos:
- `%Y-%m-%d` (ISO 8601)
- `%d-%m-%Y`
- `%m-%d-%Y`
- `%Y/%m/%d`
- `%d/%m/%Y`
- `%m/%d/%Y`
- `%Y-%m-%d %H:%M:%S` (com hora)
- `%d-%m-%Y %H:%M:%S` (com hora)
- ISO8601 (via `fromisoformat()`)

## Exemplos de Ficheiros CSV

### Exemplo 1: Formato simples com cabeçalho

```csv
Date,Price
2025-01-01,45000.50
2025-01-02,45500.25
2025-01-03,44800.75
```

### Exemplo 2: Com símbolos de moeda

```csv
Data,Cotação
01-01-2025,€45.000,50
02-01-2025,€45.500,25
03-01-2025,€44.800,75
```

### Exemplo 3: Sem cabeçalho, com delimiter diferente

```csv
2025-01-01;45000.50
2025-01-02;45500.25
2025-01-03;44800.75
```

Uso:
```python
config = CSVConfig(
    has_header=False,
    delimiter=';',
    date_column=0,
    price_column=1
)
```

### Exemplo 4: Colunas reordenadas

```csv
Preço,Criptomoeda,Data,Variação
45000.50,BTC,2025-01-01,+1.2%
45500.25,BTC,2025-01-02,+1.1%
44800.75,BTC,2025-01-03,-1.5%
```

Uso:
```python
config = CSVConfig(
    date_column='Data',
    price_column='Preço'
)
```

## API Completa

### Classe `CSVReader`

#### `__init__(config: CSVConfig = None)`
Inicializa o leitor com configuração opcional.

#### `read_file(file_path) -> List[Dict]`
Lê e processa um ficheiro CSV.

Retorna lista de dicts com chaves:
- `date`: datetime object
- `price`: float
- `date_str`: string original da data
- `price_str`: string original do preço

#### `read_and_validate(file_path) -> Tuple[List[Dict], List[str]]`
Lê ficheiro e retorna dados + avisos.

#### `guess_config(file_path) -> CSVConfig`
Tenta adivinhar a configuração apropriada (estático).

### Métodos Estáticos

#### `_parse_date(date_str, date_format=None) -> datetime`
Parse de data com auto-detecção ou formato específico.

#### `_parse_price(price_str) -> float`
Parse de preço com remoção de símbolos de moeda.

## Testes

O módulo inclui 18 testes unitários:

```bash
pytest tests/test_csv_reader.py -v
```

Cobre:
- Configuração padrão e customizada
- Parsing de datas com vários formatos
- Parsing de preços com símbolos
- Leitura de ficheiros CSV
- Delimitadores diferentes
- Skipping de linhas
- Tratamento de erros

## Tratamento de Erros

O módulo trata graciosamente vários tipos de erros:

```python
try:
    rows = reader.read_file('nonexistent.csv')
except FileNotFoundError:
    print("Ficheiro não encontrado")

try:
    price = CSVReader._parse_price("INVALID")
except ValueError:
    print("Não conseguiu fazer parse do preço")

try:
    date = CSVReader._parse_date("01-13-2025")  # Mês inválido
except ValueError:
    print("Não conseguiu fazer parse da data")
```

## Script de Linha de Comando

O script `scripts/import_from_csv.py` oferece uma interface completa:

```bash
python scripts/import_from_csv.py --help

# Exemplo com saída detalhada
python scripts/import_from_csv.py data/BTC.csv BTC --dry-run
```

Opções:
- `--date-col`: Nome ou índice da coluna de data
- `--price-col`: Nome ou índice da coluna de preço
- `--date-format`: Formato de data (strftime)
- `--no-header`: Sem linha de cabeçalho
- `--skip-rows`: Linhas a ignorar
- `--delimiter`: Separador de campos
- `--encoding`: Codificação (default: utf-8)
- `--db`: Caminho da base de dados
- `--dry-run`: Validar sem importar

## Integração com Sistema Existente

O módulo CSV Reader complementa a funcionalidade existente:

- **main.py**: A função `import_csv_data()` original continua a funcionar
- **csv_reader.py**: Novo módulo mais robusta e flexível
- **scripts/import_from_csv.py**: Interface amigável de CLI

Use o CSV Reader quando precisar de:
- Parsing mais flexible de datas
- Suporte para mais formatos de ficheiro
- Validação pré-import
- Lógica de parsing reutilizável em outras partes do código

## Limitações e Melhorias Futuras

- ✓ Auto-detecção de delimiter (Sniffer do csv)
- ⚠️ Não suporta ficheiros muito grandes (carrega tudo em memória)
- 💡 Possível: processamento streaming para ficheiros grandes
- 💡 Possível: detecção automática de coluna de data/preço
- 💡 Possível: merge de múltiplas colunas de preço

## Licença

Parte do projeto PSC_CryptoPlay
