const EngenhariaMasks = {
	onlyDigits(v) {
		return (v || "").replace(/\D/g, "");
	},

	applyCPF(v) {
		v = this.onlyDigits(v).substring(0, 11);
		if (v.length > 9) return v.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
		if (v.length > 6) return v.replace(/(\d{3})(\d{3})(\d{0,3})/, "$1.$2.$3");
		if (v.length > 3) return v.replace(/(\d{3})(\d{0,3})/, "$1.$2");
		return v;
	},

	applyCNPJ(v) {
		v = this.onlyDigits(v).substring(0, 14);
		if (v.length > 12)
			return v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
		if (v.length > 8) return v.replace(/(\d{2})(\d{3})(\d{3})(\d{0,4})/, "$1.$2.$3/$4");
		if (v.length > 5) return v.replace(/(\d{2})(\d{3})(\d{0,3})/, "$1.$2.$3");
		if (v.length > 2) return v.replace(/(\d{2})(\d{0,3})/, "$1.$2");
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
			cnpj: "99.999.999/9999-99",
			celular: "(99) 99999-9999",
			fixo: "(99) 9999-9999",
			phone: "(99) 99999-9999",
			cep: "99999-999",
		};
		return patterns[tipo] || "";
	},

	bindMask(frm, fieldname, maskFn, inputmaskTipo) {
		const field = frm.fields_dict && frm.fields_dict[fieldname];
		if (!field || !field.$input) return;

		field.$input.off(".engenharia_mask");
		if ($.fn.inputmask && field.$input.inputmask) {
			field.$input.inputmask("remove");
		}

		if ($.fn.inputmask && inputmaskTipo) {
			field.$input.inputmask(this._inputmaskPattern(inputmaskTipo));
		} else {
			this._bindInput(field.$input, maskFn);
		}

		const current = field.get_value && field.get_value();
		if (current) {
			const masked = maskFn.call(this, current);
			if (current !== masked) {
				field.set_value(masked);
			}
		}
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
		if (!frm.doc[fieldname]) return;
		const masked = maskFn.call(this, frm.doc[fieldname]);
		if (frm.doc[fieldname] !== masked) {
			frm.set_value(fieldname, masked);
		}
	},

	setupCustomerForm(frm) {
		if (!window.EngenhariaMasks) return;

		if (frm.doc.person_type === "Pessoa Física") {
			this.bindMask(frm, "cpf", this.applyCPF, "cpf");
			this.unbindMask(frm, "cnpj");
		} else if (frm.doc.person_type === "Pessoa Jurídica") {
			this.bindMask(frm, "cnpj", this.applyCNPJ, "cnpj");
			this.unbindMask(frm, "cpf");
		}

		["cpf", "cnpj", "phone"].forEach((fieldname) => {
			if (!frm.doc[fieldname]) return;
			const fn =
				fieldname === "cnpj"
					? this.applyCNPJ
					: fieldname === "cpf"
						? this.applyCPF
						: this.applyPhone;
			this.formatFormField(frm, fieldname, fn);
		});
	},
};

window.EngenhariaMasks = EngenhariaMasks;
