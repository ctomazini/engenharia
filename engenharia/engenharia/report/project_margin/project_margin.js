frappe.query_reports["project_margin"] = {
	onload(report) {
		engenharia.reports.applyReportPage(report);
		engenharia.reports.enhanceReportSettings("project_margin");
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
	],
};
