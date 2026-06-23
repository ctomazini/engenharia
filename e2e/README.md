# Testes E2E — Playwright

Sessão automatizada que valida o app **engenharia** pelo Desk: login real, navegação nos formulários, criação de dados fictícios e smoke do **Painel de Obras**.

Script principal: [`run-e2e.mjs`](run-e2e.mjs).

---

## Pré-requisitos

1. Bench com site ativo (`bench serve` ou `bench start`)
2. App instalado e migrado: `bench --site engenharia.local install-app engenharia && bench --site engenharia.local migrate`
3. Node.js 18+ e npm
4. Usuário com permissão de Administrator (ou credenciais via env)

---

## Instalação

```bash
cd e2e
npm install
npm run install:browsers   # baixa Chromium do Playwright
```

### Linux — dependências do Chromium

Se o browser falhar com `libnspr4.so` ou similar:

```bash
sudo npx playwright install-deps chromium
```

Em ambientes **sem sudo**, instale as libs do sistema por outro meio ou use um runner CI com imagem Playwright oficial.

---

## Execução

```bash
cd e2e
E2E_PASS=<senha_do_administrator> npm test
```

Com site/bench padrão local:

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `E2E_BASE_URL` | `http://127.0.0.1:8000` | URL do bench |
| `E2E_SITE_HOST` | `engenharia.local` | Header `Host` (multi-site) |
| `E2E_USER` | `Administrator` | Login |
| `E2E_PASS` | *(obrigatório)* | Senha |
| `E2E_DOCX` | `e2e/fixtures/template.docx` | Modelo para Document Template |
| `E2E_OUT_DIR` | `e2e/results/<run_id>/` | Relatório e screenshots de falha |

O script injeta o header `Host` via interceptação de rotas (necessário quando não há entrada em `/etc/hosts`).

---

## O que é exercitado

26 passos na ordem de `setup/demo_data.py` (`CREATION_ORDER`):

Cadastros auxiliares → Cliente → Obra → Etapas / Itens → Contrato (+ **sync Payment**) → Comissão, Subcontrato, Custos, Reembolsáveis → Alvará, Prazos, Tarefa, Medição → Time Log, Comunicação → Document Kit → **`/app/eng-dashboard`**.

Cada execução usa marcador único **`PLAYWRIGHT_<run_id>`** nos campos de texto para identificar registros de teste.

### Fora do escopo atual

- Geração de `.docx` com placeholders (`generate_project_documents`)
- Navegação nos 7 **Script Reports** (gráficos/KPIs) e preview Print Format PDF
- Office Expense (Despesas do Escritório)
- Asserção de parcelas individuais de subcontrato na UI

---

## Implementação (Frappe v16)

1. **Login e rotas** — Playwright abre `/login` e cada `/app/<doctype>/new` + documento salvo
2. **Persistência** — `frappe.db.insert` / `frappe.call` no contexto JS autenticado do browser

No headless, `frappe.ui.form.cur_frm` não fica disponível; a API client-side autenticada é o caminho estável. A sessão continua sendo E2E real (cookies, CSRF, permissões, validações server-side).

---

## Resultados

- Console: ✓/✗ por passo + resumo
- `e2e/results/<run_id>/summary.json` — JSON com marcador, estado e detalhes
- Screenshots em falha (mesma pasta)
- Pasta `results/` está no `.gitignore`

Exit code `0` = todos os passos OK; `1` = ao menos uma falha.

---

## Limpeza dos dados de teste

Registros ficam no site. Para remover manualmente, filtre listas por `PLAYWRIGHT_` ou use console/script customizado por DocType.

**Não** commitar senhas reais; use variável `E2E_PASS` ou conta dedicada de teste.

---

## Evolução

Melhorias futuras possíveis:

- Teardown automatizado por marcador
- Passo de geração de documento Word na obra
- Smoke dos Script Reports (KPI + gráfico)
- Mais asserções puramente UI (preenchimento de campos sem `frappe.db.insert`)
- Job CI com imagem `mcr.microsoft.com/playwright`

*Última atualização: 2026-06-23 23:24 UTC — app alvo v1.1.0*
