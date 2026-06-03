frappe.provide("engenharia.dashboard");

engenharia.dashboard.kpis = {
	render(container, data) {
		const kpis = data.kpis || {};
		const fin = data.financeiro || {};
		const utils = engenharia.dashboard.utils;
		const margin = utils.flt(kpis.received_month?.amount) - utils.flt(kpis.month_costs?.amount);

		const cards = [
			{
				label: __("A receber"),
				value: kpis.amount_receivable?.amount || 0,
				sub: `${kpis.amount_receivable?.count || 0} ${__("parcelas")}`,
				tone: "orange",
				icon: "wallet",
				is_money: true,
			},
			{
				label: __("Vencido"),
				value: kpis.amount_overdue?.amount || 0,
				sub: `${kpis.amount_overdue?.count || 0} ${__("parcelas")}`,
				tone: "red",
				icon: "circle-alert",
				is_money: true,
			},
			{
				label: __("A reembolsar"),
				value: kpis.amount_reimbursable?.amount || 0,
				sub: `${kpis.amount_reimbursable?.count || 0} ${__("despesas")}`,
				tone: "yellow",
				icon: "wallet",
				is_money: true,
			},
			{
				label: __("Custos do mês"),
				value: kpis.month_costs?.amount || 0,
				sub: `${kpis.month_costs?.count || 0} ${__("lançamentos")}`,
				tone: "blue",
				icon: "receipt",
				is_money: true,
			},
			{
				label: __("Margem (mês)"),
				value: margin,
				sub: `${fin.taxa_recebimento || kpis.taxa_recebimento || 0}% ${__("receb.")}`,
				tone: margin >= 0 ? "green" : "red",
				icon: "trending-up",
				is_money: true,
			},
		];

		const html = cards
			.map((card) => {
				const valueHtml = card.is_money
					? utils.currency_html(card.value)
					: frappe.utils.escape_html(String(card.value));
				return `
			<div class="eng-dash-kpi eng-dash-kpi--${card.tone}">
				<div class="eng-dash-kpi__icon">${utils.icon(card.icon)}</div>
				<div class="eng-dash-kpi__label">${frappe.utils.escape_html(card.label)}</div>
				<div class="eng-dash-kpi__value">${valueHtml}</div>
				${card.sub ? `<div class="eng-dash-kpi__sub">${frappe.utils.escape_html(card.sub)}</div>` : ""}
			</div>`;
			})
			.join("");

		container.html(`<div class="eng-dash-kpi-grid">${html}</div>`);
	},
};
