# Navegação hub ↔ satélites

Guia técnico da navegação entre **Construction Project** (hub) e DocTypes satélite.

## Arquivo principal

`engenharia/public/js/eng_hub_nav.js` — incluído globalmente via `hooks.py` (`app_include_js`).

## DocTypes cobertos

**Hub:** `Construction Project`

**Satélites (15):** Engineering Contract, Payment, Work Cost, Subcontract, Reimbursable Expense, Deadline, Permit, Task, Communication Log, Time Log, Construction Measurement, Commission, Project Document, Project Stage, Project Item.

Campo de vínculo padrão: `project`. Exceção: `Commission` usa `construction_project`.

## Funcionalidades

### Breadcrumb

Renderizado diretamente no `<ul class="navbar-breadcrumbs">` do formulário ativo (não depende do mecanismo nativo multi-page do Frappe).

Cadeia típica:

`Home → Workspace → [Painel] → {ID obra} → {DocType} → {ID documento}`

- IDs curtos no crumb da obra e do documento (sem título composto).
- Crumb **Painel de Obras** aparece quando a rota anterior foi `eng-dashboard`.

### Voltar à obra

Botão primário **Voltar à obra** em todos os satélites (exceto obra nova).

### Restaurar aba do hub

Antes de sair do hub, o contexto `{ project, tab }` é salvo em `sessionStorage`. Ao retornar, a aba ativa (Financeiro, Documentos, etc.) é reaberta.

Helpers globais:

| Função | Uso |
| --- | --- |
| `eng_hub_nav_follow_route(route_str)` | Navega preservando contexto da aba |
| `eng_hub_nav_new_doc(doctype, defaults)` | Novo documento satélite |
| `eng_hub_nav_set_route(...)` | Wrapper de `frappe.set_route` |
| `eng_hub_nav_restore_tab(frm)` | Restaura aba (chamado no refresh da obra) |

## API de debug

No console do browser:

```javascript
eng_hub_nav.VERSION          // versão do módulo
eng_hub_nav.debug_breadcrumbs()
```

## Integração

- `hub.js` e `construction_project.js` usam os helpers `eng_hub_nav_*`.
- `customer_from_project.js` reutiliza `eng_hub_nav.SATELLITE_DOCTYPES`.

*Última atualização: 2026-06-23 23:24 UTC — app v1.1.0*
