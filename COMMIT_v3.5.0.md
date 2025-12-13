# Commit v3.5.0 - Sistema de Classificação de Favoritos A/B/C

## Resumo das Alterações

### Nova Funcionalidade: Sistema de Classificação de Favoritos (A, B, C)

Implementado sistema de três níveis de prioridade para favoritos, substituindo o sistema binário anterior:
- **Classe A** (⭐⭐⭐): Prioridade máxima - Dourado
- **Classe B** (⭐⭐): Prioridade secundária - Laranja  
- **Classe C** (⭐): Prioridade terciária - Azul claro

### Ficheiros Modificados

#### Configuração e Documentação
- `config/config.ini` - Adicionadas listas favorites_a, favorites_b, favorites_c
- `CHANGELOG.md` - Documentada versão 3.5.0
- `DEVELOPMENT.md` - Adicionada secção de gestão de versões
- `FAVORITES_CLASSIFICATION.md` - **NOVO**: Documentação completa do sistema

#### Base de Dados
- `src/database.py` - Coluna `favorite` alterada de BOOLEAN para TEXT ('A', 'B', 'C', NULL)
  - Nova função: `set_favorite_class(code, class)`
  - Atualizado: `get_all_crypto_info(favorite_class=...)`
  - Mantida compatibilidade: `set_favorite(code, bool)` → converte para classe A

#### Módulos e Helpers
- `src/favorites_helper.py` - **NOVO**: Funções utilitárias
  - `get_favorites_from_config()` - Retorna dict por classe
  - `validate_and_update_favorites()` - Sincronização automática
  - `get_favorite_class()` - Retorna classe de um símbolo
  - `get_all_favorites_list()` - Lista plana de favoritos

#### Scripts
- `scripts/mark_favorites.py` - Atualizado para três classes com emojis diferentes
- `scripts/add_symbols.py` - **NOVO**: Adicionar símbolos com classificação via CLI
- `scripts/migrate_to_favorite_classes.py` - **NOVO**: Migração de bases existentes
- `scripts/update_version.py` - **NOVO**: Sincronização de versões

#### Aplicação Principal
- `main.py` - Adicionada validação automática de favoritos ao executar
- `src/excel_reporter.py` - Relatórios mostram A/B/C com cores
  - Ajustadas larguras de colunas (pixels → Excel units)
  - Classe A: Dourado (#FFD700)
  - Classe B: Laranja (#FFA500)
  - Classe C: Azul claro (#87CEEB)

#### Gestão de Versões
- `src/__init__.py` - Versão atualizada para 3.5.0 (fonte única)
- `setup.py` - Função `get_version()` lê dinamicamente de __init__.py
- `sonar-project.properties` - Versão sincronizada via script

### Nova Arquitetura: Single Source of Truth para Versões

Implementado padrão de centralização:
1. **`src/__init__.py`** - Única fonte de verdade (`__version__ = "3.5.0"`)
2. **`setup.py`** - Lê dinamicamente via regex
3. **`sonar-project.properties`** - Sincronizado por `update_version.py`
4. **`CHANGELOG.md`** - Atualização manual obrigatória

Elimina duplicação e inconsistências entre ficheiros.

## Comandos Git para Commit

### Usando Git Bash ou Terminal com Git:

```bash
# 1. Adicionar todas as alterações
git add -A

# 2. Verificar status
git status

# 3. Fazer commit com mensagem descritiva
git commit -m "feat: Sistema de classificação de favoritos A/B/C

- Implementado sistema de três níveis (A/B/C) para favoritos
- Coluna favorite alterada de BOOLEAN para TEXT
- Adicionados módulos favorites_helper.py e scripts auxiliares
- Relatórios Excel mostram classificação com cores
- Centralizada gestão de versões em src/__init__.py
- Criado script update_version.py para sincronização
- Atualizada documentação (FAVORITES_CLASSIFICATION.md)

Closes #versão_3.5.0"

# 4. (Opcional) Push para repositório remoto
git push origin main
```

### Usando VSCode Source Control:

1. Abra a vista **Source Control** (Ctrl+Shift+G)
2. Reveja as alterações nos ficheiros staged
3. Escreva a mensagem de commit:
   ```
   feat: Sistema de classificação de favoritos A/B/C

   - Implementado sistema de três níveis (A/B/C) para favoritos
   - Coluna favorite alterada de BOOLEAN para TEXT
   - Adicionados módulos favorites_helper.py e scripts auxiliares
   - Relatórios Excel mostram classificação com cores
   - Centralizada gestão de versões em src/__init__.py
   - Criado script update_version.py para sincronização
   - Atualizada documentação (FAVORITES_CLASSIFICATION.md)
   ```
4. Clique em **Commit** (✓)
5. (Opcional) Clique em **Push** para enviar ao remoto

## Verificação Pós-Commit

```bash
# Verificar último commit
git log -1 --stat

# Verificar versão
python -c "from src import __version__; print(f'Version: {__version__}')"

# Verificar favoritos
python scripts/mark_favorites.py

# Testar sistema completo
python main.py --report-only --favorites
```

## Estatísticas do Commit

- **13 ficheiros modificados**
- **4 novos ficheiros** (favorites_helper.py, add_symbols.py, migrate_to_favorite_classes.py, update_version.py)
- **1 novo documento** (FAVORITES_CLASSIFICATION.md)
- **Versão**: 3.5.0
- **Data**: 2025-12-13
- **Testes**: 94 testes passando (100% success rate)
  - 30 testes database (incluindo 3 novos para classificação A/B/C)
  - 10 testes excel_reporter
  - 24 testes main
  - 18 testes project
  - 9 testes volatility_analysis
  - 7 testes yfinance_api
  - 2 testes seed

## Notas Importantes

✅ **Todos os 94 testes passam** (0 falhas)  
✅ Sistema testado com 88 símbolos  
✅ Migração testada (7 favoritos → classe A)  
✅ Excel gerado com sucesso  
✅ Documentação completa  
✅ Compatibilidade retroativa mantida  
✅ Testes atualizados para o novo sistema A/B/C  
✅ Função `set_favorite_class()` corrigida para aceitar NULL  

---

Este ficheiro pode ser apagado após o commit.
