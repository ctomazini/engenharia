# Cross-audit: engenharia ↔ advocacia

> **Atualização:** 2026-06-11 — engenharia: 56 DocTypes; advocacia v1.0.0 EN + labels PT (ver `REGRAS_ADVOCACIA.md`).

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
| Reports granulares | 6× `test_report_*.py` | ✅ 6+ (`test_report_*`, `test_consolidated_cost`) |
| Print formats reports | 3 DocType | ✅ 15 (3 DocType + 12 Report) + `boot_session` |
| Office Expense | ✅ (sem hub link) | ✅ integrado painel + caixa |
| Whitelist tests | parcial | ✅ `test_whitelist.py` + `test_dashboard_api.py` |
| `CODEBASE.md` | gerado | ✅ `scripts/generate_codebase.py` |
| `.cursorrules` | ✅ | ✅ |
| `docxtpl` em pyproject | ✅ | ✅ |

## Divergências intencionais (manter)

| Item | Motivo |
| --- | --- |
| DocTypes (nomenclatura interna) | advocacia v1.0.0+ EN + labels PT; engenharia greenfield EN | UI PT em ambos |
| Hub `Legal Case` vs `Construction Project` | domínios distintos |
| KPIs do painel | jurídico vs obra |
| `agent_api` endpoints | superfícies de domínio diferentes |

## Verificação

```bash
bench --site engenharia.local migrate
bench build --app engenharia
bench --site engenharia.local run-tests --app engenharia
```
