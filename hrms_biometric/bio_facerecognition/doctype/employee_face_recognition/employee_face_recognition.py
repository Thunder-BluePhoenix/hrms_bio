# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class EmployeeFaceRecognition(Document):
    def validate(self):
        pass
        # Validate employee ID format
        # if self.employee_id and not self.employee_id.startswith('EMP'):
        #     frappe.throw("Employee ID must start with 'EMP'")
    
    def on_update(self):
        # Trigger face encoding generation after save
        if self.face_image_1 and self.face_image_2 and self.face_image_3:
            frappe.enqueue(
                'hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_face_encoding_on_save',
                doc=self,
                queue='default'
            )