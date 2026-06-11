/* Navegação hub ↔ satélites: breadcrumb da obra, voltar e restaurar aba. */
(function () {
	const ENG_HUB_NAV_VERSION = 4;
	const BREADCRUMB_PATCH_VERSION = 3;
	const RENDER_FORM_PATCH_VERSION = 2;
	const BREADCRUMB_WIDTH_PATCH_VERSION = 2;
	const HUB_CONTEXT_KEY = "eng_hub_return_context";
	const PROJECT_DOCTYPE = "Construction Project";

	const PROJECT_FIELD_BY_DOCTYPE = {
		Commission: "construction_project",
	};

	const SATELLITE_DOCTYPES = [
		"Engineering Contract",
		"Payment",
		"Work Cost",
		"Subcontract",
		"Reimbursable Expense",
		"Deadline",
		"Permit",
		"Task",
		"Communication Log",
		"Time Log",
		"Construction Measurement",
		"Commission",
		"Project Document",
		"Project Stage",
		"Project Item",
	];

	const HUB_NAV_DOCTYPES = [PROJECT_DOCTYPE, ...SATELLITE_DOCTYPES];

	function get_project_fieldname(doctype) {
		return PROJECT_FIELD_BY_DOCTYPE[doctype] || "project";
	}

	function get_project_name(frm, route) {
		route = route || frappe.get_route();
		const docname = get_route_docname(route);
		let doc = frm?.doc;

		if (docname && (!doc || doc.name !== docname)) {
			doc = frappe.get_doc(frm.doctype, docname) || doc;
		}

		if (!doc) {
			return null;
		}
		if (frm.doctype === PROJECT_DOCTYPE) {
			return doc.name;
		}
		return doc[get_project_fieldname(frm.doctype)] || null;
	}

	function project_form_route(project_name) {
		return `/desk/${frappe.router.slug(PROJECT_DOCTYPE)}/${encodeURIComponent(project_name)}`;
	}

	function build_project_crumb(frm, route) {
		if (frm.doctype === PROJECT_DOCTYPE) {
			return null;
		}

		const project_name = get_project_name(frm, route);
		if (!project_name) {
			return null;
		}

		return {
			route: project_form_route(project_name),
			label: project_name,
			css_classes: "eng-hub-project-crumb",
			parent_class: "ellipsis",
		};
	}

	function is_satellite_doctype(doctype) {
		return SATELLITE_DOCTYPES.includes(doctype);
	}

	function is_hub_nav_doctype(doctype) {
		return HUB_NAV_DOCTYPES.includes(doctype);
	}

	function get_route_docname(route) {
		route = route || frappe.get_route();
		if (route[0] !== "Form" || !route[1]) {
			return null;
		}
		const docname = route.slice(2).join("/");
		return docname || null;
	}

	function get_frm_for_route(route) {
		route = route || frappe.get_route();
		if (route[0] !== "Form" || !route[1]) {
			return null;
		}

		const doctype_layout = frappe.router.doctype_layout || route[1];
		const frm = frappe.views.formview?.[doctype_layout]?.frm;
		if (frm) {
			return frm;
		}
		return cur_frm?.doctype === route[1] ? cur_frm : null;
	}

	function is_active_form_route(frm, route) {
		route = route || frappe.get_route();
		if (route[0] !== "Form" || route[1] !== frm.doctype) {
			return false;
		}
		return Boolean(get_route_docname(route));
	}

	function should_render_form_trail(frm, route) {
		if (!frm?.page?.$title_area || frm.meta?.istable) {
			return false;
		}
		route = route || frappe.get_route();
		return is_hub_nav_doctype(frm.doctype) && is_active_form_route(frm, route);
	}

	function get_form_breadcrumb_ul(frm) {
		if (!frm?.page?.$title_area?.length) {
			return $();
		}
		return frm.page.$title_area.find("ul.navbar-breadcrumbs").first();
	}

	function should_show_dashboard_crumb() {
		const prev_route = frappe.get_prev_route ? frappe.get_prev_route() : [];
		return (
			prev_route[0] === "eng-dashboard" || prev_route.join("/") === "eng-dashboard"
		);
	}

	function build_workspace_crumb() {
		if (!frappe.app?.sidebar?.sidebar_title) {
			return null;
		}

		const icon = frappe.utils.get_desktop_icon_by_label(frappe.app.sidebar.sidebar_title);
		if (!icon) {
			return null;
		}

		const url = frappe.utils.get_route_for_icon(icon);
		if (!url) {
			return null;
		}

		return {
			route: url,
			label: __(icon.label),
			css_classes: "worksapce-breadcrumb",
			parent_class: "ellipsis",
		};
	}

	function build_dashboard_crumb() {
		if (!should_show_dashboard_crumb()) {
			return null;
		}

		return {
			route: "/app/eng-dashboard",
			label: __("Painel de Obras"),
			css_classes: "eng-hub-dashboard-crumb",
		};
	}

	function build_list_crumb(doctype) {
		const doctype_meta = frappe.get_meta(doctype);
		if (
			(doctype === "User" && !frappe.user.has_role("System Manager")) ||
			doctype_meta?.issingle
		) {
			return null;
		}

		const doctype_route = frappe.router.slug(frappe.router.doctype_layout || doctype);
		let route;
		if (doctype_meta?.is_tree) {
			const view = frappe.model.user_settings[doctype]?.last_view || "Tree";
			route = `${doctype_route}/view/${view}`;
		} else {
			route = doctype_route;
		}

		return {
			route: `/desk/${route}`,
			label: __(doctype),
			css_classes: "title-text",
			parent_class: "ellipsis",
		};
	}

	function build_form_crumb(frm, route) {
		const doctype = frm.doctype;
		const docname = get_route_docname(route);
		const doc = frappe.get_doc(doctype, docname) || frm.doc;
		const form_route = `/desk/${frappe.router.slug(doctype)}/${encodeURIComponent(docname)}`;

		let docname_title;
		if (docname.startsWith("new-" + doctype.toLowerCase().replace(/ /g, "-"))) {
			docname_title = __("New {0}", [__(doctype)]);
		} else {
			docname_title = doc?.name || docname;
		}

		return {
			route: form_route,
			label: docname_title,
			css_classes: "title-text-form",
			disabled: true,
			ellipsis: frappe.is_mobile(),
		};
	}

	function build_breadcrumb_trail(frm, route) {
		route = route || frappe.get_route();
		const items = [];

		const workspace = build_workspace_crumb();
		if (workspace) {
			items.push(workspace);
		}

		const dashboard = build_dashboard_crumb();
		if (dashboard) {
			items.push(dashboard);
		}

		const project = build_project_crumb(frm, route);
		if (project) {
			items.push(project);
		}

		const list = build_list_crumb(frm.doctype);
		if (list) {
			items.push(list);
		}

		items.push(build_form_crumb(frm, route));
		return items;
	}

	function append_breadcrumb_li($ul, item) {
		const el = document.createElement("li");
		if (item.parent_class) {
			item.parent_class.split(/\s+/).forEach((cls) => {
				if (cls) {
					el.classList.add(cls);
				}
			});
		}
		if (item.disabled) {
			el.classList.add("disabled");
		}
		if (item.ellipsis) {
			el.classList.add("ellipsis");
		}

		const a = document.createElement("a");
		if (item.route) {
			a.href = item.route;
		}
		if (item.css_classes) {
			item.css_classes.split(/\s+/).forEach((cls) => {
				if (cls) {
					a.classList.add(cls);
				}
			});
		}
		if (item.ellipsis) {
			a.classList.add("ellipsis");
		}
		a.innerHTML = item.label;
		el.appendChild(a);
		$ul.append(el);
	}

	function render_breadcrumb_items($ul, items) {
		$ul.empty();

		const home_el = document.createElement("li");
		const home_a = document.createElement("a");
		home_a.href = "/desk";
		home_a.innerHTML = frappe.utils.icon("home");
		home_el.appendChild(home_a);
		$ul.append(home_el);

		items.forEach((item) => append_breadcrumb_li($ul, item));
		$("body").addClass("no-breadcrumbs");
	}

	function render_form_breadcrumb_trail(frm, route) {
		route = route || frappe.get_route();
		frm = frm || get_frm_for_route(route);
		if (!should_render_form_trail(frm, route)) {
			return;
		}

		const $ul = get_form_breadcrumb_ul(frm);
		if (!$ul.length) {
			return;
		}

		render_breadcrumb_items($ul, build_breadcrumb_trail(frm, route));
	}

	function sync_form_breadcrumbs(frm) {
		render_form_breadcrumb_trail(frm);
	}

	const breadcrumb_sync_timers = new WeakMap();

	function queue_breadcrumb_sync(frm) {
		if (!frm) {
			return;
		}

		const existing = breadcrumb_sync_timers.get(frm);
		if (existing) {
			existing.forEach((timer_id) => clearTimeout(timer_id));
		}

		const timers = [0, 60, 200].map((delay) =>
			setTimeout(() => sync_form_breadcrumbs(frm), delay)
		);
		breadcrumb_sync_timers.set(frm, timers);
	}

	function ensure_breadcrumb_registry(doctype) {
		const route_key = frappe.breadcrumbs.current_page();
		if (frappe.breadcrumbs.all[route_key]) {
			return frappe.breadcrumbs.all[route_key];
		}

		const meta = frappe.get_meta(doctype);
		if (!meta?.module) {
			return null;
		}

		const entry = {
			module: meta.module,
			doctype,
		};
		frappe.breadcrumbs.all[route_key] = entry;
		return entry;
	}

	function patch_breadcrumbs() {
		if (!frappe.breadcrumbs) {
			return;
		}
		if (frappe.breadcrumbs.__eng_hub_nav_version >= BREADCRUMB_PATCH_VERSION) {
			return;
		}

		if (!frappe.breadcrumbs.__eng_hub_nav_original_update) {
			frappe.breadcrumbs.__eng_hub_nav_original_update =
				frappe.breadcrumbs.update.bind(frappe.breadcrumbs);
		}
		const original_update = frappe.breadcrumbs.__eng_hub_nav_original_update;

		frappe.breadcrumbs.clear = function () {
			const route = frappe.get_route();
			if (route[0] === "Form" && route[1] && is_hub_nav_doctype(route[1])) {
				const frm = get_frm_for_route(route);
				this.$breadcrumbs = frm ? get_form_breadcrumb_ul(frm) : $();
				if (this.$breadcrumbs?.length) {
					this.$breadcrumbs.empty();
					return;
				}
			}

			const $visible = $(frappe.container?.page).find("ul.navbar-breadcrumbs").first();
			if ($visible.length) {
				this.$breadcrumbs = $visible.empty();
			} else {
				this.$breadcrumbs = $(".navbar-breadcrumbs").empty();
			}
		};

		frappe.breadcrumbs.append_breadcrumb_element = function (route, label, css_classes) {
			if (!this.$breadcrumbs?.length) {
				const $visible = $(frappe.container?.page).find("ul.navbar-breadcrumbs").first();
				this.$breadcrumbs = $visible.length ? $visible : $(".navbar-breadcrumbs").first();
			}
			if (!this.$breadcrumbs?.length) {
				return;
			}

			const el = document.createElement("li");
			const a = document.createElement("a");
			if (route) {
				a.href = route;
			}
			if (css_classes) {
				a.classList.add(css_classes);
			}
			a.innerHTML = label;
			el.appendChild(a);
			this.$breadcrumbs.eq(0).append(el);
		};

		frappe.breadcrumbs.update = function () {
			const route = frappe.get_route();
			if (route[0] === "Form" && route[1] && is_hub_nav_doctype(route[1])) {
				const frm = get_frm_for_route(route);
				if (frm) {
					ensure_breadcrumb_registry(route[1]);
					render_form_breadcrumb_trail(frm, route);
					this.toggle(true);
					return;
				}
			}

			original_update();
		};

		frappe.breadcrumbs.__eng_hub_nav_version = BREADCRUMB_PATCH_VERSION;
		frappe.breadcrumbs.__eng_hub_nav_patched = true;
	}

	function patch_configure_breadcrumb_width() {
		const proto = frappe.ui?.form?.Form?.prototype;
		if (!proto || proto.__eng_hub_nav_breadcrumb_version >= BREADCRUMB_WIDTH_PATCH_VERSION) {
			return;
		}

		if (!proto.__eng_hub_nav_original_configure_breadcrumb_width) {
			proto.__eng_hub_nav_original_configure_breadcrumb_width =
				proto.configure_breadcrumb_width;
		}
		const original = proto.__eng_hub_nav_original_configure_breadcrumb_width;
		proto.configure_breadcrumb_width = function () {
			original.call(this);
			if (should_render_form_trail(this)) {
				setTimeout(() => render_form_breadcrumb_trail(this), 200);
			}
		};
		proto.__eng_hub_nav_breadcrumb_version = BREADCRUMB_WIDTH_PATCH_VERSION;
		proto.__eng_hub_nav_breadcrumb_patched = true;
	}

	function patch_form_render_form() {
		const proto = frappe.ui?.form?.Form?.prototype;
		if (!proto || proto.__eng_hub_nav_render_version >= RENDER_FORM_PATCH_VERSION) {
			return;
		}

		if (!proto.__eng_hub_nav_original_render_form) {
			proto.__eng_hub_nav_original_render_form = proto.render_form;
		}
		const original_render_form = proto.__eng_hub_nav_original_render_form;
		proto.render_form = function (...args) {
			const result = original_render_form.apply(this, args);
			if (is_hub_nav_doctype(this.doctype)) {
				this.$wrapper.one("render_complete", () => {
					queue_breadcrumb_sync(this);
				});
			}
			return result;
		};
		proto.__eng_hub_nav_render_version = RENDER_FORM_PATCH_VERSION;
		proto.__eng_hub_nav_render_patched = true;
	}

	function detect_active_hub_tab(frm) {
		if (!frm?.$wrapper) {
			return "tab_details";
		}
		const $active = frm.$wrapper.find(".form-tabs-list .nav-link.active");
		const fieldname = $active.attr("data-fieldname");
		if (fieldname && fieldname.startsWith("tab_")) {
			return fieldname;
		}
		return "tab_details";
	}

	function save_hub_context(frm, tab_fieldname) {
		if (!frm || frm.doctype !== PROJECT_DOCTYPE || frm.is_new() || !frm.doc.name) {
			return;
		}
		sessionStorage.setItem(
			HUB_CONTEXT_KEY,
			JSON.stringify({
				project: frm.doc.name,
				tab: tab_fieldname || detect_active_hub_tab(frm),
			})
		);
	}

	function save_hub_context_from_cur_frm(tab_fieldname) {
		if (cur_frm && cur_frm.doctype === PROJECT_DOCTYPE) {
			save_hub_context(cur_frm, tab_fieldname);
		}
	}

	function restore_hub_tab(frm) {
		const raw = sessionStorage.getItem(HUB_CONTEXT_KEY);
		if (!raw || !frm || frm.doctype !== PROJECT_DOCTYPE || frm.is_new()) {
			return;
		}

		let context;
		try {
			context = JSON.parse(raw);
		} catch (error) {
			sessionStorage.removeItem(HUB_CONTEXT_KEY);
			return;
		}

		if (!context?.project || context.project !== frm.doc.name || !context.tab) {
			return;
		}

		sessionStorage.removeItem(HUB_CONTEXT_KEY);

		setTimeout(() => {
			const tab_field = frm.fields_dict[context.tab];
			if (tab_field?.tab_link) {
				$(tab_field.tab_link).trigger("click");
				return;
			}
			const $tab = frm.$wrapper.find(
				`.form-tabs-list .nav-link[data-fieldname="${context.tab}"]`
			);
			if ($tab.length) {
				$tab.trigger("click");
			}
		}, 300);
	}

	function add_back_to_project_button(frm) {
		const project_name = get_project_name(frm);
		if (!project_name || frm.is_new() || frm.doctype === PROJECT_DOCTYPE) {
			return;
		}

		frm.add_custom_button(__("Voltar à obra"), () => {
			frappe.set_route("Form", PROJECT_DOCTYPE, project_name);
		});
		frm.change_custom_button_type(__("Voltar à obra"), null, "primary");
	}

	function bind_satellite_forms() {
		SATELLITE_DOCTYPES.forEach((doctype) => {
			frappe.ui.form.on(doctype, {
				refresh(frm) {
					add_back_to_project_button(frm);
				},
			});
		});

		frappe.ui.form.on(PROJECT_DOCTYPE, {
			refresh(frm) {
				restore_hub_tab(frm);
			},
		});
	}

	function bind_breadcrumb_sync() {
		$(document).on("form-refresh", (event, frm) => {
			queue_breadcrumb_sync(frm);
		});

		$(document).on("form-load", (event, frm) => {
			queue_breadcrumb_sync(frm);
		});

		$(document).on("page-change", () => {
			const route = frappe.get_route();
			const frm = get_frm_for_route(route) || cur_frm;
			if (frm) {
				queue_breadcrumb_sync(frm);
			}
		});
	}

	function publish_eng_hub_nav_api() {
		window.eng_hub_nav = {
			VERSION: ENG_HUB_NAV_VERSION,
			SATELLITE_DOCTYPES,
			PROJECT_FIELD_BY_DOCTYPE,
			get_project_fieldname,
			get_project_name,
			get_frm_for_route,
			save_hub_context,
			restore_hub_tab,
			sync_form_breadcrumbs,
			render_form_breadcrumb_trail,
			debug_breadcrumbs() {
				const route = frappe.get_route();
				const frm = get_frm_for_route(route) || cur_frm;
				const $ul = frm ? get_form_breadcrumb_ul(frm) : $();
				const info = {
					version: ENG_HUB_NAV_VERSION,
					breadcrumb_patch: frappe.breadcrumbs?.__eng_hub_nav_version,
					route: route.join("/"),
					cur_frm: cur_frm?.doctype,
					frm_for_route: frm?.doctype,
					ul_in_frm: $ul.length,
					li_in_frm: $ul.find("li").length,
					li_visible_page: $(frappe.container?.page)
						.find("ul.navbar-breadcrumbs li")
						.length,
				};
				console.log("[eng_hub_nav]", info);
				if (frm) {
					render_form_breadcrumb_trail(frm, route);
					info.li_after_render = get_form_breadcrumb_ul(frm).find("li").length;
					console.log("[eng_hub_nav] after render", info.li_after_render);
				}
				return info;
			},
		};
	}

	function init_eng_hub_nav() {
		publish_eng_hub_nav_api();

		if (!window.frappe?.breadcrumbs || !window.frappe?.ui?.form?.Form) {
			setTimeout(init_eng_hub_nav, 50);
			return;
		}

		patch_breadcrumbs();
		patch_configure_breadcrumb_width();
		patch_form_render_form();

		if (window.__eng_hub_nav_initialized) {
			return;
		}

		window.__eng_hub_nav_initialized = true;
		bind_satellite_forms();
		bind_breadcrumb_sync();
	}

	window.eng_hub_nav_follow_route = function (route_str) {
		save_hub_context_from_cur_frm();
		const parts = (route_str || "").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	};

	window.eng_hub_nav_new_doc = function (doctype, defaults) {
		save_hub_context_from_cur_frm();
		frappe.new_doc(doctype, defaults);
	};

	window.eng_hub_nav_set_route = function () {
		save_hub_context_from_cur_frm();
		frappe.set_route.apply(frappe, arguments);
	};

	window.eng_hub_nav_restore_tab = restore_hub_tab;

	init_eng_hub_nav();
})();
