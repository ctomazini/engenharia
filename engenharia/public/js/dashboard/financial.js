frappe.provide("engenharia.dashboard");

engenharia.dashboard.financial = {
	render(container, data) {
		const chart = (data.financeiro && data.financeiro.chart) || [];
		const payments = (data.financeiro && data.financeiro.pending_payments) || [];

		const toneClass = {
			warning: "eng-dash-chart-bar--warning",
			danger: "eng-dash-chart-bar--danger",
			neutral: "eng-dash-chart-bar--neutral",
			info: "eng-dash-chart-bar--info",
		};

		const maxAmount = Math.max(...chart.map((row) => row.amount || 0), 1);
		const chartHtml = chart
			.map((row) => {
				const pct = Math.round(((row.amount || 0) / maxAmount) * 100);
				return `
				<div class="eng-dash-chart-row">
					<div class="eng-dash-chart-label">${frappe.utils.escape_html(row.label)}</div>
					<div class="eng-dash-chart-track">
						<div class="eng-dash-chart-bar ${toneClass[row.tone] || ""}" style="width:${pct}%"></div>
					</div>
					<div class="eng-dash-chart-value">${engenharia.dashboard.utils.format_currency(row.amount || 0)}</div>
				</div>`;
			})
			.join("");

		const listHtml = payments.length
			? payments
					.map(
						(row) => `
				<button type="button" class="eng-dash-list-item" data-doctype="Payment" data-name="${frappe.utils.escape_html(row.name)}">
					<div class="eng-dash-list-item__title">${frappe.utils.escape_html(row.title || row.name)}</div>
					<div class="eng-dash-list-item__meta">${frappe.utils.escape_html(row.due_date || "")} · ${engenharia.dashboard.utils.format_currency(row.amount)}</div>
				</button>`
					)
					.join("")
			: `<div class="eng-dash-empty">${__("Nenhum pagamento pendente no período.")}</div>`;

		container.html(`
			<div class="eng-dash-section">
				<h3>${__("Financeiro")}</h3>
				<div class="eng-dash-chart">${chartHtml}</div>
				<div class="eng-dash-list">${listHtml}</div>
			</div>
		`);

		container.find(".eng-dash-list-item").on("click", function () {
			engenharia.dashboard.utils.route_form($(this).data("doctype"), $(this).data("name"));
		});
	},
};
