# Seção 6 — Integração Google Calendar

**App:** `engenharia` · **Frappe:** v16 · **Data:** 2026-06-06

---

## 6.1 Estado atual no app engenharia

### calendar.js / Calendar View custom

| Item | Status |
|---|---|
| `doctype_calendar_js` em hooks | ❌ Comentado — não configurado |
| DocTypes com calendar.js próprio | 0 |

### Sincronização implementada (`calendar_sync.py`)

| DocType | Evento hooks | Destino | Campos mapeados |
|---|---|---|---|
| **Deadline** | after_insert, on_update | Event nativo | `due_date` → starts_on/ends_on, subject ← description, cancel se Concluído |
| **Permit** | after_insert, on_update | Event nativo | `expiry_date` ou `protocol_date`, cancel se Cancelado/Indeferido |

**Custom fields Event:** `custom_source_doctype`, `custom_source_name` (seed migrate).

**Task:** ❌ Não sincroniza para Event/Google via app engenharia.

**Calendar View Frappe:** Deadline e Permit **podem** aparecer no calendário desk se Event for criado — usuário vê Events, não diretamente Deadline/Permit.

---

## 6.2 Google Calendar API no Frappe v16

### Verificação do bench

```
/home/frappe/frappe-bench/apps/frappe/frappe/integrations/doctype/google_calendar/
  google_calendar.py  (901 linhas)
  google_calendar.json
  google_calendar.js
```

| Pergunta | Resposta |
|---|---|
| Módulo `google_calendar` existe? | ✅ Sim — DocType **Google Calendar** (integração OAuth) |
| DocTypes nativos que usam | **Event** — sync bidirecional via `Google Calendar` settings por usuário |
| Infra OAuth Google | ✅ `GoogleOAuth`, scopes `calendar`, senha criptografada |
| engenharia usa Google Calendar DocType? | ❌ Não — só Event via calendar_sync |

### O que falta para Deadline/Task → Google Calendar

| Etapa | Esforço | Detalhe |
|---|---|---|
| Deadline → Event | ✅ Feito | Event pode sync para Google se usuário configurar Google Calendar |
| Task → Event | 🟡 Médio | Criar `sync_task_to_event` similar a Deadline |
| Permit → Google direto | 🟢 Baixo | Já passa por Event |
| OAuth setup admin | 🟡 | Configurar Google Cloud Console + Google Calendar DocType por usuário |
| Sync seletivo por projeto | 🔴 | Não implementado — todos Events do usuário |

**Estimativa esforço Task + docs:** 1–2 dias dev.

**Estimativa setup OAuth produção:** 0,5–1 dia infra + testes.

---

## 6.3 Alternativas

| Abordagem | Prós | Contras | Esforço |
|---|---|---|---|
| **A) Usar Event + Google Calendar nativo Frappe** | Zero código extra; OAuth pronto | Usuário configura sync; Tasks fora | 🟢 Baixo |
| **B) CalDAV** | Padrão aberto | Frappe não tem CalDAV built-in | 🔴 Alto |
| **C) API custom `google-api-python-client`** | Controle total | Duplica OAuth Frappe; manutenção | 🟡 Médio-alto |
| **D) Webhook outbound** | Integrações externas | Infra adicional | 🟡 Médio |

**Recomendação:** 🟢 **Opção A** — estender `calendar_sync` para **Task** e documentar configuração Google Calendar no manual admin.

---

## Inconsistências

1. 🟡 **Task** não gera Event — prazos internos não aparecem no Google Calendar.
2. 🟡 **Documentação admin** ausente para conectar Google Calendar.
3. 🟢 **Deadline/Permit** cobertos via Event.

---

*Auditoria somente leitura.*

*Última atualização: 2026-06-23 23:24 UTC — app v1.1.0*
