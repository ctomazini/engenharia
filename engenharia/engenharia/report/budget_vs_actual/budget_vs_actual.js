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
};
