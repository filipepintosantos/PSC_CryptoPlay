# Guia de Desenvolvimento - PSC CryptoPlay

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos
- Python 3.8+
- Git (recomendado)
- Editor: VS Code, PyCharm ou similar

### Setup Inicial

1. **Clone o repositório:**
   ```bash
   git clone <repository_url>
   cd PSC_CryptoPlay
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instale dependências de desenvolvimento:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pylint black isort
   ```

4. **Configure .env para desenvolvimento:**
   ```bash
   cp .env.example .env
   # Adicione sua CMC_API_KEY
   ```

5. **Execute testes:**
   ```bash
   python -m pytest tests/ -v
   ```

## Estrutura de Desenvolvimento

### Conveções de Código

- **Estilo**: PEP 8
- **Docstrings**: Google style
- **Type hints**: Recomendado
- **Line length**: 100 caracteres

### Formatação de Código

```bash
# Formatação automática
black src/ main.py

# Organização de imports
isort src/ main.py

# Linting
pylint src/ main.py
```

### Documentação

Todas as funções públicas devem ter docstrings:

```python
def my_function(param1: str, param2: int) -> Dict:
    """
    Descrição breve da função.
    
    Descrição mais longa explicando comportamento,
    casos especiais, etc.
    
    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro
    
    Returns:
        Descrição do retorno
    
    Raises:
        ValueError: Quando X acontece
        RuntimeError: Quando Y acontece
    
    Examples:
        >>> result = my_function("test", 42)
        >>> print(result)
    """
    pass
```

## Testes

### Estrutura de Testes

```
tests/
├── test_project.py
└── test_*.py
```

### Executar Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Testes específicos
python -m pytest tests/test_project.py::TestDatabase -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

### Exemplo de Teste

```python
import unittest
from src.analysis import StatisticalAnalyzer

class TestAnalysis(unittest.TestCase):
    def test_calculate_statistics(self):
        prices = [100, 150, 120]
        stats = StatisticalAnalyzer.calculate_statistics(prices)
        
        self.assertEqual(stats["min"], 100)
        self.assertEqual(stats["max"], 150)
        self.assertIsNotNone(stats["mean"])
```

## Workflow de Desenvolvimento

### 1. Branch por Feature

```bash
# Criar branch para nova feature
git checkout -b feature/nova-funcionalidade

# Fazer commits
git add .
git commit -m "Descrição clara da mudança"

# Push para remote
git push origin feature/nova-funcionalidade
```

### 2. Commit Message

Formato padrão:
```
[TIPO] Descrição breve

Descrição mais detalhada explicando:
- O que foi mudado
- Por que foi mudado
- Como foi mudado

Tipos:
- FEAT: Nova funcionalidade
- FIX: Correção de bug
- REFACTOR: Refatoração de código
- DOCS: Atualização de documentação
- TEST: Adição ou modificação de testes
```

Exemplo:
```
[FEAT] Adicionar suporte a múltiplas moedas

- Modificado CoinMarketCapAPI para aceitar currency
- Atualizado ExcelReporter para mostrar moeda
- Adicionados testes unitários

Implementa: #123
```

### 3. Pull Request

```bash
# Criar PR no GitHub com:
- Descrição clara das mudanças
- Referência a issues relacionadas
- Prints/screenshots se aplicável
- Checklist de testes executados
```

## Troubleshooting Desenvolvimento

### Erro: "ModuleNotFoundError: No module named 'src'"

```bash
# Adicione ao início do script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

### Erro: "sqlite3.OperationalError: database is locked"

- Feche outros processos usando o DB
- Use `:memory:` para testes
- Verifique permissões de arquivo

### Erro: "CMC_API_KEY not found"

```bash
# Verifique .env
type .env

# Ou defina via variável de ambiente (PowerShell)
$env:CMC_API_KEY="your_key"
```

## Adicionando Novas Funcionalidades

### Exemplo: Adicionar novo período de análise

1. **Modifique analysis.py:**
   ```python
   ROLLING_PERIODS = {
       "12_months": 365,
       "6_months": 182,
       "3_months": 91,
       "1_month": 30,
       "7_days": 7,  # Novo
   }
   ```

2. **Atualize ExcelReporter:**
   ```python
   PERIODS = ["12_months", "6_months", "3_months", "1_month", "7_days"]
   PERIOD_DISPLAY = {
       # ...
       "7_days": "7 Dias",
   }
   ```

3. **Adicione testes:**
   ```python
   def test_7_days_analysis(self):
       # Seu teste aqui
       pass
   ```

4. **Documente a mudança:**
   - Atualize README.md
   - Atualize TECHNICAL.md

### Exemplo: Adicionar nova métrica

1. **Em analysis.py:**
   ```python
   @staticmethod
   def calculate_statistics(prices):
       # ...
       percentile_25 = float(np.percentile(prices_array, 25))
       
       return {
           # ... existing metrics
           "percentile_25": percentile_25,
       }
   ```

2. **Em excel_reporter.py:**
   ```python
   metrics = [
       # ... existing metrics
       ("25º Percentil", stats.get("percentile_25")),
   ]
   ```

## Versionamento

Usar Semantic Versioning (MAJOR.MINOR.PATCH):

- `1.0.0` - Versão inicial
- `1.0.1` - Correção de bug (patch)
- `1.1.0` - Nova funcionalidade (minor)
- `2.0.0` - Mudança incompatível (major)

Atualizar em:
- `setup.py` (se existir)
- `src/__init__.py`
- `README.md`
- Git tag: `git tag v1.0.0`

## Deployment

### Produção

1. **Tag de release:**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

2. **Create release no GitHub**

3. **Instalar em produção:**
   ```bash
   pip install -r requirements.txt
   ```

### Agendamento

**Windows Task Scheduler:**
```
Program: python.exe
Arguments: C:\path\main.py --symbols BTC,ETH
Start in: C:\path\
Schedule: Daily at 08:00
```

## Performance Optimization

### Database Queries
```python
# Ruim: Múltiplas queries
for symbol in symbols:
    quotes = db.get_quotes(symbol)

# Bom: Uma query com índice
cursor.execute("SELECT * FROM price_quotes WHERE crypto_id IN (...)")
```

### Memory Usage
```python
# Ruim: Carregar tudo
df = pd.read_sql("SELECT * FROM price_quotes")

# Bom: Usar chunks
for chunk in pd.read_sql(..., chunksize=1000):
    process(chunk)
```

## Monitoramento

### Logs

Adicione logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Iniciando fetch de quotações")
logger.error(f"Erro ao processar {symbol}: {e}")
```

### Métricas

Implemente tracking:
```python
start_time = time.time()
# ... operação
duration = time.time() - start_time
print(f"Operação levou {duration:.2f}s")
```

---

**Última atualização**: Dezembro 2024
