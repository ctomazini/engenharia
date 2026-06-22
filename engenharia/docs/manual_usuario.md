# Manual do Usuário — Módulo Engenharia

Sistema de gestão de obras de engenharia civil integrado ao Frappe Desk.

Documentação técnica e de desenvolvimento: [`engenharia/docs/README.md`](README.md) · [`docs/README.md`](../../docs/README.md).

---

## 1. Visão Geral

### O que o sistema faz

O módulo **Engenharia** centraliza a operação de um escritório de projetos e obras:

- Cadastro de **clientes**, **fornecedores** e **obras**
- **Orçamento técnico** (itens do projeto) e **custos realizados** (compras, subcontratos, reembolsáveis) — camadas distintas
- **Despesas do escritório** (aluguel, energia, salários) — custos de funcionamento, separados dos custos de obra
- **Contratos de honorários**, **recebimentos** e **comissões**
- **Prazos**, **tarefas**, **alvarás** e **medições**
- **Documentos** gerados a partir de modelos Word
- **Painel** com visão operacional e financeira

### Perfis de acesso

| Perfil | O que pode fazer |
|---|---|
| **Engenharia Manager** | Acesso completo: operacional + financeiro + configurações sensíveis (orçamento total da obra, comissões, contratos, pagamentos, custos) |
| **Engenharia User** | Operacional: projetos, etapas, itens técnicos da obra, prazos, tarefas, alvarás, medições, registros de horas e comunicações. **Não vê** contratos, pagamentos, comissões, custos de obra, despesas do escritório nem a zona financeira do painel |

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
- O filtro de **período** (Hoje / 7 / 15 / 30 dias) atualiza só as seções afetadas (hero, atenção, agenda, financeiro), mantendo ações rápidas e obras ativas no lugar — sem piscar a página nem reiniciar a animação de entrada.

### Financeiro no painel *(Manager)*

| Bloco | O que mostra |
|---|---|
| **KPIs** | A receber, vencido, a reembolsar, a pagar (prestadores), saídas do mês, margem |
| **Entradas do mês × saídas do mês** | Valores **fixos do mês corrente** — **não mudam** com o filtro de 7/15/30 dias. Saídas = custos de obra **e parcelas de subcontrato** pagos pelo **escritório** |
| **Composição de custos** | Donut por **categoria de custo** (custos avulsos + subcontratos do escritório no mês) |
| **Subcontratos (KPI)** | *A pagar (prestadores)* = saldo de subcontratos **do escritório**; subcontratos *Cliente* ficam só no cadastro da obra |

### Ações rápidas

Atalhos para o **dia a dia**: novo cliente, obra, prazo, tarefa, calendário (visão Event com prazos sincronizados), comunicação e horas. **Manager** também vê pagamento, subcontrato e custo de obra. Contratos, protocolos e despesas reembolsáveis ficam na sidebar — são cadastros menos frequentes.

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

## 4. Obras

**O que é:** registro central (hub) de cada obra — endereço, cliente, status, orçamento e links para tudo relacionado.

### Como criar

1. Engenharia → **Obras** → Novo (ou atalho no Painel).
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

**Modelos de Etapas** (sidebar **Orçamento → Modelos de Etapas**): cadastre templates com tipos de etapa e pesos. Na obra, use **Aplicar modelo** para criar etapas automaticamente (substitui etapas existentes). O botão **Redistribuir pesos** divide o peso igualmente entre as etapas da obra.

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

## 5.1 Orçamento vs custos realizados

O sistema separa **dois mundos** que não se sincronizam automaticamente:

| Camada | Onde registrar | O que representa |
|---|---|---|
| **Orçamento (planejado)** | Obra → aba **Especificações**; sidebar **Orçamento → Itens do Projeto** | Quanto a obra *deveria* custar (fórmulas, itens técnicos) |
| **Custos realizados (fato)** | Obra → aba **Custos Realizados**; sidebar **Despesas** | O que *efetivamente* saiu do caixa ou foi comprometido |

**Três canais de despesa realizada:**

1. **Compras e NF avulsas** — material, taxa pontual, uma nota fiscal
2. **Subcontratos** — prestador com valor acordado e parcelas
3. **Despesas reembolsáveis** — escritório paga e o cliente devolve

O relatório **Custos Realizados** consolida as três fontes. *Compras avulsas por obra/categoria* mostram **somente** o canal 1.

**Despesas do escritório** (sidebar **Despesas → Despesas do Escritório**) são **custos de funcionamento** — não vinculados a uma obra. Entram no **fluxo de caixa** como saídas quando pagas e aparecem no painel (Manager) na lista de despesas pendentes.

