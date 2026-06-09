frappe.listview_settings["Work Cost"] = {
	...(frappe.listview_settings["Work Cost"] || {}),
	hide_name_column: true,
	add_fields: ["funded_by"],
	get_indicator(doc) {
		if (doc.funded_by === "Cliente") {
			return [__("Cliente"), "blue", "funded_by,=,Cliente"];
		}
		const map = {
			Open: [__("Aberta"), "orange", "status,=,Open"],
			"Partially Paid": [__("Parcialmente paga"), "blue", "status,=,Partially Paid"],
			Paid: [__("Paga"), "green", "status,=,Paid"],
			Cancelled: [__("Cancelada"), "red", "status,=,Cancelled"],
		};
		return map[doc.status] || [doc.status, "gray", `status,=,${doc.status}`];
	},
};
