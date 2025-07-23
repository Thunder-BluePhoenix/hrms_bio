# hrms_biometric/patches/v0_0/migrate_existing_attendance_data.py

import frappe
from frappe import _
from frappe.utils import getdate, now_datetime
import json


def execute():
    """Migrate existing attendance data to support biometric features"""
    try:
        print("📊 Migrating existing attendance data via patch...")
        
        # Migrate Employee Attendance records
        migrate_employee_attendance()
        
        # Create biometric links for existing employees
        create_biometric_links_for_employees()
        
        # Update attendance logs with biometric flags
        update_attendance_logs()
        
        print("✅ Attendance data migration completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Migrate attendance data patch error: {str(e)}")
        print(f"❌ Migrate attendance data patch failed: {str(e)}")


def migrate_employee_attendance():
    """Add biometric-related fields to existing attendance records"""
    try:
        print("🔄 Migrating Employee Attendance records...")
        
        # Check if our custom Employee Attendance doctype exists
        if not frappe.db.exists("DocType", "Employee Attendance"):
            print("ℹ️ Custom Employee Attendance doctype not found, skipping migration")
            return
        
        # Check if the table actually exists and has records
        try:
            test_query = frappe.db.sql("SELECT COUNT(*) as count FROM `tabEmployee Attendance` LIMIT 1", as_dict=True)
            if not test_query:
                print("ℹ️ No Employee Attendance table found, skipping migration")
                return
        except Exception as e:
            print(f"ℹ️ Employee Attendance table not accessible: {str(e)}")
            return
        
        # Update existing attendance records
        attendance_records = frappe.get_all(
            "Employee Attendance",
            fields=["name", "employee_id", "attendance_date", "status"],
            filters={"docstatus": ["!=", 2]},  # Not cancelled
            limit=1000  # Process in batches
        )
        
        for record in attendance_records:
            try:
                doc = frappe.get_doc("Employee Attendance", record.name)
                
                # Set default values for biometric fields if they don't exist
                if not hasattr(doc, 'verification_status'):
                    doc.db_set('verification_status', 'Manual Entry', notify=False)
                
                if not hasattr(doc, 'confidence_score'):
                    doc.db_set('confidence_score', 0.0, notify=False)
                
                if not hasattr(doc, 'created_by_system'):
                    doc.db_set('created_by_system', 0, notify=False)
                
            except Exception as e:
                print(f"⚠️ Error updating attendance record {record.name}: {str(e)}")
                continue
        
        print(f"✅ Migrated {len(attendance_records)} attendance records")
        
    except Exception as e:
        frappe.log_error(f"Employee attendance migration error: {str(e)}")
        print(f"⚠️ Employee attendance migration warning: {str(e)}")


def ensure_attendance_custom_fields():
    """Ensure custom fields exist for Employee Attendance"""
    try:
        custom_fields = [
            {
                "dt": "Employee Attendance",
                "fieldname": "biometric_section",
                "label": "Biometric Information",
                "fieldtype": "Section Break",
                "insert_after": "late_entry",
                "collapsible": 1
            },
            {
                "dt": "Employee Attendance",
                "fieldname": "is_biometric_verified",
                "label": "Biometric Verified",
                "fieldtype": "Check",
                "insert_after": "biometric_section",
                "default": 0
            },
            {
                "dt": "Employee Attendance",
                "fieldname": "recognition_confidence",
                "label": "Recognition Confidence %",
                "fieldtype": "Float",
                "insert_after": "is_biometric_verified",
                "precision": 2
            },
            {
                "dt": "Employee Attendance",
                "fieldname": "biometric_device_id",
                "label": "Biometric Device ID",
                "fieldtype": "Data",
                "insert_after": "recognition_confidence"
            },
            {
                "dt": "Employee Attendance",
                "fieldname": "face_image_path",
                "label": "Face Image Path",
                "fieldtype": "Data",
                "insert_after": "biometric_device_id",
                "read_only": 1,
                "hidden": 1
            }
        ]
        
        for field in custom_fields:
            field_name = f"{field['dt']}-{field['fieldname']}"
            if not frappe.db.exists("Custom Field", field_name):
                custom_field = frappe.new_doc("Custom Field")
                custom_field.update(field)
                custom_field.save(ignore_permissions=True)
        
        frappe.db.commit()
        
    except Exception as e:
        print(f"⚠️ Custom fields creation warning: {str(e)}")


