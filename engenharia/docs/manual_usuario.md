# Manual do Usuário — Módulo Engenharia

Sistema de gestão de obras de engenharia civil integrado ao Frappe/ERPNext Desk.

---

## 1. Visão Geral

### O que o sistema faz

O módulo **Engenharia** centraliza a operação de um escritório de projetos e obras:

- Cadastro de **clientes**, **fornecedores** e **obras**
- **Orçamento técnico** com itens, fórmulas e revisões
- **Contratos**, **parcelas** e **pagamentos**
- **Custos de obra**, **despesas reembolsáveis** e **comissões**
- **Prazos**, **tarefas**, **alvarás** e **medições**
- **Documentos** gerados a partir de modelos Word
- **Painel** com visão operacional e financeira

### Perfis de acesso

| Perfil | O que pode fazer |
|---|---|
| **Engenharia Manager** | Acesso completo: operacional + financeiro + configurações sensíveis (orçamento total da obra, comissões, contratos, pagamentos, custos) |
| **Engenharia User** | Operacional: projetos, etapas, itens técnicos da obra, prazos, tarefas, alvarás, medições, registros de horas e comunicações. **Não vê** contratos, pagamentos, comissões, custos nem a zona financeira do painel |

Se você tentar abrir um registro financeiro sem permissão, o sistema exibirá *Permissão insuficiente* — isso é esperado para o perfil User.

### Como acessar

1. Abra o navegador no endereço do site (ex.: `https://engenharia.local` ou URL da sua instalação).
2. Faça login com usuário e senha fornecidos pelo administrador.
3. No menu lateral, abra o workspace **Engenharia** ou a página **Painel de Obras**.

---

## 2. Painel Principal

O **Painel de Obras** reúne indicadores e atalhos do dia a dia.

### O que cada área mostra

| Área | Conteúdo |
|---|---|
| **Cabeçalho / Hero** | Data, período selecionado (7, 15 ou 30 dias), resumo de urgência |
| **Filtros** | Alterar janela de tempo e limites das listas |
| **Zona de atenção + Próximos compromissos** | Duas colunas lado a lado: tiles de ação imediata e os dois compromissos mais urgentes (prazos, tarefas etc.) |
| **Agenda / Timeline** | Prazos, tarefas e compromissos operacionais no período (sem pagamentos) |
| **Zona financeira** *(somente Manager)* | Saúde operacional, KPIs, entradas×saídas do mês, composição de custos, listas de parcelas/despesas |
| **Obras ativas** | Lista com filtros de linhas (5/10/15), cores por status e prazo — largura total |
| **Comissões** *(Manager, acordeão)* | KPIs e lista de comissões — expanda a seção no rodapé para ver detalhes |

### Diferença Manager vs User

- **Manager** vê KPIs financeiros, gráficos de fluxo e listas de pagamentos.
- **User** vê apenas indicadores operacionais (prazos, tarefas, protocolos, horas). A seção financeira **não aparece** — não há mensagem de “acesso negado”, a área simplesmente não é exibida.

### Agenda e compromissos

- A **agenda** e os **próximos compromissos** mostram apenas itens operacionais: prazos, tarefas e protocolos. **Pagamentos não aparecem** nessas áreas (ficam nas listas financeiras).
- Os filtros **5 / 10 / 15 linhas** nas listas (agenda, obras ativas, parcelas etc.) atualizam só aquela seção, sem recarregar o painel inteiro.

### Financeiro no painel *(Manager)*

| Bloco | O que mostra |
|---|---|
| **KPIs** | A receber, vencido, a reembolsar, a pagar (prestadores), saídas do mês, margem |
| **Entradas do mês × saídas do mês** | Valores **fixos do mês corrente** — **não mudam** com o filtro de 7/15/30 dias. Saídas = custos de obra **e parcelas de subcontrato** pagos pelo **escritório** |
| **Composição de custos** | Donut por **categoria de custo** (custos avulsos + subcontratos do escritório no mês) |
| **Subcontratos (KPI)** | *A pagar (prestadores)* = saldo de subcontratos **do escritório**; subcontratos *Cliente* ficam só no cadastro da obra |

