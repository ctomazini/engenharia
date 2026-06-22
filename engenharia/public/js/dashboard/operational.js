frappe.provide("engenharia.dashboard");

engenharia.dashboard.operational = {
	_is_onboarding(data) {
		const kpis = (data && data.kpis) || {};
		return (kpis.active_projects || 0) === 0;
	},

	_render_journey(utils) {
		const steps = [
			{
				label: __("Cadastre um cliente"),
				hint: __("Quem contrata a obra"),
				doctype: "Customer",
			},
			{
				label: __("Abra a primeira obra"),
				hint: __("Hub central do projeto"),
				doctype: "Construction Project",
			},
			{
				label: __("Monte etapas, orçamento e contrato"),
				hint: __("Na obra: checklist e pílulas do resumo"),
				route: ["List", "Construction Project"],
			},
		];

		const rows = steps
			.map((step, idx) => {
				const attrs = step.doctype
					? `data-new-dt="${frappe.utils.escape_html(step.doctype)}"`
					: `data-route="${frappe.utils.escape_html((step.route || []).join("/"))}"`;
				return `<li class="eng-dash-journey__step">
				<span class="eng-dash-journey__num">${idx + 1}</span>
				<button type="button" class="eng-dash-journey__action" ${attrs}>
					<span class="eng-dash-journey__label">${frappe.utils.escape_html(step.label)}</span>
					<span class="eng-dash-journey__hint">${frappe.utils.escape_html(step.hint)}</span>
				</button>
			</li>`;
			})
			.join("");

		return `<div class="eng-dash-empty-state eng-dash-empty-state--success eng-dash-journey">
			<div class="eng-dash-empty-state__icon">${utils.icon("map", "md")}</div>
			<p><strong>${__("Jornada inicial")}</strong></p>
			<p>${__("Siga os passos abaixo para colocar o escritório em operação.")}</p>
			<ol class="eng-dash-journey__steps">${rows}</ol>
		</div>`;
	},

	render(container, data, page) {
		const projects = data.active_projects || [];
		const meta = (data.list_meta || {}).operational;
		const limits = data.list_limits || page?.eng_dash_list_limits || {};
		const utils = engenharia.dashboard.utils;
		const onboarding = this._is_onboarding(data);

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
					<div class="eng-dash-op-side eng-dashboard-op-side">
						<div class="eng-dash-op-progress">
							<div class="eng-dash-progress eng-dashboard-progress">
								<div class="eng-dash-progress__bar" style="width:${barWidth}%"></div>
							</div>
							<span class="eng-dashboard-aux">${barWidth}%</span>
						</div>
						${this._status_pill(row.status)}
						<div class="eng-dashboard-op-deadline small ${row.next_deadline_overdue ? "text-danger" : "text-muted"}">${utils.truncate_with_title(row.next_deadline || __("Sem prazo"), 30)}</div>
					</div>
				</button>`;
					})
					.join("")
			: onboarding
				? this._render_journey(utils)
				: utils.render_empty(__("Nenhuma obra ativa"), "building");

		const title = onboarding ? __("Comece por aqui") : __("Obras Ativas");
		const subtitle = onboarding
			? __("Quando houver obras em andamento, elas aparecem nesta lista.")
			: utils.list_meta_label(meta);

		container.html(`
			<section class="eng-dash-section eng-dash-section--operational">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${title}</h3>
						<p class="eng-dash-section-sub">${subtitle}</p>
					</div>
					${onboarding ? "" : utils.render_list_limit_controls("operational", limits.operational || 5, meta)}
				</div>
				${projectsHtml}
				${onboarding ? "" : utils.render_view_all_footer("Construction Project", meta, [["status", "=", "Em andamento"]])}
			</section>
		`);

		utils.bind_routes(container);
		if (!onboarding) {
			utils.bind_view_all(container);
		}

		container.find(".eng-dash-journey__action").on("click", function () {
			const route = $(this).attr("data-route");
			if (route) {
				frappe.set_route(...route.split("/"));
				return;
			}
			const dt = $(this).attr("data-new-dt");
			if (dt) frappe.new_doc(dt);
		});
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
