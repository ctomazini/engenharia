import frappe
from frappe.utils import get_url


def boot_session(bootinfo):
	"""Expõe dados do escritório no boot para print formats de relatório (client JS)."""
	office = {
		"company_name": "Escritório de Engenharia",
		"company_cnpj": "",
		"company_crea": "",
		"company_logo_url": "",
	}

	if frappe.db.exists("DocType", "Engineering Settings"):
		settings = frappe.get_single("Engineering Settings")
		office["company_name"] = settings.company_name or office["company_name"]
		office["company_cnpj"] = settings.company_cnpj or ""
		office["company_crea"] = settings.company_crea or ""
		if settings.company_logo:
			office["company_logo_url"] = get_url(settings.company_logo)

	bootinfo["eng_office"] = office