---

## 6. Financeiro

Na **Obra → aba Financeiro**, o **Resumo Financeiro** usa os mesmos totais da aba **Custos Realizados** (compras avulsas + subcontratos + reembolsáveis). O banner **Orçamento vs realizado** compara o total do orçamento (`spec_project_total`) com o valor comprometido — são camadas independentes.

| KPI | Significado |
|---|---|
| **Contratado / Recebido / A receber** | Honorários do contrato |
| **Custos realizados** | Total **pago** (consolidado das 3 fontes) |
| **A pagar** | Saldo em aberto de compras avulsas + subcontratos (escritório) |
| **Margem** | Recebido − custos pagos pelo escritório |

*(Disponível apenas para Engenharia Manager.)*

### 6.1 Recebimentos

Recebíveis de contrato de honorários e fluxos derivados. Cada parcela gera um recebimento rastreável.

| Campo | O que preencher |
|---|---|
| Obra / Cliente | Preenchidos automaticamente a partir do contrato |
| Vencimento | Data limite da parcela |
| Valor | Valor da parcela ou recebível |
| Status | Pendente, Vencido, Recebido ou Cancelado |
| Data de Recebimento | Quando o pagamento foi efetivamente recebido |

No painel, o Manager pode marcar pagamento como recebido (atalho na lista).

### 6.2 Compras e NF Avulsas

Lançamentos **avulsos** (NF única, compra pontual) com **pagamentos em parcelas** na tabela inferior. Para contratar um prestador com valor acordado, use **Subcontratos** (seção 6.3).

| Campo | O que preencher |
|---|---|
| Obra | Onde o custo foi incorrido |
| **Quem arca** | **Escritório** (padrão): você paga e o valor entra no seu fluxo de caixa, painel e relatório de fluxo. **Cliente**: só registro administrativo — o cliente paga direto ao fornecedor e o valor **não** entra no seu caixa |
| Categoria de Custo | Materiais, Mão de obra, Equipamentos, etc. |
| Fornecedor / Etapa | Opcionais — refinam relatórios |
| Valor Total | Montante acordado (comprometido) |
| Pagamentos Efetuados | Cada parcela paga: data, valor, forma e comprovante |
| Status | Aberta / Parcialmente paga / Paga / Cancelada |

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

### 6.7 Despesas do Escritório

Custos de **funcionamento do escritório** (aluguel, energia, salários, software, etc.) — **não** são custos de uma obra específica.

| Campo | O que preencher |
|---|---|
| Descrição | Texto do lançamento (ex.: Aluguel sala) |
| Categoria | Aluguel, Energia, Salários, Software/Assinatura, … |
| Valor | Valor da despesa |
| Vencimento | Data de vencimento |
| Data de pagamento | Quando pago — marca status **Pago** |
| Recorrente | Marque para despesas mensais/anuais |
| Comprovante | Anexo por lançamento (não é copiado ao gerar a próxima recorrente) |

**Recorrência:** com **Recorrente** ativo, use **Gerar próxima** para criar o lançamento do período seguinte (vencimento avançado; comprovante zerado).

No **Painel** (Manager), despesas pendentes ou atrasadas aparecem na zona financeira; use **Marcar pago** na lista.

*(Disponível apenas para Engenharia Manager.)*

### 6.8 Relatórios operacionais

Os **sete Script Reports** da sidebar (Engenharia → Relatórios) exibem **cards KPI coloridos** no topo e um **gráfico** (barras ou donut) acima da tabela. Use os filtros de cada relatório para refinar a visão.

| Relatório | Gráfico | KPIs principais | Filtros |
|---|---|---|---|
| **Obras por Status** | Donut por status | Total, em andamento, em orçamento, concluídas | — |
| **Custo por Categoria** | Donut (top 8) | Compras avulsas pagas, nº categorias | Categoria |
| **Compras avulsas por obra** | Barras (top 10) | Total pago, nº obras, média | Obra |
| **Custos Realizados** | — | WC + Subcontratos + Reembolsáveis | Obra, período |
| **Orçado vs Realizado** | Barras (top 10) | Total orçado, realizado, saldo, obras acima do orçamento | Obra, status |
| **Fluxo de Caixa** | Barras mensais entradas × saídas | Total entradas, saídas, saldo líquido | Horizonte 3/6/12 meses |
| **Margem por Obra** | Barras margem realizada (top 10) | Valor contratado, receita, margem, % recebido médio | Obra |

