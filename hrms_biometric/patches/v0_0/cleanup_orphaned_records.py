# hrms_biometric/patches/v0_0/cleanup_orphaned_records.py

import frappe
from frappe import _
from frappe.utils import getdate, add_days


def execute():
    """Cleanup orphaned records and invalid data"""
    try:
        print("🧹 Cleaning up orphaned records via patch...")
        
        # Clean orphaned face recognition records
        cleanup_orphaned_face_recognition()
        
        # Clean orphaned attendance images
        cleanup_orphaned_attendance_images()
        
        # Clean invalid notification logs
        cleanup_invalid_notification_logs()
        
        # Clean orphaned sync logs
        cleanup_orphaned_sync_logs()
        
        # Clean temporary files
        cleanup_temporary_files()
        
        # Clean duplicate records
        cleanup_duplicate_records()
        
        # Final commit
        frappe.db.commit()
        print("✅ Orphaned records cleanup completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Cleanup orphaned records patch error: {str(e)}")
        print(f"❌ Cleanup orphaned records patch failed: {str(e)}")


def cleanup_orphaned_face_recognition():
    """Remove face recognition records for non-existent employees"""
    try:
        print("🔍 Cleaning orphaned face recognition records...")
        
        if not frappe.db.exists("DocType", "Employee Face Recognition"):
            print("ℹ️ Employee Face Recognition doctype not found, skipping...")
            return
        
        # Find face recognition records with non-existent employees using correct field name
        orphaned_records = frappe.db.sql("""
            SELECT efr.name 
            FROM `tabEmployee Face Recognition` efr
            LEFT JOIN `tabEmployee` e ON efr.employee_id = e.name
            WHERE e.name IS NULL
            LIMIT 100
        """, as_dict=True)
        
        count = 0
        for record in orphaned_records:
            try:
                frappe.delete_doc("Employee Face Recognition", record.name, ignore_permissions=True)
                count += 1
            except Exception as e:
                print(f"⚠️ Error deleting orphaned face recognition {record.name}: {str(e)}")
                continue
        
        print(f"✅ Cleaned {count} orphaned face recognition records")
        
    except Exception as e:
        frappe.log_error(f"Face recognition cleanup error: {str(e)}")
        print(f"⚠️ Face recognition cleanup warning: {str(e)}")


def cleanup_orphaned_attendance_images():
    """Remove attendance images that are no longer referenced"""
    try:
        print("🖼️ Cleaning orphaned attendance images...")
        
        # Find files that look like attendance images but are not referenced
        old_date = add_days(getdate(), -30)  # Files older than 30 days
        
        try:
            orphaned_files = frappe.db.sql("""
                SELECT name, file_url, file_name
                FROM `tabFile`
                WHERE (file_name LIKE %s OR file_name LIKE %s)
                AND creation < %s
                AND attached_to_doctype IS NULL
                LIMIT 100
            """, ('%attendance_%', '%face_capture_%', old_date), as_dict=True)
        except Exception as e:
            print(f"⚠️ Could not query files table: {str(e)}")
            return
        
        count = 0
        for file_doc in orphaned_files:
            try:
                # Verify it's really orphaned by checking if it's referenced anywhere
                if frappe.db.exists("DocType", "Employee Face Recognition"):
                    references = frappe.db.sql("""
                        SELECT COUNT(*) as count FROM `tabEmployee Face Recognition`
                        WHERE face_image_1 LIKE %s OR face_image_2 LIKE %s OR face_image_3 LIKE %s
                        OR face_image_4 LIKE %s OR face_image_5 LIKE %s OR encoding_data LIKE %s
                    """, (f"%{file_doc.file_name}%", f"%{file_doc.file_name}%", f"%{file_doc.file_name}%",
                         f"%{file_doc.file_name}%", f"%{file_doc.file_name}%", f"%{file_doc.file_name}%"), as_dict=True)
                    
                    if references and references[0].count == 0:
                        frappe.delete_doc("File", file_doc.name, ignore_permissions=True)
                        count += 1
                        
            except Exception as e:
                print(f"⚠️ Error deleting orphaned file {file_doc.name}: {str(e)}")
                continue
        
        print(f"✅ Cleaned {count} orphaned attendance images")
        
    except Exception as e:
        frappe.log_error(f"Attendance images cleanup error: {str(e)}")
        print(f"⚠️ Attendance images cleanup warning: {str(e)}")


