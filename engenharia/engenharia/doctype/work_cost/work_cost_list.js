frappe.listview_settings["Work Cost"] = {
	...(frappe.listview_settings["Work Cost"] || {}),
	hide_name_column: true,
	add_fields: ["funded_by"],
	get_indicator(doc) {
		if (doc.funded_by === "Cliente") {
			return [__("Cliente"), "blue", "funded_by,=,Cliente"];
		}
		return [__("Escritório"), "orange", "funded_by,=,Escritório"];
	},
};
