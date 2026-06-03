frappe.provide("engenharia.dashboard");

engenharia.dashboard.hero = {
	render(container, data) {
		const resumo = data.resumo || {};
		const kpis = data.kpis || {};
		const fin = data.financeiro || {};
		const period = data.periodo_dias || data.period_days || 7;
		const greeting = engenharia.dashboard.utils.greeting_for_hour();
		const urgency = resumo.urgency === "high" ? __("atenção necessária") : __("visão operacional");

		let context = __("Período de {0} dias", [period]);
		if (kpis.amount_overdue?.count) {
			context += ` · ${kpis.amount_overdue.count} ${__("vencidos")}`;
		}

		container.html(`
			<header class="eng-dash-hero">
				<h2 class="eng-dash-hero__greeting">${frappe.utils.escape_html(greeting)}</h2>
				<p class="eng-dash-hero__date">${frappe.utils.escape_html(resumo.date_label || "")}</p>
				<p class="eng-dash-hero__context">
					${frappe.utils.escape_html(context)} — ${frappe.utils.escape_html(urgency)}
					${fin.taxa_recebimento != null ? ` · ${__("Taxa recebimento")}: ${fin.taxa_recebimento}%` : ""}
				</p>
			</header>
		`);
	},
};