### Dicas

- Clique em um tile ou linha da agenda para ir direto à lista filtrada do registro correspondente.
- Use **↺ Atualizar** no canto superior para recarregar todos os dados do painel.

---

## 3. Cadastros Básicos

Cadastros devem ser criados **antes** ou **conforme** a necessidade nas obras. Nomes em português abaixo são os **rótulos na tela**.

### 3.1 Clientes

**O que é:** pessoa física ou jurídica contratante das obras.

**Como criar:** Engenharia → Clientes → Novo.

**Campos importantes:**

| Campo | O que preencher |
|---|---|
| Tipo de Pessoa | Pessoa Física ou Jurídica — define documentos obrigatórios |
| Nome / Razão social | Nome completo (PF) ou razão social (PJ) |
| CPF / CNPJ | Apenas dígitos; validação automática |
| Contatos | Telefones e e-mails na tabela inferior |
| Endereços | Logradouro, CEP, cidade; marque o principal |

**Dica:** Um cliente pode ter várias obras vinculadas.

### 3.2 Fornecedores

**O que é:** empresas ou profissionais que prestam serviço ou vendem material.

| Campo | O que preencher |
|---|---|
| Nome do Fornecedor | Razão social ou nome — identificador único |
| CNPJ | Opcional; validado automaticamente |
| Categoria | Material, Serviço, Mão de obra ou Outro |

### 3.3 Tipos de Etapa

**O que é:** catálogo reutilizável de fases da obra (ex.: Fundação, Estrutura, Acabamento).

**Uso:** Ao criar **Etapas da Obra** no projeto, você escolhe um tipo de etapa. Pode incluir **percentual de avanço** padrão.

### 3.4 Tipos de Alvará

**O que é:** classificação de protocolos (Alvará de construção, Habite-se, ART/RRT, etc.).

### 3.5 Órgãos Públicos

**O que é:** prefeituras, órgãos ambientais, corpo de bombeiros — usados em **Prazos** e **Alvarás**.

### 3.6 Categorias de Custo

**O que é:** classificação de lançamentos de **Custo de Obra** (Material, Mão de obra, Equipamento…).

### 3.7 Itens Técnicos

**O que é:** catálogo de componentes de orçamento (ex.: Concreto usinado, Forma metálica).

Cada item pode ter:

- **Parâmetros** (entrada numérica, ex.: volume)
- **Saídas calculadas** (fórmulas, ex.: custo total = quantidade × preço unitário)
- **Unidade padrão**

**Dica:** Itens técnicos são reutilizados em várias obras via **Itens do Projeto**.

---

## 4. Projetos de Obra

**O que é:** registro central (hub) de cada obra — endereço, cliente, status, orçamento e links para tudo relacionado.

### Como criar

1. Engenharia → Projetos → Novo.
2. Selecione o **Cliente** (obrigatório).
3. Preencha tipo de obra, status inicial (geralmente **Orçamento**), endereço e datas previstas.

O sistema gera um código automático (ex.: `PROJ-2026-0042`) e um **título** com cliente e cidade.

### Campos importantes

| Campo | O que preencher |
|---|---|
| Cliente | Contratante da obra (obrigatório) |
| Tipo de Obra | Residencial, Comercial, Industrial, etc. |
| Status | Orçamento → Em andamento → Concluída / Paralisada / Cancelada |
| Data de Início / Previsão de Entrega | Cronograma previsto da obra |
| Cidade / UF | Entram no título automático da obra |
| Área construída | Metragem total em m² |
| Avanço físico global | Calculado das etapas e medições (somente leitura) |
| Revisão vigente | *(Manager)* versão ativa do orçamento |
| Total especificações | *(Manager)* soma automática dos itens do projeto |
| Comissões a receber | *(Manager)* agregado das comissões abertas |

**Engenharia User** não vê a seção de orçamento nem totais financeiros agregados no projeto.

### Etapas da Obra

Crie registros **Etapa da Obra** vinculados ao projeto, escolhendo **Tipo de etapa** e informando avanço e datas.

