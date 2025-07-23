# hrms_biometric/patches/v0_0/create_default_settings.py

import frappe
from frappe import _


def execute():
    """Create default settings for Face Recognition"""
    try:
        print("⚙️ Creating default Face Recognition Settings...")
        
        if not frappe.db.exists("Face Recognition Settings", "Face Recognition Settings"):
            # Import the setup function from install module
            from hrms_biometric.install.setup import create_default_settings
            create_default_settings()
            print("✅ Default Face Recognition Settings created via patch")
        else:
            print("ℹ️ Face Recognition Settings already exist, skipping...")
            
    except Exception as e:
        frappe.log_error(f"Create default settings patch error: {str(e)}")
        print(f"❌ Create default settings patch failed: {str(e)}")