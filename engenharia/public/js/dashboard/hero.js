frappe.provide("engenharia.dashboard");

engenharia.dashboard.hero = {
	render(container, data) {
		const resumo = data.resumo || {};
		const kpis = data.kpis || {};
		const fin = data.financeiro || {};
		const period = data.periodo_dias || data.period_days || 7;
		const greeting = engenharia.dashboard.utils.greeting_for_hour();
		const isHigh = resumo.urgency === "high";
		const urgencyLabel = isHigh ? __("Atenção hoje") : __("Operação estável");
		const urgencyClass = isHigh ? "eng-dash-urgency-badge--high" : "eng-dash-urgency-badge--normal";

		let context = period === 1 ? __("Visão de hoje") : __("Visão dos próximos {0} dias", [period]);
		if (kpis.amount_overdue?.count) {
			context += ` · ${kpis.amount_overdue.count} ${__("vencidos")}`;
		}

		container.html(`
			<header class="eng-dash-hero">
				<div class="eng-dash-hero__top">
					<div>
						<h2 class="eng-dash-hero__greeting">${frappe.utils.escape_html(greeting)}</h2>
						<p class="eng-dash-hero__date">${frappe.utils.escape_html(resumo.date_label || "")}</p>
					</div>
					<span class="eng-dash-urgency-badge ${urgencyClass}">${frappe.utils.escape_html(urgencyLabel)}</span>
				</div>
				<p class="eng-dash-hero__context">
					${frappe.utils.escape_html(context)}
					${fin.taxa_recebimento != null ? ` · ${__("Taxa recebimento")}: ${fin.taxa_recebimento}%` : ""}
				</p>
			</header>
		`);
	},
};
