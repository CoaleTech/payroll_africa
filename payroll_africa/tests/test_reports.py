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

# Reports that use standard_slip_conditions from utils
from payroll_africa.payroll_africa.report.utils import standard_slip_conditions

# Reports with variable-signature get_columns (require component_names arg)
from payroll_africa.payroll_africa.report.statutory_deductions_summary.statutory_deductions_summary import (
	get_columns as sds_columns,
)
from payroll_africa.payroll_africa.report.employer_contributions.employer_contributions import (
	get_columns as ec_columns,
)

# Reports with own get_conditions and fixed get_columns
from payroll_africa.payroll_africa.report.cost_to_company.cost_to_company import (
	get_columns as ctc_columns, get_conditions as ctc_conditions,
)
from payroll_africa.payroll_africa.report.p10_monthly_tax_return.p10_monthly_tax_return import (
	get_columns as p10_columns, get_conditions as p10_conditions,
)

# Reports with no-arg get_columns that use standard_slip_conditions
from payroll_africa.payroll_africa.report.nssf_remittance.nssf_remittance import (
	get_columns as nssf_columns,
)
from payroll_africa.payroll_africa.report.shif_remittance.shif_remittance import (
	get_columns as shif_columns,
)
from payroll_africa.payroll_africa.report.housing_levy_return.housing_levy_return import (
	get_columns as hl_columns,
	get_data as hl_get_data,
)
from payroll_africa.payroll_africa.report.p9a_tax_deduction_card.p9a_tax_deduction_card import (
	get_columns as p9a_columns, get_data as p9a_get_data,
)
from payroll_africa.payroll_africa.report.mra_p9_deduction_certificate.mra_p9_deduction_certificate import (
	get_data as mra_p9_get_data,
)
from payroll_africa.payroll_africa.report.niger_cnss_remittance.niger_cnss_remittance import (
	get_columns as niger_cnss_columns,
)
from payroll_africa.payroll_africa.report.niger_pit_return.niger_pit_return import (
	get_columns as niger_pit_columns,
)
from payroll_africa.payroll_africa.report.zimbabwe_paye_return.zimbabwe_paye_return import (
	get_columns as zw_paye_columns,
)
from payroll_africa.payroll_africa.report.zimbabwe_nssa_remittance.zimbabwe_nssa_remittance import (
	get_columns as zw_nssa_columns,
)
from payroll_africa.payroll_africa.report.sudan_nsif_remittance.sudan_nsif_remittance import (
	get_columns as sudan_nsif_columns,
)
from payroll_africa.payroll_africa.report.sudan_pit_return.sudan_pit_return import (
	get_columns as sudan_pit_columns,
)
from payroll_africa.payroll_africa.report.south_africa_paye_remittance.south_africa_paye_remittance import (
	get_columns as sa_paye_columns,
)
from payroll_africa.payroll_africa.report.south_africa_uif_remittance.south_africa_uif_remittance import (
	get_columns as sa_uif_columns,
)
from payroll_africa.payroll_africa.report.togo_cnss_remittance.togo_cnss_remittance import (
	get_columns as togo_cnss_columns,
)
from payroll_africa.payroll_africa.report.togo_pit_return.togo_pit_return import (
	get_columns as togo_pit_columns,
)
from payroll_africa.payroll_africa.report.tunisia_cnss_remittance.tunisia_cnss_remittance import (
	get_columns as tunisia_cnss_columns,
)
from payroll_africa.payroll_africa.report.tunisia_irpp_remittance.tunisia_irpp_remittance import (
	get_columns as tunisia_irpp_columns,
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
		# get_columns requires component_names — call with sample set
		columns = sds_columns({"PAYE", "NSSF Employee"})
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("employee", fieldnames)
		self.assertIn("gross_pay", fieldnames)
		self.assertIn("net_pay", fieldnames)
		# Dynamic columns from component_names
		self.assertIn("paye", fieldnames)

	def test_statutory_deductions_summary_empty_components(self):
		# Should still return base columns when no components passed
		columns = sds_columns(set())
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("employee", fieldnames)
		self.assertIn("net_pay", fieldnames)

	def test_employer_contributions_columns(self):
		# get_columns requires component_names
		columns = ec_columns({"NSSF Employer"})
		self._assert_valid_columns(columns)
		fieldnames = [c["fieldname"] for c in columns]
		self.assertIn("total_employer_cost", fieldnames)

	def test_cost_to_company_columns(self):
		columns = ctc_columns(set())
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


class TestStandardSlipConditions(unittest.TestCase):
	"""standard_slip_conditions is shared by sds, ec, nssf, shif, hl reports."""

	def test_no_filters_returns_empty(self):
		self.assertEqual(standard_slip_conditions({}), "")

	def test_company_filter(self):
		cond = standard_slip_conditions({"company": "X"})
		self.assertIn("company", cond)

	def test_date_filters(self):
		cond = standard_slip_conditions({"from_date": "2025-01-01", "to_date": "2025-12-31"})
		self.assertIn("start_date", cond)
		self.assertIn("end_date", cond)

	def test_from_date_only(self):
		cond = standard_slip_conditions({"from_date": "2025-01-01"})
		self.assertIn("start_date", cond)
		self.assertNotIn("end_date", cond)

	def test_all_filters(self):
		cond = standard_slip_conditions({"company": "X", "from_date": "2025-01-01", "to_date": "2025-12-31"})
		self.assertIn("company", cond)
		self.assertIn("start_date", cond)
		self.assertIn("end_date", cond)


class TestCostToCompanyConditions(unittest.TestCase):
	"""cost_to_company has its own get_conditions with extra filters."""

	def test_no_filters(self):
		self.assertEqual(ctc_conditions({}), "")

	def test_all_filters(self):
		cond = ctc_conditions({
			"company": "X", "employee": "EMP-001",
			"department": "HR", "from_date": "2025-01-01", "to_date": "2025-12-31",
		})
		self.assertIn("company", cond)
		self.assertIn("employee", cond)
		self.assertIn("department", cond)
		self.assertIn("start_date", cond)
		self.assertIn("end_date", cond)

	def test_partial_filters(self):
		cond = ctc_conditions({"company": "X", "department": "HR"})
		self.assertIn("company", cond)
		self.assertIn("department", cond)
		self.assertNotIn("start_date", cond)


class TestP10Conditions(unittest.TestCase):
	"""p10 has its own get_conditions with posting_date logic."""

	def test_employee_filter(self):
		cond = p10_conditions({"employee": "EMP-001"})
		self.assertIn("employee", cond)

	def test_date_filters(self):
		cond = p10_conditions({"from_date": "2025-01-01", "to_date": "2025-12-31"})
		self.assertIn("posting_date", cond)

	def test_no_filters(self):
		self.assertEqual(p10_conditions({}), "")


class TestP9AEmptyData(unittest.TestCase):
	"""P9A report should return empty when required filters missing."""

	def test_returns_empty_without_employee(self):
		result = p9a_get_data({"fiscal_year": "2025"})
		self.assertEqual(result, [])

	def test_returns_empty_without_fiscal_year(self):
		result = p9a_get_data({"employee": "EMP-001"})
		self.assertEqual(result, [])


import datetime as _dt_mod


class TestMRAP9MonthDerivation(unittest.TestCase):
	"""MRA P9 Deduction Certificate must iterate months in fiscal-year order.

	Old code had a hard-coded April-March list which made January/February/March
	invisible when the fiscal year started in January (Malawi's standard config).
	"""

	def _month_names_for_fy(self, fy_start_str, fy_end_str):
		"""Return list of month-name strings produced by get_data for a fiscal
		year bounded by ISO date strings.  frappe.db.sql is stubbed empty."""
		fy_mock = MagicMock()
		# getdate = lambda x: x in the mock context: pass real date objects so
		# year_start.year / .month attributes work, and datetime.date objects
		# generated inside get_data compare correctly with year_end.
		fy_mock.year_start_date = _dt_mod.date.fromisoformat(fy_start_str)
		fy_mock.year_end_date   = _dt_mod.date.fromisoformat(fy_end_str)

		import frappe as _frappe
		with patch.object(_frappe, "get_doc", return_value=fy_mock), \
		     patch.object(_frappe.db, "sql", return_value=[]), \
		     patch.object(_frappe.db, "get_value", return_value=0):
			rows = mra_p9_get_data({
				"employee": "EMP-001",
				"fiscal_year": "TEST",
				"company": "TestCo",
			})
		return [r["month"] for r in rows]

	def test_january_december_fiscal_year_produces_jan_to_dec(self):
		months = self._month_names_for_fy("2026-01-01", "2026-12-31")
		self.assertEqual(len(months), 12)
		self.assertEqual(months[0], "January")
		self.assertEqual(months[-1], "December")
		# With the old hard-coded April-March list, April would have been first.
		self.assertEqual(months[3], "April")

	def test_april_march_fiscal_year_produces_apr_to_mar(self):
		months = self._month_names_for_fy("2025-04-01", "2026-03-31")
		self.assertEqual(len(months), 12)
		self.assertEqual(months[0], "April")
		self.assertEqual(months[-1], "March")

	def test_july_june_fiscal_year_produces_jul_to_jun(self):
		months = self._month_names_for_fy("2025-07-01", "2026-06-30")
		self.assertEqual(len(months), 12)
		self.assertEqual(months[0], "July")
		self.assertEqual(months[-1], "June")

	def test_returns_empty_without_employee(self):
		self.assertEqual(mra_p9_get_data({"fiscal_year": "2026"}), [])

	def test_returns_empty_without_fiscal_year(self):
		self.assertEqual(mra_p9_get_data({"employee": "EMP-001"}), [])


class TestHousingLevyDefensiveColumn(unittest.TestCase):
	"""Housing Levy Return must degrade gracefully when national_id column absent.

	The national_id custom field is created by a separate setup step.  Before
	that step runs the report previously raised OperationalError 1054 (unknown
	column).  The fix uses frappe.db.has_column to choose the SQL fragment at
	runtime.
	"""

	_FAKE_ROW = {
		"employee": "EMP-001",
		"employee_name": "Test Employee",
		"gross_pay": 100000,
		"national_id": "",
		"salary_slip": "SAL-001",
	}
	_AMOUNTS = {"SAL-001": {"Housing Levy": 1500, "Employer Housing Levy": 1500}}

	def _run(self, column_exists):
		import frappe as _frappe
		fake_rows = [dict(self._FAKE_ROW)]
		sql_calls = []

		def _capture_sql(query, *args, **kwargs):
			sql_calls.append(query)
			return fake_rows

		with patch.object(_frappe.db, "has_column", return_value=column_exists), \
		     patch.object(_frappe.db, "sql", side_effect=_capture_sql), \
		     patch(
		         "payroll_africa.payroll_africa.report.housing_levy_return"
		         ".housing_levy_return.fetch_component_amounts",
		         return_value=self._AMOUNTS,
		     ):
			rows = hl_get_data({"company": "TestCo", "from_date": "2026-01-01",
			                    "to_date": "2026-01-31"})
		return rows, sql_calls

	def test_returns_data_when_column_absent(self):
		rows, _ = self._run(column_exists=False)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["employee"], "EMP-001")

	def test_levy_totals_when_column_absent(self):
		rows, _ = self._run(column_exists=False)
		self.assertEqual(rows[0]["employee_levy"], 1500)
		self.assertEqual(rows[0]["employer_levy"], 1500)
		self.assertEqual(rows[0]["total_levy"], 3000)


