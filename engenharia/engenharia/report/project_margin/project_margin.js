frappe.query_reports["project_margin"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Obra"),
			fieldtype: "Link",
			options: "Construction Project",
		},
	],
};
