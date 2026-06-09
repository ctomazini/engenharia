frappe.query_reports["budget_vs_actual"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Obra"),
			fieldtype: "Link",
			options: "Construction Project",
		},
		{
			fieldname: "status",
			label: __("Status da obra"),
			fieldtype: "Select",
			options: "\nOrçamento\nEm andamento\nParalisada\nConcluída\nCancelada",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "budget_variance" && row.budget_total) {
			const cls = flt(row.budget_variance) >= 0 ? "green" : "red";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${value}</span>`;
		}
		if (column.fieldname === "budget_used_percent" && row.budget_total) {
			const pct = flt(row.budget_used_percent);
			let cls = "green";
			if (pct > 100) cls = "red";
			else if (pct > 85) cls = "orange";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${value}</span>`;
		}
		if (column.fieldname === "project_title" && row.project) {
			return `<a href="/app/construction-project/${encodeURIComponent(row.project)}">${frappe.utils.escape_html(
				row.project_title || row.project
			)}</a>`;
		}
		return value;
	},
	get_chart_data(chart) {
		return chart;
	},
};
