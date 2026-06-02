frappe.provide("engenharia.dashboard");

engenharia.dashboard.kpis = {
	render(container, data) {
		const kpis = data.kpis || {};
		const cards = [
			{
				label: __("Obras ativas"),
				value: kpis.active_projects || 0,
				tone: "blue",
			},
			{
				label: __("A receber"),
				value: engenharia.dashboard.utils.format_currency(kpis.amount_receivable?.amount || 0),
				sub: `${kpis.amount_receivable?.count || 0} ${__("parcelas")}`,
				tone: "orange",
			},
			{
				label: __("A reembolsar"),
				value: engenharia.dashboard.utils.format_currency(kpis.amount_reimbursable?.amount || 0),
				sub: `${kpis.amount_reimbursable?.count || 0} ${__("despesas")}`,
				tone: "purple",
			},
			{
				label: __("Custos do mês"),
				value: engenharia.dashboard.utils.format_currency(kpis.month_costs?.amount || 0),
				sub: `${kpis.month_costs?.count || 0} ${__("lançamentos")}`,
				tone: "green",
			},
		];

		const html = cards
			.map(
				(card) => `
			<div class="eng-dash-kpi eng-dash-kpi--${card.tone}">
				<div class="eng-dash-kpi__label">${frappe.utils.escape_html(card.label)}</div>
				<div class="eng-dash-kpi__value">${frappe.utils.escape_html(String(card.value))}</div>
				${card.sub ? `<div class="eng-dash-kpi__sub">${frappe.utils.escape_html(card.sub)}</div>` : ""}
			</div>`
			)
			.join("");

		container.html(`<div class="eng-dash-kpi-grid">${html}</div>`);
	},
};
