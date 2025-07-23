# hrms_biometric/patches/v0_0/initial_setup.py

import frappe
from frappe import _


def execute():
    """Initial setup patch for HRMS Biometric app"""
    try:
        print("🔧 Running initial setup patch...")
        
        # Create necessary database indexes for performance
        create_database_indexes()
        
        # Setup initial configuration
        setup_initial_config()
        
        # Create default workflow states if needed
        create_workflow_states()
        
        print("✅ Initial setup patch completed successfully")
        
    except Exception as e:
        frappe.log_error(f"Initial setup patch error: {str(e)}")
        print(f"❌ Initial setup patch failed: {str(e)}")


def create_database_indexes():
    """Create database indexes for better performance"""
    try:
        # Index for Employee Face Recognition
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_face_recognition_employee 
                ON `tabEmployee Face Recognition` (employee)
            """)
            
            frappe.db.sql("""
                CREATE INDEX IF NOT EXISTS idx_face_recognition_status 
                ON `tabEmployee Face Recognition` (status, employee)
            """)
        
        # Index for Employee Attendance (if we modify it)
        frappe.db.sql("""
            CREATE INDEX IF NOT EXISTS idx_attendance_employee_date 
            ON `tabEmployee Attendance` (employee, attendance_date)
        """)
        
        frappe.db.sql("""
            CREATE INDEX IF NOT EXISTS idx_attendance_date_status 
            ON `tabEmployee Attendance` (attendance_date, status)
        """)
        
        print("✅ Database indexes created")
        
    except Exception as e:
        frappe.log_error(f"Database index creation error: {str(e)}")
        print(f"⚠️ Database index creation warning: {str(e)}")


def setup_initial_config():
    """Setup initial configuration values"""
    try:
        # Set default system configuration
        frappe.db.set_default("biometric_app_initialized", "1")
        frappe.db.set_default("biometric_version", "0.0.1")
        
        # Set default recognition parameters
        frappe.db.set_default("default_recognition_tolerance", "0.4")
        frappe.db.set_default("default_confidence_threshold", "70.0")
        
        print("✅ Initial configuration set")
        
    except Exception as e:
        frappe.log_error(f"Initial config error: {str(e)}")
        print(f"⚠️ Initial config warning: {str(e)}")


def create_workflow_states():
    """Create workflow states for face recognition approval process"""
    try:
        # Create workflow states for Employee Face Recognition
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            
            # Pending state
            if not frappe.db.exists("Workflow State", "Face Recognition Pending"):
                pending_state = frappe.new_doc("Workflow State")
                pending_state.workflow_state_name = "Face Recognition Pending"
                pending_state.style = "Warning"
                pending_state.save(ignore_permissions=True)
            
            # Approved state
            if not frappe.db.exists("Workflow State", "Face Recognition Approved"):
                approved_state = frappe.new_doc("Workflow State")
                approved_state.workflow_state_name = "Face Recognition Approved"
                approved_state.style = "Success"
                approved_state.save(ignore_permissions=True)
            
            # Rejected state
            if not frappe.db.exists("Workflow State", "Face Recognition Rejected"):
                rejected_state = frappe.new_doc("Workflow State")
                rejected_state.workflow_state_name = "Face Recognition Rejected"
                rejected_state.style = "Danger"
                rejected_state.save(ignore_permissions=True)
        
        print("✅ Workflow states created")
        
    except Exception as e:
        frappe.log_error(f"Workflow states creation error: {str(e)}")
        print(f"⚠️ Workflow states warning: {str(e)}")


def cleanup_old_data():
    """Cleanup any old or invalid data"""
    try:
        # Remove any orphaned face recognition records
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            frappe.db.sql("""
                DELETE FROM `tabEmployee Face Recognition` 
                WHERE employee NOT IN (SELECT name FROM `tabEmployee`)
            """)
        
        # Clean up old attendance images if any
        frappe.db.sql("""
            DELETE FROM `tabFile` 
            WHERE file_name LIKE '%attendance_temp_%' 
            AND creation < DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        
        print("✅ Old data cleanup completed")
        
    except Exception as e:
        frappe.log_error(f"Data cleanup error: {str(e)}")
        print(f"⚠️ Data cleanup warning: {str(e)}")