# hrms_biometric/hrms_biometric/hooks.py

import frappe
from frappe import _

# App configuration - Keep existing values
app_name = "hrms_biometric"
app_title = "Hrms Biometric"
app_publisher = "BluePhoenix"
app_description = "Biometrics like face recognition etc"
app_email = "bluephoenix00995@gmail.com"
app_license = "mit"
app_version = "0.0.1"

# Required apps (minimal for compatibility)
required_apps = ["frappe"]

# Installation hooks (safe fallback if functions don't exist)
# after_install = "hrms_biometric.install.setup.run_complete_setup"

# Includes in <head> (only if files exist)
# app_include_css = "/assets/hrms_biometric/css/biometric.css"
# app_include_js = "/assets/hrms_biometric/js/biometric.js"

# Document Events - Only use existing functions
doc_events = {
    # Employee Face Recognition events - these exist in your code
    "Employee Face Recognition": {
        "after_insert": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_face_encoding_on_save",
        "on_update": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_face_encoding_on_save"
    },
    
    # Employee Attendance events - using existing function where possible
    "Employee Attendance": {
        # Only add if these functions exist in your enhanced_face_recognition.py
        # "before_save": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.calculate_working_hours",
        # "on_submit": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.finalize_attendance_record"
    }
}

# Scheduled Tasks - Only use existing functions
scheduler_events = {
    # Daily tasks - keep existing
    "daily": [
        "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.cleanup_old_attendance_images"
    ],
    
    # Weekly tasks - keep existing  
    "weekly": [
        "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.generate_attendance_reports"
    ],
    
    # Add new tasks only if functions exist
    # "hourly": [
    #     "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_attendance_notifications"
    # ],
    
    # "monthly": [
    #     "hrms_biometric.bio_facerecognition.api.payroll_integration.generate_monthly_payroll"
    # ]
}

# Permissions - basic setup
permission_query_conditions = {
    "Employee Face Recognition": "hrms_biometric.permissions.get_employee_face_recognition_permission_query",
    "Employee Attendance": "hrms_biometric.permissions.get_employee_attendance_permission_query"
}

# Basic permission check
has_permission = {
    "Employee Face Recognition": "hrms_biometric.permissions.has_employee_face_recognition_permission",
    "Employee Attendance": "hrms_biometric.permissions.has_employee_attendance_permission"
}

# Fixtures for installation - safe defaults
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "in", ["Employee", "User"]]
        ]
    },
    "Face Recognition Settings"
]

# Website route rules (only if you need them)
# website_route_rules = [
#     {"from_route": "/biometric-kiosk/<path:path>", "to_route": "biometric_kiosk"}
# ]

# Jinja methods (only if you create these functions)
# jinja = {
#     "methods": [
#         "hrms_biometric.utils.jinja_methods.get_biometric_data"
#     ]
# }

# DocType JS includes (only for existing files)
# doctype_js = {
#     "Employee Face Recognition": "public/js/employee_face_recognition.js"
# }

# Override doctype classes (only if you create these)
# override_doctype_class = {
#     "Employee": "hrms_biometric.overrides.employee.BiometricEmployee"
# }

# Global search (safe to add)
global_search_doctypes = {
    "Employee Face Recognition": 1,
    "Employee Attendance": 1,
    "Attendance Kiosk": 1
}

# Boot session (only if function exists)
# boot_session = "hrms_biometric.boot.get_boot_session_info"

# User data protection (GDPR compliance)
user_data_fields = [
    {
        "doctype": "Employee Face Recognition",
        "filter_by": "employee_id", 
        "redact_fields": ["face_image_1", "face_image_2", "face_image_3", "face_image_4", "face_image_5", "encoding_data"],
        "partial": 1
    },
    {
        "doctype": "Employee Attendance",
        "filter_by": "employee_id",
        "redact_fields": ["face_image_captured"],
        "partial": 1
    }
]

# Auto-cancel exempted doctypes
auto_cancel_exempted_doctypes = [
    "Employee Face Recognition"
]

# Log clearing
default_log_clearing_doctypes = {
    "Notification Activity Log": 90,
    "Multi Location Sync Log": 60, 
    "Attendance Conflict Log": 180
}

# Error tracking hooks (basic)
# on_session_creation = [
#     "hrms_biometric.utils.session.setup_biometric_session"
# ]

# Request hooks (only if you create these functions)
# before_request = [
#     "hrms_biometric.utils.request_handler.log_api_requests"
# ]

# Job hooks (only if you create these functions)  
# before_job = [
#     "hrms_biometric.utils.job_handler.setup_job_context"
# ]

# Regional settings
# regional_overrides = {
#     "India": {
#         "hrms_biometric.regional.india.setup"
#     }
# }

# Commands (only if you create these)
# commands = [
#     "hrms_biometric.commands.setup_biometric_system"
# ]

# =======================
# SAFE FUNCTION HELPERS
# =======================

def safe_import_and_call(module_path, function_name, *args, **kwargs):
    """
    Safely import and call a function, with fallback if it doesn't exist
    """
    try:
        module = frappe.get_module(module_path)
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            return func(*args, **kwargs)
        else:
            frappe.log_error(f"Function {function_name} not found in {module_path}")
            return None
    except ImportError:
        frappe.log_error(f"Module {module_path} not found")
        return None
    except Exception as e:
        frappe.log_error(f"Error calling {module_path}.{function_name}: {str(e)}")
        return None

# =======================
# PROGRESSIVE ENHANCEMENT
# =======================
# Uncomment sections below as you implement the corresponding functions

# Additional doc_events you can enable as you implement functions:
"""
"Employee Face Recognition": {
    "before_insert": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.validate_employee_before_insert",
    "before_save": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.validate_face_images", 
    "before_submit": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.validate_before_submit",
    "on_submit": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.create_notification_settings",
    "on_trash": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.cleanup_on_delete"
},

"Employee Attendance": {
    "before_insert": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.validate_attendance_before_insert",
    "after_insert": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.trigger_notifications_on_attendance",
    "before_save": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.calculate_working_hours",
    "before_submit": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.validate_attendance_before_submit",
    "on_submit": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.finalize_attendance_record"
},

"Attendance Kiosk": {
    "before_save": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.validate_kiosk_settings",
    "after_insert": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.setup_kiosk_interface"
}
"""

# Additional scheduler_events you can enable:
"""
"hourly": [
    "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_attendance_notifications",
    "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.check_missed_checkouts"
],

"monthly": [
    "hrms_biometric.bio_facerecognition.api.payroll_integration.generate_monthly_payroll",
    "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.archive_old_data"
],

"cron": {
    "*/10 * * * *": [
        "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_pending_recognitions"
    ]
}
"""