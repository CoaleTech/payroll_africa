import unittest

from payroll_africa.engine.payroll_entry import summarise


def _d(parent, component, amount, parentfield="deductions", dn=0, stat=0):
	return {
		"parent": parent, "parentfield": parentfield, "salary_component": component,
		"amount": amount, "do_not_include_in_total": dn, "statistical_component": stat,
	}


class TestSummarise(unittest.TestCase):
	def test_columns_and_net_reconcile(self):
		slips = [{"name": "S1", "employee": "E1", "gross_pay": 100000, "net_pay": 66000}]
		details = [
			_d("S1", "PAYE", 20000),
			_d("S1", "Employee NSSF", 6000),
			_d("S1", "SHA", 2750),
			_d("S1", "Housing Levy", 1500),
			_d("S1", "Helb", 3750),
			_d("S1", "NITA", 50, dn=1),
			_d("S1", "Employer NSSF", 6000, dn=1),
			_d("S1", "PAYEBand1", 24000, dn=1, stat=1),
		]
		t = summarise(slips, details)["E1"]
		self.assertEqual(
			(t["pa_paye"], t["pa_nssf"], t["pa_sha"], t["pa_nita"], t["pa_other_deductions"]),
			(20000, 6000, 2750, 50, 5250),
		)
		# NITA is employer-borne, so it must not enter the gross - deductions = net arithmetic.
		self.assertEqual(
			t["pa_gross_pay"] - t["pa_paye"] - t["pa_nssf"] - t["pa_sha"] - t["pa_other_deductions"],
			t["pa_net_pay"],
		)

	def test_country_suffix_and_payroll_africa_names(self):
		slips = [{"name": "S1", "employee": "E1", "gross_pay": 10, "net_pay": 7}]
		details = [_d("S1", "PAYE TZ", 1), _d("S1", "NSSF Employee UG", 1), _d("S1", "SHIF", 1)]
		t = summarise(slips, details)["E1"]
		self.assertEqual((t["pa_paye"], t["pa_nssf"], t["pa_sha"], t["pa_other_deductions"]), (1, 1, 1, 0))

	def test_other_countries_pension_and_health_land_in_nssf_and_sha(self):
		slips = [{"name": "S1", "employee": "E1", "gross_pay": 100, "net_pay": 60}]
		details = [
			_d("S1", "Pension Employee MW", 5), _d("S1", "INSS Employee BI", 4), _d("S1", "NAPSA Employee ZM", 3),
			_d("S1", "Health Insurance Employee BI", 2), _d("S1", "CBHI RW", 1), _d("S1", "NHIMA Employee ZM", 1),
			_d("S1", "Training Fund Employee BI", 7), _d("S1", "Maternity Employee RW", 6),
			_d("S1", "Pension Employer MW", 50, dn=1, stat=1), _d("S1", "WCF", 9, dn=1, stat=1),
		]
		t = summarise(slips, details)["E1"]
		self.assertEqual((t["pa_nssf"], t["pa_sha"], t["pa_other_deductions"], t["pa_nita"]), (12, 4, 13, 0))

	def test_employer_contributions_table_only_feeds_nita(self):
		slips = [{"name": "S1", "employee": "E1", "gross_pay": 10, "net_pay": 10}]
		details = [_d("S1", "NITA", 50, parentfield="employer_contributions"), _d("S1", "NSSF Employer", 9, parentfield="employer_contributions")]
		t = summarise(slips, details)["E1"]
		self.assertEqual((t["pa_nita"], t["pa_nssf"], t["pa_other_deductions"]), (50, 0, 0))

	def test_two_slips_for_one_employee_add_up(self):
		slips = [
			{"name": "S1", "employee": "E1", "gross_pay": 10, "net_pay": 8},
			{"name": "S2", "employee": "E1", "gross_pay": 5, "net_pay": 4},
		]
		t = summarise(slips, [_d("S1", "PAYE", 2), _d("S2", "PAYE", 1)])["E1"]
		self.assertEqual((t["pa_gross_pay"], t["pa_paye"], t["pa_net_pay"]), (15, 3, 12))