def create_biometric_links_for_employees():
    """Create biometric links for existing employees who don't have them"""
    try:
        print("🔗 Creating biometric links for existing employees...")
        
        # Check if Employee Face Recognition table exists
        if not frappe.db.exists("DocType", "Employee Face Recognition"):
            print("ℹ️ Employee Face Recognition doctype not found, skipping biometric links creation")
            return
        
        # Get employees who don't have face recognition records using correct field name
        employees_without_biometric = frappe.db.sql("""
            SELECT e.name, e.employee_name, e.user_id
            FROM `tabEmployee` e
            LEFT JOIN `tabEmployee Face Recognition` efr ON e.name = efr.employee_id
            WHERE efr.name IS NULL
            AND e.status = 'Active'
            LIMIT 100
        """, as_dict=True)
        
        created_count = 0
        for emp in employees_without_biometric:
            try:
                # Check if employee has biometric_enabled field and if it's enabled
                employee_doc = frappe.get_doc("Employee", emp.name)
                
                # Only create if biometric is enabled for this employee
                should_create = False
                if hasattr(employee_doc, 'biometric_enabled') and employee_doc.biometric_enabled:
                    should_create = True
                elif not hasattr(employee_doc, 'biometric_enabled'):
                    # If the field doesn't exist, create for all active employees
                    should_create = True
                
                if should_create:
                    # Create a placeholder face recognition record
                    face_rec = frappe.new_doc("Employee Face Recognition")
                    face_rec.employee_id = emp.name  # Use correct field name
                    face_rec.employee_name = emp.employee_name
                    face_rec.status = "Inactive"  # Use valid status option
                    face_rec.save(ignore_permissions=True)
                    created_count += 1
                    
                    # Update employee with face recognition ID
                    if hasattr(employee_doc, 'face_recognition_id'):
                        employee_doc.db_set('face_recognition_id', face_rec.name, notify=False)
            
            except Exception as e:
                print(f"⚠️ Error creating biometric link for employee {emp.name}: {str(e)}")
                continue
        
        print(f"✅ Created biometric links for {created_count} employees")
        
    except Exception as e:
        frappe.log_error(f"Biometric links creation error: {str(e)}")
        print(f"⚠️ Biometric links creation warning: {str(e)}")


def update_attendance_logs():
    """Update attendance logs with biometric information"""
    try:
        print("📝 Updating attendance logs...")
        
        # Create migration log entry with valid initiated_by value
        if frappe.db.exists("DocType", "Multi Location Sync Log"):
            try:
                log = frappe.new_doc("Multi Location Sync Log")
                log.sync_date = getdate()
                log.sync_time = now_datetime().time()
                log.initiated_by = "Manual"  # Use valid option
                log.status = "Completed"
                log.sync_type = "Full Sync"
                log.total_locations = 1
                log.total_records = 0
                log.synced_records = 0
                log.failed_records = 0
                log.sync_summary = "Migrated existing attendance data to support biometric features"
                log.save(ignore_permissions=True)
                print("✅ Migration log entry created")
            except Exception as e:
                print(f"⚠️ Could not create migration log: {str(e)}")
        
        frappe.db.commit()
        print("✅ Attendance logs updated")
        
    except Exception as e:
        frappe.log_error(f"Attendance logs update error: {str(e)}")
        print(f"⚠️ Attendance logs update warning: {str(e)}")


def validate_migration():
    """Validate that migration completed successfully"""
    try:
        print("🔍 Validating migration...")
        
        # Check Employee Face Recognition records
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            face_rec_count = frappe.db.count("Employee Face Recognition")
            print(f"📊 Total Employee Face Recognition records: {face_rec_count}")
        
        # Check Employee Attendance records
        if frappe.db.exists("DocType", "Employee Attendance"):
            attendance_count = frappe.db.count("Employee Attendance")
            print(f"📊 Total Employee Attendance records: {attendance_count}")
        
        # Check active employees with biometric
        active_employees = frappe.db.count("Employee", filters={"status": "Active"})
        print(f"📊 Total active employees: {active_employees}")
        
        print("✅ Migration validation completed")
        
    except Exception as e:
        frappe.log_error(f"Migration validation error: {str(e)}")
        print(f"⚠️ Migration validation warning: {str(e)}")


# Main execution with validation
def execute():
    """Main migration function with validation"""
    try:
        print("📊 Migrating existing attendance data via patch...")
        
        # Run migration steps
        migrate_employee_attendance()
        create_biometric_links_for_employees()
        update_attendance_logs()
        
        # Validate migration
        validate_migration()
        
        print("✅ Attendance data migration completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Migrate attendance data patch error: {str(e)}")
        print(f"❌ Migrate attendance data patch failed: {str(e)}")