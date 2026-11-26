import frappe
from frappe.utils import flt, getdate


def _in_period(query, ss, filters):
	"""Company and start/end date filters shared by the Salary Slip reports."""
	if filters.get("company"):
		query = query.where(ss.company == filters["company"])
	if filters.get("from_date"):
		query = query.where(ss.start_date >= filters["from_date"])
	if filters.get("to_date"):
		query = query.where(ss.end_date <= filters["to_date"])
	return query


def slip_rows(filters, slip_fields=("employee", "employee_name", "gross_pay"), employee_fields=(), extra=None):
	"""Submitted Salary Slips in the company / date range, ordered by employee; each row carries `salary_slip`.
	`employee_fields` are joined from Employee. `extra` maps Salary Slip fields to equality filters; empty values are ignored.
	"""
	ss = frappe.qb.DocType("Salary Slip")
	query = (
		frappe.qb.from_(ss)
		.select(*(ss[f] for f in slip_fields), ss.name.as_("salary_slip"))
		.where(ss.docstatus == 1)
		.orderby(ss.employee)
	)
	if employee_fields:
		emp = frappe.qb.DocType("Employee")
		query = query.left_join(emp).on(ss.employee == emp.name).select(*(emp[f] for f in employee_fields))
	query = _in_period(query, ss, filters)
	for field, value in (extra or {}).items():
		if value:
			query = query.where(ss[field] == value)
	return query.run(as_dict=True)


def component_lines(filters, components):
	"""One row per employee, month (`YYYY-MM` of the slip end date) and matching deduction component."""
	ss = frappe.qb.DocType("Salary Slip")
	sd = frappe.qb.DocType("Salary Detail")
	query = (
		frappe.qb.from_(ss)
		.inner_join(sd)
		.on(sd.parent == ss.name)
		.select(ss.employee, ss.employee_name, sd.salary_component.as_("component"), sd.amount, ss.end_date)
		.where(ss.docstatus == 1)
		.where(sd.parentfield == "deductions")
		.where(sd.salary_component.isin(list(components)))
		.orderby(ss.end_date)
		.orderby(ss.employee)
		.orderby(sd.salary_component)
	)
	rows = _in_period(query, ss, filters).run(as_dict=True)
	for row in rows:
		row["amount"] = flt(row.amount)
		row["month"] = getdate(row.pop("end_date")).strftime("%Y-%m")
	return rows


def deduction_details(slip_names, statistical=None):
	"""Salary Detail rows of the `deductions` table for the given slips.
	`statistical`: True = employer-borne (statistical) rows only, False = employee-borne only, None = all.
	"""
	sd = frappe.qb.DocType("Salary Detail")
	query = (
		frappe.qb.from_(sd)
		.select(sd.parent, sd.salary_component, sd.amount, sd.statistical_component)
		.where(sd.parent.isin(slip_names))
		.where(sd.parentfield == "deductions")
	)
	if statistical is True:
		query = query.where(sd.statistical_component == 1)
	elif statistical is False:
		query = query.where((sd.statistical_component == 0) | sd.statistical_component.isnull())
	return query.run(as_dict=True)


def fetch_component_amounts(slip_names, components, parentfield=("deductions", "employer_contributions")):
	"""Batch-fetch Salary Detail amounts for salary slips and components.
	`parentfield` is one table name or a tuple (employer components live in employer_contributions).
	Returns: {slip_name: {component_name: amount}}
	"""
	if not slip_names or not components:
		return {}

	sd = frappe.qb.DocType("Salary Detail")
	rows = (
		frappe.qb.from_(sd)
		.select(sd.parent, sd.salary_component, sd.amount)
		.where(sd.parent.isin(slip_names))
		.where(sd.salary_component.isin(components))
		.where(sd.parentfield.isin([parentfield] if isinstance(parentfield, str) else list(parentfield)))
	).run(as_dict=True)

	result = {}
	for row in rows:
		result.setdefault(row.parent, {})[row.salary_component] = flt(row.amount)
	return result
