import frappe
from frappe.model.document import Document

from payroll_africa.boot import BOOT_CACHE_KEY


class PayrollAfricaSettings(Document):
	def on_update(self):
		frappe.cache().delete_value(BOOT_CACHE_KEY)
		frappe.publish_realtime("payroll_africa_settings_updated")
		frappe.clear_cache()
