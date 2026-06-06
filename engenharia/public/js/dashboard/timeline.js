frappe.provide("engenharia.dashboard");

engenharia.dashboard.timeline = {
	render(container, data, page) {
		const items = (data.agenda || data.timeline || []).filter((row) => row.type !== "payment");
		const period = data.periodo_dias || data.period_days || 7;
		const meta = (data.list_meta || {}).timeline;
		const summary = data.agenda_summary || {};
		const limits = data.list_limits || page?.eng_dash_list_limits || {};
		const utils = engenharia.dashboard.utils;

		const eventLabel =
			period === 1
				? summary.total_events === 1
					? __("1 evento hoje")
					: __("{0} eventos hoje", [summary.total_events || 0])
				: summary.total_events === 1
					? __("1 evento nos próximos {0} dias", [period])
					: __("{0} eventos nos próximos {1} dias", [summary.total_events || 0, period]);

		const subParts = [eventLabel];

		const timelineHtml = items.length
			? this._render_grouped_timeline(items, utils)
			: utils.render_empty(
					period === 1 ? __("Nenhum compromisso hoje ✓") : __("Nenhum compromisso no período ✓"),
					"calendar-check"
				);

		const title = period === 1 ? __("Agenda de hoje") : __("Agenda — próximos {0} dias", [period]);

		container.html(`
			<section class="eng-dash-section eng-dash-section--agenda" id="eng-dash-agenda">
				<div class="eng-dash-section-head">
					<div>
						<h3 class="eng-dash-section-title">${title}</h3>
						<p class="eng-dash-section-sub">${frappe.utils.escape_html(subParts.join(" · "))}</p>
					</div>
					${utils.render_list_limit_controls("timeline", limits.timeline || 5, meta)}
				</div>
				<div class="eng-dash-timeline eng-dash-timeline--visual">${timelineHtml}</div>
			</section>
		`);

		utils.bind_routes(container);
	},

	_render_grouped_timeline(items, utils) {
		return utils
			.group_timeline_by_date(items)
			.map(
				(group) => {
					const dayTone = this._day_header_tone(group);
					return `
			<div class="eng-dash-timeline-day tone-${dayTone}">
				<div class="eng-dash-timeline-day__header">
					<span class="eng-dash-timeline-day__marker tone-${dayTone}" aria-hidden="true"></span>
					<span class="eng-dash-timeline-day__label tone-${dayTone}">${frappe.utils.escape_html(group.label)}</span>
				</div>
				<div class="eng-dash-timeline-day__events">
					${group.items.map((row) => this._render_timeline_item(row, utils)).join("")}
				</div>
			</div>`;
				}
			)
			.join("");
	},

	_day_header_tone(group) {
		if (group.label === __("Hoje")) return "today";
		const urgencies = (group.items || []).map((item) => item.urgency);
		if (urgencies.includes("red")) return "red";
		if (urgencies.includes("orange")) return "orange";
		if (urgencies.includes("yellow")) return "yellow";
		return "normal";
	},

	_render_timeline_item(row, utils) {
		const typeLabel = utils.event_type_label(row.type);
		const time = utils.extract_time_from_sort_key(row.sort_key);
		const tone = row.urgency || "gray";
		return `
			<button type="button" class="eng-dash-timeline-item tone-${tone}" data-doctype="${frappe.utils.escape_html(row.doctype)}" data-name="${frappe.utils.escape_html(row.docname)}">
				<span class="eng-dash-timeline-item__marker tone-${tone}" aria-hidden="true"></span>
				<div class="eng-dash-timeline-item__icon">${utils.icon(row.icon || "calendar")}</div>
				<div class="eng-dash-timeline-item__body">
					<div class="eng-dash-timeline-item__title">
						${time ? `<span class="eng-dash-timeline-item__time">${frappe.utils.escape_html(time)}</span>` : ""}
						<span class="eng-dash-timeline-item__type">${frappe.utils.escape_html(typeLabel)}:</span>
						${frappe.utils.escape_html(row.title || "")}
					</div>
					${row.subtitle ? `<div class="eng-dash-timeline-item__meta">${frappe.utils.escape_html(row.subtitle)}</div>` : ""}
				</div>
			</button>`;
	},
};
