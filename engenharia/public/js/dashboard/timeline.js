frappe.provide("engenharia.dashboard");

engenharia.dashboard.timeline = {
	render(container, data, page) {
		const items = data.agenda || data.timeline || [];
		const days = data.agenda_days || [];
		const period = data.periodo_dias || data.period_days || 7;
		const meta = (data.list_meta || {}).timeline;
		const limits = data.list_limits || page?.eng_dash_list_limits || {};
		const utils = engenharia.dashboard.utils;

		const stripHtml = days.length
			? `<div class="eng-dash-agenda-strip">${days
					.map(
						(day) => `
				<div class="eng-dash-agenda-day tone-${day.tone || "gray"}">
					<div class="eng-dash-agenda-day__label">${frappe.utils.escape_html(day.label || "")}</div>
					<div class="eng-dash-agenda-day__count">${day.count || 0}</div>
				</div>`
					)
					.join("")}</div>`
			: "";

		const timelineHtml = items.length
			? items
					.map(
						(row) => `
				<button type="button" class="eng-dash-timeline-item tone-${row.urgency || "gray"}" data-doctype="${frappe.utils.escape_html(row.doctype)}" data-name="${frappe.utils.escape_html(row.docname)}">
					<div class="eng-dash-timeline-item__icon">${utils.icon(row.icon || "calendar")}</div>
					<div class="eng-dash-timeline-item__body">
						<div class="eng-dash-timeline-item__title">${frappe.utils.escape_html(row.title || "")}</div>
						<div class="eng-dash-timeline-item__meta">
							<span class="eng-dash-when tone-${row.urgency || "gray"}">${frappe.utils.escape_html(row.when_label || row.date || "")}</span>
							${row.subtitle ? ` · ${frappe.utils.escape_html(row.subtitle)}` : ""}
						</div>
					</div>
					${row.amount ? `<div class="eng-dash-timeline-item__amount">${utils.currency_html(row.amount, { alignEnd: true })}</div>` : ""}
				</button>`
					)
					.join("")
			: utils.render_empty(
					period === 1 ? __("Nenhum compromisso hoje ✓") : __("Nenhum compromisso no período ✓"),
					"calendar-check"
				);

		const title =
			period === 1 ? __("Agenda de hoje") : __("Agenda — próximos {0} dias", [period]);

		container.html(`
			<section class="eng-dash-section eng-dash-section--agenda" id="eng-dash-agenda">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${title}</h3>
						<p class="eng-dash-section-sub">${utils.list_meta_label(meta)}</p>
					</div>
				</div>
				${stripHtml}
				<div class="eng-dash-timeline">${timelineHtml}</div>
			</section>
		`);

		utils.bind_routes(container);
	},
};
