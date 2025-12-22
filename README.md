# PSC CryptoPlay - Cryptocurrency Price Tracker & Analysis

**Versão: 4.2.0**

Rastreamento de cotações de criptomoedas em EUR, análise estatística de volatilidade e relatórios Excel profissionais.

## 🚀 Setup Rápido

```bash
setup.cmd
python main.py --all-from-db --days 700
```

## 📚 Documentação

- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido
- **[CONFIGURATION.md](CONFIGURATION.md)** - Opções de configuração
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões
- **[TECHNICAL.md](TECHNICAL.md)** - Arquitetura técnica

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
```

## 🖥️ Interface Gráfica (Novo)

Execute `run_ui.cmd` para abrir a interface desktop (PyQt6) com barra lateral, área de gráficos e integração futura para atualização de dados, relatórios e consultas.

## 📊 Features

✅ Yahoo Finance (gratuito, sem API key)  
✅ Análise de volatilidade detalhada
✅ Sistema de favoritos A/B/C  
✅ Modo auto-range (busca apenas dados novos)  
✅ 101 testes automatizados

---

**Pinto Santos Consulting © 2025**
