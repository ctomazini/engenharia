frappe.provide("engenharia.dashboard");

engenharia.dashboard.budget_margin = {
	_budget_tone(used_pct) {
		const pct = parseFloat(used_pct) || 0;
		if (pct > 100) return "danger";
		if (pct > 85) return "warning";
		return "success";
	},

	_margin_tone(margin_pct) {
		const pct = parseFloat(margin_pct) || 0;
		if (pct <= 0) return "danger";
		if (pct < 20) return "warning";
		return "success";
	},

	_kpi_card(label, value, sub, tone, options = {}) {
		const utils = engenharia.dashboard.utils;
		const valueHtml = options.as_int
			? frappe.utils.escape_html(String(value || 0))
			: utils.currency_html(value);
		return `<div class="eng-dash-kpi eng-dash-kpi--${tone || "blue"}">
			<div class="eng-dash-kpi__label">${frappe.utils.escape_html(label)}</div>
			<div class="eng-dash-kpi__value">${valueHtml}</div>
			${sub ? `<div class="eng-dash-kpi__sub">${frappe.utils.escape_html(sub)}</div>` : ""}
		</div>`;
	},

	_bar_row({ project, title, barPct, tone, amountHtml }) {
		const utils = engenharia.dashboard.utils;
		const label = utils.truncate_with_title(title || project, 28);
		const width = Math.max(4, Math.min(100, Math.round(barPct)));
		return `<button type="button" class="eng-dash-chart-row eng-dash-chart-row--link" data-doctype="Construction Project" data-name="${frappe.utils.escape_html(project)}">
			<span class="eng-dash-chart-label">${label}</span>
			<div class="eng-dash-chart-track">
				<div class="eng-dash-chart-fill ${tone}" style="--eng-dash-fill-pct: ${width}%"></div>
			</div>
			<span class="eng-dash-chart-amt">${amountHtml}</span>
		</button>`;
	},

	render_budget_section(budget) {
		const utils = engenharia.dashboard.utils;
		const totals = budget.totals || {};
		const items = budget.items || [];

		const kpiHtml = `
			<div class="eng-dash-kpi-grid eng-dash-kpi-grid--compact">
				${this._kpi_card(__("Total orçado"), totals.total_budget || 0, null, "blue")}
				${this._kpi_card(__("Total realizado"), totals.total_realized || 0, null, "orange")}
				${this._kpi_card(__("Desvio"), totals.total_variance || 0, null, (totals.total_variance || 0) > 0 ? "red" : "green")}
				${this._kpi_card(
					__("Obras acima do orçamento"),
					totals.projects_over_budget || 0,
					__("obras ativas"),
					(totals.projects_over_budget || 0) > 0 ? "red" : "green",
					{ as_int: true }
				)}
			</div>`;

		const barsHtml = items.length
			? items
					.map((row) => {
						const tone = this._budget_tone(row.used_pct);
						const amountHtml = `${utils.currency_html(row.realized)} <span class="muted">/ ${utils.fmt_currency(row.budget, true)} (${row.used_pct}%)</span>`;
						return this._bar_row({
							project: row.project,
							title: row.title,
							barPct: row.used_pct,
							tone,
							amountHtml,
						});
					})
					.join("")
			: utils.render_empty(__("Nenhuma obra com orçamento cadastrado"), "bar-chart-2", "muted");

		return `<section class="eng-dash-section eng-dash-budget-section" id="eng-dash-budget-overview">
			<h3 class="eng-dash-section-title">${__("Orçado vs Realizado")}</h3>
			<p class="eng-dash-section-sub">${__(
				"Top 10 obras com maior desvio — visão acumulada (não filtra por período)"
			)}</p>
			${kpiHtml}
			<div class="eng-dash-finance-bars eng-dash-budget-bars">${barsHtml}</div>
		</section>`;
	},

	render_margin_section(margin) {
		const utils = engenharia.dashboard.utils;
		const totals = margin.totals || {};
		const items = margin.items || [];
		const totalMargin = totals.total_margin || 0;

		const kpiHtml = `
			<div class="eng-dash-kpi-grid eng-dash-kpi-grid--compact">
				${this._kpi_card(__("Total recebido"), totals.total_received || 0, null, "blue")}
				${this._kpi_card(__("Total pago"), totals.total_paid || 0, null, "orange")}
				${this._kpi_card(__("Margem total"), totalMargin, __("recebido − pago"), totalMargin >= 0 ? "green" : "red")}
			</div>`;

		const barsHtml = items.length
			? items
					.map((row) => {
						const tone = this._margin_tone(row.margin_pct);
						const barPct = Math.max(0, Math.min(100, row.margin_pct));
						const amountHtml = `${utils.currency_html(row.margin)} <span class="muted">(${row.margin_pct}%)</span>`;
						return this._bar_row({
							project: row.project,
							title: row.title,
							barPct,
							tone,
							amountHtml,
						});
					})
					.join("")
			: utils.render_empty(__("Nenhuma obra com receita recebida"), "trending-up", "muted");

		return `<section class="eng-dash-section eng-dash-margin-section" id="eng-dash-margin-by-project">
			<h3 class="eng-dash-section-title">${__("Margem por Obra")}</h3>
			<p class="eng-dash-section-sub">${__(
				"Top 10 por margem realizada — visão acumulada (não filtra por período)"
			)}</p>
			${kpiHtml}
			<div class="eng-dash-finance-bars eng-dash-margin-bars">${barsHtml}</div>
		</section>`;
	},

	render(container, data) {
		if (!data.is_manager) return;

		const budget = data.budget_overview;
		const margin = data.margin_by_project;
		if (!budget && !margin) return;

		let html = "";
		if (budget && budget.items && budget.items.length) {
			html += this.render_budget_section(budget);
		}
		if (margin && margin.items && margin.items.length) {
			html += this.render_margin_section(margin);
		}
		if (!html) return;

		container.html(html);
		engenharia.dashboard.utils.bind_routes(container);
	},
};
