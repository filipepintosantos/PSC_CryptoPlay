# 📖 Índice de Documentação - PSC CryptoPlay

## 🚀 Começar Rápido

**Tempo**: 5 minutos

1. **[QUICKSTART.md](QUICKSTART.md)** ← COMECE AQUI!
   - Setup automático (1 clique)
   - Configuração API key
   - Primeiros comandos

## 📚 Documentação Completa

### Instalação & Setup

- **[VENV_GUIDE.md](VENV_GUIDE.md)** - Guia Virtual Environment
  - O que é venv
  - Como usar (automático/manual)
  - Troubleshooting
  - Dicas e boas práticas

- **[VENV_SETUP.md](VENV_SETUP.md)** - Resumo Setup Virtual Environment
  - Scripts de automação
  - Estrutura pós-setup
  - Benefícios e segurança

- **[README.md](README.md)** - Documentação Geral
  - Overview do projeto
  - Instalação completa
  - Uso e exemplos
  - Agendamento automático

### Configuração

- **[CONFIGURATION.md](CONFIGURATION.md)** - Guia de Configuração
  - Ficheiro config.ini completo
  - Arquivo .env
  - Exemplos para diferentes cenários
  - Workflow recomendado
  - Troubleshooting

### Funcionalidades

- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Melhorias Implementadas
  - Configuração centralizada
  - Dois modos de fetch
  - Filtros Excel
  - CLI flexível
  - Benefícios resumidos

### Desenvolvimento

- **[TECHNICAL.md](TECHNICAL.md)** - Documentação Técnica
  - Arquitetura do sistema
  - Descrição de módulos
  - Fluxo de dados
  - Tratamento de erros
  - Performance e segurança

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guia para Desenvolvedores
  - Setup de desenvolvimento
  - Conveções de código
  - Estrutura de testes
  - Workflow de desenvolvimento
  - Adicionando novas funcionalidades

## 🗂️ Estrutura de Ficheiros

```
PSC_CryptoPlay/
├── 📄 Documentação
│   ├── README.md                 # Overview & instalação
│   ├── QUICKSTART.md            # 5 minutos para começar
│   ├── CONFIGURATION.md         # Guia de configuração
│   ├── TECHNICAL.md             # Arquitetura técnica
│   ├── DEVELOPMENT.md           # Desenvolvimento
│   ├── IMPROVEMENTS.md          # Melhorias
│   ├── VENV_GUIDE.md           # Virtual environment
│   ├── VENV_SETUP.md           # Setup venv (resumo)
│   └── INDEX.md                 # Este ficheiro
│
├── 🔧 Setup & Configuração
│   ├── setup.bat                # Setup automático (Windows)
│   ├── requirements.txt         # Dependências Python
│   ├── .env.example            # Template variáveis ambiente
│   ├── config/config.ini       # Configuração principal
│   └── .gitignore              # Ficheiros ignorados Git
│
├── 💻 Código Principal
│   ├── main.py                 # Script principal
│   ├── src/
│   │   ├── __init__.py
│   │   ├── api.py              # Integração CoinMarketCap
│   │   ├── database.py         # Gerenciador SQLite
│   │   ├── analysis.py         # Análise estatística
│   │   └── excel_reporter.py   # Gerador relatórios Excel
│   └── tests/
│       └── test_project.py     # Testes unitários
│
├── 📂 Dados & Relatórios
│   ├── data/                   # Base de dados SQLite (criado)
│   ├── reports/                # Relatórios Excel (criado)
│   └── logs/                   # Ficheiros log (criado)
│
├── ⚙️ Automação
│   └── schedule_windows.bat    # Agendamento Windows
│
└── 🐍 Virtual Environment
    └── venv/                   # Environment isolado (criado)
```

## 📋 Tabela de Conteúdos por Persona

### 👤 Usuário Comum

Quer começar rápido?

1. **[QUICKSTART.md](QUICKSTART.md)** - 5 minutos
2. Execute `setup.bat`
3. Configure `.env`
4. Execute `python main.py`
5. Abra o Excel gerado

### 👨‍💼 Administrador/DevOps

Quer configurar para produção?

