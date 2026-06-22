from frappe import _


def get_data():
	return {
		"internal_links": {
			"Construction Project": "project",
		},
		"non_standard_fieldnames": {
			"Payment": "contract",
		},
		"transactions": [
			{
				"label": _("Obra"),
				"items": ["Construction Project"],
			},
			{
				"label": _("Recebimentos"),
				"items": ["Payment"],
			},
		],
	}
