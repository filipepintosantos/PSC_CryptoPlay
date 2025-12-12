# Estrutura de Colunas do Relatório Excel

## Versão 2.9.2 - 21 Colunas (A-U)

### Colunas Base (A-E)
- **A**: Favorito (X ou vazio)
- **B**: Símbolo (BTC, ETH, etc.)
- **C**: Última Cotação
- **D**: Penúltima Cotação
- **E**: Período (12M, 6M, 3M, 1M)

### Estatísticas Baseadas em Média (F-J)
- **F**: Mínimo
- **G**: Máximo
- **H**: Média
- **I**: Desvio Padrão (Std)
- **J**: Média-Desvio = `H - I`

### Comparações com Média (K-N)
- **K**: Last-AVG% = `(C - H) / H` 
- **L**: Last-A-S% = `(C - J) / J`
- **M**: 2nd-AVG% = `(D - H) / H`
- **N**: 2nd-A-S% = `(D - J) / J`

### Estatísticas Baseadas em Mediana (O-Q)
- **O**: MEDIAN (Mediana)
- **P**: MAD (Median Absolute Deviation)
- **Q**: MED-MAD = `O - P`

### Comparações com Mediana (R-U)
- **R**: Last-MED% = `(C - O) / O`
- **S**: Last-M-M% = `(C - Q) / Q`
- **T**: 2nd-MED% = `(D - O) / O`
- **U**: 2nd-M-M% = `(D - Q) / Q`

## Validação das Fórmulas

### Comparações com Média
| Coluna | Nome | Fórmula | Validação |
|--------|------|---------|-----------|
| K | Last-AVG% | `(C-H)/H` | ✅ Compara última cotação com média |
| L | Last-A-S% | `(C-J)/J` | ✅ Compara última cotação com média-desvio |
| M | 2nd-AVG% | `(D-H)/H` | ✅ Compara penúltima cotação com média |
| N | 2nd-A-S% | `(D-J)/J` | ✅ Compara penúltima cotação com média-desvio |

### Comparações com Mediana
| Coluna | Nome | Fórmula | Validação |
|--------|------|---------|-----------|
| R | Last-MED% | `(C-O)/O` | ✅ Compara última cotação com mediana |
| S | Last-M-M% | `(C-Q)/Q` | ✅ Compara última cotação com mediana-MAD |
| T | 2nd-MED% | `(D-O)/O` | ✅ Compara penúltima cotação com mediana |
| U | 2nd-M-M% | `(D-Q)/Q` | ✅ Compara penúltima cotação com mediana-MAD |

## Formatação Condicional
- **Verde (C6EFCE)**: Valor acima da baseline (positivo)
- **Vermelho (FFC7CE)**: Valor abaixo da baseline (negativo)

Aplicada em todas as colunas de comparação (L-O e R-U)
