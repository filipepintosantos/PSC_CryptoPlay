# PSC CryptoPlay - Cryptocurrency Price Tracker & Analysis

**Versão: 3.6.0**

Ferramenta Python para rastreamento de quotações de criptomoedas em EUR, análise estatística de volatilidade e geração de relatórios Excel profissionais.

## 🚀 Setup Rápido (5 minutos)

```bash
setup.cmd
python main.py --all-from-db --days 700
```

## 📚 Documentação

- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido detalhado
- **[CONFIGURATION.md](CONFIGURATION.md)** - Todas as opções de configuração
- **[FAVORITES_CLASSIFICATION.md](FAVORITES_CLASSIFICATION.md)** - Sistema de favoritos A/B/C
- **[TECHNICAL.md](TECHNICAL.md)** - Arquitetura e detalhes técnicos
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guia para contribuidores
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões

## 🎯 Uso Comum

```bash
# Gerar relatório de todas as moedas na BD
python main.py --all-from-db --report-only

# Atualizar quotações (últimos 3 dias)
update_quotes.cmd

# Ver favoritos
python scripts\mark_favorites.py

# Adicionar nova moeda
python scripts\add_symbols.py

# Popular BD com criptos >$100M market cap
python scripts\seed_large_cryptos_yfinance.py --dry-run --max-pages 5
```

## 🧪 Testes

```bash
# Executar todos os testes
run_tests.cmd

# Com cobertura
pytest --cov=src --cov-report=html
```

## 📝 Notas

- Usa Yahoo Finance (gratuito, sem API key)
- Market cap mínimo: $100M USD
- Base de dados SQLite em `data/crypto_prices.db`
- Relatórios em `reports/AnaliseCrypto.xlsx`

---

**Pinto Santos Consulting © 2025**
