from frappe import _


def get_data():
	return {
		"internal_links": {
			"Construction Project": "project",
			"Supplier": "supplier",
		},
		"transactions": [
			{
				"label": _("Obra"),
				"items": ["Construction Project"],
			},
			{
				"label": _("Prestador"),
				"items": ["Supplier"],
			},
		],
	}
