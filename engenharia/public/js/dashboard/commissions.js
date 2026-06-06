frappe.provide("engenharia.dashboard");

engenharia.dashboard.commissions = {
	render(container, data) {
		const kpis = data.commission_kpis || data.kpis || {};
		const rows = data.pending_commissions || [];
		const utils = engenharia.dashboard.utils;

		const kpiHtml = `
				<div class="eng-dash-kpi eng-dash-kpi--blue">
					<div class="eng-dash-kpi__label">${__("Total")}</div>
					<div class="eng-dash-kpi__value">${utils.currency_html(kpis.commission_total || 0)}</div>
				</div>
				<div class="eng-dash-kpi eng-dash-kpi--green">
					<div class="eng-dash-kpi__label">${__("Recebido")}</div>
					<div class="eng-dash-kpi__value">${utils.currency_html(kpis.commission_paid || 0)}</div>
				</div>
				<div class="eng-dash-kpi eng-dash-kpi--orange">
					<div class="eng-dash-kpi__label">${__("A Receber")}</div>
					<div class="eng-dash-kpi__value">${utils.currency_html(kpis.commission_outstanding || 0)}</div>
				</div>`;

		const listHtml = rows.length
			? rows
					.map(
						(row) => `
				<button type="button" class="eng-dash-op-row" data-doctype="Commission" data-name="${frappe.utils.escape_html(row.name)}">
					<div>
						<div class="eng-dash-op-row__title">${frappe.utils.escape_html(row.project_title || row.construction_project || "")}</div>
						<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(row.supplier_name || "")}</div>
					</div>
					<div class="eng-dash-op-side">
						<div>${utils.currency_html(row.total_value, { alignEnd: true })}</div>
						<div class="text-muted small">${__("A receber")}: ${utils.currency_html(row.outstanding, { alignEnd: true })}</div>
					</div>
				</button>`
					)
					.join("")
			: utils.render_empty(__("Nenhuma comissão pendente ✓"), "check-circle");

		container.html(`
			<section class="eng-dash-section" id="eng-dash-commissions">
				<h3 class="eng-dash-section-title">${__("Comissões")}</h3>
				<div class="eng-dash-kpi-grid eng-dash-kpi-grid--3">${kpiHtml}</div>
				<h4 class="eng-dash-section-sub mt-3">${__("Comissões Pendentes")}</h4>
				${listHtml}
			</section>
		`);

		container.find(".eng-dash-op-row[data-doctype]").on("click", function () {
			const doctype = $(this).data("doctype");
			const name = $(this).data("name");
			if (doctype && name) {
				frappe.set_route("Form", doctype, name);
			}
		});
	},
};
