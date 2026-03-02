import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	data, component_names = get_data(filters)
	columns = get_columns(component_names)
	return columns, data


def get_columns(component_names):
	columns = [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 120},
	]

	for name in sorted(component_names):
		fieldname = name.lower().replace(" ", "_")
		columns.append({
			"fieldname": fieldname,
			"label": _(name),
			"fieldtype": "Currency",
			"width": 130,
		})

	columns.append(
		{"fieldname": "net_pay", "label": _("Net Pay"), "fieldtype": "Currency", "width": 120},
	)

	return columns


def get_data(filters):
	conditions = get_conditions(filters)

	salary_slips = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.gross_pay, ss.net_pay,
			ss.name as salary_slip
		FROM `tabSalary Slip` ss
		WHERE ss.docstatus = 1 {conditions}
		ORDER BY ss.employee
		""".format(conditions=conditions),
		filters,
		as_dict=True,
	)

	if not salary_slips:
		return [], set()

	slip_names = [s.salary_slip for s in salary_slips]

	# Get all non-statistical deduction components across all slips
	details = frappe.db.sql(
		"""
		SELECT parent, salary_component, amount
		FROM `tabSalary Detail`
		WHERE parent IN %s
			AND parentfield = 'deductions'
			AND (statistical_component = 0 OR statistical_component IS NULL)
		""",
		(slip_names,),
		as_dict=True,
	)

	# Collect unique component names
	component_names = set()
	slip_details = {}
	for d in details:
		component_names.add(d.salary_component)
		slip_details.setdefault(d.parent, []).append(d)

	# Populate each slip with component amounts
	for slip in salary_slips:
		for detail in slip_details.get(slip.salary_slip, []):
			fieldname = detail.salary_component.lower().replace(" ", "_")
			slip[fieldname] = flt(detail.amount)
		del slip["salary_slip"]

	return salary_slips, component_names


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("from_date"):
		conditions += " AND ss.start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.end_date <= %(to_date)s"
	return conditions
