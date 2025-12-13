# PSC CryptoPlay - Cryptocurrency Price Tracker & Analysis

**Versão: 3.0.0**

Ferramenta Python para rastreamento de quotações de criptomoedas em EUR, armazenamento em SQLite e geração de relatórios em Excel com análises estatísticas.

## 🚀 Características Principais

### 📊 Recolha de Dados
- **Yahoo Finance API gratuito** (yfinance) - Sem necessidade de chave API
- **Descoberta automática** de criptomoedas via CoinGecko API
- **Filtragem inteligente**: Market cap > $100M USD, idade > 3 meses, dados EUR disponíveis
- **400+ dias de histórico** por criptomoeda
- **Atualização incremental** - Busca apenas dados novos
- **Gestão UPSERT** - Sem entradas duplicadas

### 📈 Análise e Relatórios
- **Análise multi-período**: 12 meses, 6 meses, 3 meses, 1 mês
- **Métricas estatísticas**: Mínimo, Máximo, Média, Desvio Padrão, Média-Desvio
- **Tracking de desvios**: Percentagens de desvio da Média e Média-Desvio
- **Coluna de favoritos**: Destaque visual com marcação dourada
- **Fórmulas Excel**: Cálculos dinâmicos para médias e desvios
- **Ordenação por capitalização** de mercado
- **Relatórios Excel** com freeze panes, cores e formatação profissional

### 🔄 Automação
- **Script de atualização** (`update_quotes.bat`) - Atualiza todas as moedas com 3 dias de dados
- **Script de seeding** - Popula automaticamente a base de dados com moedas qualificadas

## 🚀 Começar Rapidamente (5 minutos)

```bash
setup.bat
```

Depois execute:

```bash
python main.py --all-from-db --days 700
```

Para atualizar quotações regularmente:

```bash
update_quotes.bat
```

Para mais informações, consulte [QUICKSTART.md](QUICKSTART.md)

## Funcionalidades Detalhadas

- 📊 **Fetch de Quotações**: Busca preços em EUR do Yahoo Finance (gratuito)
- 🔍 **Auto-discovery**: Encontra automaticamente criptomoedas com market cap > $250M
- 💾 **Banco de Dados SQLite**: Armazena histórico de quotações com gestão UPSERT
- 📈 **Análise Estatística**: Calcula min, máximo, média, desvio padrão e média-desvio padrão
- 📅 **Períodos Rolantes**: Análises para 12 meses, 6 meses, 3 meses e 1 mês
- 📑 **Relatórios Excel**: Gera folhas de cálculo com:
  - Resumo geral de todas as criptomoedas ordenadas por market cap
  - Última cotação em coluna dedicada (coluna B)
  - Desvios percentuais da Média e Média-Desvio
  - Formatação profissional com cores e freeze panes
  - Análises detalhadas por símbolo
- 🤖 **Automação**: Scripts batch para atualização diária e seeding inicial

## Estrutura do Projeto

```
PSC_CryptoPlay/
├── src/
│   ├── api_yfinance.py        # Interface com Yahoo Finance API
│   ├── database.py            # Gerenciador SQLite com UPSERT
│   ├── analysis.py            # Análise estatística
│   └── excel_reporter.py      # Geração de relatórios Excel
├── scripts/
│   └── seed_large_cryptos_yfinance.py  # Auto-discovery de criptomoedas
├── data/
│   └── crypto_prices.db       # Banco de dados (criado automaticamente)
├── reports/
│   └── AnaliseCrypto.xlsx     # Relatório Excel (criado automaticamente)
├── config/
│   └── config.ini            # Configurações (favoritas, períodos, etc)
├── tests/                     # Testes unitários
├── main.py                    # Script principal
├── update_quotes.bat          # Atualização rápida (3 dias)
├── requirements.txt           # Dependências Python
└── README.md                 # Este arquivo
```

## Instalação

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone ou extraia o projeto**:
   ```bash
   cd PSC_CryptoPlay
   ```

2. **Setup Automático** (Recomendado):
   
   ```bash
   setup.bat
   ```
   
   Este script irá:
   - ✅ Criar virtual environment
   - ✅ Instalar todas as dependências
   - ✅ Criar ficheiro `.env`
   - ✅ Criar diretórios necessários

