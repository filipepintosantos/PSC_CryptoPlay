# PSC CryptoPlay - Cryptocurrency Price Tracker & Analysis
**Versão: 5.1.1**

## 🚀 Setup Rápido

```bash
setup.cmd
python main.py --all-from-db --days 7000
```

## 🎯 Comandos Principais

```bash
# Atualizar cotações (modo auto-range)
update_quotes.cmd

# Gerar relatório
python main.py --all-from-db --report-only

# Abrir interface gráfica
run_ui.cmd

# Adicionar moeda
python scripts\add_symbols.py

# Testes
run_tests.cmd
```

**Nota:** A suite de testes regista um handler de limpeza que remove automaticamente quaisquer ficheiros de BD de teste `data/test*.db` ao terminar. Se quiseres preservar um DB de teste, mova-o antes de executar os testes.

## 🖥️ Interface Gráfica

Execute `run_ui.cmd` para abrir a interface desktop (PyQt6).

**Funcionalidades:**
- Menu **Consultar Base de Dados**: Lista de Moedas, Cotações Históricas, Transações Binance
- Menu **Atualizar Dados**: Atualização Diária, Reavaliar Moedas, Forçar Atualização
- Menu **Analisar Transações**: Filtros avançados para análise de transações Binance
- **Barra Lateral**: Visualização rápida de moedas e cotações

## 📊 Features

✅ Visualização de moedas e cotações no menu lateral
✅ Yahoo Finance (gratuito, sem API key)
✅ Análise de volatilidade detalhada
✅ Sistema de favoritos A/B/C
✅ Modo auto-range (busca apenas dados novos)
✅ Cliente Binance API com `get_price_at_second`
✅ 135+ testes automatizados
✅ Análise avançada de transações Binance
✅ Relatórios em Excel com análise detalhada

## 📋 Configuração

### config/config.ini

```ini
[symbols]
# Lista de favoritos (padrão)
favorites = BTC,ETH,ADA,XRP,SOL

# Lista completa (use com --all-symbols)
all = BTC,ETH,ADA,XRP,SOL,DOGE,LTC,BNB,CARDANO,POLKADOT

[fetch]
# Modo: 'incremental' ou 'full'
mode = incremental

# Atualizar duplicatas de timestamp
upsert_duplicates = true

[symbols]
# Sistema de favoritos A/B/C
favorites_a = BTC,ETH,SOL
favorites_b = ADA,XRP,LINK
favorites_c = DOT,AVAX,DOGE
```

### Opções de linha de comando

```bash
python main.py                              # Usa favoritos
python main.py --all-from-db --days 365     # Histórico de 365 dias
python main.py --all-symbols                # Todas as moedas
python main.py --symbols BTC,ETH            # Moedas específicas
python main.py --report-only                # Apenas gerar relatório
```

## 🗄️ Base de Dados

- Database schema canonicalizado em `scripts/create_schema.sql`
- On first run, a aplicação executa este script automaticamente
- Schema inclui tabela `schema_info` com controlo de versão
- Triggers automáticos sincronizam `crypto_info.last_quote_date`

## 🧪 Testes

```bash
# Executar todos os testes
run_tests.cmd

# Ou via Python
python -m unittest discover -s tests -p "test_*.py" -v
```

Suíte de testes inclui:
- Testes unitários para API (Yahoo Finance, Binance)
- Testes de base de dados e schema
- Testes de importação CSV
- Testes de análise de volatilidade

## 📚 Arquitetura

```
main.py                    # Orquestrador principal
├── src/api_yfinance.py    # API Yahoo Finance
├── src/api_binance.py     # API Binance
├── src/database.py        # Camada de dados SQLite
├── src/analysis.py        # Análise estatística
├── src/ui_main.py         # Interface PyQt6
└── src/csv_reader.py      # Importação CSV
```

## 🛠️ Scripts Utilitários

- `add_symbols.py` - Adicionar criptomoedas
- `import_from_csv.py` - Importar dados de ficheiro CSV
- `import_binance_csv_cli.py` - Importar transações Binance
- `inspect_schema.py` - Inspecionar schema da BD
- `mark_favorites.py` - Gerenciar favoritos

Scripts legados arquivados em `scripts/legacy/` para referência histórica.

## 📄 Histórico de Versões

Ver [CHANGELOG.md](CHANGELOG.md) para histórico detalhado de alterações.

---

**Pinto Santos Consulting © 2026**
