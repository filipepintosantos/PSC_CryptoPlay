# v4.3.9 — 2025-12-29

### Added
- `scripts/create_schema.sql`: DDL completo para criar o esquema do zero em novas instalações.

### Changed
- `init_db.py` agora aplica `scripts/create_schema.sql` quando o ficheiro de BD não existe, depois semeia as criptomoedas padrão.
- `scripts/create_schema.sql` inclui triggers para manter `crypto_info.last_quote_date` sincronizado.
- Integração de limpeza automática de DBs de teste durante a execução da suite de testes (`tests/test_cleanup.py`).
- Arquivadas migrações antigas em `scripts/legacy/` e convertidos os scripts originais em stubs para evitar execuções acidentais.
- Atualizado `QUICKSTART.md` e `README.md` com instruções e notas sobre criação de BD e testes.

### Testing
- Executado: suite de testes unitários (105 testes) — todos passaram (OK).
