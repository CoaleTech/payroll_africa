import frappe


def execute():
	"""Fix Custom Field names that conflict during fixture sync.

	The p10a_tax_deduction_card_type field may exist with a mismatched name
	(e.g., custom_ prefix) causing fixture import to fail with duplicate fieldname error.
	"""
	expected = {
		"p10a_tax_deduction_card_type": "Salary Component-p10a_tax_deduction_card_type",
		"p9a_tax_deduction_card_type": "Salary Component-p9a_tax_deduction_card_type",
		"payroll_africa_section": "Salary Component-payroll_africa_section",
		"payroll_country": "Employee-payroll_country",
	}

	for fieldname, expected_name in expected.items():
		dt = expected_name.split("-")[0]
		# Find any Custom Field with this fieldname on the target doctype
		existing = frappe.db.get_all(
			"Custom Field",
			filters={"dt": dt, "fieldname": fieldname},
			pluck="name",
		)
		for name in existing:
			if name != expected_name:
				frappe.db.sql(
					"UPDATE `tabCustom Field` SET `name`=%s WHERE `name`=%s",
					(expected_name, name),
				)
				frappe.db.commit()
