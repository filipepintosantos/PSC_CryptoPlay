# SonarQube Integration Guide

## Configuração Local do SonarQube

### 1. Instalar SonarQube Server (Local)

**Opção A: Docker (Recomendado)**

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest
```

Acesse: http://localhost:9000
Credenciais padrão: admin / admin

**Opção B: Download e instalação manual**

1. Download: https://www.sonarqube.org/downloads/
2. Extract para uma pasta (ex: `C:\SonarQube`)
3. Execute: `C:\SonarQube\bin\windows-x86-64\StartSonar.bat`
4. Acesse: http://localhost:9000

### 2. Instalar SonarQube Scanner

```bash
# Download: https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/
# Extract para uma pasta

# Adicionar ao PATH (Windows):
setx PATH "%PATH%;C:\path\to\sonar-scanner\bin"

# Verificar instalação:
sonar-scanner --version
```

### 3. Configurar Projeto no SonarQube

1. Aceda a http://localhost:9000
2. Clique em "Create project"
3. Defina o "Project key" e "Project name"
4. Copie o "Project key"

### 4. Atualizar `sonar-project.properties`

Edite o ficheiro e atualize (se necessário):

```ini
sonar.projectKey=YOUR_PROJECT_KEY
sonar.host.url=http://localhost:9000
sonar.login=YOUR_TOKEN
```

### 5. Executar Análise

**Opção 1: Script preparado (recomendado)**

```bash
sonar-scan.bat
```

Este script irá:
- Gerar relatório de coverage automaticamente
- Executar o SonarQube Scanner
- Enviar resultados para o servidor

**Opção 2: Comando direto**

```bash
# Gerar coverage (opcional, melhora resultados)
pytest tests/ --cov=src --cov-report=xml

# Executar SonarQube Scanner
sonar-scanner
```

### 6. Visualizar Resultados

Aceda a: http://localhost:9000/dashboard?id=YOUR_PROJECT_KEY

## SonarQube Cloud (Online)

Para análise automatizada em CI/CD (GitHub, GitLab, etc):

### 1. Criar Conta

1. Aceda a https://sonarcloud.io
2. Login com GitHub / GitLab
3. Autorize o acesso ao seu repositório

### 2. Configurar Projeto

1. Importe seu repositório
2. Copie o "Project Key"

### 3. Configurar CI/CD

**GitHub Actions:**

```yaml
name: SonarCloud
on: [push, pull_request]

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**GitLab CI:**

```yaml
sonarcloud-check:
  image: python:3.11
  script:
    - pip install -r requirements-dev.txt
    - pytest tests/ --cov=src --cov-report=xml
    - sonar-scanner
```

## Métricas Monitoradas

O SonarQube analisa:

- **Code Quality**: Duplicação, Complexidade, Violações de regras
- **Code Security**: Vulnerabilidades, Hotspots de segurança
- **Test Coverage**: Cobertura de testes, linhas não testadas
- **Maintainability**: Índice de manutenibilidade
- **Reliability**: Bugs potenciais

## Ficheiros de Configuração

- **sonar-project.properties**: Configuração do projeto
- **sonar-scan.bat**: Script para executar análise (Windows)
- **coverage.xml**: Relatório de cobertura (gerado automaticamente)

## Troubleshooting

### "sonar-scanner not found"

```bash
# Verificar instalação
sonar-scanner --version

# Adicionar ao PATH (Windows PowerShell)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\sonar-scanner\bin", "User")

# Reabra o terminal e tente novamente
```

### "Coverage report not found"

```bash
# Gerar coverage manualmente
pip install -r requirements-dev.txt
pytest tests/ --cov=src --cov-report=xml
```

### Conexão recusada ao servidor SonarQube

```bash
# Verificar se o servidor está rodando
# Local: http://localhost:9000
# Cloud: https://sonarcloud.io

# Se Local, certifique-se que SonarQube está ativo
# Restart SonarQube se necessário
```

## Próximos Passos

1. Instale SonarQube (local ou cloud)
2. Configure o projeto em SonarQube
3. Execute `sonar-scan.bat`
4. Revise os resultados no dashboard
5. Corrija issues críticas e bloqueadores
6. Automatize em CI/CD

## Recursos

- Documentação SonarQube: https://docs.sonarqube.org/
- SonarCloud: https://sonarcloud.io/
- Regras Python: https://rules.sonarsource.com/python/
