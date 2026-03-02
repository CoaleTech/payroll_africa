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
		{"fieldname": "department", "label": _("Department"), "fieldtype": "Link", "options": "Department", "width": 140},
		{"fieldname": "designation", "label": _("Designation"), "fieldtype": "Link", "options": "Designation", "width": 140},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "employee_deductions", "label": _("Employee Deductions"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "net_pay", "label": _("Net Pay"), "fieldtype": "Currency", "width": 120},
	]

	for name in sorted(component_names):
		fieldname = name.lower().replace(" ", "_")
		columns.append({
			"fieldname": fieldname,
			"label": _(name),
			"fieldtype": "Currency",
			"width": 140,
		})

	columns.extend([
		{"fieldname": "total_employer_contributions", "label": _("Total Employer Contributions"), "fieldtype": "Currency", "width": 170},
		{"fieldname": "cost_to_company", "label": _("Cost to Company"), "fieldtype": "Currency", "width": 140},
	])

	return columns


def get_data(filters):
	conditions = get_conditions(filters)

	salary_slips = frappe.db.sql(
		"""
		SELECT
			ss.employee, ss.employee_name, ss.department, ss.designation,
			ss.gross_pay, ss.total_deduction, ss.net_pay,
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

	# Get all deduction details in one query
	details = frappe.db.sql(
		"""
		SELECT parent, salary_component, amount, statistical_component
		FROM `tabSalary Detail`
		WHERE parent IN %s AND parentfield = 'deductions'
		""",
		(slip_names,),
		as_dict=True,
	)

	# Group by parent
	employer_component_names = set()
	slip_details = {}
	for d in details:
		slip_details.setdefault(d.parent, []).append(d)
		if d.statistical_component:
			employer_component_names.add(d.salary_component)

	for slip in salary_slips:
		total_employer = 0
		employee_deductions = 0

		for detail in slip_details.get(slip.salary_slip, []):
			if detail.statistical_component:
				fieldname = detail.salary_component.lower().replace(" ", "_")
				slip[fieldname] = flt(detail.amount)
				total_employer += flt(detail.amount)
			else:
				employee_deductions += flt(detail.amount)

		slip["employee_deductions"] = employee_deductions
		slip["total_employer_contributions"] = total_employer
		slip["cost_to_company"] = flt(slip.gross_pay) + total_employer
		del slip["salary_slip"]

	return salary_slips, employer_component_names


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND ss.company = %(company)s"
	if filters.get("employee"):
		conditions += " AND ss.employee = %(employee)s"
	if filters.get("department"):
		conditions += " AND ss.department = %(department)s"
	if filters.get("from_date"):
		conditions += " AND ss.start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND ss.end_date <= %(to_date)s"
	return conditions