### Itens do Projeto

São as linhas de orçamento/especificação técnica da obra:

1. Escolha um **Item técnico** do catálogo.
2. Informe **quantidade** e parâmetros.
3. O sistema calcula **custos** e **valor total** conforme fórmulas do item técnico.

**Lógica automática:** sempre que um item é salvo ou removido, o **total de especificações da obra** é recalculado *(visível ao Manager)*.

### Aba Conexões

No projeto, use a aba **Conexões** para abrir contratos, pagamentos, custos, comissões, prazos, tarefas, etc. *(links financeiros só funcionam para Manager)*.

---

## 5. Contratos

**O que é:** acordo de honorários/serviços vinculado a uma obra.

### Criar contrato

1. Abra a obra ou vá em Engenharia → Contratos → Novo.
2. Selecione a **Obra** — o **Cliente** é preenchido automaticamente.
3. Informe valores e status **Vigente**.

### Campos importantes

| Campo | O que preencher |
|---|---|
| Obra | Vincula o contrato; cliente é preenchido automaticamente |
| Valor Base | Valor original antes de aditivos |
| Valor Atual | Calculado com aditivos (somente leitura) |
| Status | Vigente, Encerrado, Cancelado ou Quitado |
| Parcelas | Datas e valores; gera pagamentos ao salvar |

### Parcelas

Na tabela **Parcelas**, defina datas de vencimento e valores. Ao salvar o contrato, o sistema **gera ou atualiza** registros de **Pagamento** correspondentes.

### Aditivos

Registre alterações contratuais na tabela de **Aditivos**. Use o botão **Aplicar aditivo** para:

- Regerar parcelas futuras (preservando as já recebidas), ou
- Apenas registrar histórico

### Acompanhamento

- **Pagamentos** mostram status: Pendente, Vencido, Recebido.
- O valor **atual do contrato** considera aditivos aprovados.

*(Disponível apenas para Engenharia Manager.)*

---

## 6. Financeiro

### 6.1 Pagamentos

Recebíveis de contrato e fluxos derivados. Cada parcela gera um pagamento rastreável.

| Campo | O que preencher |
|---|---|
| Obra / Cliente | Preenchidos automaticamente a partir do contrato |
| Vencimento | Data limite da parcela |
| Valor | Valor da parcela ou recebível |
| Status | Pendente, Vencido, Recebido ou Cancelado |
| Data de Recebimento | Quando o pagamento foi efetivamente recebido |

No painel, o Manager pode marcar pagamento como recebido (atalho na lista).

### 6.2 Custos de Obra

Lançamentos **avulsos** (NF única, compra pontual). Para contratar um prestador com valor acordado e parcelas, use **Subcontratos** (seção 6.3).

| Campo | O que preencher |
|---|---|
| Obra | Onde o custo foi incorrido |
| **Quem arca** | **Escritório** (padrão): você paga e o valor entra no seu fluxo de caixa, painel e relatório de fluxo. **Cliente**: só registro administrativo — o cliente paga direto ao fornecedor e o valor **não** entra no seu caixa |
| Categoria de Custo | Materiais, Mão de obra, Equipamentos, etc. |
| Fornecedor / Etapa | Opcionais — refinam relatórios |
| Valor | Montante em reais |
| Descrição | Detalhe do que foi comprado ou contratado |
| Status | Pago, Pendente ou Cancelado |

**Quando usar Cliente:** você administra a obra mas o dono da obra paga o material, o pedreiro ou a NF diretamente. O lançamento continua visível na obra e nos relatórios por categoria, porém é ignorado em custos do mês, margem realizada e fluxo de caixa do escritório.

### 6.3 Subcontratos

Controle de **pagamentos a prestadores** (pedreiro, eletricista, etc.) com valor total acordado e parcelas.

