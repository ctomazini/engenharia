frappe.provide("engenharia.dashboard");

engenharia.dashboard.operational = {
	render(container, data) {
		const measurements = data.recent_measurements || [];
		const projects = data.active_projects || [];
		const utils = engenharia.dashboard.utils;

		const measurementsHtml = measurements.length
			? measurements
					.map(
						(row) => `
				<button type="button" class="eng-dash-op-row" data-doctype="Construction Measurement" data-name="${frappe.utils.escape_html(row.name)}">
					<div>
						<div class="eng-dash-op-row__title">${frappe.utils.escape_html(row.project_title || row.project || "")}</div>
						<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(row.reference_period || "")}</div>
					</div>
					<div class="eng-dash-op-side">${frappe.utils.escape_html(frappe.datetime.str_to_user(row.measurement_date) || "")}</div>
				</button>`
					)
					.join("")
			: utils.render_empty(__("Nenhuma medição recente"), "ruler");

		const projectsHtml = projects.length
			? `
			<div class="table-responsive">
				<table class="table table-sm eng-dash-active-projects">
					<thead>
						<tr>
							<th>${__("Obra")}</th>
							<th>${__("Cliente")}</th>
							<th>${__("Progresso")}</th>
							<th>${__("Próximo prazo")}</th>
						</tr>
					</thead>
					<tbody>
						${projects
							.map((row) => {
								const pct = Math.min(100, Math.max(0, utils.flt(row.physical_progress)));
								const barWidth = Math.round(pct);
								const deadlineClass = row.next_deadline_overdue ? "text-danger" : "";
								const alert = row.next_deadline_overdue ? " ⚠️" : "";
								return `
							<tr class="eng-dash-project-row" data-name="${frappe.utils.escape_html(row.name)}">
								<td>${frappe.utils.escape_html(row.title || row.name)}</td>
								<td>${frappe.utils.escape_html(row.customer_short || row.customer_name || "")}</td>
								<td>
									<div class="eng-dash-progress">
										<div class="eng-dash-progress__bar" style="width:${barWidth}%"></div>
									</div>
									<span class="small text-muted">${barWidth}%</span>
								</td>
								<td class="small ${deadlineClass}">${frappe.utils.escape_html(row.next_deadline || "—")}${alert}</td>
							</tr>`;
							})
							.join("")}
					</tbody>
				</table>
			</div>`
			: utils.render_empty(__("Nenhuma obra ativa"), "building");

		container.html(`
			<div class="eng-dash-operational-duo">
				<section class="eng-dash-section">
					<h3 class="eng-dash-section-title">${__("Obras Ativas")} (${projects.length})</h3>
					${projectsHtml}
				</section>
				<section class="eng-dash-section">
					<h3 class="eng-dash-section-title">${__("Últimas Medições")}</h3>
					${measurementsHtml}
				</section>
			</div>
		`);

		container.find(".eng-dash-op-row[data-doctype]").on("click", function () {
			frappe.set_route("Form", $(this).data("doctype"), $(this).data("name"));
		});
		container.find(".eng-dash-project-row").on("click", function () {
			frappe.set_route("Form", "Construction Project", $(this).data("name"));
		});
	},
};
