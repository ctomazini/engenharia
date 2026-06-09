frappe.provide("engenharia.dashboard");

engenharia.dashboard.financial = {
	_build_bars_html(grafico, emptyMessage) {
		const utils = engenharia.dashboard.utils;
		const items = (grafico || []).filter((g) => utils.flt(g.valor != null ? g.valor : g.amount) > 0);
		if (!items.length) {
			return `<div class="eng-dash-empty-state eng-dash-empty-state--muted"><p>${emptyMessage}</p></div>`;
		}
		const maxVal = Math.max(...items.map((g) => utils.flt(g.valor != null ? g.valor : g.amount)), 1);
		const total = items.reduce((sum, g) => sum + utils.flt(g.valor != null ? g.valor : g.amount), 0);

		return items
			.map((g) => {
				const val = utils.flt(g.valor != null ? g.valor : g.amount);
				const barPct = Math.max(4, Math.round((val / maxVal) * 100));
				const sharePct = total ? Math.round((val / total) * 100) : 0;
				const tone = g.tone || "neutral";
				return `<div class="eng-dash-chart-row">
					<span class="eng-dash-chart-label" title="${frappe.utils.escape_html(g.label)}">${frappe.utils.escape_html(g.label)}</span>
					<div class="eng-dash-chart-track">
						<div class="eng-dash-chart-fill ${tone}" style="--eng-dash-fill-pct: ${barPct}%"></div>
					</div>
					<span class="eng-dash-chart-amt">${utils.currency_html(val)} <span class="muted">(${sharePct}%)</span></span>
				</div>`;
			})
			.join("");
	},

	init_chart($root, fin) {
		const $projectBars = $root.find("#eng-dash-finance-bars-project");
		const $officeBars = $root.find("#eng-dash-finance-bars-office");
		if (!$projectBars.length) return;
		$projectBars.html(
			this._build_bars_html(
				(fin && fin.grafico) || [],
				__("Nenhum custo de obra lançado neste mês")
			)
		);
		if ($officeBars.length) {
			$officeBars.html(
				this._build_bars_html(
					(fin && fin.grafico_office) || [],
					__("Nenhuma despesa do escritório paga neste mês")
				)
			);
		}
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
						<div class="eng-dash-fluxo-vs eng-dashboard-fluxo-vs">${__("vs")}</div>
						<div class="eng-dash-fluxo-card eng-dash-fluxo-card--${saida.tone || "info"}">
							<div class="eng-dash-fluxo-card__label">${frappe.utils.escape_html(saida.label || __("Saídas do mês"))}</div>
							<div class="eng-dash-fluxo-card__value">${utils.currency_html(saida.amount || 0)}</div>
							${saida.detail ? `<div class="eng-dash-fluxo-card__detail">${frappe.utils.escape_html(saida.detail)}</div>` : ""}
						</div>
					</div>
					<div class="eng-dash-finance-composition">
						<p class="eng-dash-section-sub">${__(
							"Custos de obra e subcontratos (por categoria de gasto da obra)"
						)}</p>
						<div id="eng-dash-finance-bars-project" class="eng-dash-finance-bars"></div>
						<p class="eng-dash-section-sub eng-dash-section-sub--spaced">${__(
							"Despesas de funcionamento do escritório pagas no mês"
						)}</p>
						<div id="eng-dash-finance-bars-office" class="eng-dash-finance-bars eng-dash-finance-bars--office"></div>
					</div>
				</div>
			</section>
		`);

		this.init_chart(container, fin, page);
	},
};
