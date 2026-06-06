from frappe import _


def get_data():
	return {
		"non_standard_fieldnames": {
			"Subcontract": "supplier",
			"Work Cost": "supplier",
		},
		"transactions": [
			{
				"label": _("Custos e contratos"),
				"items": ["Subcontract", "Work Cost"],
			},
		],
	}
