import frappe
from frappe.model.document import Document

from payroll_africa.boot import BOOT_CACHE_KEY


class PayrollAfricaSettings(Document):
	def on_update(self):
		frappe.cache.delete_value(BOOT_CACHE_KEY)
		# Scope to current user — sidebar will also refresh on next boot for all users
		frappe.publish_realtime(
			"payroll_africa_settings_updated",
			user=frappe.session.user,
			after_commit=True,
		)
		frappe.clear_cache()
