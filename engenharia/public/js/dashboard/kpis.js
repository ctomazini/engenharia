frappe.provide("engenharia.dashboard");

engenharia.dashboard.kpis = {
	render(container, data) {
		const kpis = data.kpis || {};
		const cards = [
			{
				label: __("Obras ativas"),
				value: String(kpis.active_projects || 0),
				sub: `${kpis.active_contracts || 0} ${__("contratos")}`,
				tone: "blue",
				is_money: false,
			},
			{
				label: __("A receber"),
				value: kpis.amount_receivable?.amount || 0,
				sub: `${kpis.amount_receivable?.count || 0} ${__("parcelas")}`,
				tone: "orange",
				is_money: true,
			},
			{
				label: __("A reembolsar"),
				value: kpis.amount_reimbursable?.amount || 0,
				sub: `${kpis.amount_reimbursable?.count || 0} ${__("despesas")}`,
				tone: "purple",
				is_money: true,
			},
			{
				label: __("Custos do mês"),
				value: kpis.month_costs?.amount || 0,
				sub: `${kpis.month_costs?.count || 0} ${__("lançamentos")}`,
				tone: "green",
				is_money: true,
			},
		];

		const html = cards
			.map((card) => {
				const valueHtml = card.is_money
					? engenharia.dashboard.utils.currency_html(card.value)
					: frappe.utils.escape_html(card.value);
				return `
			<div class="eng-dash-kpi eng-dash-kpi--${card.tone}">
				<div class="eng-dash-kpi__label">${frappe.utils.escape_html(card.label)}</div>
				<div class="eng-dash-kpi__value">${valueHtml}</div>
				${card.sub ? `<div class="eng-dash-kpi__sub">${frappe.utils.escape_html(card.sub)}</div>` : ""}
			</div>`;
			})
			.join("");

		container.html(`<div class="eng-dash-kpi-grid">${html}</div>`);
	},
};
