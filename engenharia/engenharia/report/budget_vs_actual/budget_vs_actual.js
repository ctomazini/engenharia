frappe.query_reports["budget_vs_actual"] = {
	onload(report) {
		engenharia.reports.applyReportPage(report);
		engenharia.reports.enhanceReportSettings("budget_vs_actual");
	},

	get_datatable_options(options) {
		return engenharia.reports.get_datatable_options(options);
	},

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
};
