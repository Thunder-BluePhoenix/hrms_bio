# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class EmployeeAttendance(Document):
    def validate(self):
        # Auto-populate employee details
        if self.employee_id:
            employee = frappe.get_doc("Employee Face Recognition", self.employee_id)
            self.employee_name = employee.employee_name
            self.department = employee.department
    
    def before_submit(self):
        # Calculate total hours if both times are present
        if self.check_in_time and self.check_out_time:
            time_diff = self.check_out_time - self.check_in_time
            self.total_hours = round(time_diff.total_seconds() / 3600, 2)