1. **[CONFIGURATION.md](CONFIGURATION.md)** - Configurar tudo
2. **[VENV_GUIDE.md](VENV_GUIDE.md)** - Entender venv
3. **[README.md#agendamento-automático](README.md)** - Agendamento automático
4. Use `schedule_windows.bat` ou Windows Task Scheduler

### 👨‍💻 Desenvolvedor

Quer contribuir ou estender?

1. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup dev
2. **[TECHNICAL.md](TECHNICAL.md)** - Arquitetura
3. Explore `src/` e `tests/`
4. **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Ideias para novas features

### 🔧 Operador/Data Analyst

Quer usar e analisar dados?

1. **[QUICKSTART.md](QUICKSTART.md)** - Setup rápido
2. **[CONFIGURATION.md](CONFIGURATION.md)** - Personalizar moedas
3. **[README.md](README.md#uso)** - Comandos principais
4. Use Excel gerado com AutoFilter

## 🎯 Exemplos por Use Case

### Cenário 1: Primeira Execução

```bash
# 1. Setup
setup.bat

# 2. Configurar
# Editar .env com sua API key

# 3. Executar
python main.py

# 4. Analisar
# Abrir reports/crypto_analysis.xlsx
```

📖 Consulte: [QUICKSTART.md](QUICKSTART.md)

### Cenário 2: Agendamento Diário

```bash
# 1. Setup
setup.bat

# 2. Configurar agendamento
# Use schedule_windows.bat ou Windows Task Scheduler

# 3. Adicionar nova moeda
# Editar config/config.ini [symbols] section
```

📖 Consulte: [CONFIGURATION.md](CONFIGURATION.md), [README.md#agendamento-automático](README.md)

### Cenário 3: Análise Personalizada

```bash
# 1. Configurar moedas
# Editar config/config.ini

# 2. Fetch incremental
python main.py --fetch-mode incremental

# 3. Análise completa
python main.py --report-only
```

📖 Consulte: [README.md#uso](README.md), [CONFIGURATION.md](CONFIGURATION.md)

### Cenário 4: Desenvolvimento

```bash
# 1. Setup dev
pip install -r requirements.txt
pip install pytest pylint black

# 2. Executar testes
python -m pytest tests/ -v

# 3. Adicionar nova métrica
# Editar src/analysis.py
```

📖 Consulte: [DEVELOPMENT.md](DEVELOPMENT.md), [TECHNICAL.md](TECHNICAL.md)

## 🔍 Procurando Algo Específico?

| O que preciso? | Consulte |
|---|---|
| Começar em 5 minutos | [QUICKSTART.md](QUICKSTART.md) |
| Virtual environment | [VENV_GUIDE.md](VENV_GUIDE.md) |
| Configurar moedas | [CONFIGURATION.md](CONFIGURATION.md) |
| Agendamento automático | [README.md#agendamento-automático](README.md) |
| Usar Excel | [README.md#saída](README.md) |
| Entender arquitetura | [TECHNICAL.md](TECHNICAL.md) |
| Contribuir código | [DEVELOPMENT.md](DEVELOPMENT.md) |
| Novos comandos CLI | [README.md#uso](README.md) |
| Fetch incremental | [CONFIGURATION.md](CONFIGURATION.md) |
| Troubleshooting | [CONFIGURATION.md#troubleshooting](CONFIGURATION.md) |

## ✅ Checklist de Setup

- [ ] Python 3.8+ instalado
- [ ] Executar `setup.bat`
- [ ] Editar `.env` com API key
- [ ] Executar `python main.py`
- [ ] Verificar `reports/crypto_analysis.xlsx`
- [ ] Editar `config/config.ini` se necessário
- [ ] (Opcional) Configurar agendamento automático

## 🆘 Ajuda Rápida

**Setup não funciona?**
→ Consulte [VENV_GUIDE.md#troubleshooting](VENV_GUIDE.md)

**Não tenho API key?**
→ Consulte [README.md#obtendo-a-api-key](README.md)

**Quer adicionar mais moedas?**
→ Consulte [CONFIGURATION.md](CONFIGURATION.md)

**Excel não aparece?**
→ Consulte [CONFIGURATION.md#troubleshooting](CONFIGURATION.md)

**Quer fazer fetch completo?**
→ Consulte [README.md#controlar-modo-de-fetch](README.md)

---

**Última atualização**: Dezembro 2024

**Versão**: 1.1.0 (com Virtual Environment integrado)
