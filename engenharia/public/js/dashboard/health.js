frappe.provide("engenharia.dashboard");

engenharia.dashboard.health = {
	render(container, data) {
		const health = data.saude_operacional || {};
		const score = health.score != null ? health.score : 0;
		const tone = health.tone || "green";
		const label = health.label || __("Saudável");
		const breakdown = health.breakdown || [];
		const radius = 40;
		const circumference = 2 * Math.PI * radius;
		const offset = circumference - (circumference * score) / 100;

		const rows = breakdown
			.map(
				(row) => `
			<div class="eng-dash-saude-row tone-${row.tone || "gray"}">
				<span class="eng-dash-saude-row__label">
					<span class="eng-dash-tone-dot tone-${row.tone || "gray"}" aria-hidden="true"></span>
					${frappe.utils.escape_html(row.label || "")}
				</span>
				<strong>${frappe.utils.escape_html(String(row.count))}</strong>
			</div>`
			)
			.join("");

		container.html(`
			<section class="eng-dash-saude" id="eng-dash-saude">
				<h3 class="eng-dash-section-title">${__("Saúde Operacional")}</h3>
				<div class="eng-dash-saude__body">
					<div class="eng-dash-saude-ring">
						<svg viewBox="0 0 96 96" aria-hidden="true">
							<circle class="eng-dash-saude-ring-bg" cx="48" cy="48" r="${radius}"></circle>
							<circle class="eng-dash-saude-ring-fill tone-${tone}" cx="48" cy="48" r="${radius}"
								stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"></circle>
						</svg>
						<div class="eng-dash-saude-score">
							<span class="eng-dash-saude-score__num">${score}%</span>
							<span class="eng-dash-saude-score__label">${frappe.utils.escape_html(label)}</span>
						</div>
					</div>
					<div class="eng-dash-saude-breakdown">${rows}</div>
				</div>
			</section>
		`);
	},
};
