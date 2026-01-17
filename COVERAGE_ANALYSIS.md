# Análise de Cobertura de Testes - PSC CryptoPlay

## Resumo Geral
- **Cobertura Local**: 78%
- **Cobertura SonarQube**: 71.3%
- **Total de Statements**: 3928
- **Statements Não Testados**: 851

## Cobertura por Módulo

### Altamente Testados (>90%)
- ✅ **src/__init__.py** - 100%
- ✅ **src/api_binance.py** - 94%
- ✅ **src/excel_reporter.py** - 96%
- ✅ **src/volatility_analysis.py** - 97%
- ✅ **tests/** (maioria) - 96-99%

### Moderadamente Testados (70-90%)
- ⚠️ **src/database.py** - 70% (315 statements, 96 não testados)
- ⚠️ **src/api_yfinance.py** - 87%
- ⚠️ **src/analysis.py** - 92%
- ⚠️ **src/csv_reader.py** - 77%
- ⚠️ **src/ui_main.py** - 69% (808 statements, 252 não testados)

### Baixa Cobertura (<50%)
- ❌ **main.py** - 51% (311 statements, 152 não testados)
- ❌ **scripts/import_binance_csv_cli.py** - 21% (CLI script, largamente não testado)
- ❌ **scripts/seed_large_cryptos_yfinance.py** - 32% (Script de seeding)
- ❌ **src/favorites_helper.py** - 18% (39 statements, 32 não testados)

## Porquê 71.3% no SonarQube vs 78% Local?

1. **SonarQube inclui ficheiros de scripts**: `main.py`, `scripts/import_binance_csv_cli.py`, etc., que não têm testes unitários
2. **SonarQube pode excluir ficheiros de teste**: Dependendo da configuração
3. **Coverage.xml vs sonar-project.properties**: Possível diferença nas regras de inclusão/exclusão

## Recomendações para Melhorar Cobertura

### Alta Prioridade
1. **src/database.py** (70%)
   - Adicionar testes para métodos FIFO: `rebuild_binance_wallet()`, `_load_wallet_ops_config()`
   - Testar casos edge de transações

2. **src/ui_main.py** (69%)
   - UI é difícil de testar automaticamente
   - Considerar separar lógica de negócio da UI
   - Testar callbacks de FIFO Wallet

3. **main.py** (51%)
   - Muita lógica não coberta
   - Refatorar em funções menores testáveis

### Média Prioridade
4. **scripts/import_binance_csv_cli.py** (21%)
   - Criar testes de integração para o script CLI
   - Testar casos de erro e fallbacks

5. **src/favorites_helper.py** (18%)
   - Adicionar testes básicos para lógica de favoritos

## Ações Imediatas
- Manter foco em coverage de `src/` > 90% (código principal)
- Scripts e UI podem ter cobertura menor (ferramentas, difíceis de testar)
- Próxima meta: 80%+ cobertura geral
