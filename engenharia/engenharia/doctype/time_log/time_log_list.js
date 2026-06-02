frappe.listview_settings["Time Log"] = {
	...(frappe.listview_settings["Time Log"] || {}),
	hide_name_column: true,
	get_indicator(doc) {
		if (doc.timer_active) {
			return [__("Timer ativo"), "red", "timer_active,=,1"];
		}
		return [__("Parado"), "grey", "timer_active,=,0"];
	},
	add_fields: ["timer_active"],
};
