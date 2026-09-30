import frappe
from frappe.model.document import Document

from payroll_africa.boot import BOOT_CACHE_KEY, COUNTRY_FIELD_MAP
from payroll_africa.setup import reconcile_countries


class PayrollAfricaSettings(Document):
	def on_update(self):
		before = self.get_doc_before_save()
		if not self.flags.skip_reconcile and (
			before is None or any(before.get(f) != self.get(f) for f in COUNTRY_FIELD_MAP.values())
		):
			reconcile_countries()
		frappe.cache.delete_value(BOOT_CACHE_KEY)
		# Scope to current user — sidebar will also refresh on next boot for all users
		frappe.publish_realtime(
			"payroll_africa_settings_updated",
			user=frappe.session.user,
			after_commit=True,
		)
		frappe.clear_cache()
