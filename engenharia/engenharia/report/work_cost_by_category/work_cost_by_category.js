frappe.query_reports["work_cost_by_category"] = {
	filters: [
		{
			fieldname: "cost_category",
			label: __("Categoria"),
			fieldtype: "Link",
			options: "Cost Category",
		},
	],
};
