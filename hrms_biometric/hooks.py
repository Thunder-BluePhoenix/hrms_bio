# hrms_biometric/hooks.py - CORRECTED VERSION

import frappe
from frappe import _

# App configuration
app_name = "hrms_biometric"
app_title = "Hrms Biometric"
app_publisher = "BluePhoenix"
app_description = "Biometrics like face recognition etc"
app_email = "bluephoenix00995@gmail.com"
app_license = "mit"
app_version = "0.0.1"

# Required apps
required_apps = ["frappe"]

# Installation hooks - enable after creating the setup functions
after_install = "hrms_biometric.install.setup.run_complete_setup"

# Document Events - Only use functions that actually exist
doc_events = {
    "Employee Face Recognition": {
        "after_insert": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_face_encoding_on_save",
        "on_update": "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.process_face_encoding_on_save"
    }
}

# Scheduled Tasks - TEMPORARILY DISABLED until cv2 is installed
scheduler_events = {
    # Commented out until dependencies are installed
    # "daily": [
    #     "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.cleanup_old_attendance_images"
    # ],
    # "weekly": [
    #     "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.generate_attendance_reports"
    # ]
}

# Safe scheduled tasks that don't depend on cv2
scheduler_events_safe = {
    "daily": [
        "hrms_biometric.install.setup.cleanup_old_logs"
    ],
    "weekly": [
        "hrms_biometric.install.setup.generate_weekly_summary"
    ]
}

# Permissions
permission_query_conditions = {
    "Employee Face Recognition": "hrms_biometric.permissions.get_employee_face_recognition_permission_query"
}

has_permission = {
    "Employee Face Recognition": "hrms_biometric.permissions.has_employee_face_recognition_permission"
}

# Fixtures for installation
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "in", ["Employee", "User"]]
        ]
    }
]

# Global search
global_search_doctypes = {
    "Employee Face Recognition": 1,
    "Employee Attendance": 1,
    "Attendance Kiosk": 1
}

# User data protection (GDPR compliance)
user_data_fields = [
    {
        "doctype": "Employee Face Recognition",
        "filter_by": "employee_id",
        "redact_fields": ["face_image_1", "face_image_2", "face_image_3", "face_image_4", "face_image_5", "encoding_data"],
        "rename": None
    }
]

# Error handling function for hooks
def safe_hook_call(function_name, *args, **kwargs):
    """Safely call hook functions with error handling"""
    try:
        # Get the function from the module path
        module_path, func_name = function_name.rsplit('.', 1)
        module = frappe.get_module(module_path)
        func = getattr(module, func_name, None)
        
        if func:
            return func(*args, **kwargs)
        else:
            frappe.log_error(f"Hook function not found: {function_name}")
            return None
            
    except Exception as e:
        frappe.log_error(f"Error in hook {function_name}: {str(e)}")
        return None

# Migration helpers
def before_migrate():
    """Run before migration"""
    pass

def after_migrate():
    """Run after migration"""
    # Check if cv2 is available and enable scheduled tasks
    try:
        import cv2
        # If cv2 is available, enable the scheduled tasks
        global scheduler_events
        scheduler_events = {
            "daily": [
                "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.cleanup_old_attendance_images"
            ],
            "weekly": [
                "hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.generate_attendance_reports"
            ]
        }
        print("✅ OpenCV available - biometric scheduled tasks enabled")
    except ImportError:
        print("⚠️ OpenCV not available - biometric scheduled tasks disabled")
        # Use safe scheduled tasks instead
        scheduler_events.update(scheduler_events_safe)

# Enable auto-switch to full functionality when dependencies are available
def check_and_enable_features():
    """Check if all dependencies are available and enable features accordingly"""
    try:
        # Check for cv2
        import cv2
        # Check for face_recognition
        import face_recognition
        # Check for numpy
        import numpy
        
        # All dependencies available - enable full functionality
        return True
        
    except ImportError as e:
        frappe.log_error(f"Missing dependencies: {str(e)}")
        return False

# Boot session
def boot_session(bootinfo):
    """Add information to boot session"""
    try:
        # Add biometric system status to boot info
        bootinfo.biometric_system = {
            "enabled": True,
            "dependencies_available": check_and_enable_features(),
            "app_version": app_version
        }
        
        # Add user permissions
        if frappe.session.user != "Guest":
            user_roles = frappe.get_roles(frappe.session.user)
            bootinfo.biometric_permissions = {
                "can_manage_biometric": any(role in ["System Manager", "HR Manager", "Biometric Administrator"] for role in user_roles),
                "can_operate_kiosk": any(role in ["System Manager", "HR Manager", "HR User", "Biometric Operator"] for role in user_roles),
                "can_view_reports": any(role in ["System Manager", "HR Manager", "HR User"] for role in user_roles)
            }
            
    except Exception as e:
        frappe.log_error(f"Boot session error: {str(e)}")

# Website route rules (for kiosk interface)
website_route_rules = [
    {"from_route": "/biometric-kiosk", "to_route": "biometric_kiosk"},
    {"from_route": "/face-capture", "to_route": "face_capture"}
]

# Jinja methods for templates
jinja = {
    "methods": [
        "hrms_biometric.utils.jinja_methods.get_biometric_status",
        "hrms_biometric.utils.jinja_methods.format_attendance_time"
    ]
}

# Override standard doctypes (when available)
# override_doctype_class = {
#     "Employee": "hrms_biometric.overrides.employee.BiometricEmployee"
# }

# DocType specific JS (when files exist)
# doctype_js = {
#     "Employee": "public/js/employee.js",
#     "Employee Face Recognition": "public/js/employee_face_recognition.js"
# }

# CSS and JS includes (when files exist)
# app_include_css = "/assets/hrms_biometric/css/biometric.css"
# app_include_js = "/assets/hrms_biometric/js/biometric.js"

# Notification config
# notification_config = "hrms_biometric.notifications.get_notification_config"

# Standard search
standard_queries = {
    "Employee Face Recognition": "hrms_biometric.queries.employee_face_recognition_query"
}

# Dashboard data
# dashboards = {
#     "Employee Face Recognition": "hrms_biometric.dashboards.employee_face_recognition"
# }

# Custom modules (when available)
# modules = {
#     "Biometric System": "hrms_biometric.modules.biometric_system"
# }