3. **Setup Manual** (Se preferir):
   
   Crie um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate.bat
   ```
   
   Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `config/config.ini`** (opcional):
   
   Edite a seção `[symbols]` para adicionar/remover criptomoedas:
   ```ini
   [symbols]
   all = BTC,ETH,SOL,ADA,LINK,ATOM,XTZ
   favorites = BTC,ETH,SOL,ADA,LINK,ATOM,XTZ
   ```
   
   Configure o modo de fetch em `[fetch]`:
   ```ini
   [fetch]
   mode = incremental          # ou 'full'
   upsert_duplicates = true    # atualiza valores em datas duplicadas
   ```

## Uso

### Modo Básico

Executa o fluxo completo: fetch → armazenar → analisar → exportar

```bash
python main.py
```

Por padrão, analisa os símbolos definidos em `config/config.ini` seção `[symbols]`

### Usar Todas as Criptomoedas Configuradas

```bash
python main.py --all-symbols
```

### Usar Apenas Favoritos

```bash
python main.py --favorites
```

### Especificar Símbolos

```bash
python main.py --symbols BTC,ETH,XRP,DOGE,LTC
```

### Controlar Modo de Fetch

**Modo Incremental** (padrão: continua desde última data registada):
```bash
python main.py --fetch-mode incremental
```

**Modo Full** (recolhe desde a data mais antiga e atualiza valores em datas duplicadas):
```bash
python main.py --fetch-mode full
```

### Apenas Fetch (Coletar dados sem gerar relatório)

```bash
python main.py --fetch-only
```

### Apenas Relatório (Gerar relatório dos dados existentes)

```bash
python main.py --report-only
```

### Especificar Caminhos Personalizados

```bash
python main.py --db-path data/my_crypto.db --report-path reports/MinhaAnalise.xlsx
```

### Usar API Key via Linha de Comando

```bash
python main.py --api-key YOUR_API_KEY
```

### Ajuda

```bash
python main.py --help
```

## 📖 Documentação Completa

Consulte o **[Índice de Documentação](INDEX.md)** para navegação completa:

- **[QUICKSTART.md](QUICKSTART.md)** - Começar em 5 minutos
- **[CONFIGURATION.md](CONFIGURATION.md)** - Guia de configuração detalhada
- **[VENV_GUIDE.md](VENV_GUIDE.md)** - Guia de Virtual Environment
- **[TECHNICAL.md](TECHNICAL.md)** - Documentação técnica e arquitetura
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guia para desenvolvedores
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Melhorias implementadas

## Exemplos de Uso Avançado

### Coletar dados de todas as moedas em modo full (recolhe tudo)

```bash
python main.py --all-symbols --fetch-mode full
```

### Analisar apenas BTC incrementalmente (continua de onde parou)

```bash
python main.py --symbols BTC --fetch-mode incremental
```

### Regenerar relatório sem recolher dados

```bash
python main.py --favorites --report-only
```

### Modo workflow completo com logging

```bash
# Coleta incrementais diárias
python main.py --favorites --fetch-mode incremental --fetch-only

# Gera relatório no fim de semana
python main.py --favorites --report-only
```

## Saída

### Banco de Dados (SQLite)

Arquivo: `data/crypto_prices.db`

**Tabelas**:
- `cryptocurrencies`: Metadados das criptomoedas (id, symbol, name, created_at)
- `price_quotes`: Histórico de quotações com timestamp
- `crypto_info`: Informações de criptomoedas (code, name, market_entry, market_cap, favorite)

### Relatório Excel

Arquivo: `reports/AnaliseCrypto.xlsx`

**Sheets**:
1. **Resumo**: Tabela geral com todas as criptomoedas
   - Mínimo, Máximo, Média, Desvio Padrão
   - Média - Desvio Padrão
   - Última Quotação (com highlight de cor)
   - Desvio da última quotação à média
   - **AutoFilter ativado para pesquisas simples** (clique na seta do cabeçalho)

2. **Detalhado (um por criptomoeda)**: Análise completa
   - Período de dados
   - Total de pontos de dados
   - Para cada período (12m, 6m, 3m, 1m):
     - Todas as estatísticas
     - Desvios da última quotação

## Métricas Calculadas

Para cada período (12 meses, 6 meses, 3 meses, 1 mês):

- **Mínimo**: Preço mais baixo no período
- **Máximo**: Preço mais alto no período
- **Média**: Valor médio dos preços
- **Desvio Padrão**: Variabilidade dos preços
- **Média - Desvio Padrão**: Limite inferior estatístico
- **Última Quotação**: Preço mais recente
- **Desvio da Última Quotação à Média**: Diferença atual vs média
- **Desvio da Última Quotação à Média-Desvio**: Diferença vs limite inferior

## Exemplo de Execução

```bash
# 1. Executar análise completa
python main.py --symbols BTC,ETH

