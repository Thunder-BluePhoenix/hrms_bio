# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AttendanceKiosk(Document):
    def validate(self):
        # Validate kiosk settings
        if self.is_active and not self.location:
            frappe.throw("Location is required for active kiosks")
    
    def on_update(self):
        # Update kiosk interface when saved
        if self.is_active:
            # Set the HTML interface content
            pass