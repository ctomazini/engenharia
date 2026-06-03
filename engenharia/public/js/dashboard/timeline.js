frappe.provide("engenharia.dashboard");

engenharia.dashboard.timeline = {
	render(container, data) {
		const items = data.timeline || [];
		const alerts = data.alertas || [];
		const horas = data.horas_periodo != null ? { period_hours: data.horas_periodo } : data.horas || {};
		const comunicacoes = data.comunicacoes_pendentes || data.ultimas_comunicacoes || [];

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

		const commHtml = comunicacoes.length
			? comunicacoes
					.map(
						(row) => `
				<button type="button" class="eng-dash-timeline-item" data-doctype="Communication Log" data-name="${frappe.utils.escape_html(row.name)}">
					<div class="eng-dash-timeline-item__title">${frappe.utils.escape_html(row.subject || row.name)}</div>
					<div class="eng-dash-timeline-item__meta">${frappe.utils.escape_html(row.communication_date || "")}</div>
				</button>`
					)
					.join("")
			: `<div class="eng-dash-empty">${__("Sem comunicações recentes.")}</div>`;

		container.html(`
			<div class="eng-dash-section">
				<h3>${__("Alertas")}</h3>
				<div class="eng-dash-alerts">${alertHtml || `<div class="eng-dash-empty">${__("Sem alertas urgentes.")}</div>`}</div>
			</div>
			<div class="eng-dash-section">
				<h3>${__("Agenda")}</h3>
				<div class="eng-dash-timeline">${timelineHtml}</div>
			</div>
			<div class="eng-dash-section">
				<h3>${__("Comunicações")}</h3>
				<div class="eng-dash-timeline">${commHtml}</div>
			</div>
			<div class="eng-dash-section eng-dash-hours">
				<span>${__("Horas na semana")}: <strong>${horas.week_hours || 0}h</strong></span>
				<span>${__("Horas no período")}: <strong>${data.horas_periodo != null ? data.horas_periodo : 0}h</strong></span>
				<span>${__("Horas no mês")}: <strong>${horas.month_hours || 0}h</strong></span>
			</div>
		`);

		engenharia.dashboard.utils.bind_routes(container);
	},
};
