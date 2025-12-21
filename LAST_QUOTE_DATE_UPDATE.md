# Versão 3.6.0 - Auto-Range Update Mode

**Data**: 21 de Dezembro de 2025

## Resumo

Nova funcionalidade de atualização inteligente que busca apenas cotações faltantes desde a última atualização, reduzindo tráfego de API e tempo de execução.

## Principais Alterações

### Nova Coluna: `last_quote_date`
- Adicionada à tabela `crypto_info` (tipo DATE)
- Armazena data da última cotação de cada criptomoeda
- Atualizada automaticamente após inserções

### Novos Métodos (database.py)
- `update_last_quote_date(symbol)` - Atualiza data da última cotação
- `get_last_quote_date_for_symbol(symbol)` - Consulta data da última cotação

### Modo Auto-Range
- **Argumento**: `--auto-range`
- **Comportamento**: Busca desde última cotação até ontem
- **Fallback**: Se sem dados prévios, busca últimos 365 dias
- `fetch_historical_range()` aceita parâmetro `start_date` opcional

### Update Script Otimizado
```bash
# Antes (sempre 3 dias):
python main.py --all-from-db --days 3

# Agora (apenas dados novos):
python main.py --all-from-db --auto-range
# ou simplesmente:
update_quotes.cmd
```

## Migração de BD Existente

```bash
python scripts/add_last_quote_date_column.py
```

Adiciona coluna e popula com datas históricas automaticamente.

## Exemplos de Uso

```bash
# Atualização inteligente (recomendado)
update_quotes.cmd

# Período específico (se necessário)
python main.py --all-from-db --days 7
```

## Benefícios

✅ Reduz chamadas à API  
✅ Execução mais rápida  
✅ Rastreamento de última atualização  
✅ Compatível com modo antigo (`--days`)
