import frappe


def execute():
	"""Work Injury Insurance: clear wrongly-set statistical_component and do_not_include_in_total.

	setup_cabo_verde previously set statistical_component=1 and do_not_include_in_total=1 on the
	shared 'Work Injury Insurance' component.  This causes the component to be invisible in net pay
	for Guinea (which also uses Work Injury Insurance as a real employer cost line).  Clear both
	flags; the engine already appends employer-only components with those row-level flags at slip
	time, so marking the component itself as statistical is redundant and harmful.
	"""
	if not frappe.db.exists("Salary Component", "Work Injury Insurance"):
		return

	current = frappe.db.get_value(
		"Salary Component",
		"Work Injury Insurance",
		["statistical_component", "do_not_include_in_total"],
		as_dict=True,
	)
	# Only correct if still in the wrong state; do not clobber deliberate user changes.
	if current.get("statistical_component") or current.get("do_not_include_in_total"):
		frappe.db.set_value(
			"Salary Component",
			"Work Injury Insurance",
			{
				"statistical_component": 0,
				"do_not_include_in_total": 0,
			},
		)
