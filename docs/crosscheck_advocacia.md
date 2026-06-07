# Cross-audit: engenharia ↔ advocacia

> **Atualização:** 2026-06-07 — pós-nivelamento técnico (13 estágios).

## Paridade alcançada

| Área | Advocacia | Engenharia (pós-nivelamento) |
| --- | --- | --- |
| `list_nav.js` | ✅ | ✅ `engenharia.list_nav.goto` + patch Dashboard |
| `customer_from_*` | `cliente_from_servico.js` | ✅ `customer_from_project.js` |
| Placeholders globais | `documentos_placeholders.js` | ✅ `documents_placeholders.js` |
| Notificações scheduler | `notificacoes.py` + daily jobs | ✅ `notifications.py` (4 funções) |
| Scheduler weekly | `verificar_status_servicos` | ✅ `check_project_status_weekly` |
| Reinstall istable | `reinstalar_istable_doctypes` | ✅ `reinstall_child_doctypes` |
| `standard_queries` hub | `legal_case_query` | ✅ `construction_project_query` |
| Hub dashboards | `legal_case_dashboard.py` | ✅ `construction_project_dashboard.py` |
| Client dashboards | `client_dashboard.py` | ✅ `customer_dashboard.py` |
| `test_imports.py` | ✅ | ✅ |
| Reports granulares | 6× `test_report_*.py` | ✅ 5× `test_report_*.py` |
| Whitelist tests | parcial | ✅ `test_whitelist.py` + `test_dashboard_api.py` |
| `CODEBASE.md` | gerado | ✅ `scripts/generate_codebase.py` |
| `.cursorrules` | ✅ | ✅ |
| `docxtpl` em pyproject | ✅ | ✅ |

## Divergências intencionais (manter)

| Item | Motivo |
| --- | --- |
| DocTypes PT vs EN | advocacia brownfield; engenharia greenfield |
| Hub `Legal Case` vs `Construction Project` | domínios distintos |
| KPIs do painel | jurídico vs obra |
| `agent_api` endpoints | superfícies de domínio diferentes |

## Verificação

```bash
bench --site engenharia.local migrate
bench build --app engenharia
bench --site engenharia.local run-tests --app engenharia
```
