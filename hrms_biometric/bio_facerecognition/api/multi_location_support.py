import frappe
import json
from datetime import datetime, timedelta
from frappe import _

# Multi-Location Kiosk Management
@frappe.whitelist()
def get_all_kiosk_locations():
    """Get all active kiosk locations with their status"""
    try:
        kiosks = frappe.get_all(
            "Attendance Kiosk",
            filters={"is_active": 1},
            fields=[
                "name", "kiosk_name", "location", "timezone", 
                "creation", "modified"
            ],
            order_by="kiosk_name"
        )
        
        # Add real-time status for each kiosk
        for kiosk in kiosks:
            # Get today's attendance count for this kiosk
            today_count = frappe.db.count(
                "Employee Attendance",
                filters={
                    "kiosk_location": kiosk.kiosk_name,
                    "attendance_date": datetime.now().date()
                }
            )
            
            # Get last activity timestamp
            last_activity = frappe.db.sql("""
                SELECT MAX(creation) as last_activity
                FROM `tabEmployee Attendance`
                WHERE kiosk_location = %s
                AND DATE(creation) = CURDATE()
            """, (kiosk.kiosk_name,), as_dict=True)
            
            kiosk.update({
                "today_attendance_count": today_count,
                "last_activity": last_activity[0].get("last_activity") if last_activity[0].get("last_activity") else None,
                "status": "active" if last_activity[0].get("last_activity") else "idle"
            })
        
        return {
            "success": True,
            "kiosks": kiosks,
            "total_locations": len(kiosks)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting kiosk locations: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def sync_attendance_across_locations():
    """Synchronize attendance data across multiple locations"""
    try:
        # Get all attendance records from today that need sync
        today_attendance = frappe.get_all(
            "Employee Attendance",
            filters={
                "attendance_date": datetime.now().date(),
                "docstatus": 1  # Only submitted records
            },
            fields=[
                "name", "employee_id", "employee_name", "kiosk_location",
                "check_in_time", "check_out_time", "attendance_type",
                "confidence_score", "face_image_captured"
            ]
        )
        
        # Create sync log
        sync_log = frappe.new_doc("Multi Location Sync Log")
        sync_log.sync_date = datetime.now().date()
        sync_log.total_records = len(today_attendance)
        sync_log.status = "In Progress"
        sync_log.insert()
        
        synced_count = 0
        failed_count = 0
        
        for attendance in today_attendance:
            try:
                # Check for conflicts (same employee at different locations)
                conflicts = frappe.get_all(
                    "Employee Attendance",
                    filters={
                        "employee_id": attendance.employee_id,
                        "attendance_date": datetime.now().date(),
                        "kiosk_location": ["!=", attendance.kiosk_location],
                        "name": ["!=", attendance.name]
                    }
                )
                
                if conflicts:
                    # Log conflict for manual resolution
                    conflict_log = frappe.new_doc("Attendance Conflict Log")
                    conflict_log.employee_id = attendance.employee_id
                    conflict_log.conflict_date = datetime.now().date()
                    conflict_log.primary_location = attendance.kiosk_location
                    conflict_log.conflict_locations = json.dumps([c.kiosk_location for c in conflicts])
                    conflict_log.status = "Pending Resolution"
                    conflict_log.insert()
                    failed_count += 1
                else:
                    synced_count += 1
                    
            except Exception as e:
                frappe.log_error(f"Sync error for attendance {attendance.name}: {str(e)}")
                failed_count += 1
        
        # Update sync log
        sync_log.synced_records = synced_count
        sync_log.failed_records = failed_count
        sync_log.status = "Completed"
        sync_log.save()
        
        return {
            "success": True,
            "synced": synced_count,
            "failed": failed_count,
            "sync_log_id": sync_log.name
        }
        
    except Exception as e:
        frappe.log_error(f"Multi-location sync error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_location_analytics():
    """Get analytics data for all locations"""
    try:
        locations = frappe.get_all("Attendance Kiosk", filters={"is_active": 1}, pluck="kiosk_name")
        
        analytics = {}
        
        for location in locations:
            # Daily stats
            daily_stats = frappe.db.sql("""
                SELECT 
                    DATE(attendance_date) as date,
                    COUNT(*) as count,
                    AVG(confidence_score) as avg_confidence
                FROM `tabEmployee Attendance`
                WHERE kiosk_location = %s
                AND attendance_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(attendance_date)
                ORDER BY date DESC
            """, (location,), as_dict=True)
            
            # Peak hours
            peak_hours = frappe.db.sql("""
                SELECT 
                    HOUR(check_in_time) as hour,
                    COUNT(*) as count
                FROM `tabEmployee Attendance`
                WHERE kiosk_location = %s
                AND attendance_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                AND check_in_time IS NOT NULL
                GROUP BY HOUR(check_in_time)
                ORDER BY count DESC
                LIMIT 5
            """, (location,), as_dict=True)
            
            # Department distribution
            dept_stats = frappe.db.sql("""
                SELECT 
                    department,
                    COUNT(*) as count
                FROM `tabEmployee Attendance`
                WHERE kiosk_location = %s
                AND attendance_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY department
                ORDER BY count DESC
            """, (location,), as_dict=True)
            
            analytics[location] = {
                "daily_trends": daily_stats,
                "peak_hours": peak_hours,
                "department_distribution": dept_stats
            }
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        frappe.log_error(f"Location analytics error: {str(e)}")
        return {"success": False, "message": str(e)}

# New DocTypes for Multi-Location Support

def create_multi_location_doctypes():
    """Create additional DocTypes for multi-location support"""
    
    # Multi Location Sync Log DocType
    sync_log_doctype = {
        "doctype": "DocType",
        "name": "Multi Location Sync Log",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "sync_date", "fieldtype": "Date", "label": "Sync Date", "reqd": 1},
            {"fieldname": "total_records", "fieldtype": "Int", "label": "Total Records"},
            {"fieldname": "synced_records", "fieldtype": "Int", "label": "Synced Records"},
            {"fieldname": "failed_records", "fieldtype": "Int", "label": "Failed Records"},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", 
             "options": "In Progress\nCompleted\nFailed"},
            {"fieldname": "error_log", "fieldtype": "Long Text", "label": "Error Log"}
        ]
    }
    
    # Attendance Conflict Log DocType
    conflict_log_doctype = {
        "doctype": "DocType",
        "name": "Attendance Conflict Log",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "employee_id", "fieldtype": "Link", "options": "Employee Face Recognition", 
             "label": "Employee ID", "reqd": 1},
            {"fieldname": "conflict_date", "fieldtype": "Date", "label": "Conflict Date", "reqd": 1},
            {"fieldname": "primary_location", "fieldtype": "Data", "label": "Primary Location"},
            {"fieldname": "conflict_locations", "fieldtype": "Long Text", "label": "Conflict Locations"},
            {"fieldname": "resolution", "fieldtype": "Select", "label": "Resolution",
             "options": "Pending Resolution\nResolved - Primary\nResolved - Manual\nIgnored"},
            {"fieldname": "resolved_by", "fieldtype": "Link", "options": "User", "label": "Resolved By"},
            {"fieldname": "resolution_notes", "fieldtype": "Text", "label": "Resolution Notes"}
        ]
    }
    
    return [sync_log_doctype, conflict_log_doctype]