def cleanup_invalid_notification_logs():
    """Remove invalid notification logs"""
    try:
        print("📧 Cleaning invalid notification logs...")
        
        if not frappe.db.exists("DocType", "Notification Activity Log"):
            print("ℹ️ Notification Activity Log doctype not found, skipping...")
            return
        
        # Remove logs with invalid employee references using correct field name
        invalid_logs = frappe.db.sql("""
            SELECT nal.name
            FROM `tabNotification Activity Log` nal
            LEFT JOIN `tabEmployee Face Recognition` efr ON nal.employee_id = efr.name
            WHERE efr.name IS NULL
            LIMIT 100
        """, as_dict=True)
        
        count = 0
        for log in invalid_logs:
            try:
                frappe.delete_doc("Notification Activity Log", log.name, ignore_permissions=True)
                count += 1
            except Exception as e:
                print(f"⚠️ Error deleting invalid notification log {log.name}: {str(e)}")
                continue
        
        # Also remove very old logs (older than 90 days)
        old_date = add_days(getdate(), -90)
        old_logs = frappe.get_all(
            "Notification Activity Log",
            filters={"timestamp": ["<", old_date]},
            fields=["name"],
            limit=500
        )
        
        old_count = 0
        for log in old_logs:
            try:
                frappe.delete_doc("Notification Activity Log", log.name, ignore_permissions=True)
                old_count += 1
            except Exception as e:
                continue
        
        print(f"✅ Cleaned {count} invalid and {old_count} old notification logs")
        
    except Exception as e:
        frappe.log_error(f"Notification logs cleanup error: {str(e)}")
        print(f"⚠️ Notification logs cleanup warning: {str(e)}")


def cleanup_orphaned_sync_logs():
    """Remove orphaned sync logs"""
    try:
        print("🔄 Cleaning orphaned sync logs...")
        
        if not frappe.db.exists("DocType", "Multi Location Sync Log"):
            print("ℹ️ Multi Location Sync Log doctype not found, skipping...")
            return
        
        # Remove very old sync logs (older than 6 months)
        old_date = add_days(getdate(), -180)
        old_sync_logs = frappe.get_all(
            "Multi Location Sync Log",
            filters={"sync_date": ["<", old_date]},
            fields=["name"],
            limit=500
        )
        
        count = 0
        for log in old_sync_logs:
            try:
                frappe.delete_doc("Multi Location Sync Log", log.name, ignore_permissions=True)
                count += 1
            except Exception as e:
                continue
        
        print(f"✅ Cleaned {count} old sync logs")
        
    except Exception as e:
        frappe.log_error(f"Sync logs cleanup error: {str(e)}")
        print(f"⚠️ Sync logs cleanup warning: {str(e)}")


def cleanup_temporary_files():
    """Remove temporary biometric processing files"""
    try:
        print("🗂️ Cleaning temporary files...")
        
        # Remove temporary face processing files
        try:
            temp_files = frappe.db.sql("""
                SELECT name, file_url, file_name
                FROM `tabFile`
                WHERE (file_name LIKE %s OR file_name LIKE %s OR file_name LIKE %s)
                AND (file_name LIKE %s OR file_name LIKE %s OR file_name LIKE %s)
                AND creation < DATE_SUB(NOW(), INTERVAL 1 DAY)
                LIMIT 100
            """, ('%temp_%', '%tmp_%', '%processing_%', '%.jpg', '%.png', '%.jpeg'), as_dict=True)
        except Exception as e:
            print(f"⚠️ Could not query temporary files: {str(e)}")
            return
        
        count = 0
        for file_doc in temp_files:
            try:
                frappe.delete_doc("File", file_doc.name, ignore_permissions=True)
                count += 1
            except Exception as e:
                continue
        
        print(f"✅ Cleaned {count} temporary files")
        
    except Exception as e:
        frappe.log_error(f"Temporary files cleanup error: {str(e)}")
        print(f"⚠️ Temporary files cleanup warning: {str(e)}")


def cleanup_duplicate_records():
    """Remove duplicate biometric records"""
    try:
        print("🔍 Cleaning duplicate records...")
        
        if not frappe.db.exists("DocType", "Employee Face Recognition"):
            print("ℹ️ Employee Face Recognition doctype not found, skipping...")
            return
        
        # Find duplicate face recognition records for the same employee using correct field name
        duplicates = frappe.db.sql("""
            SELECT employee_id, COUNT(*) as count, GROUP_CONCAT(name) as names
            FROM `tabEmployee Face Recognition`
            GROUP BY employee_id
            HAVING COUNT(*) > 1
            LIMIT 50
        """, as_dict=True)
        
        count = 0
        for dup in duplicates:
            try:
                # Keep the most recent record, delete others
                names = dup.names.split(',')
                records = frappe.get_all(
                    "Employee Face Recognition",
                    filters={"name": ["in", names]},
                    fields=["name", "creation"],
                    order_by="creation desc"
                )
                
                # Delete all but the first (most recent)
                for record in records[1:]:
                    frappe.delete_doc("Employee Face Recognition", record.name, ignore_permissions=True)
                    count += 1
                    
            except Exception as e:
                print(f"⚠️ Error cleaning duplicates for employee {dup.employee_id}: {str(e)}")
                continue
        
        print(f"✅ Cleaned {count} duplicate face recognition records")
        
    except Exception as e:
        frappe.log_error(f"Duplicate records cleanup error: {str(e)}")
        print(f"⚠️ Duplicate records cleanup warning: {str(e)}")


