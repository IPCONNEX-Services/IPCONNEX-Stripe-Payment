
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document



class StripeSettings(Document):
    def before_save(self, *args, **kwargs):
        if 'secret_key' in self.get_dirty_fields():  
            if frappe.session.user != "Administrator":
                if self.secret_key.strip():  
                    original_value = self.get_original_value('secret_key')
                    self.secret_key = original_value if original_value else self.secret_key
        return super().save(*args, **kwargs)

    def get(self, *args, **kwargs):
        if frappe.session.user == "Administrator" or frappe.local.request_ip.startswith("127.0.0"):
            pass
        else: 	
            self.secret_key = "*"*len(self.secret_key)
        return super().get(*args, **kwargs)
	