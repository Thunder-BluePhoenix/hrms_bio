# hrms_biometric/patches/v0_0/setup_custom_fields.py

import frappe
from frappe import _


def execute():
    """Setup custom fields for Employee doctype"""
    try:
        print("📝 Setting up custom fields via patch...")
        
        # Import the setup function from install module
        from hrms_biometric.install.setup import setup_custom_fields
        setup_custom_fields()
        
        print("✅ Custom fields setup completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Setup custom fields patch error: {str(e)}")
        print(f"❌ Setup custom fields patch failed: {str(e)}")