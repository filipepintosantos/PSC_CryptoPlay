# PSC CryptoPlay - Cryptocurrency Price Tracker & Analysis
**Versão: 5.0.2**

## 🚀 Setup Rápido

```bash
setup.cmd
python main.py --all-from-db --days 7000
```

## 📚 Documentação

 - Database schema is now canonicalized in `scripts/create_schema.sql`.
     - On first run the application executes this script to create the database schema.
     - The schema includes a `schema_info` table with a `version` value.
     - Application code (`src/database.py`) no longer contains the full DDL; it loads the canonical SQL file.

## 🎯 Comandos Principais

```bash
# Atualizar cotações (modo auto-range)
update_quotes.cmd

# Gerar relatório
python main.py --all-from-db --report-only

# Adicionar moeda
python scripts\add_symbols.py

# Testes
run_tests.cmd

Nota: a suite de testes regista um handler de limpeza que remove automaticamente quaisquer ficheiros de BD de teste `data/test*.db` ao terminar. Se quiseres preservar um DB de teste, mova-o antes de executar os testes.
## 🖥️ Interface Gráfica (Atualizado)

Execute `run_ui.cmd` para abrir a interface desktop (PyQt6) com barra lateral.

### Novidades na v4.3.6
- Menu **Consultar Base de Dados** agora inclui:
    - **Lista de Moedas**: Visualiza todas as moedas cadastradas (tabela crypto_info)
    - **Cotações**: Consulta todas as cotações históricas (tabela price_quotes)
- Menu **Atualizar Dados**: Atualização Diária, Reavaliar Moedas, Forçar Atualização
	- Atualização Diária
## 📊 Features

✅ Visualização de moedas e cotações no menu lateral
✅ Yahoo Finance (gratuito, sem API key)
✅ Análise de volatilidade detalhada
✅ Sistema de favoritos A/B/C
✅ Modo auto-range (busca apenas dados novos)
✅ Cliente Binance API (`src/api_binance.py`) com `get_price_at_second`
✅ 135 testes automatizados (inclui testes para Binance API)

---

**Pinto Santos Consulting © 2026**
