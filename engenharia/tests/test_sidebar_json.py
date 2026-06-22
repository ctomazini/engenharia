import json
import os
import unittest

from engenharia.setup.sidebar import SIDEBAR_LINK_ORDER


class TestSidebarJson(unittest.TestCase):
	def test_workspace_sidebar_matches_canonical_order(self):
		path = os.path.join(
			os.path.dirname(__file__),
			"..",
			"workspace_sidebar",
			"engenharia.json",
		)
		with open(path, encoding="utf-8") as handle:
			doc = json.load(handle)

		links = [
			(item["label"], item.get("link_to") or item.get("url"), item["link_type"])
			for item in doc["items"]
			if item.get("type") == "Link"
		]

		expected = [(label, link_to, link_type) for label, link_to, link_type in SIDEBAR_LINK_ORDER]

		self.assertEqual(
			len(links),
			len(expected),
			f"sidebar JSON has {len(links)} links; SIDEBAR_LINK_ORDER has {len(expected)}",
		)
		for idx, (actual, want) in enumerate(zip(links, expected, strict=True)):
			self.assertEqual(
				actual,
				want,
				f"link #{idx + 1}: expected {want}, got {actual}",
			)