**Regras de caixa vs analítico:**

- **Fluxo de Caixa** e **Margem Realizada** consideram apenas custos e subcontratos com **Quem arca = Escritório**.
- **Custo por Categoria/Obra** incluem todos os lançamentos (Escritório e Cliente) para visão analítica da obra.
- Saídas do fluxo de caixa somam **Custo de Obra** + **Subcontrato** (escritório) + **Despesa Reembolsável** + **Despesa do Escritório** (pagas).

Na tabela, valores críticos aparecem com **destaque colorido** (margem negativa em vermelho, custos em vermelho, status com pills).

### Impressão PDF dos relatórios

Em qualquer Script Report, abra o menu **Imprimir** e escolha um formato **Engenharia - …** (Resumo, Detalhado ou Paisagem). O cabeçalho usa logo e dados do escritório configurados em **Configurações do Escritório** (Engineering Settings).

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

Cadastre modelos Word (.docx) com **placeholders** Jinja no formato `{{ nome_do_campo }}` (ex.: `{{ customer_name }}`, `{{ project_address_full }}`).

No formulário **Modelo de Documento**, use o botão **Ver Placeholders Disponíveis** para a lista completa e atualizada. A lista é gerada automaticamente pelo sistema — sempre reflete os campos suportados.

**Grupos disponíveis:**

| Grupo | Conteúdo |
|---|---|
| **Escritório** | Nome, CNPJ, CREA, logotipo, dados bancários e PIX |
| **Cliente** | Nome, CPF/CNPJ, RG, representante legal, etc. |
| **Endereço do cliente** | Logradouro, número, bairro, cidade, UF, CEP, endereço completo |
| **Contato** | Nome, telefone, celular, e-mail |
| **Obra** | Código, título, status, endereço, área, avanço, ART, totais de orçamento |
| **Orçamento (obra)** | Quantidade e lista de itens da revisão vigente |
| **Item do orçamento** *(loop)* | Campos de cada **Item do Projeto** |
| **Subcontratos (obra)** | Totais agregados e lista `subcontracts` |
| **Subcontrato** *(loop)* | Prestador, valores, status, quem arca, parcelas pagas |
| **Pagamento de subcontrato** *(loop)* | Data, valor, forma, comprovante |
| **Protocolo** *(condicional)* | Dados do protocolo selecionado no diálogo de geração |
| **Contrato** *(condicional)* | Valores, parcelas, retenção, multa — vazio se não houver contrato |
| **Parcela do contrato** *(loop)* | Vencimento, valor, recebido, status, NF — dentro de `contract_installments` |
| **Data** | `today`, `today_iso` |

**Aliases legados:** alguns campos aceitam nomes em português (`{{ nome }}`, `{{ cpf }}`, `{{ endereco }}`, `{{ titulo_obra }}`, etc.) — equivalentes aos nomes em inglês.

**Orçamento — loop no Word:**

```
{% for item in project_items %}
  {{ item.title }} — {{ item.quantity }} {{ item.unit }} — {{ item.total_value_fmt }}
  Parâmetros: {{ item.params_summary }}
  Resultados: {{ item.outputs_summary }}
{% endfor %}
```

**Subcontratos — totais agregados:**

| Placeholder | Conteúdo |
|---|---|
| `subcontract_count` | Quantidade de subcontratos |
| `subcontract_total_value` / `_fmt` | Valor total acordado com prestadores |
| `subcontract_total_paid` / `_fmt` | Total já pago |
| `subcontract_outstanding` / `_fmt` | Saldo a pagar |

**Subcontratos — loop detalhado:**

```
{% for s in subcontracts %}
  {{ s.supplier_name }} ({{ s.funded_by }}) — {{ s.total_value_fmt }} — saldo {{ s.outstanding_fmt }}
  {% for p in s.payments %}
    {{ p.payment_date_fmt }}: {{ p.amount_fmt }} ({{ p.payment_method }})
  {% endfor %}
{% endfor %}
```

**Contrato** *(preenchido quando existe contrato vigente na obra):*

| Placeholder | Conteúdo |
|---|---|
| `contract_value` / `_fmt` | Valor atual do contrato |
| `contract_base_value` / `_fmt` | Valor base (antes de aditivos) |
| `contract_installment_count` | Número de parcelas |
| `contract_installment_value` / `_fmt` | Valor da parcela |
| `contract_technical_retention_pct` | Retenção técnica (%) |
| `contract_late_fee_pct` | Multa por mora (%) |
| `contract_total_received` / `_fmt` | Total já recebido nas parcelas |
| `contract_total_outstanding` / `_fmt` | Saldo a receber nas parcelas |

