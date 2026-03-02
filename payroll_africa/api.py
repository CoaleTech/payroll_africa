import frappe
from frappe import _
from frappe.utils import flt

from payroll_africa.engine.registry import get_calculator, _country_map


@frappe.whitelist()
def calculate_deductions(country, gross_pay, basic_pay=None):
	"""Calculate statutory deductions for a country without creating a Salary Slip.

	Args:
		country: Country name (e.g. "Kenya", "Uganda")
		gross_pay: Monthly gross pay amount
		basic_pay: Monthly basic pay (defaults to gross_pay if not provided)

	Returns:
		dict with deductions list and totals
	"""
	gross_pay = flt(gross_pay)
	basic_pay = flt(basic_pay) if basic_pay else gross_pay

	if country not in _country_map:
		frappe.throw(
			_("Country {0} is not supported. Supported countries: {1}").format(
				country, ", ".join(sorted(_country_map.keys()))
			)
		)

	calculator = get_calculator(country)
	if not calculator:
		frappe.throw(_("Payroll settings not found for {0}").format(country))

	# Create a minimal mock that satisfies calculator.compute()
	mock_slip = frappe._dict({
		"gross_pay": gross_pay,
		"earnings": [
			frappe._dict({"salary_component": "Basic Salary", "amount": basic_pay})
		],
	})

	results = calculator.compute(mock_slip)

	deductions = []
	employee_total = 0
	employer_total = 0

	for component, data in results.items():
		amount = flt(data["amount"], 2)
		deductions.append({
			"component": component,
			"amount": amount,
			"is_employer_only": data["is_employer_only"],
		})
		if data["is_employer_only"]:
			employer_total += amount
		else:
			employee_total += amount

	return {
		"country": country,
		"gross_pay": gross_pay,
		"basic_pay": basic_pay,
		"deductions": deductions,
		"employee_total": flt(employee_total, 2),
		"employer_total": flt(employer_total, 2),
		"net_pay": flt(gross_pay - employee_total, 2),
		"cost_to_company": flt(gross_pay + employer_total, 2),
	}


@frappe.whitelist()
def get_supported_countries():
	"""Return list of supported countries."""
	return sorted(_country_map.keys())


@frappe.whitelist()
def recalculate_salary_slips(country, from_date, to_date, company=None):
	"""Recalculate statutory deductions on draft Salary Slips.

	Use after updating statutory rates to apply new rates to existing drafts.

	Args:
		country: Country name to filter employees
		from_date: Start of posting date range
		to_date: End of posting date range
		company: Optional company filter

	Returns:
		dict with count of updated slips
	"""
	filters = {
		"docstatus": 0,
		"posting_date": ["between", [from_date, to_date]],
	}
	if company:
		filters["company"] = company

	# Get employees belonging to this country
	employee_filters = {"payroll_country": country}
	if company:
		employee_filters["company"] = company
	employees = frappe.get_all("Employee", filters=employee_filters, pluck="name")

	if not employees:
		# Fall back to company country
		if company:
			company_country = frappe.db.get_value("Company", company, "country")
			if company_country == country:
				employees = frappe.get_all(
					"Employee",
					filters={"company": company, "payroll_country": ["in", ["", None]]},
					pluck="name",
				)

	if not employees:
		return {"updated": 0, "message": _("No employees found for {0}").format(country)}

	filters["employee"] = ["in", employees]
	slips = frappe.get_all("Salary Slip", filters=filters, pluck="name")

	updated = 0
	for slip_name in slips:
		slip = frappe.get_doc("Salary Slip", slip_name)
		slip.flags.ignore_permissions = True
		slip.save()
		updated += 1

	if updated:
		frappe.db.commit()

	return {
		"updated": updated,
		"message": _("{0} salary slip(s) recalculated for {1}").format(updated, country),
	}
