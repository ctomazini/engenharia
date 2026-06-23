frappe.query_reports["cash_flow"] = {
	onload(report) {
		engenharia.reports.applyReportPage(report);
		engenharia.reports.enhanceReportSettings("cash_flow");
	},

	get_datatable_options(options) {
		return engenharia.reports.get_datatable_options(options);
	},

	filters: [
		{
			fieldname: "months",
			label: __("Horizonte (meses)"),
			fieldtype: "Select",
			options: "3\n6\n12",
			default: "6",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		if (column.fieldname === "description" && row.description && !row.date) {
			return `<strong>${frappe.utils.escape_html(row.description)}</strong>`;
		}
		return default_formatter();
	},
};
