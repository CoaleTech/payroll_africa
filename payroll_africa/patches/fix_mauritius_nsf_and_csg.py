"""Patch: correct Mauritius NSF ceiling, PRGF rate and seed missing CSG fields.

Changes:
  nsf_ceiling  : 25,475 → 28,570 MUR/month (Budget 2024-25 cap)
  prgf_rate    : 2.5% → 4.5% (current statutory rate)
  csg_high_threshold    : seed to 50,000 MUR/month (new field)
  csg_employee_high_rate: seed to 3% (new field)
  csg_employer_rate     : seed to 3% (new field)
  csg_employer_high_rate: seed to 6% (new field)

CSG fields were set by setup.py but the DocType lacked columns, causing them
to be silently dropped on save. After this patch (and the DocType migration)
they will be persisted correctly.

Only updates NSF/PRGF when values are still at stale defaults.
CSG fields are only seeded when the value is absent/zero (never overwrite).
"""
import frappe


def execute():
    if not frappe.db.exists("DocType", "Mauritius Payroll Settings"):
        return

    updates = {}

    # NSF ceiling
    current_nsf = frappe.db.get_single_value("Mauritius Payroll Settings", "nsf_ceiling")
    if current_nsf is None or float(current_nsf or 0) == 25475.0:
        updates["nsf_ceiling"] = 28570

    # PRGF rate
    current_prgf = frappe.db.get_single_value("Mauritius Payroll Settings", "prgf_rate")
    if current_prgf is None or float(current_prgf or 0) == 2.5:
        updates["prgf_rate"] = 4.5

    # CSG fields — seed only when absent/zero (new columns added by DocType migration)
    csg_fields = {
        "csg_high_threshold": 50000,
        "csg_employee_high_rate": 3,
        "csg_employer_rate": 3,
        "csg_employer_high_rate": 6,
    }
    for field, default_value in csg_fields.items():
        try:
            current = frappe.db.get_single_value("Mauritius Payroll Settings", field)
            if not current or float(current or 0) == 0:
                updates[field] = default_value
        except Exception:
            # Field may not exist yet if migration hasn't run; skip silently
            pass

    if updates:
        for field, value in updates.items():
            try:
                frappe.db.set_single_value("Mauritius Payroll Settings", field, value)
            except Exception:
                pass
        frappe.db.commit()
