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

		const periodButtons = [{ days: 1, label: __("Hoje") }]
			.concat(this.period_options())
			.map(
				(op) =>
					`<button type="button" class="eng-dash-periodo-btn${current === op.days ? " active" : ""}" data-period-days="${op.days}">${frappe.utils.escape_html(op.label)}</button>`
			)
			.join("");

		container.html(`
			<div class="eng-dash-periodo-bar" id="eng-dash-periodo-bar">
				<span class="eng-dash-periodo-label">${frappe.utils.escape_html(this.scope_label(current))}</span>
				<div class="eng-dash-periodo-filters">${periodButtons}</div>
			</div>
		`);
	},

	update_ui($root, period_days) {
		const days = cint(period_days) || 7;
		$root.find(".eng-dash-periodo-label").text(this.scope_label(days));
		$root.find(".eng-dash-periodo-btn").removeClass("active");
		$root.find(`.eng-dash-periodo-btn[data-period-days="${days}"]`).addClass("active");
	},

	bind($root, page, reload_fn) {
		$root.off("click.engDashPeriod", ".eng-dash-periodo-btn");
		$root.on("click.engDashPeriod", ".eng-dash-periodo-btn", function () {
			const days = cint($(this).attr("data-period-days"));
			if (!page || days === page.period_days) return;
			page.period_days = days;
			engenharia.dashboard.filters.update_ui($root, days);
			reload_fn(page);
		});
	},
};
