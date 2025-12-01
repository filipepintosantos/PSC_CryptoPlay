# Quick Start Guide - PSC CryptoPlay

**Tempo estimado de setup: 5 minutos**

## 1️⃣ Instalação Rápida

### Automática (Recomendado)

```bash
setup.bat
```

Isto criará automaticamente o virtual environment e instalará todas as dependências.

### Manual

```bash
python -m venv venv
venv\Scripts\activate.bat

# Depois:
pip install -r requirements.txt
cp .env.example .env
```

## 2️⃣ Configurar API Key

Edite `.env`:
```
CMC_API_KEY=your_api_key_from_coinmarketcap
```

Obtenha em: https://coinmarketcap.com/api/

## 3️⃣ Primeira Execução

```bash
# Recolhe histórico completo (5-10 min)
python main.py --all-symbols --fetch-mode full

# Saída esperada:
# ✓ Analysis complete!
#   Symbols analyzed: BTC, ETH, ADA, XRP, SOL, DOGE, LTC, BNB
#   Database: data/crypto_prices.db
#   Report: reports/crypto_analysis.xlsx
```

## 4️⃣ Usar Relatório Excel

Abra `reports/crypto_analysis.xlsx`:
- **Sheet "Resumo"**: Tabela com todas as moedas
  - Clique na seta 🔽 dos cabeçalhos para **filtrar/pesquisar**
  - Verde = preço acima da média | Vermelho = preço abaixo
- **Sheets por moeda**: Análise detalhada de cada uma

## 5️⃣ Execuções Seguintes (Mais Rápidas)

```bash
# Apenas favoritos (BTC, ETH, ADA, XRP, SOL)
python main.py

# Modo incremental: continua de onde parou (30 segundos)
python main.py --fetch-mode incremental

# Apenas gerar novo relatório (5 segundos)
python main.py --report-only
```

## 📋 Comandos Frequentes

| Tarefa | Comando |
|--------|---------|
| Atualizar dados favoritos | `python main.py` |
| Adicionar nova moeda | `python main.py --symbols BTC,ETH,NOVO` |
| Recolher tudo novamente | `python main.py --all-symbols --fetch-mode full` |
| Regenerar só o Excel | `python main.py --report-only` |
| Ver ajuda completa | `python main.py --help` |

## ⚙️ Personalizações

**Edite `config/config.ini`** para:

```ini
[symbols]
# Suas moedas favoritas
favorites = BTC,ETH,ADA

# Todas as moedas a rastrear
all = BTC,ETH,ADA,XRP,SOL,DOGE,LTC

[fetch]
# Modo rápido (incremental) ou completo (full)
mode = incremental
```

## 🔄 Agendamento Automático

1. Abra **Task Scheduler**
2. Crie **New Basic Task**
3. Nome: "CryptoPlay Update"
4. Trigger: **Daily 8:00 AM**
5. Action: Execute `python` com argumento `main.py`
6. (Ou use o script `schedule_windows.bat`)

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| "CMC_API_KEY not found" | Edite `.env` e adicione a chave |
| "No module named 'requests'" | Execute `pip install -r requirements.txt` |
| Excel não abre | Feche se estiver aberto e regenere: `python main.py --report-only` |
| Muito lento | Use `--fetch-only` em hora de pico, gere relatório depois |

## 📖 Documentação Completa

- **README.md** - Documentação geral
- **CONFIGURATION.md** - Guia de configuração
- **TECHNICAL.md** - Arquitetura técnica
- **DEVELOPMENT.md** - Guia para desenvolvedores
- **IMPROVEMENTS.md** - Melhorias implementadas

## ✨ Principais Funcionalidades

✅ Recolhe cotações de criptomoedas em EUR  
✅ Armazena tudo em SQLite  
✅ Calcula estatísticas: min, max, média, desvio padrão  
✅ Gera relatórios Excel com filtros  
✅ Dois modos de fetch: incremental e completo  
✅ Configurável via ficheiro INI  
✅ Pronto para agendamento automático  

---

**Pronto para começar! 🚀**

Dúvidas? Consulte a documentação ou execute `python main.py --help`
