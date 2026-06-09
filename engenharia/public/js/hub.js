/* ═══════════════════════════════════════════════════════════
   eng_hub — Render functions for Construction Project hub tabs
   ═══════════════════════════════════════════════════════════ */

function eng_hub_load(frm) {
	frappe.call({
		method: "engenharia.project_hub.get_project_hub_data",
		args: { project: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			eng_hub_render_stages(frm, data.stages || []);
			eng_hub_render_financial(frm, data.financial);
			eng_hub_render_deadlines(frm, data.deadlines || []);
			eng_hub_render_permits(frm, data.permits || []);
			eng_hub_render_tasks(frm, data.tasks || []);
			eng_hub_render_communications(frm, data.communications || []);
			eng_hub_render_measurements(frm, data.measurements || []);
			eng_hub_render_timelogs(frm, data.timelogs || []);

			if (data.financial) {
				eng_hub_render_costs(frm);
				eng_hub_render_payments(frm, data.financial.payments || []);
				eng_hub_render_reimbursables(frm, data.financial.reimbursables || []);
				eng_hub_render_commissions_hub(frm, data.financial.commissions || []);
			}
		},
	});

	frappe.call({
		method: "engenharia.project_hub.get_project_counts",
		args: { project: frm.doc.name },
		callback(r) {
			eng_hub_render_summary_bar(frm, r.message || {});
		},
	});
}

