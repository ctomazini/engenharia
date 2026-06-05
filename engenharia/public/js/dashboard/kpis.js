frappe.provide("engenharia.dashboard");

engenharia.dashboard.kpis = {
	render(container, data) {
		const kpis = data.kpis || {};
		const utils = engenharia.dashboard.utils;
		const receivedMonth = utils.flt(kpis.received_month?.amount);
		const monthCosts = utils.flt(kpis.month_costs?.amount);
		const margin = receivedMonth - monthCosts;

		const cards = [
			{
				label: __("A receber (total)"),
				value: kpis.amount_receivable?.amount || 0,
				sub: `${kpis.amount_receivable?.count || 0} ${__("itens")}`,
				tone: "orange",
				icon: "wallet",
			},
			{
				label: __("Vencido"),
				value: kpis.amount_overdue?.amount || 0,
				sub: `${kpis.amount_overdue?.count || 0} ${__("parcelas")}`,
				tone: "red",
				icon: "circle-alert",
			},
			{
				label: __("A reembolsar (cliente)"),
				value: kpis.amount_reimbursable?.amount || 0,
				sub: `${kpis.amount_reimbursable?.count || 0} ${__("despesas pendentes de devolução")}`,
				tone: "yellow",
				icon: "wallet",
			},
			{
				label: __("Custos do mês"),
				value: kpis.month_costs?.amount || 0,
				sub: `${kpis.month_costs?.count || 0} ${__("lançamentos")}`,
				tone: "blue",
				icon: "receipt",
			},
			{
				label: __("Margem (mês)"),
				value: margin,
				sub: __("recebido no mês − custos do mês"),
				tone: margin >= 0 ? "green" : "red",
				icon: "trending-up",
			},
		];

		const html = cards
			.map(
				(card) => `
			<div class="eng-dash-kpi eng-dash-kpi--${card.tone}">
				<div class="eng-dash-kpi__icon">${utils.icon(card.icon)}</div>
				<div class="eng-dash-kpi__label">${frappe.utils.escape_html(card.label)}</div>
				<div class="eng-dash-kpi__value">${utils.currency_html(card.value)}</div>
				${card.sub ? `<div class="eng-dash-kpi__sub">${frappe.utils.escape_html(card.sub)}</div>` : ""}
			</div>`
			)
			.join("");

		container.html(`<div class="eng-dash-kpi-grid">${html}</div>`);
	},
};
