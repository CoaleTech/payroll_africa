import unittest
from unittest.mock import patch, MagicMock
import sys


# Mock frappe before importing report modules
_mock_frappe = MagicMock()
_mock_frappe._ = lambda x: x  # translation passthrough
_mock_frappe.utils.flt = lambda x, precision=None: round(float(x or 0), precision or 9)
_mock_frappe.utils.getdate = lambda x: x
sys.modules.setdefault("frappe", _mock_frappe)
sys.modules.setdefault("frappe.utils", _mock_frappe.utils)

from payroll_africa.payroll_africa.report.statutory_deductions_summary.statutory_deductions_summary import (
	get_columns as sds_columns, get_conditions as sds_conditions,
)
from payroll_africa.payroll_africa.report.employer_contributions.employer_contributions import (
	get_columns as ec_columns, get_conditions as ec_conditions,
)
from payroll_africa.payroll_africa.report.cost_to_company.cost_to_company import (
	get_columns as ctc_columns, get_conditions as ctc_conditions,
)
from payroll_africa.payroll_africa.report.nssf_remittance.nssf_remittance import (
	get_columns as nssf_columns, get_conditions as nssf_conditions,
)
from payroll_africa.payroll_africa.report.shif_remittance.shif_remittance import (
	get_columns as shif_columns, get_conditions as shif_conditions,
)
from payroll_africa.payroll_africa.report.housing_levy_return.housing_levy_return import (
	get_columns as hl_columns, get_conditions as hl_conditions,
)
from payroll_africa.payroll_africa.report.p10_monthly_tax_return.p10_monthly_tax_return import (
	get_columns as p10_columns, get_conditions as p10_conditions,
)
from payroll_africa.payroll_africa.report.p9a_tax_deduction_card.p9a_tax_deduction_card import (
	get_columns as p9a_columns, get_data as p9a_get_data,
)


class TestReportColumns(unittest.TestCase):
	"""Verify each report returns proper column definitions."""

	def _assert_valid_columns(self, columns):
		"""All columns must have fieldname, label, fieldtype, width."""
		self.assertIsInstance(columns, list)
		self.assertGreater(len(columns), 0)
		for col in columns:
			self.assertIn("fieldname", col)
			self.assertIn("label", col)
			self.assertIn("fieldtype", col)
			self.assertIn("width", col)

	def test_statutory_deductions_summary_columns(self):
		columns = sds_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("employee", fieldnames)
		self.assertIn("gross_pay", fieldnames)
		self.assertIn("paye", fieldnames)
		self.assertIn("net_pay", fieldnames)

	def test_employer_contributions_columns(self):
		columns = ec_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("nssf_employer", fieldnames)
		self.assertIn("total_employer_cost", fieldnames)

	def test_cost_to_company_columns(self):
		columns = ctc_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("cost_to_company", fieldnames)
		self.assertIn("total_employer_contributions", fieldnames)
		self.assertIn("department", fieldnames)

	def test_nssf_remittance_columns(self):
		columns = nssf_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("nssf_employee", fieldnames)
		self.assertIn("nssf_employer", fieldnames)
		self.assertIn("total_nssf", fieldnames)

	def test_shif_remittance_columns(self):
		columns = shif_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("shif", fieldnames)
		self.assertIn("gross_pay", fieldnames)

	def test_housing_levy_return_columns(self):
		columns = hl_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("employee_levy", fieldnames)
		self.assertIn("employer_levy", fieldnames)
		self.assertIn("total_levy", fieldnames)

	def test_p9a_tax_deduction_card_columns(self):
		columns = p9a_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("month", fieldnames)
		self.assertIn("basic_salary", fieldnames)
		self.assertIn("paye_tax", fieldnames)
		self.assertIn("housing_levy", fieldnames)
		self.assertIn("shif", fieldnames)

	def test_p10_monthly_tax_return_columns(self):
		columns = p10_columns()
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("tax_id", fieldnames)
		self.assertIn("employee", fieldnames)
		self.assertIn("basic_salary", fieldnames)
		self.assertIn("paye_tax", fieldnames)


class TestReportConditions(unittest.TestCase):
	"""Verify filter conditions are built correctly."""

	def test_sds_no_filters(self):
		self.assertEqual(sds_conditions({}), "")

	def test_sds_all_filters(self):
		cond = sds_conditions({"company": "X", "from_date": "2025-01-01", "to_date": "2025-12-31"})
		self.assertIn("company", cond)
		self.assertIn("start_date", cond)
		self.assertIn("end_date", cond)

	def test_ec_company_filter(self):
		cond = ec_conditions({"company": "X"})
		self.assertIn("company", cond)

	def test_ctc_all_filters(self):
		cond = ctc_conditions({
			"company": "X", "employee": "EMP-001",
			"department": "HR", "from_date": "2025-01-01", "to_date": "2025-12-31",
		})
		self.assertIn("company", cond)
		self.assertIn("employee", cond)
		self.assertIn("department", cond)

	def test_nssf_date_filters(self):
		cond = nssf_conditions({"from_date": "2025-01-01", "to_date": "2025-01-31"})
		self.assertIn("start_date", cond)
		self.assertIn("end_date", cond)

	def test_shif_date_filters(self):
		cond = shif_conditions({"from_date": "2025-01-01", "to_date": "2025-01-31"})
		self.assertIn("start_date", cond)
		self.assertIn("end_date", cond)

	def test_hl_date_filters(self):
		cond = hl_conditions({"from_date": "2025-01-01"})
		self.assertIn("start_date", cond)
		self.assertNotIn("end_date", cond)

	def test_p10_employee_filter(self):
		cond = p10_conditions({"employee": "EMP-001"})
		self.assertIn("employee", cond)

	def test_p10_date_filters(self):
		cond = p10_conditions({"from_date": "2025-01-01", "to_date": "2025-12-31"})
		self.assertIn("posting_date", cond)


class TestP9AEmptyData(unittest.TestCase):
	"""P9A report should return empty when required filters missing."""

	def test_returns_empty_without_employee(self):
		result = p9a_get_data({"fiscal_year": "2025"})
		self.assertEqual(result, [])

	def test_returns_empty_without_fiscal_year(self):
		result = p9a_get_data({"employee": "EMP-001"})
		self.assertEqual(result, [])


if __name__ == "__main__":
	unittest.main()
