from frappe import _
from frappe.utils import formatdate

from payroll_africa.payroll_africa.report.utils import fetch_component_amounts, slip_rows


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 120},
		{"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
		{"fieldname": "gross_pay", "label": _("Gross Pay"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "bpf_employee", "label": _("BPF Employee"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "bpf_employer", "label": _("BPF Employer"), "fieldtype": "Currency", "width": 140},
	]


def get_data(filters):
	data = slip_rows(filters, ("employee", "employee_name", "gross_pay", "start_date"))
	data.sort(key=lambda r: (r.employee, r.start_date))

	slip_names = [r.salary_slip for r in data]
	amounts = fetch_component_amounts(slip_names, ["BPF Employee", "BPF Employer"])

	for row in data:
		slip_amounts = amounts.get(row.salary_slip, {})
		row["bpf_employee"] = slip_amounts.get("BPF Employee", 0)
		row["bpf_employer"] = slip_amounts.get("BPF Employer", 0)
		row["month"] = formatdate(row.start_date, "MMM-YYYY")
		del row["salary_slip"]
		del row["start_date"]

	return data
