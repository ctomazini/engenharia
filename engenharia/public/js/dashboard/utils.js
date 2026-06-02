frappe.provide("engenharia.dashboard");

engenharia.dashboard.utils = {
	format_currency(value) {
		return frappe.format(value, { fieldtype: "Currency" });
	},

	route_form(doctype, name) {
		if (doctype && name) {
			frappe.set_route("Form", doctype, name);
		}
	},
};