class TestFixedReportColumns(unittest.TestCase):
	"""Column-shape regression tests for reports that received country-filter JS files
	or Python fixes in this patch set.  All get_columns() are no-arg; none hit the DB."""

	def _assert_valid_columns(self, columns):
		self.assertIsInstance(columns, list)
		self.assertGreater(len(columns), 0)
		for col in columns:
			self.assertIn("fieldname", col)
			self.assertIn("label", col)
			self.assertIn("fieldtype", col)
			self.assertIn("width", col)

	# --- Niger ---
	def test_niger_cnss_columns(self):
		cols = niger_cnss_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("gross_pay", fnames)
		self.assertIn("cnss_emp", fnames)
		self.assertIn("cnss_empr", fnames)

	def test_niger_pit_columns(self):
		cols = niger_pit_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("pit", fnames)
		self.assertIn("cnss_emp", fnames)

	# --- Zimbabwe ---
	def test_zimbabwe_paye_columns(self):
		cols = zw_paye_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("paye", fnames)
		self.assertIn("aids_levy", fnames)

	def test_zimbabwe_nssa_columns(self):
		cols = zw_nssa_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("nssa_emp", fnames)
		self.assertIn("nssa_empr", fnames)

	# --- Sudan ---
	def test_sudan_nsif_columns(self):
		cols = sudan_nsif_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("nsif_emp", fnames)
		self.assertIn("nsif_empr", fnames)

	def test_sudan_pit_columns(self):
		cols = sudan_pit_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("pit", fnames)
		self.assertIn("nsif_emp", fnames)

	# --- South Africa ---
	def test_south_africa_paye_columns(self):
		cols = sa_paye_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("component", fnames)
		self.assertIn("amount", fnames)

	def test_south_africa_uif_columns(self):
		cols = sa_uif_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("component", fnames)
		self.assertIn("amount", fnames)

	# --- Togo ---
	def test_togo_cnss_columns(self):
		cols = togo_cnss_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("cnss_emp", fnames)
		self.assertIn("cnss_empr", fnames)

	def test_togo_pit_columns(self):
		cols = togo_pit_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("pit", fnames)
		self.assertIn("cnss_emp", fnames)

	# --- Tunisia ---
	def test_tunisia_cnss_columns_dynamic_rate(self):
		"""Tunisia CNSS column label must reflect cnss_employee_rate from settings or fall back to 9.68."""
		# Mock returns None so fallback 9.68 is used
		_mock_frappe.db.get_value.return_value = None
		cols = tunisia_cnss_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("cnss_employee", fnames)
		self.assertIn("cnss_employer", fnames)
		# Column label must contain the fallback rate
		labels = {c["fieldname"]: c["label"] for c in cols}
		self.assertIn("9.68", labels["cnss_employee"])

	def test_tunisia_cnss_columns_rate_from_settings(self):
		"""When settings row exists with cnss_employee_rate, label reflects it."""
		_mock_frappe.db.get_value.side_effect = lambda dt, name, field: (
			10.0 if field == "cnss_employee_rate" else 17.07
		)
		try:
			cols = tunisia_cnss_columns()
			labels = {c["fieldname"]: c["label"] for c in cols}
			self.assertIn("10.0", labels["cnss_employee"])
		finally:
			_mock_frappe.db.get_value.side_effect = None

	def test_tunisia_irpp_columns(self):
		cols = tunisia_irpp_columns()
		self._assert_valid_columns(cols)
		fnames = [c["fieldname"] for c in cols]
		self.assertIn("employee", fnames)
		self.assertIn("irpp", fnames)
		self.assertIn("professional_deduction", fnames)


if __name__ == "__main__":
	unittest.main()
