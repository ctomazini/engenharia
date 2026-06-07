frappe.query_reports["work_cost_by_project"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Obra"),
			fieldtype: "Link",
			options: "Construction Project",
		},
	],
};
