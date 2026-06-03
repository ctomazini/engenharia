frappe.provide("engenharia.dashboard");

engenharia.dashboard.financial = {
	init_chart($root, fin, page) {
		const grafico = (fin && fin.grafico) || [];
		if (!grafico.length || typeof frappe.Chart === "undefined") return;
		const $el = $root.find("#eng-dash-finance-donut");
		if (!$el.length) return;
		if (page?.eng_dash_finance_chart) {
			try {
				page.eng_dash_finance_chart.destroy();
			} catch (e) {
				/* ignore */
			}
			page.eng_dash_finance_chart = null;
		}
		const labels = [];
		const values = [];
		const colors = [];
		const utils = engenharia.dashboard.utils;
		grafico.forEach((g) => {
			const val = utils.flt(g.valor != null ? g.valor : g.amount);
			if (val <= 0) return;
			labels.push(g.label);
			values.push(val);
			colors.push(utils.tone_color(g.tone));
		});
		if (!values.length) return;
		page.eng_dash_finance_chart = new frappe.Chart($el[0], {
			type: "donut",
			height: 220,
			data: { labels, datasets: [{ values }] },
			colors,
			tooltipOptions: {
				formatTooltipY: (d) => format_currency(d, "BRL"),
			},
		});
	},

	render(container, data, page) {
		const fin = data.financeiro || {};
		const grafico = fin.grafico || fin.chart || [];
		const utils = engenharia.dashboard.utils;
		let maxVal = 1;
		grafico.forEach((g) => {
			const v = utils.flt(g.valor != null ? g.valor : g.amount);
			if (v > maxVal) maxVal = v;
		});

		const chartRows = grafico
			.map((g) => {
				const val = utils.flt(g.valor != null ? g.valor : g.amount);
				const pct = Math.max(4, Math.round((val / maxVal) * 100));
				return `
				<div class="eng-dash-chart-row">
					<span>${frappe.utils.escape_html(g.label)}</span>
					<div class="eng-dash-chart-track">
						<div class="eng-dash-chart-fill ${g.tone || "neutral"}" style="width:${pct}%"></div>
					</div>
					<span class="eng-dash-chart-amt">${utils.currency_html(val)}</span>
				</div>`;
			})
			.join("");

		const taxa = fin.taxa_recebimento || 0;
		const recebido = fin.recebido_mes?.amount || fin.recebido_mes?.valor || 0;
		const vencido = fin.vencido?.valor || fin.vencido?.amount || 0;
		const previsto = fin.previsto_periodo?.valor || fin.previsto_periodo?.amount || 0;

		container.html(`
			<section class="eng-dash-section" id="eng-dash-financeiro">
				<h3>${__("Financeiro")}</h3>
				<p class="eng-dash-section-sub">${__("Recebíveis e custos consolidados")}</p>
				<div class="eng-dash-finance-grid">
					<div>
						<div class="eng-dash-stat-row">
							<div class="eng-dash-stat">
								<div class="eng-dash-stat__label">${__("Recebido no mês")}</div>
								<div class="eng-dash-stat__value eng-dash-stat__value--success">${utils.currency_html(recebido)}</div>
							</div>
							<div class="eng-dash-stat">
								<div class="eng-dash-stat__label">${__("Vencido")}</div>
								<div class="eng-dash-stat__value eng-dash-stat__value--danger">${utils.currency_html(vencido)}</div>
							</div>
							<div class="eng-dash-stat">
								<div class="eng-dash-stat__label">${__("Previsto período")}</div>
								<div class="eng-dash-stat__value">${utils.currency_html(previsto)}</div>
							</div>
							<div class="eng-dash-stat">
								<div class="eng-dash-stat__label">${__("Inadimplência")}</div>
								<div class="eng-dash-stat__value eng-dash-stat__value--danger">${fin.taxa_inadimplencia || 0}%</div>
							</div>
						</div>
					</div>
					<div>
						<div id="eng-dash-finance-donut" class="eng-dash-finance-donut-wrap"></div>
						<div class="eng-dash-chart-row">
							<span>${__("Taxa de recebimento")}</span>
							<div class="eng-dash-chart-track">
								<div class="eng-dash-chart-fill success" style="width:${Math.max(4, Math.min(100, taxa))}%"></div>
							</div>
							<span class="eng-dash-chart-amt">${taxa}%</span>
						</div>
						${chartRows}
					</div>
				</div>
			</section>
		`);

		this.init_chart(container, fin, page);
	},
};