def cleanup_invalid_file_references():
    """Clean up invalid file references in biometric records"""
    try:
        print("🔗 Cleaning invalid file references...")
        
        if not frappe.db.exists("DocType", "Employee Face Recognition"):
            return
        
        # Get all face recognition records
        face_records = frappe.get_all(
            "Employee Face Recognition",
            fields=["name", "face_image_1", "face_image_2", "face_image_3", "face_image_4", "face_image_5"],
            limit=500
        )
        
        cleaned_count = 0
        for record in face_records:
            try:
                doc = frappe.get_doc("Employee Face Recognition", record.name)
                needs_update = False
                
                # Check each face image field
                for field in ["face_image_1", "face_image_2", "face_image_3", "face_image_4", "face_image_5"]:
                    if hasattr(doc, field) and getattr(doc, field):
                        file_url = getattr(doc, field)
                        # Check if file exists
                        if not frappe.db.exists("File", {"file_url": file_url}):
                            setattr(doc, field, None)
                            needs_update = True
                
                if needs_update:
                    doc.save(ignore_permissions=True)
                    cleaned_count += 1
                    
            except Exception as e:
                print(f"⚠️ Error cleaning file references for {record.name}: {str(e)}")
                continue
        
        print(f"✅ Cleaned invalid file references in {cleaned_count} records")
        
    except Exception as e:
        frappe.log_error(f"File references cleanup error: {str(e)}")
        print(f"⚠️ File references cleanup warning: {str(e)}")


def cleanup_invalid_employee_references():
    """Clean up records with invalid employee references"""
    try:
        print("👥 Cleaning invalid employee references...")
        
        # Clean Employee Notification Settings
        if frappe.db.exists("DocType", "Employee Notification Settings"):
            invalid_notifications = frappe.db.sql("""
                SELECT ens.name
                FROM `tabEmployee Notification Settings` ens
                LEFT JOIN `tabEmployee Face Recognition` efr ON ens.employee_id = efr.name
                WHERE efr.name IS NULL
                LIMIT 100
            """, as_dict=True)
            
            notif_count = 0
            for notif in invalid_notifications:
                try:
                    frappe.delete_doc("Employee Notification Settings", notif.name, ignore_permissions=True)
                    notif_count += 1
                except:
                    continue
            
            print(f"✅ Cleaned {notif_count} invalid employee notification settings")
        
    except Exception as e:
        frappe.log_error(f"Employee references cleanup error: {str(e)}")
        print(f"⚠️ Employee references cleanup warning: {str(e)}")


def generate_cleanup_summary():
    """Generate summary of cleanup operations"""
    try:
        print("📊 Generating cleanup summary...")
        
        summary = {
            "cleanup_date": getdate(),
            "doctypes_processed": [],
            "records_remaining": {}
        }
        
        # Count remaining records
        doctypes_to_check = [
            "Employee Face Recognition",
            "Employee Attendance", 
            "Notification Activity Log",
            "Multi Location Sync Log",
            "Employee Notification Settings"
        ]
        
        for doctype in doctypes_to_check:
            if frappe.db.exists("DocType", doctype):
                count = frappe.db.count(doctype)
                summary["records_remaining"][doctype] = count
                summary["doctypes_processed"].append(doctype)
        
        # Log the summary
        frappe.log_error(
            f"Cleanup Summary: {summary}",
            "Biometric Cleanup Summary"
        )
        
        print("✅ Cleanup summary generated")
        
    except Exception as e:
        frappe.log_error(f"Cleanup summary error: {str(e)}")
        print(f"⚠️ Cleanup summary warning: {str(e)}")


# Main execution function with all cleanup operations
def execute():
    """Main cleanup function with comprehensive cleanup"""
    try:
        print("🧹 Cleaning up orphaned records via patch...")
        
        # Core cleanup operations
        cleanup_orphaned_face_recognition()
        cleanup_orphaned_attendance_images()
        cleanup_invalid_notification_logs()
        cleanup_orphaned_sync_logs()
        cleanup_temporary_files()
        cleanup_duplicate_records()
        
        # Additional cleanup operations
        cleanup_invalid_file_references()
        cleanup_invalid_employee_references()
        
        # Generate summary
        generate_cleanup_summary()
        
        # Final commit
        frappe.db.commit()
        print("✅ Orphaned records cleanup completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Cleanup orphaned records patch error: {str(e)}")
        print(f"❌ Cleanup orphaned records patch failed: {str(e)}")