# Documentação — app Engenharia

Índice da documentação do repositório. Arquivos normativos e de entrada ficam na **raiz**; material operacional e auditorias ficam nesta pasta.

---

## Entrada e normas

| Documento | Público | Descrição |
| --- | --- | --- |
| [`../../CHANGELOG.md`](../../CHANGELOG.md) | Histórico de versões |
| [`../../README.md`](../../README.md) | Visão geral do app, instalação e links principais |
| [`REGRAS_OBRIGATORIAS.md`](../../REGRAS_OBRIGATORIAS.md) | Desenvolvedores | Padrões fechados: DocTypes, dashboard, testes, commits |
| [`../../docs/audit-deploy-ready.md`](../../docs/audit-deploy-ready.md) | Dev / release | Auditoria deploy-ready |
| [`../../CODEBASE.md`](../../CODEBASE.md) | Desenvolvedores | Inventário técnico (`scripts/generate_codebase.py`) |
| [`../../docs/crosscheck_advocacia.md`](../../docs/crosscheck_advocacia.md) | Desenvolvedores | Paridade estrutural com advocacia |

---

## Usuário final

| Documento | Descrição |
| --- | --- |
| [`manual_usuario.md`](manual_usuario.md) | Manual completo do Desk: obras, financeiro, painel, documentos |
| [`hub_navigation.md`](hub_navigation.md) | Navegação hub, breadcrumb, restaurar aba |
| [`project_documents.md`](project_documents.md) | Document Category, Project Document, naming |

---

## Desenvolvimento e testes

| Documento | Descrição |
| --- | --- |
| [`desenvolvimento.md`](desenvolvimento.md) | Fluxo local: bench, migrate, testes unitários, pre-commit |
| [`../../e2e/README.md`](../../e2e/README.md) | Sessão E2E Playwright (Desk + dados fictícios `PLAYWRIGHT_*`) |

Módulos de teste relevantes: `test_documents.py`, `test_project_document.py`, `test_project_hub.py`, `test_subcontract.py`, `test_reports.py`, `test_print_formats.py`.

---

## Auditorias técnicas (jun/2026, revisão **2026-06-23** — v1.1.0)

Relatórios pontuais de conformidade e UX. Não substituem `REGRAS_OBRIGATORIAS.md`. Métricas: **46** DocTypes, **6** Script Reports, **320** testes, painel com orçado/margem.

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
| Relatórios / placeholders docx | `manual_usuario.md` §10; `engenharia/documents.py`; `project_documents.md` |
| Documentos da obra / categorias | `project_documents.md`; `manual_usuario.md` §10.4 |
| Navegação hub | `hub_navigation.md`; `eng_hub_nav.js` |
| Despesas do Escritório | `manual_usuario.md` §6.7; DocType `Office Expense` |
| Modelos de Etapas | `manual_usuario.md` §4; `Project Stage Template` |
| Guia de dev / CI | `engenharia/docs/desenvolvimento.md` ou `e2e/README.md` |
| Norma / padrão obrigatório | `REGRAS_OBRIGATORIAS.md` (atualizar no mesmo PR) |
| Auditoria ou relatório pontual | `engenharia/docs/audit_<tema>.md` + entrada neste índice |

---

*Última atualização: 2026-06-23 23:24 UTC*
