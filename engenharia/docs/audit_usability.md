# Seção 3 — Verificação de Usabilidade

**App:** `engenharia` · **Data:** 2026-06-06 (nota 2026-06-09: Office Expense e Modelos de Etapas não auditados neste snapshot)

---

## 3.1 Formulários — resumo por DocType standalone

Legenda: ✅ OK · 🟡 Atenção · 🔴 Problema

| DocType | Ordem campos | Seções | reqd | read_only | Observações |
|---|---|---|---|---|---|
| Construction Project | ✅ | ✅ Hub completo | customer reqd | Título, progresso, totais | 🟡 Campos financeiros em permlevel 1 — User não vê orçamento |
| Customer | ✅ | Contatos/endereços | Nome + doc | — | CPF/CNPJ validados |
| Engineering Contract | ✅ | Parcelas, aditivos | project reqd | current_value parcial | Botão aplicar aditivo |
| Commission | ✅ | Valores, pagamentos | project, supplier, total | total_paid, outstanding, status | set_query exclui obra cancelada |
| Payment | ✅ | Financeiro | project | título auto | Indicador list view |
| Work Cost | ✅ | Custo | project, amount | — | `funded_by` Escritório/Cliente afeta caixa |
| Subcontract | ✅ | Valores, pagamentos | project, supplier, total | total_paid, outstanding, status | `funded_by` Escritório/Cliente afeta KPI e caixa |
| Project Item | 🟡 | Técnico denso | technical_item | outputs computed | Curva de aprendizado alta |
| Task | ✅ | Simples | subject | — | Timer global disponível |
| Deadline | ✅ | Prazo + órgão | due_date | — | — |
| Permit | ✅ | Protocolo | project | — | — |
| Construction Measurement | ✅ | Medição | project | — | Poucos testes |
| Time Log | ✅ | Timer | activity, project | duration se timer | UX timer global |
| Communication Log | ✅ | Comunicação | subject | — | — |
| Technical Item | 🟡 | Fórmulas | item_name | — | Requer treinamento |
| Cadastros auxiliares | ✅ | Minimal | nome único | — | Quick entry onde aplicável |
| Engineering Settings | ✅ | Single | — | — | CNPJ escritório |

### Inconsistências transversais

1. 🟡 **Project Item** — formulário complexo para usuário operacional; falta `description` em campos de fórmula.
2. 🟡 **set_query** só em Commission — outros Links de projeto poderiam filtrar obras canceladas.
3. 🟢 **Títulos compostos** — listas mostram descritor legível (hide_name_column nos list.js principais).

---

## 3.2 List Views

| DocType | list.js | hide_name | Indicador status | Filtros rápidos |
|---|---|---|---|---|
| Construction Project | ✅ | ✅ title | via status field | 🟡 |
| Payment | ✅ | ✅ | ✅ cores | ✅ onload buttons |
| Commission | ✅ | ✅ | ✅ | 🟡 |
| Engineering Contract | ✅ | ✅ | ✅ | 🟡 |
| Work Cost | ✅ | ✅ | ✅ | 🟡 |
| Subcontract | ✅ | ✅ | ✅ funded_by Cliente | 🟡 |
| Deadline | ✅ | ✅ | ✅ | 🟡 |
| Permit | ✅ | ✅ | ✅ | 🟡 |
| Customer | ✅ | parcial | 🟡 | — |
| Task | ❌ stub | — | 🟡 | — |
| Project Stage | ❌ | — | 🟡 | — |
| Time Log | ✅ | ✅ | 🟡 | — |

**Gap:** 🟡 Task e Project Stage sem `*_list.js` customizado — coluna `name` ainda visível ou menos indicadores.

---

## 3.3 Fluxos operacionais

### Fluxo 1: Nova obra

1. **Customer** — criar cliente (CPF/CNPJ) ✅  
2. **Construction Project** — vincular customer, endereço, status Orçamento ✅  
3. **Project Item** — adicionar itens técnicos / orçamento 🟡 (complexo)  
4. **Engineering Contract** — contrato + parcelas ✅  
5. **Payment** — sync automático das parcelas ✅  

**Fricção:** 🟡 Orçamento detalhado (Project Item + BDI) exige perfil Manager para ver totais no projeto. User operacional não vê `spec_project_total`.

### Fluxo 2: Registro de medição

1. **Construction Measurement** — selecionar projeto ✅  
2. Itens com etapa (Project Stage) ✅  
3. Vínculo contrato 🟡 manual se necessário  

**Fricção:** 🟡 Pouca documentação in-app; apenas 2 testes.

### Fluxo 3: Controle de comissão

1. **Commission** — projeto + fornecedor + valor ✅  
2. Pagamentos na child table ✅  
3. Saldo no projeto (Manager) ✅  

**Fricção:** 🟢 set_query evita obra cancelada. User **não acessa** Commission (by design).

### Fluxo 4: Gestão de prazos

1. **Deadline** — projeto, data, tipo ✅  
2. Sync calendário Frappe Event ✅  
3. Notificações fixture ✅  

### Fluxo 5: Despesas de obra

1. **Work Cost** — lançamento avulso ✅  
2. **Subcontract** — contrato com prestador + parcelas ✅  
3. Campo **Quem arca** (`funded_by`) em ambos: Escritório (fluxo de caixa, KPIs, margem) vs Cliente (só administração na obra) ✅  
4. Categoria/fornecedor via Link ✅  
5. Manager only (write) ✅  

### Fluxo 6: Controle de contratos

1. **Engineering Contract** ✅  
2. Parcelas child ✅  
3. Aditivos + botão aplicar ✅  
4. Sync Payment ✅  

### Fluxo 7: Documentos e templates

1. **Document Template** + **Engineering Settings** ✅  
2. Gerar via botão no projeto ✅  
3. Document Kit para pacotes ✅  

**Fricção:** 🟡 Template exige campos técnicos; manual necessário (Seção 10).

---

## Inconsistências prioritárias

| # | Problema | Severidade |
|---|---|---|
| 1 | Engenharia User bloqueado de fluxos financeiros sem mensagem explicativa | 🟡 |
| 2 | Task/Project Stage list views básicas | 🟡 |
| 3 | Project Item curva de aprendizado | 🟡 |
| 4 | Measurement subdocumentado | 🟡 |

---

*Auditoria somente leitura.*
