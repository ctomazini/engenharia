const EngenhariaMasks = {
	onlyDigits(v) {
		return (v || "").replace(/\D/g, "");
	},

	onlyCnpjChars(v) {
		// 12 primeiras: A-Z/0-9; 2 últimas (DV): somente dígitos (Receita Federal).
		const raw = (v || "")
			.toUpperCase()
			.replace(/[^0-9A-Z]/g, "");
		const body = raw.slice(0, 12);
		const dv = raw.slice(12).replace(/[^0-9]/g, "").slice(0, 2);
		return body + dv;
	},

	applyCPF(v) {
		v = this.onlyDigits(v).substring(0, 11);
		if (v.length > 9) return v.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
		if (v.length > 6) return v.replace(/(\d{3})(\d{3})(\d{0,3})/, "$1.$2.$3");
		if (v.length > 3) return v.replace(/(\d{3})(\d{0,3})/, "$1.$2");
		return v;
	},

	applyCNPJ(v) {
		// CNPJ numérico ou alfanumérico (Receita): 12 chars A-Z/0-9 + 2 DVs numéricos.
		v = this.onlyCnpjChars(v);
		if (v.length > 12)
			return v.replace(/([0-9A-Z]{2})([0-9A-Z]{3})([0-9A-Z]{3})([0-9A-Z]{4})(\d{2})/, "$1.$2.$3/$4-$5");
		if (v.length > 8) return v.replace(/([0-9A-Z]{2})([0-9A-Z]{3})([0-9A-Z]{3})([0-9A-Z]{0,4})/, "$1.$2.$3/$4");
		if (v.length > 5) return v.replace(/([0-9A-Z]{2})([0-9A-Z]{3})([0-9A-Z]{0,3})/, "$1.$2.$3");
		if (v.length > 2) return v.replace(/([0-9A-Z]{2})([0-9A-Z]{0,3})/, "$1.$2");
		return v;
	},

	applyPhone(v) {
		v = this.onlyDigits(v).substring(0, 11);
		if (v.length > 10) return v.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
		if (v.length > 6) return v.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3");
		if (v.length > 2) return v.replace(/(\d{2})(\d{0,5})/, "($1) $2");
		return v;
	},

	applyCEP(v) {
		v = this.onlyDigits(v).substring(0, 8);
		if (v.length > 5) return v.replace(/(\d{5})(\d{0,3})/, "$1-$2");
		return v;
	},

	listFormatters: {
		cpf(value) {
			return EngenhariaMasks.applyCPF(value) || "";
		},
		cnpj(value) {
			return EngenhariaMasks.applyCNPJ(value) || "";
		},
		phone(value) {
			return EngenhariaMasks.applyPhone(value) || "";
		},
		cep(value) {
			return EngenhariaMasks.applyCEP(value) || "";
		},
	},

	_bindInput($input, maskFn) {
		if (!$input || !$input.length) return;

		if ($.fn.inputmask) {
			$input.off("input.engenharia_mask");
			return;
		}

		$input.off("input.engenharia_mask").on("input.engenharia_mask", function () {
			const val = $(this).val();
			const masked = maskFn.call(EngenhariaMasks, val);
			if (val !== masked) {
				const pos = this.selectionStart;
				const diff = masked.length - val.length;
				$(this).val(masked);
				this.setSelectionRange(pos + diff, pos + diff);
			}
		});
	},

	_inputmaskPattern(tipo) {
		const patterns = {
			cpf: "999.999.999-99",
			// * = alfanumérico (A-Z/0-9); DV permanece numérico.
			cnpj: "**.***.***/****-99",
			celular: "(99) 99999-9999",
			fixo: "(99) 9999-9999",
			phone: "(99) 99999-9999",
			cep: "99999-999",
		};
		return patterns[tipo] || "";
	},

	_refreshDisplay(field, maskFn) {
		if (!field || !field.$input) return;
		const raw = field.get_value && field.get_value();
		if (!raw) return;
		const masked = maskFn.call(this, raw);
		if (field.$input.val() !== masked) {
			field.$input.val(masked);
		}
	},

	bindMask(frm, fieldname, maskFn, inputmaskTipo) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !field.$input) return;

		field.$input.off(".engenharia_mask");
		if ($.fn.inputmask && field.$input.inputmask) {
			field.$input.inputmask("remove");
		}

		if ($.fn.inputmask && inputmaskTipo) {
			const opts = { mask: this._inputmaskPattern(inputmaskTipo) };
			if (inputmaskTipo === "cnpj") {
				opts.casing = "upper";
				opts.autoUnmask = true;
				opts.removeMaskOnSubmit = true;
			}
			field.$input.inputmask(opts);
		} else {
			this._bindInput(field.$input, maskFn);
		}

		this._refreshDisplay(field, maskFn);
	},

	unbindMask(frm, fieldname) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !field.$input) return;
		field.$input.off(".engenharia_mask input.engenharia_mask");
		if ($.fn.inputmask && field.$input.inputmask) {
			field.$input.inputmask("remove");
		}
	},

	formatFormField(frm, fieldname, maskFn) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !frm.doc[fieldname]) return;
		this._refreshDisplay(field, maskFn);
	},

	formatChildField(cdt, cdn, fieldname, maskFn) {
		const row = locals[cdt] && locals[cdt][cdn];
		if (!row || !row[fieldname]) return;
		const masked = maskFn.call(this, row[fieldname]);
		if (row[fieldname] !== masked) {
			frappe.model.set_value(cdt, cdn, fieldname, masked);
		}
	},

	setupGridMaskFormatters(frm, tableFieldname, specs) {
		const grid = frm.fields_dict[tableFieldname] && frm.fields_dict[tableFieldname].grid;
		if (!grid) return;

		specs.forEach(({ fieldname, maskFn }) => {
			const df = grid.get_docfield(fieldname);
			if (!df) return;
			df.formatter = (value) => {
				if (!value) return "";
				return frappe.utils.escape_html(maskFn.call(EngenhariaMasks, value));
			};
		});
		grid.refresh();
	},

	setupCustomerForm(frm) {
		if (!window.EngenhariaMasks) return;

		if (frm.doc.person_type === "Pessoa Física") {
			this.bindMask(frm, "cpf", this.applyCPF, "cpf");
			this.unbindMask(frm, "cnpj");
			this.unbindMask(frm, "legal_representative_cpf");
		} else if (frm.doc.person_type === "Pessoa Jurídica") {
			this.bindMask(frm, "cnpj", this.applyCNPJ, "cnpj");
			this.bindMask(frm, "legal_representative_cpf", this.applyCPF, "cpf");
			this.unbindMask(frm, "cpf");
		}

		["cpf", "cnpj", "legal_representative_cpf"].forEach((fieldname) => {
			if (!frm.doc[fieldname]) return;
			const fn = fieldname === "cnpj" ? this.applyCNPJ : this.applyCPF;
			this.formatFormField(frm, fieldname, fn);
		});

		this.setupGridMaskFormatters(frm, "contacts", [
			{ fieldname: "phone", maskFn: this.applyPhone },
			{ fieldname: "mobile", maskFn: this.applyPhone },
		]);
		this.setupGridMaskFormatters(frm, "addresses", [{ fieldname: "cep", maskFn: this.applyCEP }]);
	},

	setupSupplierForm(frm) {
		if (!window.EngenhariaMasks) return;
		this.bindMask(frm, "cnpj", this.applyCNPJ, "cnpj");
		this.bindMask(frm, "phone", this.applyPhone, "phone");
		this.formatFormField(frm, "cnpj", this.applyCNPJ);
		this.formatFormField(frm, "phone", this.applyPhone);
	},

	setupEngineeringSettingsForm(frm) {
		if (!window.EngenhariaMasks) return;
		this.bindMask(frm, "company_cnpj", this.applyCNPJ, "cnpj");
		this.bindMask(frm, "engineer_cpf", this.applyCPF, "cpf");
		this.bindMask(frm, "engineer_phone", this.applyPhone, "phone");
		this.formatFormField(frm, "company_cnpj", this.applyCNPJ);
		this.formatFormField(frm, "engineer_cpf", this.applyCPF);
		this.formatFormField(frm, "engineer_phone", this.applyPhone);
	},
};

window.EngenhariaMasks = EngenhariaMasks;