function eng_hub_render_stages(frm, stages) {
	const $w = frm.fields_dict.stages_panel?.$wrapper;
	if (!$w) return;

	if (!stages.length) {
		$w.html(
			_eng_hub_empty("📐", __("Nenhuma etapa cadastrada"), __("+ Nova Etapa"), "new-stage")
		);
		$w.find('[data-hub-action="new-stage"]').on("click", () => {
			frappe.new_doc("Project Stage", { project: frm.doc.name });
		});
		return;
	}

	const totalWeight = stages.reduce((sum, row) => sum + (row.weight || 0), 0);
	const weightOk = Math.abs(totalWeight - 100) < 0.01;
	const weightHtml = `<div class="eng-hub-weight-alert eng-hub-weight-alert--${
		weightOk ? "ok" : "warn"
	}">
		⚖️ ${__("Soma dos pesos")}: <strong>${totalWeight.toFixed(1)}%</strong>
		${weightOk ? "" : " — " + __("ideal: 100%")}
	</div>`;

	const statusMap = { Concluída: "green", "Em andamento": "blue", "Não iniciada": "gray" };
	const bars = stages
		.map((stage) => {
			const pct = Math.min(100, Math.max(0, stage.progress || 0));
			const fillClass =
				pct >= 100 ? "--completed" : pct > 0 ? "--active" : "--not-started";
			const badgeColor = statusMap[stage.status] || "gray";
			return `<div class="eng-hub-progress" data-stage="${frappe.utils.escape_html(
				stage.name
			)}" title="${__("Clique para editar")}">
			<span class="eng-hub-progress__label">${frappe.utils.escape_html(stage.stage_type)}</span>
			<div class="eng-hub-progress__track">
				<div class="eng-hub-progress__fill eng-hub-progress__fill${fillClass}" style="width:${pct}%"></div>
			</div>
			<span class="eng-hub-progress__value">${pct.toFixed(0)}%</span>
			<span class="eng-hub-badge eng-hub-badge--${badgeColor}">${stage.status || ""}</span>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">🏗️</span>
				${__("Etapas da Obra")}
				<span class="eng-hub-panel__count">${stages.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-stage">
				${__("+ Etapa")}
			</button>
		</div>
		${weightHtml}
		${bars}
	</div>`);

	$w.find('[data-hub-action="new-stage"]').on("click", () => {
		frappe.new_doc("Project Stage", { project: frm.doc.name });
	});
	$w.find(".eng-hub-progress").on("click", function () {
		eng_hub_edit_stage(frm, $(this).attr("data-stage"));
	});
}

function eng_hub_edit_stage(frm, stage_name) {
	frappe.call({
		method: "frappe.client.get",
		args: { doctype: "Project Stage", name: stage_name },
		callback(r) {
			const stage = r.message;
			const dialog = new frappe.ui.Dialog({
				title: __("Atualizar: {0}", [stage.stage_type]),
				fields: [
					{
						fieldname: "progress",
						fieldtype: "Percent",
						label: __("Avanço (%)"),
						default: stage.progress,
					},
					{
						fieldname: "status",
						fieldtype: "Select",
						label: __("Status"),
						options: "Não iniciada\nEm andamento\nConcluída",
						default: stage.status,
					},
				],
				primary_action_label: __("Salvar"),
				primary_action(values) {
					frappe.call({
						method: "frappe.client.set_value",
						args: {
							doctype: "Project Stage",
							name: stage_name,
							fieldname: {
								progress: values.progress,
								status: values.status,
							},
						},
						callback() {
							dialog.hide();
							frm.reload_doc();
						},
					});
				},
			});
			dialog.show();
		},
	});
}

function eng_hub_render_financial(frm, financial) {
	const panels = [
		"financial_summary_panel",
		"installments_panel",
		"costs_panel",
		"payments_panel",
		"reimbursables_panel",
		"commissions_hub_panel",
	];
	if (!financial) {
		panels.forEach((panel) => {
			if (frm.fields_dict[panel]) {
				frm.fields_dict[panel].$wrapper.html("");
			}
		});
		return;
	}

	_eng_hub_render_financial_summary(frm, financial.summary);
	_eng_hub_render_installments(frm, financial.installments);
}

function _eng_hub_render_financial_summary(frm, summary) {
	const $w = frm.fields_dict.financial_summary_panel?.$wrapper;
	if (!$w || !summary) return;

	const total = summary.total_contracted || 1;
	const pctReceived = Math.round((summary.total_received / total) * 100);
	const pctCosts = Math.round((summary.total_costs / total) * 100);
	const pctPending = Math.max(0, 100 - pctReceived - pctCosts);

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">💰</span>
				${__("Resumo Financeiro")}
			</h3>
		</div>
		<div class="eng-hub-kpi-row">
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--blue-500)">${format_currency(
					summary.total_contracted
				)}</div>
				<div class="eng-hub-kpi__label">${__("Contratado")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--green-600)">${format_currency(
					summary.total_received
				)}</div>
				<div class="eng-hub-kpi__label">${__("Recebido")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--orange-500)">${format_currency(
					summary.total_pending
				)}</div>
				<div class="eng-hub-kpi__label">${__("A Receber")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:var(--red-500)">${format_currency(
					summary.total_costs + summary.total_subcontracts
				)}</div>
				<div class="eng-hub-kpi__label">${__("Custos + Sub")}</div>
			</div>
			<div class="eng-hub-kpi">
				<div class="eng-hub-kpi__value" style="color:${
					summary.margin >= 0 ? "var(--green-600)" : "var(--red-600)"
				}">${format_currency(summary.margin)}</div>
				<div class="eng-hub-kpi__label">${__("Margem")}</div>
			</div>
		</div>
		<div class="eng-hub-stacked-bar">
			<div class="eng-hub-stacked-bar__segment" style="width:${pctReceived}%;background:var(--green-500)" title="${__(
				"Recebido"
			)}"></div>
			<div class="eng-hub-stacked-bar__segment" style="width:${pctCosts}%;background:var(--red-500)" title="${__(
				"Custos"
			)}"></div>
			<div class="eng-hub-stacked-bar__segment" style="width:${pctPending}%;background:var(--orange-500);opacity:.4" title="${__(
				"Pendente"
			)}"></div>
		</div>
	</div>`);
}

function _eng_hub_render_installments(frm, installments) {
	const $w = frm.fields_dict.installments_panel?.$wrapper;
	if (!$w) return;

	if (!installments || !installments.length) {
		$w.html(`<div class="eng-hub-empty">${__("Nenhuma parcela registrada.")}</div>`);
		return;
	}

	const rows = installments
		.map((row) => {
			const badge = _eng_hub_status_badge(row.status);
			const dt = row.due_date ? frappe.datetime.str_to_user(row.due_date) : "—";
			return `<div class="eng-hub-list-row" data-route="Form/Engineering Contract/${frappe.utils.escape_html(
				row.contract
			)}">
			<div class="eng-hub-list-row__main">
				<span style="color:var(--text-muted);margin-right:4px">#${row.idx}</span>
				${dt}
				<span class="eng-hub-list-row__secondary">${frappe.utils.escape_html(
					row.contract_title || ""
				)}</span>
			</div>
			<div class="eng-hub-list-row__value">${format_currency(row.amount)}</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📋</span>
				${__("Parcelas")}
				<span class="eng-hub-panel__count">${installments.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="list-contracts">
				${__("Ver Contratos")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="list-contracts"]').on("click", () => {
		frappe.set_route("List", "Engineering Contract", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_costs(frm) {
	const $w = frm.fields_dict.costs_panel?.$wrapper;
	if (!$w) return;

	frappe.call({
		method: "engenharia.engenharia.api.costs.get_consolidated_costs",
		args: { project: frm.doc.name },
		callback(r) {
			const payload = r.message || {};
			const items = payload.items || [];
			const summary = payload.summary || {};
			_eng_hub_render_costs_panel(frm, $w, items, summary);
		},
	});
}

function _eng_hub_render_costs_panel(frm, $w, items, summary) {
	if (!items.length) {
		$w.html(_eng_hub_empty("📊", __("Nenhum custo registrado"), __("+ Custo"), "new-cost"));
		$w.find('[data-hub-action="new-cost"]').on("click", () => {
			frappe.new_doc("Work Cost", { project: frm.doc.name });
		});
		return;
	}

	const filterState = { source: "", category: "", stage: "", funded_by: "" };
	const sourceColors = {
		work_cost: "blue",
		reimbursable_expense: "orange",
		subcontract: "green",
	};

	const filterOptions = _eng_hub_costs_filter_options(items);
	const kpiHtml = _eng_hub_costs_kpi_html(summary);
	const filtersHtml = _eng_hub_costs_filters_html(filterOptions);

	$w.html(`<div class="eng-hub-panel eng-hub-costs" data-project="${frappe.utils.escape_html(frm.doc.name)}">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📊</span>
				${__("Custos Consolidados")}
				<span class="eng-hub-panel__count">${items.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-cost">
				${__("+ Custo")}
			</button>
		</div>
		${kpiHtml}
		${filtersHtml}
		<div class="eng-hub-costs-table-wrap">
			<table class="eng-hub-costs-table">
				<thead>
					<tr>
						<th>${__("Data")}</th>
						<th>${__("Tipo")}</th>
						<th>${__("Categoria")}</th>
						<th>${__("Descrição")}</th>
						<th>${__("Fornecedor")}</th>
						<th>${__("Etapa")}</th>
						<th class="eng-hub-costs-table__num">${__("Valor")}</th>
						<th>${__("Status")}</th>
						<th></th>
					</tr>
				</thead>
				<tbody class="eng-hub-costs-table__body"></tbody>
				<tfoot class="eng-hub-costs-table__foot"></tfoot>
			</table>
		</div>
	</div>`);

	const $panel = $w.find(".eng-hub-costs");
	const $tbody = $panel.find(".eng-hub-costs-table__body");
	const $tfoot = $panel.find(".eng-hub-costs-table__foot");

	function renderRows() {
		const filtered = _eng_hub_filter_cost_items(items, filterState);
		const totals = filtered.reduce(
			(acc, row) => {
				acc.amount += flt(row.amount);
				acc.paid += flt(row.paid);
				acc.outstanding += flt(row.outstanding);
				return acc;
			},
			{ amount: 0, paid: 0, outstanding: 0 }
		);

		if (!filtered.length) {
			$tbody.html(`<tr><td colspan="9" class="eng-hub-costs-table__empty">${__(
				"Nenhum item corresponde aos filtros."
			)}</td></tr>`);
		} else {
			$tbody.html(
				filtered
					.map((row) => {
						const dt = row.date ? frappe.datetime.str_to_user(row.date) : "—";
						const badgeColor = sourceColors[row.source] || "gray";
						const desc = frappe.utils.escape_html(row.description || "");
						const descShort =
							desc.length > 40 ? desc.slice(0, 39) + "…" : desc;
						const statusDot = _eng_hub_costs_status_dot(row.status, row.source);
						return `<tr class="eng-hub-costs-row" data-route="Form/${frappe.utils.escape_html(
							row.source_doctype
						)}/${frappe.utils.escape_html(row.name)}">
						<td>${dt}</td>
						<td><span class="eng-hub-badge eng-hub-badge--${badgeColor}">${frappe.utils.escape_html(
							row.source_label || ""
						)}</span></td>
						<td>${frappe.utils.escape_html(row.category || "—")}</td>
						<td class="eng-hub-costs-table__desc" title="${desc}">${descShort || "—"}</td>
						<td>${frappe.utils.escape_html(row.supplier || "—")}</td>
						<td>${frappe.utils.escape_html(row.stage || "—")}</td>
						<td class="eng-hub-costs-table__num">${format_currency(row.amount)}</td>
						<td>${statusDot}</td>
						<td class="eng-hub-costs-table__link">↗</td>
					</tr>`;
					})
					.join("")
			);
		}

		$tfoot.html(`<tr class="eng-hub-costs-table__totals">
			<td colspan="6"><strong>${__("Totais filtrados")}</strong></td>
			<td class="eng-hub-costs-table__num"><strong>${format_currency(totals.amount)}</strong></td>
			<td colspan="2">
				<span class="eng-hub-costs-table__subtotal">${__("Pago")}: ${format_currency(
					totals.paid
				)}</span>
				<span class="eng-hub-costs-table__subtotal">${__("Em aberto")}: ${format_currency(
					totals.outstanding
				)}</span>
			</td>
		</tr>`);

		$panel.find(".eng-hub-costs-row[data-route]").off("click").on("click", function () {
			const parts = $(this).attr("data-route").split("/");
			frappe.set_route(parts[0], parts[1], parts[2]);
		});
	}

	renderRows();

	$panel.find(".eng-hub-costs-filter").on("change", function () {
		const field = $(this).attr("data-filter");
		filterState[field] = $(this).val() || "";
		renderRows();
	});

	$w.find('[data-hub-action="new-cost"]').on("click", () => {
		frappe.new_doc("Work Cost", { project: frm.doc.name });
	});
}

function _eng_hub_costs_kpi_html(summary) {
	const bySource = summary.by_source || {};
	const sourceCards = Object.entries(bySource)
		.map(
			([label, bucket]) => `<div class="eng-hub-kpi eng-hub-kpi--compact">
			<div class="eng-hub-kpi__value" style="font-size:var(--text-md)">${format_currency(
				bucket.amount || 0
			)}</div>
			<div class="eng-hub-kpi__label">${frappe.utils.escape_html(label)}</div>
		</div>`
		)
		.join("");

	return `<div class="eng-hub-kpi-row">
		<div class="eng-hub-kpi">
			<div class="eng-hub-kpi__value" style="color:var(--blue-500)">${format_currency(
				summary.total_amount || 0
			)}</div>
			<div class="eng-hub-kpi__label">${__("Total")}</div>
		</div>
		<div class="eng-hub-kpi">
			<div class="eng-hub-kpi__value" style="color:var(--green-600)">${format_currency(
				summary.total_paid || 0
			)}</div>
			<div class="eng-hub-kpi__label">${__("Pago")}</div>
		</div>
		<div class="eng-hub-kpi">
			<div class="eng-hub-kpi__value" style="color:var(--orange-500)">${format_currency(
				summary.total_outstanding || 0
			)}</div>
			<div class="eng-hub-kpi__label">${__("Em aberto")}</div>
		</div>
		${sourceCards}
	</div>`;
}

function _eng_hub_costs_filters_html(options) {
	const opt = (values, allLabel) =>
		`<option value="">${frappe.utils.escape_html(allLabel)}</option>` +
		values
			.map(
				(v) =>
					`<option value="${frappe.utils.escape_html(v.value)}">${frappe.utils.escape_html(
						v.label
					)}</option>`
			)
			.join("");

	return `<div class="eng-hub-costs-filters">
		<select class="eng-hub-costs-filter" data-filter="source">${opt(
			options.sources,
			__("Todos os tipos")
		)}</select>
		<select class="eng-hub-costs-filter" data-filter="category">${opt(
			options.categories,
			__("Todas categorias")
		)}</select>
		<select class="eng-hub-costs-filter" data-filter="stage">${opt(
			options.stages,
			__("Todas etapas")
		)}</select>
		<select class="eng-hub-costs-filter" data-filter="funded_by">${opt(
			options.funded_by,
			__("Quem arca")
		)}</select>
	</div>`;
}

function _eng_hub_costs_filter_options(items) {
	const uniq = (key) => {
		const seen = new Map();
		items.forEach((row) => {
			const val = row[key];
			if (val && !seen.has(val)) {
				seen.set(val, row[key === "source" ? "source_label" : key] || val);
			}
		});
		return [...seen.entries()].map(([value, label]) => ({ value, label }));
	};

	return {
		sources: uniq("source").map((row) => ({
			value: row.value,
			label: items.find((i) => i.source === row.value)?.source_label || row.label,
		})),
		categories: uniq("category"),
		stages: uniq("stage").filter((row) => row.value),
		funded_by: uniq("funded_by").filter((row) => row.value),
	};
}

function _eng_hub_filter_cost_items(items, filterState) {
	return items.filter((row) => {
		if (filterState.source && row.source !== filterState.source) return false;
		if (filterState.category && row.category !== filterState.category) return false;
		if (filterState.stage && row.stage !== filterState.stage) return false;
		if (filterState.funded_by && row.funded_by !== filterState.funded_by) return false;
		return true;
	});
}

function _eng_hub_costs_status_dot(status, source) {
	const paidStatuses = {
		work_cost: ["Paid", "Partially Paid"],
		reimbursable_expense: ["Reembolsado", "Parcialmente reembolsado"],
		subcontract: ["Paid", "Closed"],
	};
	const cancelledStatuses = ["Cancelado", "Cancelled"];
	let color = "orange";
	if (paidStatuses[source]?.includes(status)) {
		color = "green";
	} else if (cancelledStatuses.includes(status)) {
		color = "gray";
	} else if (source === "subcontract" && status === "Open") {
		color = "blue";
	}
	return `<span class="eng-hub-costs-status-dot eng-hub-costs-status-dot--${color}" title="${frappe.utils.escape_html(
		status || ""
	)}"></span>`;
}

function eng_hub_render_payments(frm, payments) {
	const $w = frm.fields_dict.payments_panel?.$wrapper;
	if (!$w) return;

	if (!payments || !payments.length) {
		$w.html("");
		return;
	}

	const statusMap = {
		Recebido: "green",
		Received: "green",
		Pendente: "orange",
		Pending: "orange",
		Atrasado: "red",
		Overdue: "red",
		Cancelado: "gray",
	};

	const rows = payments
		.map((payment) => {
			const dt = payment.received_date
				? frappe.datetime.str_to_user(payment.received_date)
				: "—";
			const badge = `<span class="eng-hub-badge eng-hub-badge--${
				statusMap[payment.status] || "gray"
			}">${payment.status || ""}</span>`;
			return `<div class="eng-hub-list-row" data-route="Form/Payment/${frappe.utils.escape_html(
				payment.name
			)}">
			<div class="eng-hub-list-row__icon">💵</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(payment.title || payment.name)}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
			<div class="eng-hub-list-row__value">${format_currency(payment.amount)}</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">💵</span>
				${__("Pagamentos")}
				<span class="eng-hub-panel__count">${payments.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-payment">
				${__("+ Pagamento")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-payment"]').on("click", () => {
		frappe.new_doc("Payment", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_reimbursables(frm, reimbursables) {
	const $w = frm.fields_dict.reimbursables_panel?.$wrapper;
	if (!$w) return;

	if (!reimbursables || !reimbursables.length) {
		$w.html("");
		return;
	}

	const statusMap = {
		Pendente: "orange",
		Reembolsado: "green",
		Pago: "green",
		Cancelado: "gray",
		Recusado: "red",
	};

	const rows = reimbursables
		.map((expense) => {
			const badge = `<span class="eng-hub-badge eng-hub-badge--${
				statusMap[expense.status] || "gray"
			}">${expense.status || ""}</span>`;
			return `<div class="eng-hub-list-row" data-route="Form/Reimbursable Expense/${frappe.utils.escape_html(
				expense.name
			)}">
			<div class="eng-hub-list-row__icon">🧾</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(expense.title || expense.name)}
			</div>
			<div class="eng-hub-list-row__value">${format_currency(expense.amount)}</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">🧾</span>
				${__("Despesas Reembolsáveis")}
				<span class="eng-hub-panel__count">${reimbursables.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-reimbursable">
				${__("+ Despesa")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-reimbursable"]').on("click", () => {
		frappe.new_doc("Reimbursable Expense", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_commissions_hub(frm, commissions) {
	const $w = frm.fields_dict.commissions_hub_panel?.$wrapper;
	if (!$w) return;

	if (!commissions || !commissions.length) {
		$w.html("");
		return;
	}

	const statusMap = {
		Pendente: "orange",
		"A receber": "orange",
		Pago: "green",
		Recebido: "green",
		Cancelado: "gray",
	};

	const rows = commissions
		.map((commission) => {
			const badge = `<span class="eng-hub-badge eng-hub-badge--${
				statusMap[commission.status] || "gray"
			}">${commission.status || ""}</span>`;
			return `<div class="eng-hub-list-row" data-route="Form/Commission/${frappe.utils.escape_html(
				commission.name
			)}">
			<div class="eng-hub-list-row__icon">🤝</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(commission.title || commission.name)}
			</div>
			<div class="eng-hub-list-row__value">${format_currency(commission.total_value)}</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">🤝</span>
				${__("Comissões")}
				<span class="eng-hub-panel__count">${commissions.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-commission">
				${__("+ Comissão")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-commission"]').on("click", () => {
		frappe.new_doc("Commission", { construction_project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_summary_bar(frm, counts) {
	const $w = frm.fields_dict.hub_summary_bar?.$wrapper;
	if (!$w) return;

	const items = [
		{
			icon: "🏗️",
			label: __("Etapas"),
			count: counts.stages,
			doctype: "Project Stage",
			fieldname: "project",
		},
		{
			icon: "📋",
			label: __("Contratos"),
			count: counts.contracts,
			doctype: "Engineering Contract",
			fieldname: "project",
		},
		{
			icon: "💵",
			label: __("Pagamentos"),
			count: counts.payments,
			doctype: "Payment",
			fieldname: "project",
		},
		{
			icon: "📊",
			label: __("Custos"),
			count: counts.costs,
			doctype: "Work Cost",
			fieldname: "project",
		},
		{
			icon: "🧾",
			label: __("Reembolsáveis"),
			count: counts.reimbursables,
			doctype: "Reimbursable Expense",
			fieldname: "project",
		},
		{
			icon: "🤝",
			label: __("Comissões"),
			count: counts.commissions,
			doctype: "Commission",
			fieldname: "construction_project",
		},
		{
			icon: "📦",
			label: __("Subcontratos"),
			count: counts.subcontracts,
			doctype: "Subcontract",
			fieldname: "project",
		},
		{
			icon: "📅",
			label: __("Prazos"),
			count: counts.deadlines,
			doctype: "Deadline",
			fieldname: "project",
		},
		{
			icon: "🏛️",
			label: __("Protocolos"),
			count: counts.permits,
			doctype: "Permit",
			fieldname: "project",
		},
		{
			icon: "✅",
			label: __("Tarefas"),
			count: counts.tasks,
			doctype: "Task",
			fieldname: "project",
		},
		{
			icon: "💬",
			label: __("Comunicações"),
			count: counts.communications,
			doctype: "Communication Log",
			fieldname: "project",
		},
		{
			icon: "📏",
			label: __("Medições"),
			count: counts.measurements,
			doctype: "Construction Measurement",
			fieldname: "project",
		},
		{
			icon: "⏱️",
			label: __("Horas"),
			count: counts.timelogs,
			doctype: "Time Log",
			fieldname: "project",
		},
		{
			icon: "🔧",
			label: __("Itens"),
			count: counts.items,
			doctype: "Project Item",
			fieldname: "project",
		},
	];

	const project = frm.doc.name;

	const pills = items
		.map((item) => {
			const hasData = (item.count || 0) > 0;
			const listUrl = `/app/${frappe.router.slug(item.doctype)}?${item.fieldname}=${encodeURIComponent(
				project
			)}`;

			return `<div class="eng-hub-summary-pill${
				hasData ? " eng-hub-summary-pill--active" : ""
			}">
			<a class="eng-hub-summary-pill__link" href="${listUrl}"
				data-doctype="${frappe.utils.escape_html(item.doctype)}"
				data-fieldname="${frappe.utils.escape_html(item.fieldname)}"
				title="${frappe.utils.escape_html(__("Ver lista de {0}", [item.label]))}">
				<span class="eng-hub-summary-pill__icon">${item.icon}</span>
				<span class="eng-hub-summary-pill__label">${item.label}</span>
				<span class="eng-hub-summary-pill__count">${item.count || 0}</span>
			</a>
			<span class="eng-hub-summary-pill__add"
				data-doctype="${frappe.utils.escape_html(item.doctype)}"
				data-fieldname="${frappe.utils.escape_html(item.fieldname)}"
				title="${frappe.utils.escape_html(__("Criar {0}", [item.label]))}">+</span>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-summary-bar">${pills}</div>`);

	$w.find(".eng-hub-summary-pill__link").on("click", function (e) {
		e.preventDefault();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		frappe.set_route("List", doctype, { [fieldname]: project });
	});
	$w.find(".eng-hub-summary-pill__add").on("click", function (e) {
		e.stopPropagation();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		frappe.new_doc(doctype, { [fieldname]: project });
	});
}

function eng_hub_render_deadlines(frm, deadlines) {
	const $w = frm.fields_dict.deadlines_panel?.$wrapper;
	if (!$w) return;

	if (!deadlines.length) {
		$w.html(_eng_hub_empty("📅", __("Nenhum prazo cadastrado"), __("+ Prazo"), "new-deadline"));
		$w.find('[data-hub-action="new-deadline"]').on("click", () => {
			frappe.new_doc("Deadline", { project: frm.doc.name });
		});
		return;
	}

	const items = deadlines
		.map((deadline) => {
			const dt = deadline.due_date ? frappe.datetime.str_to_user(deadline.due_date) : "—";
			let daysHtml = "";
			if (deadline.days_remaining !== null && deadline.urgency !== "done") {
				if (deadline.days_remaining < 0) {
					daysHtml = `<span style="color:var(--red-500);font-weight:600">${Math.abs(
						deadline.days_remaining
					)}d ${__("atrasado")}</span>`;
				} else if (deadline.days_remaining === 0) {
					daysHtml = `<span style="color:var(--orange-500);font-weight:600">${__(
						"Vence hoje!"
					)}</span>`;
				} else {
					daysHtml = `<span>${deadline.days_remaining}d</span>`;
				}
			}
			return `<div class="eng-hub-timeline-item" data-route="Form/Deadline/${frappe.utils.escape_html(
				deadline.name
			)}">
			<div class="eng-hub-timeline-dot eng-hub-timeline-dot--${deadline.urgency}"></div>
			<div style="flex:1">
				<div class="eng-hub-timeline-title">${frappe.utils.escape_html(
					deadline.title || deadline.name
				)}</div>
				<div class="eng-hub-timeline-meta">
					<span>${dt}</span>
					${daysHtml ? "<span>·</span>" + daysHtml : ""}
					${
						deadline.public_agency
							? "<span>·</span><span>" +
							  frappe.utils.escape_html(deadline.public_agency) +
							  "</span>"
							: ""
					}
				</div>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📅</span>
				${__("Prazos")}
				<span class="eng-hub-panel__count">${deadlines.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-deadline">
				${__("+ Prazo")}
			</button>
		</div>
		${items}
	</div>`);

	$w.find('[data-hub-action="new-deadline"]').on("click", () => {
		frappe.new_doc("Deadline", { project: frm.doc.name });
	});
	$w.find(".eng-hub-timeline-item[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_permits(frm, permits) {
	const $w = frm.fields_dict.permits_panel?.$wrapper;
	if (!$w) return;

	if (!permits.length) {
		$w.html(_eng_hub_empty("🏛️", __("Nenhum alvará registrado"), __("+ Protocolo"), "new-permit"));
		$w.find('[data-hub-action="new-permit"]').on("click", () => {
			frappe.new_doc("Permit", { project: frm.doc.name });
		});
		return;
	}

	const statusMap = {
		Deferido: "green",
		Vigente: "green",
		"Em análise": "orange",
		Protocolado: "blue",
		Indeferido: "red",
		Vencido: "red",
	};

	const rows = permits
		.map((permit) => {
			const badge = `<span class="eng-hub-badge eng-hub-badge--${
				statusMap[permit.status] || "gray"
			}">${permit.status || ""}</span>`;
			return `<div class="eng-hub-list-row" data-route="Form/Permit/${frappe.utils.escape_html(
				permit.name
			)}">
			<div class="eng-hub-list-row__icon">🏛️</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(permit.permit_type || "")}
				${
					permit.permit_number
						? " — " + frappe.utils.escape_html(permit.permit_number)
						: ""
				}
			</div>
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">🏛️</span>
				${__("Alvarás e Protocolos")}
				<span class="eng-hub-panel__count">${permits.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-permit">
				${__("+ Protocolo")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-permit"]').on("click", () => {
		frappe.new_doc("Permit", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_tasks(frm, tasks) {
	const $w = frm.fields_dict.tasks_panel?.$wrapper;
	if (!$w) return;

	if (!tasks.length) {
		$w.html(_eng_hub_empty("✅", __("Nenhuma tarefa pendente"), __("+ Tarefa"), "new-task"));
		$w.find('[data-hub-action="new-task"]').on("click", () => {
			frappe.new_doc("Task", { project: frm.doc.name });
		});
		return;
	}

	const prioColor = { Urgente: "red", Alta: "orange", Média: "blue", Baixa: "gray" };
	const rows = tasks
		.map((task) => {
			const pc = prioColor[task.priority] || "gray";
			const dt = task.due_date ? frappe.datetime.str_to_user(task.due_date) : "";
			const dotClass =
				task.priority === "Urgente"
					? "overdue"
					: task.priority === "Alta"
					? "urgent"
					: "normal";
			return `<div class="eng-hub-list-row" data-route="Form/Task/${frappe.utils.escape_html(
				task.name
			)}">
			<div class="eng-hub-timeline-dot eng-hub-timeline-dot--${dotClass}" style="margin:0 8px 0 4px"></div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(task.subject)}
				${dt ? '<span class="eng-hub-list-row__secondary">' + dt + "</span>" : ""}
			</div>
			<span class="eng-hub-badge eng-hub-badge--${pc}">${task.priority || ""}</span>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">✅</span>
				${__("Tarefas Pendentes")}
				<span class="eng-hub-panel__count">${tasks.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-task">
				${__("+ Tarefa")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-task"]').on("click", () => {
		frappe.new_doc("Task", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_communications(frm, communications) {
	const $w = frm.fields_dict.communications_panel?.$wrapper;
	if (!$w) return;

	if (!communications.length) {
		$w.html(
			_eng_hub_empty("💬", __("Nenhuma comunicação registrada"), __("+ Comunicação"), "new-comm")
		);
		$w.find('[data-hub-action="new-comm"]').on("click", () => {
			frappe.new_doc("Communication Log", { project: frm.doc.name });
		});
		return;
	}

	const icons = {
		Telefone: "📞",
		WhatsApp: "💬",
		Email: "📧",
		"Reunião Presencial": "🤝",
		"Reunião Virtual": "💻",
		Outro: "📝",
	};

	const rows = communications
		.map((comm) => {
			const icon = icons[comm.communication_type] || "📝";
			const dt = comm.communication_date
				? frappe.datetime.str_to_user(comm.communication_date)
				: "";
			return `<div class="eng-hub-list-row" data-route="Form/Communication Log/${frappe.utils.escape_html(
				comm.name
			)}">
			<div class="eng-hub-list-row__icon">${icon}</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(comm.subject || comm.title || comm.name)}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">💬</span>
				${__("Comunicações")}
				<span class="eng-hub-panel__count">${communications.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-comm">
				${__("+ Comunicação")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-comm"]').on("click", () => {
		frappe.new_doc("Communication Log", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_measurements(frm, measurements) {
	const $w = frm.fields_dict.measurements_panel?.$wrapper;
	if (!$w) return;

	if (!measurements.length) {
		$w.html(
			_eng_hub_empty("📏", __("Nenhuma medição registrada"), __("+ Medição"), "new-measurement")
		);
		$w.find('[data-hub-action="new-measurement"]').on("click", () => {
			frappe.new_doc("Construction Measurement", { project: frm.doc.name });
		});
		return;
	}

	const rows = measurements
		.map((measurement) => {
			const dt = measurement.measurement_date
				? frappe.datetime.str_to_user(measurement.measurement_date)
				: "";
			return `<div class="eng-hub-list-row" data-route="Form/Construction Measurement/${frappe.utils.escape_html(
				measurement.name
			)}">
			<div class="eng-hub-list-row__icon">📏</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(
					measurement.reference_period || measurement.title || measurement.name
				)}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">📏</span>
				${__("Medições")}
				<span class="eng-hub-panel__count">${measurements.length}</span>
			</h3>
			<button type="button" class="eng-hub-panel__action" data-hub-action="new-measurement">
				${__("+ Medição")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-measurement"]').on("click", () => {
		frappe.new_doc("Construction Measurement", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function eng_hub_render_timelogs(frm, timelogs) {
	const $w = frm.fields_dict.timelogs_panel?.$wrapper;
	if (!$w) return;

	if (!timelogs.length) {
		$w.html(_eng_hub_empty("⏱️", __("Nenhum registro de horas"), __("+ Horas"), "new-timelog"));
		$w.find('[data-hub-action="new-timelog"]').on("click", () => {
			frappe.new_doc("Time Log", { project: frm.doc.name });
		});
		return;
	}

	const total = timelogs.reduce((sum, row) => sum + (row.duration_hours || 0), 0);
	const rows = timelogs
		.slice(0, 8)
		.map((timelog) => {
			const dt = timelog.log_date ? frappe.datetime.str_to_user(timelog.log_date) : "";
			return `<div class="eng-hub-list-row" data-route="Form/Time Log/${frappe.utils.escape_html(
				timelog.name
			)}">
			<div class="eng-hub-list-row__icon">⏱️</div>
			<div class="eng-hub-list-row__main">
				${frappe.utils.escape_html(timelog.activity || "")}
				<span class="eng-hub-list-row__secondary">${dt}</span>
			</div>
			<div class="eng-hub-list-row__value">${(timelog.duration_hours || 0).toFixed(1)}h</div>
		</div>`;
		})
		.join("");

	const seeAll =
		timelogs.length > 8
			? `<div style="text-align:center;padding:10px 0">
			<a style="font-size:var(--text-xs);color:var(--primary);cursor:pointer" data-hub-action="list-timelogs">
				${__("Ver todos")} →
			</a>
		</div>`
			: "";

	$w.html(`<div class="eng-hub-panel">
		<div class="eng-hub-panel__header">
			<h3 class="eng-hub-panel__title">
				<span class="eng-hub-panel__title-icon">⏱️</span>
				${__("Horas Trabalhadas")}
			</h3>
			<div style="display:flex;align-items:center;gap:12px">
				<span style="font-size:var(--text-sm);color:var(--text-muted)">
					${__("Total")}: <strong style="color:var(--text-color)">${total.toFixed(1)}h</strong>
				</span>
				<button type="button" class="eng-hub-panel__action" data-hub-action="new-timelog">
					${__("+ Horas")}
				</button>
			</div>
		</div>
		${rows}
		${seeAll}
	</div>`);

	$w.find('[data-hub-action="new-timelog"]').on("click", () => {
		frappe.new_doc("Time Log", { project: frm.doc.name });
	});
	$w.find('[data-hub-action="list-timelogs"]').on("click", () => {
		frappe.set_route("List", "Time Log", { project: frm.doc.name });
	});
	$w.find(".eng-hub-list-row[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function _eng_hub_empty(icon, msg, btnLabel, actionName) {
	return `<div class="eng-hub-empty">
		<div class="eng-hub-empty__icon">${icon}</div>
		<div>${msg}</div>
		<button type="button" class="eng-hub-empty__action" data-hub-action="${actionName}">${btnLabel}</button>
	</div>`;
}

function _eng_hub_status_badge(status) {
	const map = {
		Pago: "green",
		Recebido: "green",
		Received: "green",
		Vencida: "red",
		Vencido: "red",
		Overdue: "red",
		Atrasado: "red",
		"A vencer": "orange",
		Pending: "orange",
		Pendente: "orange",
		"Em aberto": "blue",
		Open: "blue",
	};
	return `<span class="eng-hub-badge eng-hub-badge--${
		map[status] || "gray"
	}" style="margin-left:8px">${status || ""}</span>`;
}
