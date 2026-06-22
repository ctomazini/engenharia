(function () {
	const PROJECT_FIELD_BY_DOCTYPE =
		(window.eng_hub_nav && window.eng_hub_nav.PROJECT_FIELD_BY_DOCTYPE) || {
			Commission: "construction_project",
		};

	// Satélites com campo project/construction_project mas sem customer (ex.: Etapa, Item).
	const DOCTYPES_WITHOUT_CUSTOMER = new Set([
		"Commission",
		"Project Stage",
		"Project Item",
	]);

	const FALLBACK_SATELLITE_DOCTYPES = [
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
		"Project Document",
	];

	function get_satellite_doctypes() {
		return (
			(window.eng_hub_nav && window.eng_hub_nav.SATELLITE_DOCTYPES) ||
			FALLBACK_SATELLITE_DOCTYPES
		);
	}

	function get_doctypes_with_customer() {
		return get_satellite_doctypes().filter(
			(doctype) => !DOCTYPES_WITHOUT_CUSTOMER.has(doctype)
		);
	}

	function get_project_fieldname(doctype) {
		return PROJECT_FIELD_BY_DOCTYPE[doctype] || "project";
	}

	function fetch_customer_from_project(project, callback) {
		if (!project) {
			callback("");
			return;
		}
		frappe.db.get_value("Construction Project", project, "customer", (value) => {
			callback((value && value.customer) || "");
		});
	}

	function set_customer_if_present(frm, customer) {
		if (!frm.fields_dict.customer) {
			return;
		}
		if (frm.doc.customer === customer) {
			return;
		}
		frm.set_value("customer", customer || "");
	}

	function sync_customer_on_form(frm) {
		const project_field = get_project_fieldname(frm.doctype);
		if (!frm.fields_dict.customer || !frm.fields_dict[project_field]) {
			return;
		}
		const project = frm.doc[project_field];
		if (!project) {
			if (frm.doc.customer) {
				set_customer_if_present(frm, "");
			}
			return;
		}
		if (frm.doc.customer) {
			return;
		}
		fetch_customer_from_project(project, (customer) => {
			set_customer_if_present(frm, customer);
		});
	}

	get_doctypes_with_customer().forEach((doctype) => {
		const project_field = get_project_fieldname(doctype);
		const handlers = {
			refresh(frm) {
				sync_customer_on_form(frm);
			},
		};
		handlers[project_field] = function (frm) {
			const project = frm.doc[project_field];
			fetch_customer_from_project(project, (customer) => {
				set_customer_if_present(frm, customer);
			});
		};
		frappe.ui.form.on(doctype, handlers);
	});

	if (!frappe.ui.form.QuickEntryForm) {
		return;
	}

	const QuickEntryForm = frappe.ui.form.QuickEntryForm;
	const original_open_doc = QuickEntryForm.prototype.open_doc;
	const original_render_dialog = QuickEntryForm.prototype.render_dialog;

	function bind_project_on_quick_entry(me) {
		if (!get_doctypes_with_customer().includes(me.doctype)) {
			return;
		}
		const project_field = get_project_fieldname(me.doctype);
		const project_field_control = me.fields_dict && me.fields_dict[project_field];
		if (!project_field_control || !me.fields_dict.customer) {
			return;
		}

		const update_customer = () => {
			const project = me.get_value(project_field);
			fetch_customer_from_project(project, (customer) => {
				me.doc.customer = customer || "";
			});
		};

		project_field_control.$input.on("change", update_customer);
		if (me.doc[project_field] && !me.doc.customer) {
			update_customer();
		}
	}

	QuickEntryForm.prototype.render_dialog = function () {
		original_render_dialog.call(this);
		bind_project_on_quick_entry(this);
	};

	QuickEntryForm.prototype.open_doc = function (set_hooks) {
		const me = this;
		const project_field = get_project_fieldname(me.doctype);
		if (
			get_doctypes_with_customer().includes(me.doctype) &&
			me.doc[project_field] &&
			!me.doc.customer &&
			me.fields_dict.customer
		) {
			fetch_customer_from_project(me.doc[project_field], (customer) => {
				if (customer) {
					me.doc.customer = customer;
				}
				original_open_doc.call(me, set_hooks);
			});
			return;
		}
		original_open_doc.call(me, set_hooks);
	};
})();
