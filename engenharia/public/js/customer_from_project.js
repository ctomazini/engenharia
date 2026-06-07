(function () {
	const DOCTYPES_WITH_PROJECT = [
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
	];

	function fetch_customer_from_project(project, callback) {
		if (!project) {
			callback("");
			return;
		}
		frappe.db.get_value("Construction Project", project, "customer", (value) => {
			callback((value && value.customer) || "");
		});
	}

	function sync_customer_on_form(frm) {
		if (!frm.fields_dict.customer || !frm.fields_dict.project) {
			return;
		}
		if (!frm.doc.project) {
			if (frm.doc.customer) {
				frm.set_value("customer", "");
			}
			return;
		}
		if (frm.doc.customer) {
			return;
		}
		fetch_customer_from_project(frm.doc.project, (customer) => {
			if (customer && frm.doc.customer !== customer) {
				frm.set_value("customer", customer);
			}
		});
	}

	DOCTYPES_WITH_PROJECT.forEach((doctype) => {
		frappe.ui.form.on(doctype, {
			project(frm) {
				fetch_customer_from_project(frm.doc.project, (customer) => {
					frm.set_value("customer", customer);
				});
			},
			refresh(frm) {
				sync_customer_on_form(frm);
			},
		});
	});

	if (!frappe.ui.form.QuickEntryForm) {
		return;
	}

	const QuickEntryForm = frappe.ui.form.QuickEntryForm;
	const original_open_doc = QuickEntryForm.prototype.open_doc;
	const original_render_dialog = QuickEntryForm.prototype.render_dialog;

	function bind_project_on_quick_entry(me) {
		if (!DOCTYPES_WITH_PROJECT.includes(me.doctype)) {
			return;
		}
		const project_field = me.fields_dict && me.fields_dict.project;
		if (!project_field) {
			return;
		}

		const update_customer = () => {
			const project = me.get_value("project");
			fetch_customer_from_project(project, (customer) => {
				me.doc.customer = customer || "";
			});
		};

		project_field.$input.on("change", update_customer);
		if (me.doc.project && !me.doc.customer) {
			update_customer();
		}
	}

	QuickEntryForm.prototype.render_dialog = function () {
		original_render_dialog.call(this);
		bind_project_on_quick_entry(this);
	};

	QuickEntryForm.prototype.open_doc = function (set_hooks) {
		const me = this;
		if (
			DOCTYPES_WITH_PROJECT.includes(me.doctype) &&
			me.doc.project &&
			!me.doc.customer
		) {
			fetch_customer_from_project(me.doc.project, (customer) => {
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
