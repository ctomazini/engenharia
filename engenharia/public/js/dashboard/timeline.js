frappe.provide("engenharia.dashboard");

engenharia.dashboard.timeline = {
	render(container, data) {
		const items = data.timeline || [];
		const alerts = data.alertas || [];

		const alertHtml = alerts.length
			? alerts
					.map(
						(row) => `
				<button type="button" class="eng-dash-alert eng-dash-alert--${row.level || "yellow"}" data-doctype="${frappe.utils.escape_html(row.doctype)}" data-name="${frappe.utils.escape_html(row.docname)}">
					<strong>${frappe.utils.escape_html(row.title || "")}</strong>
					<span>${frappe.utils.escape_html(row.date || "")}</span>
				</button>`
					)
					.join("")
			: "";

		const timelineHtml = items.length
			? items
					.map(
						(row) => `
				<button type="button" class="eng-dash-timeline-item eng-dash-timeline-item--${row.urgency || "gray"}" data-doctype="${frappe.utils.escape_html(row.doctype)}" data-name="${frappe.utils.escape_html(row.docname)}">
					<div class="eng-dash-timeline-item__title">${frappe.utils.escape_html(row.title || "")}</div>
					<div class="eng-dash-timeline-item__meta">${frappe.utils.escape_html(row.subtitle || "")} · ${frappe.utils.escape_html(row.date || "")}</div>
				</button>`
					)
					.join("")
			: `<div class="eng-dash-empty">${__("Nada agendado no período.")}</div>`;

		const horas = data.horas || {};
		container.html(`
			<div class="eng-dash-section">
				<h3>${__("Alertas")}</h3>
				<div class="eng-dash-alerts">${alertHtml || `<div class="eng-dash-empty">${__("Sem alertas urgentes.")}</div>`}</div>
			</div>
			<div class="eng-dash-section">
				<h3>${__("Agenda")}</h3>
				<div class="eng-dash-timeline">${timelineHtml}</div>
			</div>
			<div class="eng-dash-section eng-dash-hours">
				<span>${__("Horas na semana")}: <strong>${horas.week_hours || 0}h</strong></span>
				<span>${__("Horas no mês")}: <strong>${horas.month_hours || 0}h</strong></span>
			</div>
		`);

		container.find("[data-doctype][data-name]").on("click", function () {
			engenharia.dashboard.utils.route_form($(this).data("doctype"), $(this).data("name"));
		});
	},
};
