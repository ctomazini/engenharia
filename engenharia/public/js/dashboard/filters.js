frappe.provide("engenharia.dashboard");

engenharia.dashboard.filters = {
	period_options() {
		return [
			{ days: 7, label: __("7 dias") },
			{ days: 15, label: __("15 dias") },
			{ days: 30, label: __("30 dias") },
		];
	},

	scope_label(days) {
		const d = cint(days) || 7;
		if (d === 1) return __("Período: hoje");
		return __("Período: {0} dias", [d]);
	},

	render(container, data, page) {
		const current = data.periodo_dias || data.period_days || page.period_days || 7;
		const limits = data.list_limits || page.eng_dash_list_limits || engenharia.dashboard.utils.default_list_limits();
		const utils = engenharia.dashboard.utils;

		const periodButtons = [{ days: 1, label: __("Hoje") }]
			.concat(this.period_options())
			.map(
				(op) =>
					`<button type="button" class="eng-dash-periodo-btn${current === op.days ? " active" : ""}" data-period-days="${op.days}">${frappe.utils.escape_html(op.label)}</button>`
			)
			.join("");

		const listKeys = [
			{ key: "timeline", label: __("Agenda") },
			{ key: "parcelas", label: __("A receber") },
			{ key: "despesas", label: __("Despesas") },
		];
		const listControls = listKeys
			.map(
				(row) => `
			<div class="eng-dash-filtro-list-block">
				<span class="eng-dash-filtro-list-label">${frappe.utils.escape_html(row.label)}</span>
				${utils.render_list_limit_controls(row.key, limits[row.key] || 5, (data.list_meta || {})[row.key === "parcelas" ? "parcelas" : row.key])}
			</div>`
			)
			.join("");

		container.html(`
			<div class="eng-dash-periodo-bar">
				<div class="eng-dash-filtro-group">
					<div>
						<span class="eng-dash-periodo-label">${frappe.utils.escape_html(this.scope_label(current))}</span>
						<div class="eng-dash-periodo-filters">${periodButtons}</div>
					</div>
					<div class="eng-dash-filtro-lists">${listControls}</div>
				</div>
			</div>
		`);
	},

	bind($root, page, reload_fn) {
		$root.find(".eng-dash-periodo-btn").on("click", function () {
			const days = cint($(this).attr("data-period-days"));
			if (!page || days === page.period_days) return;
			page.period_days = days;
			reload_fn(page);
		});
		engenharia.dashboard.utils.bind_list_limits($root, page, reload_fn);
	},
};