| Campo | O que preencher |
|---|---|
| Obra | Obra onde o serviço será executado |
| Prestador | Fornecedor cadastrado (ex.: João Pedreiro) |
| **Quem arca** | **Escritório** (padrão): você paga o prestador e entra no fluxo de caixa. **Cliente**: só acompanhamento — o cliente paga direto e **não** entra no seu caixa |
| Valor Total | Valor acordado do serviço (editável — registre o motivo em Observações de aditivo) |
| Pagamentos Efetuados | Cada parcela paga: data, valor, forma e comprovante |
| Saldo a Pagar | Calculado automaticamente (Total − Pago) |
| Status | Aberta / Parcial / Paga / Cancelada |

**Exemplo:** João cobrou R$ 5.000 pelo reboco — registre R$ 2.000 em janeiro e R$ 3.000 em fevereiro na tabela de pagamentos. O saldo zera e o status vira **Paga**.

**Quando usar Cliente:** o dono da obra contrata e paga o pedreiro ou eletricista diretamente; você só acompanha valores e parcelas na obra. O subcontrato continua visível na obra e no fornecedor, mas é ignorado em custos do mês, KPI *A pagar (prestadores)*, margem realizada e fluxo de caixa do escritório.

Na **Obra → Conexões** e no cadastro do **Fornecedor** você vê todos os subcontratos vinculados. No painel *(Manager)*, o KPI **A pagar (prestadores)** resume o saldo pendente de subcontratos **do escritório** (subcontratos *Cliente* ficam fora desse KPI).

*(Engenharia User: somente leitura.)*

### 6.4 Despesas Reembolsáveis

Despesas pagas pelo escritório que o **cliente deve devolver**. Fluxo separado dos custos de obra.

Status típico: **A reembolsar** → reembolsado via pagamento vinculado.

### 6.5 Comissões

| Campo | O que preencher |
|---|---|
| Obra | Obra que gerou a comissão |
| Tipo | Pré-Moldado ou Outro |
| Fornecedor | Empresa que paga a comissão |
| Valor Total | Valor acordado |
| Pagamentos | Cada recebimento com data, valor e comprovante |
| Saldo a receber | Calculado automaticamente |

Registro de comissões a receber (ex.: pré-moldado, parceiro).

1. Crie **Comissão** vinculada à **Obra**.
2. Informe fornecedor, valor total e tipo.
3. Registre **pagamentos recebidos** na tabela inferior (com data, valor e opcionalmente **comprovante** anexo).
4. O sistema calcula **Total pago**, **Saldo a receber** e status (Aberta / Parcial / Paga).
5. O campo **Comissões a receber** na obra agrega todas as comissões abertas *(Manager)*.

---

## 7. Medições

**O que é:** registro de medição de serviços executados em campo, vinculado à obra.

### Como registrar

1. Engenharia → Medições → Novo.
2. Selecione a **Obra** e o **Período de referência**.
3. Na tabela de **Itens**, informe etapas e quantidades medidas.

Útil para conferência de avanço físico e faturamento por medição.

---

## 8. Prazos e Tarefas

### 8.1 Prazos

**O que é:** compromissos com data limite — especialmente relacionados a **órgãos públicos** (protocolos, licenças) ou obrigações contratuais.

| Campo | O que preencher |
|---|---|
| Obra | Obra vinculada ao compromisso |
| Descrição | O que deve ser entregue ou protocolado |
| Data do Prazo | Data limite — gera alertas automáticos |
| Status | Pendente, Concluído ou Vencido |
| Órgão Público | Prefeitura, CREA, etc., quando aplicável |

**Calendário:** ao salvar, um evento aparece no **Calendário** do Frappe. Se o administrador configurou **Google Calendar**, o evento pode sincronizar.

### 8.2 Tarefas

**O que é:** ações internas da equipe (ligar cliente, revisar projeto, visita técnica).

| Campo | O que preencher |
|---|---|
| Assunto | Título curto da tarefa |
| Obra | Vínculo opcional com a obra |
| Prioridade | Baixa, Média ou Alta |
| Prazo | Data limite opcional |
| Status | A fazer, Fazendo, Feito ou Cancelada |
| Responsável | Usuário encarregado da tarefa |

**Timer:** use o registro de **Horas** ou o timer global para cronometrar atividades.

### Diferença conceitual

