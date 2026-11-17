import unittest
from unittest.mock import patch

from payroll_africa import setup
from payroll_africa.boot import COUNTRY_FIELD_MAP


class TestCountrySetup(unittest.TestCase):
	def test_every_enable_field_has_a_setup_function(self):
		"""_setup_country resolves enable_<name> to setup_<name>; a gap would silently skip a country."""
		for country, field in COUNTRY_FIELD_MAP.items():
			fn = getattr(setup, "setup_" + field.removeprefix("enable_"), None)
			self.assertTrue(callable(fn), country)

	def test_run_setup_seeds_only_company_countries(self):
		with (
			patch.object(setup, "_ensure_currencies"),
			patch.object(setup, "_setup_custom_fields"),
			patch.object(setup, "setup_desktop_icon"),
			patch.object(setup.frappe, "get_all", return_value=["Kenya", "Kenya", None]),
			patch.object(setup, "setup_kenya") as kenya,
			patch.object(setup, "setup_uganda") as uganda,
		):
			setup._run_setup()
		kenya.assert_called_once()
		uganda.assert_not_called()
