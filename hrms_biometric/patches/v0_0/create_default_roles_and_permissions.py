# hrms_biometric/patches/v0_0/create_default_roles_and_permissions.py

import frappe
from frappe import _


def execute():
    """Create default roles and permissions for biometric system"""
    try:
        print("🔐 Creating default roles and permissions via patch...")
        
        # Import the setup function from install module
        from hrms_biometric.install.setup import setup_permissions
        setup_permissions()
        
        # Also create any additional biometric-specific roles
        create_biometric_roles()
        
        print("✅ Default roles and permissions created via patch")
            
    except Exception as e:
        frappe.log_error(f"Create roles and permissions patch error: {str(e)}")
        print(f"❌ Create roles and permissions patch failed: {str(e)}")


def create_biometric_roles():
    """Create biometric-specific roles if they don't exist"""
    try:
        # Biometric Administrator role
        if not frappe.db.exists("Role", "Biometric Administrator"):
            role = frappe.new_doc("Role")
            role.role_name = "Biometric Administrator"
            role.desk_access = 1
            role.save(ignore_permissions=True)
            print("✅ Created Biometric Administrator role")
        
        # Biometric Operator role
        if not frappe.db.exists("Role", "Biometric Operator"):
            role = frappe.new_doc("Role")
            role.role_name = "Biometric Operator"
            role.desk_access = 1
            role.save(ignore_permissions=True)
            print("✅ Created Biometric Operator role")
        
        # Attendance Kiosk User role
        if not frappe.db.exists("Role", "Attendance Kiosk User"):
            role = frappe.new_doc("Role")
            role.role_name = "Attendance Kiosk User"
            role.desk_access = 0  # Kiosk users don't need desk access
            role.save(ignore_permissions=True)
            print("✅ Created Attendance Kiosk User role")
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Biometric roles creation error: {str(e)}")
        print(f"⚠️ Warning: Biometric roles creation: {str(e)}")