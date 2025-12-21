# Atualização: Coluna last_quote_date e Modo Auto-Range

## Data: 21 de Dezembro de 2025

## Resumo das Alterações

Foram implementadas melhorias no sistema de atualização de cotações para rastrear a data da cotação mais recente e otimizar o processo de atualização.

## Mudanças Implementadas

### 1. Nova Coluna na Tabela crypto_info

- **Coluna adicionada**: `last_quote_date` (tipo DATE)
- **Propósito**: Armazenar a data da cotação mais recente para cada criptomoeda
- **Valor padrão**: NULL (para criptomoedas sem cotações)

### 2. Novos Métodos no database.py

#### `update_last_quote_date(symbol: str) -> bool`
- Atualiza a coluna `last_quote_date` na tabela `crypto_info`
- Define o valor como a data mais recente da tabela `price_quotes` para o símbolo especificado
- Chamado automaticamente após cada inserção/atualização de cotação

#### `get_last_quote_date_for_symbol(symbol: str) -> Optional[datetime]`
- Retorna a data da última cotação de um símbolo específico
- Busca o valor da coluna `last_quote_date` na tabela `crypto_info`
- Retorna None se não houver dados

### 3. Modificações no Processo de Atualização

#### Modo Auto-Range
- **Novo argumento**: `--auto-range`
- **Comportamento**: Para cada criptomoeda, busca cotações desde a data da última cotação até ontem
- **Vantagem**: Reduz o tráfego de API e evita buscar dados duplicados

#### Modificações em api_yfinance.py
- O método `fetch_historical_range()` agora aceita um parâmetro opcional `start_date`
- Se `start_date` for fornecido, busca desde essa data até ontem
- Mantém compatibilidade com o parâmetro `days` existente

#### Modificações em main.py
- A função `fetch_historical_range()` agora aceita parâmetro `auto_range`
- Em modo auto-range:
  - Verifica a última data de cotação para cada símbolo
  - Se existir, busca desde o dia seguinte até ontem
  - Se não existir, busca os últimos 365 dias (fallback)
- O modo auto-range é ativado com `--auto-range` ou é o padrão quando `--days` não é especificado

### 4. Atualização do update_quotes.cmd

**Antes:**
```bat
venv\Scripts\python.exe main.py --all-from-db --days 3
```

**Depois:**
```bat
venv\Scripts\python.exe main.py --all-from-db --auto-range
```

### 5. Script de Migração

**Arquivo**: `scripts/add_last_quote_date_column.py`

**Função**:
- Adiciona a coluna `last_quote_date` em bases de dados existentes
- Popula a coluna com as datas mais recentes da tabela `price_quotes`
- Pode ser executado com: `python scripts/add_last_quote_date_column.py`

**Uso**:
```bash
# Usar base de dados padrão
python scripts/add_last_quote_date_column.py

# Especificar caminho da base de dados
python scripts/add_last_quote_date_column.py --db-path path/to/database.db
```

## Exemplos de Uso

### Atualização Automática (Recomendado)
```bash
# Atualiza todas as criptomoedas desde a última cotação até ontem
python main.py --all-from-db --auto-range

# Ou simplesmente execute o script:
update_quotes.cmd
```

### Buscar Período Específico (Modo Antigo)
```bash
# Buscar últimos 7 dias
python main.py --all-from-db --days 7

# Buscar último ano
python main.py --all-from-db --days 365
```

## Benefícios

1. **Eficiência**: Reduz chamadas desnecessárias à API do Yahoo Finance
2. **Velocidade**: Busca apenas dados novos desde a última atualização
3. **Rastreabilidade**: Permite saber rapidamente quando foi a última cotação de cada moeda
4. **Flexibilidade**: Mantém compatibilidade com o modo antigo usando `--days`

## Compatibilidade

- ✅ Totalmente compatível com bases de dados existentes (use o script de migração)
- ✅ Mantém todos os modos de atualização anteriores
- ✅ Não quebra nenhum comando ou script existente

## Migração de Bases de Dados Existentes

Para bases de dados já em uso:

1. Execute o script de migração:
   ```bash
   python scripts/add_last_quote_date_column.py
   ```

2. O script irá:
   - Adicionar a coluna `last_quote_date` se não existir
   - Popular a coluna com as datas das cotações mais recentes
   - Exibir o resultado para cada criptomoeda

3. Após a migração, o modo `--auto-range` funcionará corretamente

## Notas Técnicas

- A coluna `last_quote_date` é atualizada automaticamente após cada inserção/atualização de cotação
- O método `insert_or_update_quote()` chama `update_last_quote_date()` automaticamente
- Em modo auto-range, se não houver cotações anteriores, busca os últimos 365 dias
- O script de migração é idempotente (pode ser executado múltiplas vezes sem problemas)
