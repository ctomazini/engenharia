frappe.provide("engenharia.dashboard");

engenharia.dashboard.subcontracts = {
	render(container, data) {
		const kpis = data.subcontract_kpis || {};
		const rows = data.pending_subcontracts || [];
		const utils = engenharia.dashboard.utils;

		const kpiHtml = `
			<div class="eng-dash-kpi-grid eng-dash-kpi-grid--compact">
				<div class="eng-dash-kpi eng-dash-kpi--blue">
					<div class="eng-dash-kpi__label">${__("Subcontratos (total)")}</div>
					<div class="eng-dash-kpi__value">${utils.currency_html(kpis.subcontract_total || 0)}</div>
				</div>
				<div class="eng-dash-kpi eng-dash-kpi--green">
					<div class="eng-dash-kpi__label">${__("Já pago a prestadores")}</div>
					<div class="eng-dash-kpi__value">${utils.currency_html(kpis.subcontract_paid || 0)}</div>
				</div>
				<div class="eng-dash-kpi eng-dash-kpi--orange">
					<div class="eng-dash-kpi__label">${__("A pagar a prestadores")}</div>
					<div class="eng-dash-kpi__value">${utils.currency_html(kpis.subcontract_outstanding || 0)}</div>
				</div>
			</div>`;

		const listHtml = rows.length
			? `
			<table class="table table-bordered table-sm eng-dash-table">
				<thead>
					<tr>
						<th>${__("Subcontrato")}</th>
						<th>${__("Obra")}</th>
						<th>${__("Prestador")}</th>
						<th class="text-right">${__("Saldo")}</th>
					</tr>
				</thead>
				<tbody>
					${rows
						.map(
							(row) => `
						<tr>
							<td><a href="/app/subcontract/${encodeURIComponent(row.name)}">${frappe.utils.escape_html(row.title || row.name)}</a></td>
							<td>${frappe.utils.escape_html(row.project_title || row.project || "")}</td>
							<td>${frappe.utils.escape_html(row.supplier_name || row.supplier || "")}</td>
							<td class="text-right">${utils.currency_html(row.outstanding)}</td>
						</tr>`
						)
						.join("")}
				</tbody>
			</table>`
			: `<p class="text-muted eng-dash-empty">${__("Nenhum subcontrato com saldo a pagar.")}</p>`;

		container.html(`
			<details class="eng-dash-commissions-accordion eng-dash-subcontracts-accordion" id="eng-dash-subcontracts">
				<summary class="eng-dash-commissions-accordion__summary">
					<span class="eng-dash-commissions-accordion__title">${__("Subcontratos")}</span>
					<span class="eng-dash-commissions-accordion__hint text-muted">${__("Clique para expandir")}</span>
				</summary>
				<div class="eng-dash-commissions-accordion__body">
					${kpiHtml}
					${listHtml}
				</div>
			</details>
		`);
	},
};
