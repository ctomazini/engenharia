frappe.listview_settings["Subcontract"] = {
	...(frappe.listview_settings["Subcontract"] || {}),
	hide_name_column: true,
	get_indicator(doc) {
		const map = {
			Open: [__("Aberta"), "orange", "status,=,Open"],
			"Partially Paid": [__("Parcialmente paga"), "blue", "status,=,Partially Paid"],
			Paid: [__("Paga"), "green", "status,=,Paid"],
			Cancelled: [__("Cancelada"), "red", "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "gray", `status,=,${doc.status}`];
	},
};
