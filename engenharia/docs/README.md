# Documentação — app Engenharia

Índice da documentação do repositório. Arquivos normativos e de entrada ficam na **raiz**; material operacional e auditorias ficam nesta pasta.

---

## Entrada e normas

| Documento | Público | Descrição |
| --- | --- | --- |
| [`README.md`](../../README.md) | Todos | Visão geral do app, instalação e links principais |
| [`REGRAS_OBRIGATORIAS.md`](../../REGRAS_OBRIGATORIAS.md) | Desenvolvedores | Padrões fechados: DocTypes, dashboard, testes, commits |
| [`../../docs/audit-deploy-ready.md`](../../docs/audit-deploy-ready.md) | Dev / release | Auditoria deploy-ready (2026-06-07) |

---

## Usuário final

| Documento | Descrição |
| --- | --- |
| [`manual_usuario.md`](manual_usuario.md) | Manual completo do Desk: obras, financeiro, painel, documentos |

---

## Desenvolvimento e testes

| Documento | Descrição |
| --- | --- |
| [`desenvolvimento.md`](desenvolvimento.md) | Fluxo local: bench, migrate, testes unitários, pre-commit |
| [`../../e2e/README.md`](../../e2e/README.md) | Sessão E2E Playwright (Desk + dados fictícios `PLAYWRIGHT_*`) |

Módulos de teste relevantes: `test_reports.py` (gráficos/KPIs dos Script Reports), `test_documents.py` (placeholders docx), `test_subcontract.py`.

---

## Auditorias técnicas (jun/2026)

Relatórios pontuais de conformidade e UX. Não substituem `REGRAS_OBRIGATORIAS.md`.

| Documento | Escopo |
| --- | --- |
| [`audit_code.md`](audit_code.md) | Código Python/JS, permissões, queries, hooks |
| [`audit_dashboard.md`](audit_dashboard.md) | Painel de Obras (backend + frontend) |
| [`audit_data_integrity.md`](audit_data_integrity.md) | Integridade de dados e rollups |
| [`audit_links.md`](audit_links.md) | Links, navegação e workspace |
| [`audit_usability.md`](audit_usability.md) | Usabilidade e formulários |
| [`audit_ai_readiness.md`](audit_ai_readiness.md) | Preparação para agentes/API |
| [`audit_google_calendar.md`](audit_google_calendar.md) | Sincronização com calendário |
| [`../../docs/audit-deploy-ready.md`](../../docs/audit-deploy-ready.md) | Veredito deploy-ready + gates E2E |

---

## Onde colocar documentação nova

| Tipo | Local |
| --- | --- |
| Manual de uso (PT) | `engenharia/docs/manual_usuario.md` |
| Relatórios / placeholders docx | `manual_usuario.md` §6.6 e §10; código em `engenharia/documents.py`, `engenharia/report_visuals.py` |
| Guia de dev / CI | `engenharia/docs/desenvolvimento.md` ou `e2e/README.md` |
| Norma / padrão obrigatório | `REGRAS_OBRIGATORIAS.md` (atualizar no mesmo PR) |
| Auditoria ou relatório pontual | `engenharia/docs/audit_<tema>.md` + entrada neste índice |
