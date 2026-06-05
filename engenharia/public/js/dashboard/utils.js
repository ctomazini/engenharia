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

	icon(name, size = "sm") {
		try {
			return frappe.utils.icon(name, size) || "";
		} catch (e) {
			return "";
		}
	},

	list_limit_options() {
		return [
			{ value: 5, label: "5" },
			{ value: 10, label: "10" },
			{ value: 15, label: "15" },
		];
	},

	default_list_limits() {
		return {
			timeline: 5,
			payments: 5,
			parcelas: 5,
			despesas: 5,
			comunicacoes: 5,
			deadlines: 5,
			tasks: 5,
		};
	},

	list_meta_label(meta) {
		if (!meta) return "";
		if (meta.showing >= meta.total) {
			return __("Todos ({0})", [meta.total]);
		}
		return __("{0} de {1}", [meta.showing, meta.total]);
	},

	render_list_limit_controls(list_key, current, meta) {
		const options = this.list_limit_options()
			.map(
				(op) =>
					`<button type="button" class="eng-dash-linhas-btn${current === op.value ? " active" : ""}" data-list-key="${list_key}" data-list-limit="${op.value}">${op.label}</button>`
			)
			.join("");
		const badge = meta ? `<span class="eng-dash-linhas-meta">${frappe.utils.escape_html(this.list_meta_label(meta))}</span>` : "";
		return `
			<div class="eng-dash-linhas-wrap">
				<span class="eng-dash-linhas-label">${__("Linhas")}</span>
				<div class="eng-dash-linhas-filters">${options}</div>
				${badge}
			</div>`;
	},

	status_pill(status) {
		const map = {
			Vencido: "red",
			Pendente: "orange",
			Recebido: "green",
			"A reembolsar": "orange",
			Reembolsado: "green",
			Cancelado: "gray",
			Renegociado: "blue",
		};
		const cls = map[status] || "gray";
		const label = frappe.utils.escape_html(status || "");
		return `<span class="indicator-pill ${cls} filterable no-indicator-dot ellipsis">${label}</span>`;
	},

	goto_list(doctype, filters) {
		if (!doctype) return;
		frappe.route_options = {};
		(filters || []).forEach((filter) => {
			if (Array.isArray(filter) && filter.length >= 3) {
				frappe.route_options[filter[1]] = [filter[0], filter[2]];
			}
		});
		frappe.set_route("List", doctype);
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

	bind_attention_routes($root) {
		$root.find(".eng-dash-atencao-card[data-atencao-index]").on("click", function () {
			const index = cint($(this).attr("data-atencao-index"));
			const tiles = ($root.data("atencao-tiles") || [])[index];
			if (tiles && tiles.deep_link) {
				engenharia.dashboard.utils.goto_list(tiles.deep_link.doctype, tiles.deep_link.filters);
			}
		});
	},

	bind_list_limits($root, page, reload_fn) {
		$root.find(".eng-dash-linhas-btn").on("click", function () {
			const key = $(this).attr("data-list-key");
			const limit = cint($(this).attr("data-list-limit"));
			if (!page.eng_dash_list_limits) {
				page.eng_dash_list_limits = engenharia.dashboard.utils.default_list_limits();
			}
			if (page.eng_dash_list_limits[key] === limit) return;
			page.eng_dash_list_limits[key] = limit;
			reload_fn(page);
		});
	},

	render_skeleton($container) {
		$container.html(`
			<div class="eng-dash-skeleton">
				<div class="eng-dash-skeleton-block eng-dash-skeleton-block--hero"></div>
				<div class="eng-dash-skeleton-grid">
					<div class="eng-dash-skeleton-block"></div>
					<div class="eng-dash-skeleton-block"></div>
					<div class="eng-dash-skeleton-block"></div>
					<div class="eng-dash-skeleton-block"></div>
				</div>
				<div class="eng-dash-skeleton-block eng-dash-skeleton-block--wide"></div>
			</div>
		`);
	},

	render_empty(message, icon = "check-circle", variant = "success") {
		const variantClass = variant ? ` eng-dash-empty-state--${variant}` : "";
		return `
			<div class="eng-dash-empty-state${variantClass}">
				<div class="eng-dash-empty-state__icon">${this.icon(icon, "md")}</div>
				<p>${frappe.utils.escape_html(message)}</p>
			</div>`;
	},

	event_type_label(type) {
		const map = {
			deadline: __("Prazo"),
			task: __("Tarefa"),
			payment: __("Pagamento"),
			permit: __("Protocolo"),
		};
		return map[type] || __("Compromisso");
	},

	extract_time_from_sort_key(sort_key) {
		if (!sort_key) return "";
		const parts = String(sort_key).trim().split(/\s+/);
		if (parts.length < 2) return "";
		return parts[1].slice(0, 5);
	},

	group_timeline_by_date(items) {
		const groups = [];
		const seen = new Map();
		(items || []).forEach((item) => {
			const key = item.date || item.when_label || "";
			if (!seen.has(key)) {
				const group = {
					date: key,
					label: item.when_label || String(key),
					items: [],
				};
				seen.set(key, group);
				groups.push(group);
			}
			seen.get(key).items.push(item);
		});
		return groups;
	},

	render_view_all_footer(doctype, meta) {
		if (!meta || !meta.total || meta.showing >= meta.total) return "";
		return `
			<div class="eng-dash-list-footer">
				<button type="button" class="eng-dash-view-all" data-doctype="${frappe.utils.escape_html(doctype)}">
					${__("Ver todos ({0})", [meta.total])}
				</button>
			</div>`;
	},

	bind_view_all($root) {
		$root.find(".eng-dash-view-all[data-doctype]").on("click", function () {
			frappe.set_route("List", $(this).attr("data-doctype"));
		});
	},
};