**Parcelas do contrato — loop:**

```
{% for i in contract_installments %}
  {{ i.due_date_fmt }} — {{ i.amount_fmt }} — {{ i.status }}
  Recebido: {{ i.received_amount_fmt }} — NF: {{ i.nf_number }}
{% endfor %}
```

**Protocolo** *(preenchido quando um protocolo é selecionado em Gerar Documentos):*

| Placeholder | Conteúdo |
|---|---|
| `permit_number` | Número do protocolo |
| `permit_type_label` | Tipo legível (cadastro Tipos de Alvará) |
| `permit_agency` | Órgão público |
| `permit_protocol_date` | Data do protocolo |
| `permit_expiry_date` | Validade |
| `permit_art_rrt_number` | Nº ART/RRT |
| `permit_responsible_professional` | Responsável técnico |

Tipos de modelo: **Contrato**, **Proposta**, **Relatório** ou **Outro**.

### 10.2 Kits de Documentos

Agrupe vários modelos em um **Kit** para gerar pacotes completos de uma vez.

### 10.3 Gerar documento Word

Na **Obra**, use o botão **Gerar Documentos**:

1. Escolha um ou mais modelos (ou um **Kit**).
2. Opcionalmente selecione um **Protocolo** vinculado à obra (placeholders do grupo Protocolo).
3. O sistema preenche placeholders com dados do escritório, cliente, obra, orçamento (itens da revisão vigente), contrato (incluindo parcelas) e subcontratos.
4. O `.docx` é **baixado no navegador** — não é arquivado automaticamente na obra.

Para guardar na obra, use **+ Enviar documento** na aba Documentos (upload manual).

Configure em **Configurações do Escritório**: CNPJ, razão social, CREA, **logotipo** (`{{ company_logo }}`), dados bancários e PIX.

### 10.4 Arquivos da obra (Documento da Obra)

A aba **Documentos** da obra é o repositório de PDFs, plantas, memoriais e anexos enviados manualmente:

| Campo | Uso |
|---|---|
| **Categoria** | Cadastro rígido (Memorial, ART, Protocolo, Planta…) |
| **Versão** | Ex.: Rev 01, v2 |
| **Descritor** | Complemento opcional do título |
| **Status** | Rascunho, Enviado, Aprovado… |
| **Protocolo relacionado** | Vínculo opcional com alvará/protocolo |

O **título** exibido segue `{Obra} — {Categoria} — {Versão}`; o **nome do arquivo** anexo é renomeado automaticamente para `{ID_obra}_{categoria}_{versão}_{descritor}.ext`.

Cadastros auxiliares: **Categorias de Documento** e **Tipos de Edificação** (sidebar Cadastros).

Detalhes técnicos: [`project_documents.md`](project_documents.md).

### 10.5 Navegação hub da obra

A **Obra** funciona como hub central. Ao abrir contratos, pagamentos, documentos ou outros satélites:

- O **breadcrumb** mantém o caminho até a obra (IDs curtos, ex.: `PROJ-2026-0042`).
- O botão **Voltar à obra** retorna ao hub na **mesma aba** de onde você saiu.
- Satélites acessíveis pelo hub: contratos, pagamentos, custos, subcontratos, prazos, protocolos, tarefas, medições, horas, comunicações, comissões, documentos da obra, etapas e itens.

Detalhes técnicos: [`hub_navigation.md`](hub_navigation.md).

---

## 11. Registro de Atividades

### 11.1 Registro de Horas

Controle tempo gasto por **atividade** e **obra**.

- Crie manualmente informando duração, ou
- Use **Iniciar timer** / **Parar timer** ( também disponível globalmente na barra do sistema).

### 11.2 Registro de Comunicação

Histórico de ligações, e-mails e reuniões com clientes ou órgãos.

Informe **Assunto**, obra, tipo de comunicação e resumo. Opcionalmente marque **Gerar Tarefa** e **Data de retorno** (`follow_up_date`) — a data de retorno vira vencimento da tarefa criada automaticamente.

---

## 12. Configurações

**Configurações da Engenharia** (registro único):

- Dados do escritório (CNPJ, razão social, CREA)
- Logotipo (URL exibida em documentos e impressos)
- Dados bancários e chave PIX (placeholders de documentos)
- Parâmetros globais usados em relatórios

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

*Manual versão 1.1 — junho/2026. Alinhado ao app engenharia no Frappe v16.*
