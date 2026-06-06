frappe.provide("engenharia.dashboard");

engenharia.dashboard.financial = {
	init_chart($root, fin, page) {
		const grafico = (fin && fin.grafico) || [];
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
		if (!grafico.length || typeof frappe.Chart === "undefined") {
			$el.html(
				`<div class="eng-dash-empty-state eng-dash-empty-state--success"><p>${__(
					"Nenhum custo lançado neste mês"
				)}</p></div>`
			);
			return;
		}
		$el.empty();
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
		if (!values.length) {
			$el.html(
				`<div class="eng-dash-empty-state eng-dash-empty-state--success"><p>${__(
					"Nenhum custo lançado neste mês"
				)}</p></div>`
			);
			return;
		}
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
		const fluxo = fin.fluxo || {};
		const utils = engenharia.dashboard.utils;
		const entrada = fluxo.entrada || {};
		const saida = fluxo.saida || {};
		const monthLabel = fluxo.month_label || "";

		container.html(`
			<section class="eng-dash-section" id="eng-dash-financeiro">
				<h3 class="eng-dash-section-title">${__("Entradas do mês × saídas do mês")}</h3>
				<p class="eng-dash-section-sub">${monthLabel ? `${frappe.utils.escape_html(monthLabel)} · ` : ""}${__(
					"valores fixos do mês corrente — não mudam com o filtro de período"
				)}</p>
				<div class="eng-dash-finance-grid">
					<div class="eng-dash-fluxo-pair">
						<div class="eng-dash-fluxo-card eng-dash-fluxo-card--${entrada.tone || "success"}">
							<div class="eng-dash-fluxo-card__label">${frappe.utils.escape_html(entrada.label || __("Entradas do mês"))}</div>
							<div class="eng-dash-fluxo-card__value">${utils.currency_html(entrada.amount || 0)}</div>
							${entrada.detail ? `<div class="eng-dash-fluxo-card__detail">${frappe.utils.escape_html(entrada.detail)}</div>` : ""}
						</div>
						<div class="eng-dash-fluxo-vs">${__("vs")}</div>
						<div class="eng-dash-fluxo-card eng-dash-fluxo-card--${saida.tone || "info"}">
							<div class="eng-dash-fluxo-card__label">${frappe.utils.escape_html(saida.label || __("Saídas do mês"))}</div>
							<div class="eng-dash-fluxo-card__value">${utils.currency_html(saida.amount || 0)}</div>
							${saida.detail ? `<div class="eng-dash-fluxo-card__detail">${frappe.utils.escape_html(saida.detail)}</div>` : ""}
						</div>
					</div>
					<div>
						<p class="eng-dash-section-sub">${__("Composição de custos do mês por categoria")}</p>
						<div id="eng-dash-finance-donut" class="eng-dash-finance-donut-wrap"></div>
					</div>
				</div>
			</section>
		`);

		this.init_chart(container, fin, page);
	},
};
