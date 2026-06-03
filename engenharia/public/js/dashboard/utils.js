frappe.provide("engenharia.dashboard");

engenharia.dashboard.utils = {
	fmt_currency(val, plain) {
		if (plain) {
			return format_currency(val || 0, "BRL");
		}
		return frappe.format(val || 0, { fieldtype: "Currency", currency: "BRL" });
	},

	currency_html(val, options = {}) {
		const plain = options.plain !== false;
		const end = options.alignEnd ? " eng-dash-currency--end" : "";
		return (
			`<span class="eng-dash-currency${end}">` +
			frappe.utils.escape_html(this.fmt_currency(val, plain)) +
			"</span>"
		);
	},

	css_var(name, fallback = "") {
		const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
		return value || fallback;
	},

	tone_color(tone) {
		const map = {
			danger: "--red-500",
			success: "--green-500",
			warning: "--orange-500",
			info: "--blue-500",
			neutral: "--gray-600",
		};
		const key = map[tone] || map.neutral;
		return this.css_var(key, "");
	},

	flt(val) {
		return parseFloat(val) || 0;
	},

	greeting_for_hour() {
		const h = new Date().getHours();
		if (h < 12) return __("Bom dia");
		if (h < 18) return __("Boa tarde");
		return __("Boa noite");
	},

	status_pill(status) {
		const map = {
			Vencido: "red",
			Pendente: "orange",
			Recebido: "green",
			"A reembolsar": "orange",
			Reembolsado: "green",
			Cancelado: "gray",
		};
		const cls = map[status] || "gray";
		const label = frappe.utils.escape_html(status || "");
		return `<span class="indicator-pill ${cls} filterable no-indicator-dot ellipsis">${label}</span>`;
	},

	route_form(doctype, name) {
		if (doctype && name) {
			frappe.set_route("Form", doctype, name);
		}
	},

	bind_routes($root) {
		$root.find("[data-doctype][data-name]").on("click", function () {
			engenharia.dashboard.utils.route_form($(this).data("doctype"), $(this).data("name"));
		});
	},
};