# Output:
# Initializing database...
# Fetching prices for: BTC, ETH
# Successfully stored 2 quotes in database
# Generating statistical analysis...
# Generating Excel report: reports/AnaliseCrypto.xlsx
# ✓ Analysis complete!
#   Database: data/crypto_prices.db
#   Report: reports/AnaliseCrypto.xlsx
```

## Agendamento Automático (Opcional)

### Windows (Task Scheduler)

1. Abra "Agendador de Tarefas"
2. Crie nova tarefa básica
3. Defina acionador (ex: diariamente às 08:00)
4. Ação: `python C:\caminho\PSC_CryptoPlay\main.py`
5. Inicie a tarefa

Ou use o ficheiro `schedule_windows.bat` como base.

## Testes

### Executar Testes com Unittest (recomendado)

```bash
# Todos os testes
python -m unittest discover -s tests -p "test_*.py" -v

# Testes específicos
python -m unittest tests.test_project.TestDatabase -v
```

### Executar Testes com Pytest (opcional)

Instale as dependências de desenvolvimento:
```bash
pip install -r requirements-dev.txt
```

Execute os testes:
```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=src --cov-report=html

# Ou use o script preparado
run_tests.bat        # Executa com pytest
run_tests.bat -u     # Executa com unittest
run_tests.bat -c     # Executa com coverage
```

### Testes Disponíveis

- **TestDatabase**: Testa operações de base de dados (criar tabelas, adicionar criptomoedas, inserir quotas)
- **TestStatisticalAnalyzer**: Testa cálculos estatísticos e análises de períodos rolantes

## Desenvolvimento

### Instalar Ferramentas de Desenvolvimento

```bash
pip install -r requirements-dev.txt
```

Isso instala:
- pytest (testes)
- pytest-cov (cobertura)
- pylint (linting)
- black (formatação)
- isort (organização de imports)
- mypy (type checking)

### Formatação de Código

```bash
# Formatar com black
black src/ main.py

# Organizar imports
isort src/ main.py

# Lint com pylint
pylint src/ main.py
```

## Troubleshooting

### Banco de dados vazio

- Certifique-se de executar sem `--fetch-only` na primeira vez
- Verifique permissões de escrita no diretório `data/`
- Execute `python scripts\seed_large_cryptos_yfinance.py` para popular com criptomoedas

### Excel não abre

- Use `--report-only` para regenerar
- Certifique-se de que não há outro programa com o arquivo aberto

### Erro ao buscar dados

- Verifique sua conexão de internet
- Verifique se o Yahoo Finance está acessível
- Algumas criptomoedas podem não ter pares EUR disponíveis

## Dependências

- **yfinance**: API gratuita do Yahoo Finance para cotações de criptomoedas
- **requests**: HTTP library para CoinGecko API
- **pandas**: Análise e manipulação de dados
- **openpyxl**: Criação de arquivos Excel
- **python-dotenv**: Carregamento de variáveis de ambiente

## Licença

Este projeto é fornecido como está.

## Suporte

Para problemas ou sugestões, verifique:
- Logs de execução
- Conteúdo de `config/config.ini`
- Permissões de arquivo e diretório
- Disponibilidade das APIs (Yahoo Finance, CoinGecko)

---

**Versão**: 2.3.0  
**Última atualização**: Dezembro 2025
