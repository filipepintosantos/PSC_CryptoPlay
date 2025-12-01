# PSC CryptoPlay - Cryptocurrency Price Tracker & Analysis

Ferramenta Python para rastreamento de quotações de criptomoedas em EUR, armazenamento em SQLite e geração de relatórios em Excel com análises estatísticas.

## 🚀 Começar Rapidamente (5 minutos)

```bash
setup.bat
```

Depois configure a API key em `.env` e execute:

```bash
python main.py
```

Para mais informações, consulte [QUICKSTART.md](QUICKSTART.md)

## Funcionalidades

- 📊 **Fetch de Quotações**: Busca preços em EUR do CoinMarketCap
- 💾 **Banco de Dados SQLite**: Armazena histórico de quotações
- 📈 **Análise Estatística**: Calcula min, máximo, média, desvio padrão e média-desvio padrão
- 📅 **Períodos Rolantes**: Análises para 12 meses, 6 meses, 3 meses e 1 mês
- 📑 **Relatórios Excel**: Gera folhas de cálculo com:
  - Resumo geral de todas as criptomoedas
  - Análises detalhadas por símbolo
  - Desvio da última quotação em relação às médias
  - Formatação profissional com cores

## Estrutura do Projeto

```
PSC_CryptoPlay/
├── src/
│   ├── api.py                 # Interface com CoinMarketCap API
│   ├── database.py            # Gerenciador SQLite
│   ├── analysis.py            # Análise estatística
│   └── excel_reporter.py      # Geração de relatórios Excel
├── data/
│   └── crypto_prices.db       # Banco de dados (criado automaticamente)
├── reports/
│   └── crypto_analysis.xlsx   # Relatório Excel (criado automaticamente)
├── config/                    # Configurações
├── tests/                     # Testes
├── main.py                    # Script principal
├── requirements.txt           # Dependências Python
├── .env.example              # Exemplo de arquivo .env
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

4. **Configure a API key**:
   
   Copie `.env.example` para `.env`:
   ```bash
   copy .env.example .env
   ```
   
   Edite `.env` e adicione sua chave da API do CoinMarketCap:
   ```
   CMC_API_KEY=your_actual_api_key_here
   ```
   
   **Obtendo a API Key**:
   - Acesse https://coinmarketcap.com/api/
   - Crie uma conta gratuita
   - Copie sua API Key

5. **Configure o arquivo `config/config.ini`** (opcional):
   
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
python main.py --db-path data/my_crypto.db --report-path reports/my_analysis.xlsx
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
- `cryptocurrencies`: Metadados das criptomoedas
- `price_quotes`: Histórico de quotações com timestamp

### Relatório Excel

Arquivo: `reports/crypto_analysis.xlsx`

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
# Generating Excel report: reports/crypto_analysis.xlsx
# ✓ Analysis complete!
#   Database: data/crypto_prices.db
#   Report: reports/crypto_analysis.xlsx
```

## Agendamento Automático (Opcional)

### Windows (Task Scheduler)

1. Abra "Agendador de Tarefas"
2. Crie nova tarefa básica
3. Defina acionador (ex: diariamente às 08:00)
4. Ação: `python C:\caminho\PSC_CryptoPlay\main.py`
5. Inicie a tarefa

Ou use o ficheiro `schedule_windows.bat` como base.

## Troubleshooting

### Erro: "CMC_API_KEY not provided"

- Certifique-se de que `.env` existe e contém `CMC_API_KEY`
- Ou passe via linha de comando: `--api-key YOUR_KEY`

### Erro: "Error fetching from CoinMarketCap"

- Verifique sua conexão de internet
- Verifique se a API key é válida
- Verifique limite de requisições da API (plano gratuito tem limites)

### Banco de dados vazio

- Certifique-se de executar sem `--fetch-only` na primeira vez
- Verifique permissões de escrita no diretório `data/`

### Excel não abre

- Use `--report-only` para regenerar
- Certifique-se de que não há outro programa com o arquivo aberto

## Dependências

- **requests**: HTTP library para CoinMarketCap API
- **pandas**: Análise e manipulação de dados
- **openpyxl**: Criação de arquivos Excel
- **python-dotenv**: Carregamento de variáveis de ambiente

## Licença

Este projeto é fornecido como está.

## Suporte

Para problemas ou sugestões, verifique:
- Logs de execução
- Conteúdo de `.env`
- Permissões de arquivo e diretório
- Disponibilidade da API do CoinMarketCap

---

**Versão**: 1.0.0  
**Última atualização**: Dezembro 2024
