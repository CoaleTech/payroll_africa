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


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_salary_components(doctype, txt, searchfield, start, page_len, filters):
	"""Return salary components excluding those from disabled countries.

	Country suffixes: UG, TZ, RW, BI, ZM, MW, CD, NG, MZ, AO
	Kenya components have no suffix (e.g. "PAYE", "NSSF Employee").
	"""
	disabled_suffixes = filters.get("disabled_suffixes", [])

	# Remove empty string — Kenya filtering is handled separately below
	non_empty_suffixes = [s for s in disabled_suffixes if s]

	if not non_empty_suffixes and "" not in disabled_suffixes:
		# All countries enabled — return all components matching txt
		return frappe.db.sql(
			"""
			SELECT name
			FROM `tabSalary Component`
			WHERE (name LIKE %(txt)s OR salary_component_abbr LIKE %(txt)s)
			ORDER BY name
			LIMIT %(start)s, %(page_len)s
			""",
			{"txt": f"%{txt}%", "start": start, "page_len": page_len},
		)

	# Build exclusion conditions for non-empty suffixes
	# Exclude components whose name ends with " <SUFFIX>"
	suffix_conditions = " AND ".join(
		[f"name NOT LIKE %(suffix_{i}s)s" for i, _ in enumerate(non_empty_suffixes)]
	)

	suffix_params = {
		f"suffix_{i}s": f"% {s}" for i, s in enumerate(non_empty_suffixes)
	}
	suffix_params["txt"] = f"%{txt}%"
	suffix_params["start"] = start
	suffix_params["page_len"] = page_len

	where_clause = "(name LIKE %(txt)s OR salary_component_abbr LIKE %(txt)s)"
	if suffix_conditions:
		where_clause += f" AND ({suffix_conditions})"

	return frappe.db.sql(
		f"""
		SELECT name
		FROM `tabSalary Component`
		WHERE {where_clause}
		ORDER BY name
		LIMIT %(start)s, %(page_len)s
		""",
		suffix_params,
	)
