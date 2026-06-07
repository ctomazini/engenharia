frappe.provide("engenharia.dashboard");

engenharia.dashboard.hero = {
	_period_received_label(period) {
		if (period === 1) {
			return __("recebido hoje");
		}
		return __("recebido no período");
	},

	_pulse_stats_html(data) {
		const kpis = data.kpis || {};
		const utils = engenharia.dashboard.utils;
		const period = data.periodo_dias || data.period_days || 7;
		const isManager = !!data.is_manager;

		let html = `
			<span class="eng-dash-hero-stat">
				<strong>${frappe.utils.escape_html(String(kpis.urgent_deadlines || 0))}</strong>
				${__("prazo(s) crítico(s)")}
			</span>
			<span class="eng-dash-hero-stat">
				<strong>${frappe.utils.escape_html(String(kpis.overdue_deadlines || 0))}</strong>
				${__("prazo(s) vencido(s)")}
			</span>
			<span class="eng-dash-hero-stat">
				<strong>${frappe.utils.escape_html(String(kpis.open_tasks || 0))}</strong>
				${__("tarefa(s) aberta(s)")}
			</span>`;

		if (isManager) {
			const overdueCount = (kpis.amount_overdue || {}).count || 0;
			const receivedPeriod = kpis.received_period || {};
			html += `
			<span class="eng-dash-hero-stat">
				<strong>${frappe.utils.escape_html(String(overdueCount))}</strong>
				${__("parcela(s) vencida(s)")}
			</span>
			<span class="eng-dash-hero-stat eng-dash-hero-stat--money">
				<strong class="eng-dash-currency">${frappe.utils.escape_html(utils.fmt_currency(receivedPeriod.amount || 0, true))}</strong>
				${frappe.utils.escape_html(this._period_received_label(period))}
			</span>`;
		}

		return html;
	},

	render(container, data) {
		const resumo = data.resumo || {};
		const period = data.periodo_dias || data.period_days || 7;
		const utils = engenharia.dashboard.utils;
		const greeting = utils.greeting_for_hour();
		const isHigh = resumo.urgency === "high";
		const urgencyLabel = isHigh ? __("Atenção hoje") : __("Operação estável");
		const urgencyClass = isHigh ? "eng-dash-urgency-badge--high" : "eng-dash-urgency-badge--normal";
		const context = period === 1 ? __("Visão de hoje") : __("Visão dos próximos {0} dias", [period]);

		container.html(`
			<header class="eng-dash-hero" id="eng-dash-hero">
				<div class="eng-dash-hero__top">
					<div>
						<h2 class="eng-dash-hero__greeting">${frappe.utils.escape_html(greeting)}</h2>
						<p class="eng-dash-hero__date">${frappe.utils.escape_html(resumo.date_label || "")}</p>
					</div>
				</div>
				<p class="eng-dash-hero__context">${frappe.utils.escape_html(context)}</p>
				<div class="eng-dash-hero-pulse">
					<div class="eng-dash-hero-pulse-stats">${this._pulse_stats_html(data)}</div>
					<span class="eng-dash-urgency-badge ${urgencyClass}">${frappe.utils.escape_html(urgencyLabel)}</span>
				</div>
			</header>
		`);
	},

	bind($root) {
		engenharia.dashboard.utils.bind_routes($root);
	},
};
