# Sistema de Classificação de Favoritos (A, B, C)

## Visão Geral

O sistema de favoritos foi atualizado de um sistema binário (favorito/não favorito) para um sistema de classificação com três níveis (A, B, C):

- **Classe A**: Criptomoedas de prioridade máxima (top priority)
- **Classe B**: Criptomoedas de prioridade secundária
- **Classe C**: Criptomoedas de prioridade terciária

## Alterações Realizadas

### 1. Configuração (config/config.ini)

Foram adicionadas três novas listas de configuração:

```ini
[symbols]
# Class A: Top priority cryptocurrencies
favorites_a = BTC,ETH,SOL,ADA,LINK,ATOM,XTZ

# Class B: Secondary priority cryptocurrencies
favorites_b = XRP,BNB,TRX,DOGE,DOT,AVAX

# Class C: Tertiary priority cryptocurrencies
favorites_c = BCH,XMR,XLM,LTC,AAVE
```

A lista `favorites` foi mantida para compatibilidade retroativa e corresponde à Classe A.

### 2. Base de Dados

#### Alteração da Coluna

A tabela `crypto_info` foi atualizada:
- **Antes**: `favorite BOOLEAN DEFAULT 0`
- **Depois**: `favorite_class TEXT DEFAULT NULL` com constraint `CHECK(favorite_class IN ('A', 'B', 'C', NULL))`

#### Script de Migração

Execute o script de migração para atualizar bases de dados existentes:

```bash
python scripts/migrate_to_favorite_classes.py
```

Este script:
1. Adiciona a coluna `favorite_class`
2. Migra favoritos existentes para Classe A
3. Mantém a coluna `favorite` antiga para compatibilidade

### 3. Funções da Base de Dados (src/database.py)

Novas funções adicionadas:

```python
# Nova função principal
db.set_favorite_class(code, 'A')  # Define classe A, B, C ou None

# Função de compatibilidade (converte para classe A)
db.set_favorite(code, True)  # Marca como favorito classe A

# Buscar favoritos por classe
db.get_all_crypto_info(favorite_class='A')  # Apenas classe A
db.get_all_crypto_info(favorites_only=True)  # Todas as classes
```

### 4. Validação Automática de Favoritos

O sistema agora valida automaticamente as classificações sempre que executa `main.py`:

```python
from favorites_helper import validate_and_update_favorites

# Atualiza automaticamente as classificações baseado no config.ini
updated = validate_and_update_favorites(db, config)
```

### 5. Scripts Atualizados

#### mark_favorites.py

Atualizado para marcar favoritos em todas as três classes:

```bash
python scripts/mark_favorites.py
```

Saída:
```
Favorites from config.ini:
  Class A (Top priority): BTC, ETH, SOL, ADA, LINK, ATOM, XTZ
  Class B (Secondary): XRP, BNB, TRX, DOGE, DOT, AVAX
  Class C (Tertiary): BCH, XMR, XLM, LTC, AAVE

Marked cryptocurrencies as favorites:
  Class A: 7
  Class B: 6
  Class C: 5

Class A favorites in database:
  ⭐⭐⭐ BTC - Bitcoin
  ⭐⭐⭐ ETH - Ethereum
  ...
```

#### add_symbols.py (NOVO)

Script para adicionar novos símbolos com classificação:

```bash
# Adicionar símbolos específicos
python scripts/add_symbols.py BTC ETH --class A
python scripts/add_symbols.py XRP BNB --class B

# Adicionar todos do config.ini com classificações
python scripts/add_symbols.py --from-config
```

### 6. Relatórios Excel

Os relatórios Excel foram atualizados para mostrar as classificações:

- **Coluna de Favoritos**: Mostra `A`, `B` ou `C` em vez de `X`
- **Cores**:
  - Classe A: 🟡 Dourado (#FFD700)
  - Classe B: 🟠 Laranja (#FFA500)
  - Classe C: 🔵 Azul Claro (#87CEEB)

## Como Usar

### Adicionar Novos Símbolos com Classificação

1. Edite `config/config.ini` e adicione o símbolo à lista apropriada (`favorites_a`, `favorites_b`, ou `favorites_c`)
2. Execute o main.py - a validação automática irá aplicar as classificações

Ou use o script helper:

```bash
python scripts/add_symbols.py MATIC ALGO --class B
```

### Atualizar Classificações Existentes

1. Mova o símbolo entre as listas no `config/config.ini`
2. Execute `python scripts/mark_favorites.py` ou execute o `main.py`

### Visualizar Favoritos Atuais

```bash
python scripts/mark_favorites.py
```

## Módulo Helper (src/favorites_helper.py)

Novas funções utilitárias disponíveis:

```python
from favorites_helper import (
    get_favorites_from_config,      # Retorna dict {'A': [...], 'B': [...], 'C': [...]}
    get_all_favorites_list,          # Retorna lista plana de todos os favoritos
    get_favorite_class,              # Retorna classe de um símbolo específico
    validate_and_update_favorites    # Valida e atualiza todas as classificações
)
```

## Compatibilidade Retroativa

O sistema mantém compatibilidade com código antigo:

- A função `set_favorite(code, True)` ainda funciona e define como Classe A
- A coluna `favorite` antiga é mantida (opcional)
- Listas de favoritos antigas são aceitas (tratadas como Classe A)

## Vantagens do Novo Sistema

1. **Priorização**: Permite priorizar atualizações por importância
2. **Organização**: Agrupa criptomoedas por relevância
3. **Flexibilidade**: Fácil de mover símbolos entre classes
4. **Validação Automática**: Garante consistência entre config e banco de dados
5. **Visualização Clara**: Cores diferentes no Excel facilitam identificação

## Próximos Passos Sugeridos

1. **Filtros por Classe**: Adicionar argumentos CLI `--class A/B/C`
2. **Alertas Prioritários**: Configurar alertas diferentes por classe
3. **Análise Separada**: Gerar relatórios específicos por classe
4. **Quotas de API**: Priorizar chamadas de API baseado na classe
