import importlib
import json
import os
import pkgutil
from pathlib import Path

import engenharia
import frappe
from frappe.model.base_document import get_controller
from frappe.tests.utils import FrappeTestCase


class TestImports(FrappeTestCase):
	def test_all_modules_import(self):
		"""Import quebrado impede @frappe.whitelist() de registrar → 403 na UI."""
		failures = []
		for _finder, name, _ispkg in pkgutil.walk_packages(engenharia.__path__, "engenharia."):
			if ".tests" in name or name.endswith(".test_setup"):
				continue
			try:
				importlib.import_module(name)
			except Exception as exc:
				failures.append(f"{name}: {exc!r}")
		self.assertEqual(failures, [], f"Módulos com import quebrado: {failures}")

	def test_all_doctype_controllers_resolve(self):
		"""get_controller falha se o nome da classe não bate com o DocType."""
		dt_dir = Path(__file__).resolve().parents[1] / "engenharia" / "doctype"
		failures = []
		for folder in sorted(os.listdir(dt_dir)):
			json_path = dt_dir / folder / f"{folder}.json"
			if not json_path.is_file():
				continue
			meta = json.loads(json_path.read_text())
			dt = meta["name"]
			expected = dt.replace(" ", "").replace("-", "")
			try:
				controller = get_controller(dt)
				if controller.__name__ != expected:
					failures.append(
						f"{dt}: esperado {expected!r}, encontrado {controller.__name__!r}"
					)
			except Exception as exc:
				failures.append(f"{dt}: {exc!r}")
		self.assertEqual(failures, [], f"Controllers quebrados: {failures}")

	def test_whitelisted_modules_import_cleanly(self):
		modules = [
			"engenharia.documents",
			"engenharia.dashboard_api",
			"engenharia.financial",
			"engenharia.engenharia.doctype.construction_project.construction_project",
		]
		for mod in modules:
			with self.subTest(module=mod):
				importlib.import_module(mod)
				self.assertTrue(frappe.get_attr(mod))