| | Prazo | Tarefa |
|---|---|---|
| Foco | Externo / compliance / órgão | Interno / equipe |
| Exemplo | Vencimento alvará | Revisar memorial descritivo |
| Calendário automático | Sim (Event) | Não (por padrão) |

---

## 9. Alvarás e Protocolos

**O que é:** controle de protocolos em prefeituras e órgãos (número, data, validade, status).

Vincule **Tipo de alvará**, **Órgão público** e **Obra**.

Status incluem deferido, indeferido, cancelado — eventos de calendário são atualizados automaticamente.

---

## 10. Documentos

### 10.1 Modelos de Documento

Cadastre modelos Word (.docx) com **placeholders** no formato `{{ nome_do_campo }}` (ex.: `{{ customer_name }}`, `{{ project_address_full }}`).

No formulário do template, use o botão **Ver Placeholders** para a lista completa. Grupos disponíveis: Escritório, Cliente, Obra, Contrato, **Subcontratos** e Data.

**Subcontratos na obra** (totais agregados):

| Placeholder | Conteúdo |
|---|---|
| `subcontract_count` | Quantidade de subcontratos |
| `subcontract_total_value` / `_fmt` | Valor total acordado com prestadores |
| `subcontract_total_paid` / `_fmt` | Total já pago |
| `subcontract_outstanding` / `_fmt` | Saldo a pagar |

**Lista detalhada** (loop no Word):

```
{% for s in subcontracts %}
  {{ s.supplier_name }} — {{ s.total_value_fmt }} — saldo {{ s.outstanding_fmt }}
  {% for p in s.payments %}
    {{ p.payment_date_fmt }}: {{ p.amount_fmt }} ({{ p.payment_method }})
  {% endfor %}
{% endfor %}
```

Tipos: contrato, proposta, memorial, etc.

### 10.2 Kits de Documentos

Agrupe vários modelos em um **Kit** para gerar pacotes completos de uma vez.

### 10.3 Gerar documento

Na **Obra**, use o botão de geração de documentos (ou menu Documentos):

1. Escolha o modelo.
2. O sistema preenche placeholders com dados da obra, cliente, especificações e contrato.
3. Baixe o `.docx` gerado ou anexe à obra.

Configure **CNPJ do escritório** em **Configurações da Engenharia** para aparecer nos documentos.

---

## 11. Registro de Atividades

### 11.1 Registro de Horas

Controle tempo gasto por **atividade** e **obra**.

- Crie manualmente informando duração, ou
- Use **Iniciar timer** / **Parar timer** ( também disponível globalmente na barra do sistema).

### 11.2 Registro de Comunicação

Histórico de ligações, e-mails e reuniões com clientes ou órgãos.

Informe **Assunto**, obra, tipo de comunicação e resumo.

---

## 12. Configurações

**Configurações da Engenharia** (registro único):

- Dados do escritório (CNPJ, razão social)
- Parâmetros globais usados em documentos e relatórios

*(Acesso tipicamente restrito ao Manager.)*

---

## 13. Dicas e Atalhos

### Busca rápida

- **Ctrl+K** (ou ícone de lupa): busca global por clientes, obras, contratos, etc.
- Digite parte do **título** visível (ex.: nome do cliente) — não é necessário memorizar códigos internos.

### Filtros em listas

- Use filtros de **Status**, **Cliente** ou **Obra** nas colunas.
- Listas de pagamentos e prazos têm **indicadores coloridos** (verde/laranja/vermelho).

### Workspace e favoritos

- Fixe o workspace **Engenharia** no menu.
- Marque registros com estrela para acesso rápido.

### Importação

Clientes, fornecedores, obras e órgãos públicos suportam **importação CSV** (menu Importar na lista).

### O que o perfil User **não** vê

Contratos, pagamentos, custos, despesas reembolsáveis, comissões, totais de orçamento na obra e toda a zona financeira do painel. Para essas funções, solicite perfil **Engenharia Manager** ao administrador.

---

*Manual versão 1.0 — junho/2026. Alinhado ao app engenharia no Frappe v16.*
