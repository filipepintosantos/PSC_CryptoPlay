
# Quick Start Guide

**Versão: 4.3.15**

**Tempo de setup: ~5 minutos**

## 1️⃣ Instalação

```bash
setup.bat
 
### Criação da base de dados a partir do SQL

Se preferir criar a base de dados diretamente a partir de um script SQL, o ficheiro
`scripts/create_schema.sql` contém o DDL necessário. O `setup.bat` (via `init_db.py`) irá
aplicar automaticamente esse script quando a BD ainda não existir. Para forçar a criação
manual, execute:

```bash
python init_db.py --db-path data/crypto_prices.db
```

Nota: o esquema agora contém uma tabela `schema_info` com uma coluna `version`.
```

### Criação da base de dados a partir do SQL

Se preferir criar a base de dados diretamente a partir de um script SQL, o ficheiro
`scripts/create_schema.sql` contém o DDL necessário. O `setup.bat` (via `init_db.py`) irá
aplicar automaticamente esse script quando a BD ainda não existir. Para forçar a criação
manual, execute:

```bash
python init_db.py --db-path data/crypto_prices.db
```



## 2️⃣ Primeira Execução

```bash

# Interface gráfica (desktop)
run_ui.cmd

# Novidades v4.3.6
- Menu "Consultar Base de Dados":
	- Lista de Moedas: Visualiza todas as moedas cadastradas
	- Cotações: Consulta todas as cotações históricas
- Menu "Atualizar Dados":
	- Atualização Diária
	- Reavaliar Moedas
	- Forçar Atualização

# Ou modo linha de comando:
python main.py --all-symbols --fetch-mode full
```

## 3️⃣ Relatório Excel

Abra `reports/AnaliseCrypto.xlsx`:
- **Sheet "Resumo"**: Filtros nos cabeçalhos 🔽
- Verde = preço acima da média | Vermelho = abaixo
- **Sheets individuais**: Análise por moeda

## 4️⃣ Atualizações Seguintes

```bash
# Modo auto-range (recomendado - apenas dados novos)
update_quotes.cmd

# Ou último N dias
python main.py --all-from-db --days 7

# Só regenerar relatório
python main.py --report-only
```

## 🔄 Modo Auto-Range (Novo em 3.6.0!)

Busca automaticamente apenas cotações faltantes:

```bash
update_quotes.cmd  # Desde última cotação até ontem
```

**Migração de BD existente:**
```bash
python scripts/add_last_quote_date_column.py
```

## 📋 Comandos Frequentes

| Tarefa | Comando |
|--------|---------|
| Atualizar dados | `update_quotes.cmd` |
| Adicionar moeda | `python main.py --symbols BTC,ETH,NOVO` |
| Últimos N dias | `python main.py --all-from-db --days 30` |
| Só relatório | `python main.py --report-only` |
| Migrar BD | `python scripts/add_last_quote_date_column.py` |

## ⚙️ Personalizar

Edite `config/config.ini`:

```ini
[symbols]
favorites = BTC,ETH,ADA
all = BTC,ETH,ADA,XRP,SOL,DOGE,LTC

[fetch]
mode = incremental
```

## 🔄 Agendamento Automático

1. Task Scheduler → New Basic Task
2. Trigger: Daily 8:00 AM
3. Action: `python main.py --all-from-db --auto-range`

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| "No module found" | `pip install -r requirements.txt` |
| Excel não abre | Feche e regenere: `python main.py --report-only` |
| Muito lento | Use `--fetch-only`, gere relatório depois |

## ✨ Features Principais

## 🧪 Testes

- A suite de testes (`run_tests.cmd` / `python -m unittest discover`) executa um handler de limpeza que remove automaticamente quaisquer ficheiros de BD de teste `data/test*.db` ao terminar. Para preservar um DB de teste, mova-o antes de executar os testes.


✅ Cotações em EUR via Yahoo Finance  
✅ Estatísticas: min, max, média, desvio padrão  
✅ Relatórios Excel com filtros  
✅ Modo auto-range (busca só dados novos)  
✅ Sistema de favoritos A/B/C  
✅ 101 testes automatizados

---

**Ajuda completa**: `python main.py --help`
