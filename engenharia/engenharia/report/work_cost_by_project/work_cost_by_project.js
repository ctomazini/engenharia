frappe.query_reports["work_cost_by_project"] = {
	refresh(report) {
		engenharia.reports.applyReportPage(report);
		engenharia.reports.enhanceReportSettings("work_cost_by_project");
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
