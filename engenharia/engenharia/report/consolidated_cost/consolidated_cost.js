frappe.query_reports["consolidated_cost"] = {
	filters: [
		{
			fieldname: "project",
			label: __("Obra"),
			fieldtype: "Link",
			options: "Construction Project",
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("De"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("Até"),
			fieldtype: "Date",
		},
		{
			fieldname: "cost_type",
			label: __("Tipo de custo"),
			fieldtype: "Select",
			options: "\nwork_cost\nreimbursable_expense\nsubcontract",
		},
		{
			fieldname: "category",
			label: __("Categoria"),
			fieldtype: "Link",
			options: "Cost Category",
		},
		{
			fieldname: "supplier",
			label: __("Fornecedor"),
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "stage",
			label: __("Etapa"),
			fieldtype: "Link",
			options: "Project Stage",
		},
		{
			fieldname: "funded_by",
			label: __("Quem arca"),
			fieldtype: "Select",
			options: "\nEscritório\nCliente",
		},
	],
};
