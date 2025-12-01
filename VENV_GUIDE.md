# Virtual Environment Guide

## O que é um Virtual Environment?

Um virtual environment é um diretório isolado que contém uma instalação independente do Python com suas próprias dependências. Isto permite:

- ✅ Evitar conflitos entre projetos
- ✅ Manter dependências organizadas
- ✅ Facilitar deployment em produção
- ✅ Garantir reproducibilidade

## Setup Automático (Recomendado)

### Windows

```bash
# Duplo clique no ficheiro setup.bat OU execute no terminal:
setup.bat
```

O script irá:
1. Verificar se Python 3 está instalado
2. Criar pasta `venv/`
3. Instalar todas as dependências
4. Criar ficheiro `.env`
5. Criar diretórios de dados e relatórios

**Resultado:** O ambiente está ativado e pronto para usar!

## Setup Manual

Se preferir fazer manualmente:

### 1. Criar Virtual Environment

```bash
python -m venv venv
```

Isto cria uma pasta `venv/` com:
```
venv/
├── Scripts/
├── Lib/
├── include/
└── pyvenv.cfg
```

### 2. Ativar Virtual Environment

**CMD:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

Quando ativado, o prompt mostra:
```
(venv) C:\path\to\PSC_CryptoPlay>
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Desativar Virtual Environment

```bash
deactivate
```

O prompt volta ao normal.

## Workflow Diário

```bash
# 1. Abrir terminal (CMD ou PowerShell)
# 2. Navegar até o projeto
cd C:\path\to\PSC_CryptoPlay

# 3. Ativar virtual environment (CMD)
venv\Scripts\activate.bat

# 3. Ativar virtual environment (PowerShell)
venv\Scripts\Activate.ps1

# 4. Executar comando
python main.py

# 5. Desativar quando terminar
deactivate
```

## Ficheiro requirements.txt

Lista todas as dependências do projeto:

```
requests==2.31.0
pandas==2.1.4
openpyxl==3.1.2
python-dotenv==1.0.0
```

Para adicionar nova dependência:

```bash
pip install novo_pacote
pip freeze > requirements.txt
```

## Troubleshooting

### Erro: "venv is not recognized"

**Windows PowerShell:**
- Use `venv\Scripts\Activate.ps1` em vez de `.bat`
- Ou execute em CMD em vez de PowerShell

**Solução alternativa (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "No module named 'requests'"

Certifique-se de que:
1. Venv está ativado (vê `(venv)` no prompt)
2. Executou `pip install -r requirements.txt`

### Venv ocupa muito espaço

Isto é normal - venv pode ocupar 50-100MB com todas as dependências.

Para economizar espaço em backups/deploy:
- Não inclua `venv/` no controle de versão (já está em `.gitignore`)
- Regenere em novo servidor com `setup.bat`

## Upgrade de Dependências

```bash
# Ativar venv primeiro
pip install --upgrade -r requirements.txt

# Depois atualizar requirements.txt
pip freeze > requirements.txt
```

## Venv em Produção

```bash
# No servidor Windows:
git clone repository
cd PSC_CryptoPlay
setup.bat

# Depois agendar com Windows Task Scheduler ou schedule_windows.bat
```

## Dicas Úteis

### 1. Usar requirements de desenvolvimento

```bash
# Criar requirements-dev.txt com pacotes extras
pip install pytest pylint black
pip freeze > requirements-dev.txt

# Em desenvolvimento:
pip install -r requirements-dev.txt

# Em produção:
pip install -r requirements.txt
```

### 2. Verificar versões instaladas

```bash
pip list
```

### 3. Mostrar localização do Python

```bash
where python      # Windows
```

### 4. Testar sem ativar venv

```bash
# Usar python.exe do venv diretamente
venv\Scripts\python.exe main.py
```

---

**Última atualização**: Dezembro 2024
