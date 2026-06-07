# Guia de desenvolvimento — app Engenharia

Referência rápida para quem mantém o app no bench Frappe v16 (**sem ERPNext**).

Normas completas: [`REGRAS_OBRIGATORIAS.md`](../../REGRAS_OBRIGATORIAS.md).

---

## Ambiente local

```bash
cd $PATH_TO_BENCH
bench start                    # ou bench serve --port 8000
bench --site <site> migrate
bench --site <site> run-tests --app engenharia
```

Site de referência deste repositório: `engenharia.local`.

---

## Testes automatizados

### Unitários e integração (Python)

```bash
bench --site engenharia.local run-tests --app engenharia
```

- Código em `engenharia/tests/`
- Gates úteis após mudanças pontuais:
  - Relatórios: `bench --site engenharia.local run-tests --module engenharia.tests.test_reports`
  - Documentos/placeholders: `bench --site engenharia.local run-tests --module engenharia.tests.test_documents`
  - Subcontratos: `bench --site engenharia.local run-tests --module engenharia.tests.test_subcontract`
- Padrão: `tearDown` com `frappe.db.rollback()`; CPF/CNPJ únicos nos factories
- **Definition of Done:** suite verde em site com app instalado

### E2E Playwright (Desk)

Sessão de fumaça ponta a ponta: login, todos os DocTypes principais, sync de pagamentos e painel.

```bash
cd e2e
npm install
npm run install:browsers
E2E_PASS=<senha_admin> npm test
```

Detalhes, variáveis de ambiente e limpeza de dados: [`e2e/README.md`](../../e2e/README.md).

Recomendado após mudanças em formulários, permissões, sync financeiro, painel, **Script Reports** ou **placeholders de documento**.

---

## Estrutura útil

| Área | Caminho |
| --- | --- |
| DocTypes | `engenharia/engenharia/doctype/` |
| Painel | `engenharia/engenharia/page/eng_dashboard/`, `engenharia/dashboard/` |
| Relatórios | `engenharia/engenharia/report/`, helper `engenharia/report_visuals.py` |
| Documentos docx | `engenharia/documents.py` (`PLACEHOLDER_REFERENCE`) |
| Setup / migrate | `engenharia/engenharia/setup/` |
| Testes Python | `engenharia/tests/` |
| Testes E2E | `e2e/` |

---

## Qualidade de código

```bash
cd apps/engenharia
pre-commit install
pre-commit run --all-files
```

Ferramentas: ruff, eslint, prettier, pyupgrade.

---

## Commits

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `test:`, …)
- Preferência histórica: **um DocType por commit** em features novas
- Checklist pré-commit: §13 de `REGRAS_OBRIGATORIAS.md`

---

## Dados de demonstração

Seed idempotente (marcador `_DEMO_`):

```bash
bench --site engenharia.local execute engenharia.engenharia.setup.demo_data.setup
```

Teardown:

```bash
bench --site engenharia.local execute engenharia.engenharia.setup.demo_data.teardown
```

Não usar seed de demo em produção.
