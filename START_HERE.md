# ⚡ COMECE AQUI - PSC CryptoPlay

## 🚀 Setup em 3 Passos (5 minutos)

### 1️⃣ Executar Setup Automático

```bash
setup.bat
```

✅ Virtual environment criado  
✅ Dependências instaladas  
✅ Diretórios criados  

### 2️⃣ Configurar API Key

Edite o ficheiro `.env` criado:

```
CMC_API_KEY=sua_chave_aqui
```

Obtenha grátis em: https://coinmarketcap.com/api/

### 3️⃣ Executar Primeira Vez

```bash
python main.py
```

✅ Dados recolhidos  
✅ Análise realizada  
✅ Relatório gerado em `reports/crypto_analysis.xlsx`

---

## 📖 Próximos Passos

1. **Abra o Excel**: `reports/crypto_analysis.xlsx`
   - Clique nas setas 🔽 para pesquisar/filtrar
   - Verde = preço acima da média
   - Vermelho = preço abaixo da média

2. **Customize o projeto**: Edite `config/config.ini`
   - Adicione/remova moedas
   - Altere modo de fetch
   - Configure diretórios

3. **Leia documentação completa**: Consulte `INDEX.md`

---

## 💡 Comandos Úteis

```bash
# Atualizar dados (modo rápido)
python main.py

# Adicionar nova moeda
python main.py --symbols BTC,ETH,NOVA_MOEDA

# Recolher histórico completo
python main.py --all-symbols --fetch-mode full

# Apenas gerar novo relatório
python main.py --report-only

# Ver todos os comandos
python main.py --help
```

---

## 🆘 Problemas?

| Problema | Solução |
|----------|---------|
| "Python não reconhecido" | Instale de https://www.python.org/ |
| "Setup não funciona" | Veja `VENV_GUIDE.md` |
| "Sem dados no Excel" | Verifique `.env` tem API key válida |
| "Excel não abre" | Regenere: `python main.py --report-only` |

---

## 📚 Documentação

- **[INDEX.md](INDEX.md)** - Índice completo 📖
- **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido ⚡
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuração 🔧
- **[VENV_GUIDE.md](VENV_GUIDE.md)** - Virtual Environment 🐍
- **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** - Projeto finalizado ✅

---

## ✅ Checklist

- [ ] Setup executado (`setup.bat`)
- [ ] `.env` configurado com API key
- [ ] Primeiro `python main.py` executado
- [ ] `reports/crypto_analysis.xlsx` gerado
- [ ] Excel aberto e analisado

**Pronto! 🎉**

---

**Versão**: 1.1.0  
**Data**: Dezembro 1, 2024

Dúvidas? Consulte `INDEX.md` para navegação completa.
