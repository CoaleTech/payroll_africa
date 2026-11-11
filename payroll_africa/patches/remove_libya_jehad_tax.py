"""Patch: remove Jehad Tax from the Libya salary structure template.

The Jehad Tax was abolished in Libya effective 14 July 2025 (EY Tax News
Update 2025-1651 "Libya cancels Jihad Tax"; confirmed by Orbitax).

Action: remove the "Jehad Tax" component row from the "Libya Payroll Template"
salary structure ONLY if no submitted salary slip in that structure uses it.
If submitted slips do use it, skip silently (historical data is preserved;
the calculator no longer computes it for new slips).

Does NOT delete the salary component record so that submitted slips that
pre-date July 2025 remain intact.
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Salary Structure"):
        return
    if not frappe.db.exists("Salary Structure", "Libya Payroll Template"):
        return

    # Check whether any submitted slip under this structure has the Jehad Tax component.
    submitted_with_jehad = frappe.db.sql(
        """
        SELECT COUNT(*) FROM `tabSalary Detail` sd
        JOIN `tabSalary Slip` ss ON ss.name = sd.parent
        WHERE ss.docstatus = 1
          AND ss.salary_structure = 'Libya Payroll Template'
          AND sd.salary_component = 'Jehad Tax'
        """,
        as_list=True,
    )
    if submitted_with_jehad and int(submitted_with_jehad[0][0]) > 0:
        # Historical submitted slips reference it — skip; calculator already
        # does not compute it for new slips so no new rows will be generated.
        return

    # Safe to remove from the template.
    frappe.db.delete(
        "Salary Detail",
        {
            "parent": "Libya Payroll Template",
            "parenttype": "Salary Structure",
            "salary_component": "Jehad Tax",
        },
    )
    frappe.db.commit()
