from frappe import _
from frappe.utils import flt

from payroll_africa.payroll_africa.report.utils import deduction_details, slip_rows


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
			"width": 140,
		})

	columns.append(
		{"fieldname": "total_employer_cost", "label": _("Total Employer Cost"), "fieldtype": "Currency", "width": 150},
	)

	return columns


def get_data(filters):
	salary_slips = slip_rows(filters, ("employee", "employee_name", "gross_pay"))

	if not salary_slips:
		return [], set()

	slip_names = [s.salary_slip for s in salary_slips]

	details = deduction_details(slip_names, statistical=True)

	component_names = set()
	slip_details = {}
	for d in details:
		component_names.add(d.salary_component)
		slip_details.setdefault(d.parent, []).append(d)

	for slip in salary_slips:
		total = 0
		for detail in slip_details.get(slip.salary_slip, []):
			fieldname = detail.salary_component.lower().replace(" ", "_")
			slip[fieldname] = flt(detail.amount)
			total += flt(detail.amount)
		slip["total_employer_cost"] = total
		del slip["salary_slip"]

	return salary_slips, component_names
