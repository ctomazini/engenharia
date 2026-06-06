frappe.provide("engenharia.dashboard");

engenharia.dashboard.operational = {
	render(container, data, page) {
		const projects = data.active_projects || [];
		const meta = (data.list_meta || {}).operational;
		const limits = data.list_limits || page?.eng_dash_list_limits || {};
		const utils = engenharia.dashboard.utils;

		const projectsHtml = projects.length
			? projects
					.map((row) => {
						let rowClass = "eng-dash-op-row";
						if (row.next_deadline_overdue) rowClass += " eng-dash-op-row--overdue";
						else if (row.status === "Paralisada") rowClass += " eng-dash-op-row--pending";
						const pct = Math.min(100, Math.max(0, utils.flt(row.physical_progress)));
						const barWidth = Math.round(pct);
						return `
				<button type="button" class="${rowClass}" data-doctype="Construction Project" data-name="${frappe.utils.escape_html(row.name)}">
					<div>
						<div class="eng-dash-op-row__title">${frappe.utils.escape_html(row.title || row.name)}</div>
						<div class="eng-dash-op-row__sub">${frappe.utils.escape_html(row.customer_name || "")}</div>
					</div>
					<div class="eng-dash-op-side">
						<div class="eng-dash-op-progress">
							<div class="eng-dash-progress">
								<div class="eng-dash-progress__bar" style="width:${barWidth}%"></div>
							</div>
							<span class="small text-muted">${barWidth}%</span>
						</div>
						${this._status_pill(row.status)}
						<div class="small ${row.next_deadline_overdue ? "text-danger" : "text-muted"}">${frappe.utils.escape_html(row.next_deadline || __("Sem prazo"))}</div>
					</div>
				</button>`;
					})
					.join("")
			: utils.render_empty(__("Nenhuma obra ativa"), "building");

		container.html(`
			<section class="eng-dash-section eng-dash-section--operational">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${__("Obras Ativas")}</h3>
						<p class="eng-dash-section-sub">${utils.list_meta_label(meta)}</p>
					</div>
					${utils.render_list_limit_controls("operational", limits.operational || 5, meta)}
				</div>
				${projectsHtml}
				${utils.render_view_all_footer("Construction Project", meta)}
			</section>
		`);

		utils.bind_routes(container);
		utils.bind_view_all(container);
	},

	_status_pill(status) {
		const map = {
			"Em andamento": "blue",
			Paralisada: "orange",
			Orçamento: "gray",
		};
		const cls = map[status] || "gray";
		const label = frappe.utils.escape_html(status || "");
		return `<span class="indicator-pill ${cls} filterable no-indicator-dot ellipsis">${label}</span>`;
	},
};
