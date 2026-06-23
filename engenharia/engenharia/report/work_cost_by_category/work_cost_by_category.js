frappe.query_reports["work_cost_by_category"] = {
	onload(report) {
		engenharia.reports.applyReportPage(report);
		engenharia.reports.enhanceReportSettings("work_cost_by_category");
	},

	get_datatable_options(options) {
		return engenharia.reports.get_datatable_options(options);
	},

	filters: [
		{
			fieldname: "cost_category",
			label: __("Categoria"),
			fieldtype: "Link",
			options: "Cost Category",
		},
	],
};
