# hrms_biometric/utils/jinja_methods.py

"""
Jinja template methods for HRMS Biometric app

This module contains Jinja template functions that can be used in HTML templates
throughout the application.
"""

import frappe
from frappe import _
from frappe.utils import formatdate, format_time, get_time_str, now_datetime
from datetime import datetime


def get_biometric_status(employee_id=None):
    """
    Get biometric system status for an employee or general system status
    
    Args:
        employee_id (str, optional): Employee ID to check specific status
        
    Returns:
        dict: Status information including biometric enabled status, 
              face recognition status, and system health
    """
    try:
        if not employee_id:
            # Return general system status
            return {
                "system_enabled": True,
                "total_employees": frappe.db.count("Employee", {"status": "Active"}),
                "biometric_enabled_employees": frappe.db.count("Employee", {"biometric_enabled": 1}),
                "active_kiosks": frappe.db.count("Attendance Kiosk", {"is_active": 1}),
                "status": "healthy"
            }
        
        # Get employee specific status
        employee = frappe.get_doc("Employee", employee_id)
        
        # Check if employee has face recognition enabled
        face_recognition_doc = None
        if hasattr(employee, 'face_recognition_id') and employee.face_recognition_id:
            face_recognition_doc = frappe.get_doc("Employee Face Recognition", employee.face_recognition_id)
        
        biometric_status = {
            "employee_id": employee_id,
            "employee_name": employee.employee_name,
            "biometric_enabled": getattr(employee, 'biometric_enabled', 0),
            "face_recognition_id": getattr(employee, 'face_recognition_id', None),
            "face_images_count": 0,
            "recognition_active": False,
            "last_attendance": None
        }
        
        if face_recognition_doc:
            # Count face images
            face_image_fields = ['face_image_1', 'face_image_2', 'face_image_3', 'face_image_4', 'face_image_5']
            biometric_status["face_images_count"] = sum(
                1 for field in face_image_fields 
                if getattr(face_recognition_doc, field, None)
            )
            biometric_status["recognition_active"] = face_recognition_doc.is_active
        
        # Get last attendance
        last_attendance = frappe.db.get_value(
            "Employee Attendance",
            filters={"employee": employee_id},
            fieldname=["attendance_date", "time"],
            order_by="attendance_date desc, time desc"
        )
        
        if last_attendance:
            biometric_status["last_attendance"] = {
                "date": last_attendance[0],
                "time": last_attendance[1]
            }
        
        return biometric_status
        
    except Exception as e:
        frappe.log_error(f"Error getting biometric status: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "employee_id": employee_id
        }


def format_attendance_time(attendance_time, format_type="12h"):
    """
    Format attendance time for display in templates
    
    Args:
        attendance_time: Time string or datetime object
        format_type (str): "12h" for 12-hour format, "24h" for 24-hour format
        
    Returns:
        str: Formatted time string
    """
    try:
        if not attendance_time:
            return ""
        
        # Handle different input types
        if isinstance(attendance_time, str):
            # Try to parse string time
            try:
                if ":" in attendance_time:
                    time_obj = datetime.strptime(attendance_time, "%H:%M:%S").time()
                else:
                    time_obj = datetime.strptime(attendance_time, "%H%M%S").time()
            except ValueError:
                # Try with datetime string
                try:
                    time_obj = datetime.fromisoformat(attendance_time).time()
                except ValueError:
                    return attendance_time  # Return as-is if can't parse
        elif hasattr(attendance_time, 'time'):
            # DateTime object
            time_obj = attendance_time.time()
        else:
            # Assume it's already a time object
            time_obj = attendance_time
        
        if format_type == "12h":
            # 12-hour format with AM/PM
            return time_obj.strftime("%I:%M %p")
        else:
            # 24-hour format
            return time_obj.strftime("%H:%M")
            
    except Exception as e:
        frappe.log_error(f"Error formatting attendance time: {str(e)}")
        return str(attendance_time) if attendance_time else ""


def get_attendance_summary(employee_id, from_date=None, to_date=None):
    """
    Get attendance summary for an employee within a date range
    
    Args:
        employee_id (str): Employee ID
        from_date (str, optional): Start date (YYYY-MM-DD)
        to_date (str, optional): End date (YYYY-MM-DD)
        
    Returns:
        dict: Attendance summary with counts and percentages
    """
    try:
        from frappe.utils import getdate, add_days, today
        
        if not from_date:
            from_date = add_days(today(), -30)  # Last 30 days
        if not to_date:
            to_date = today()
        
        # Get attendance records
        attendance_records = frappe.db.get_all(
            "Employee Attendance",
            filters={
                "employee": employee_id,
                "attendance_date": ["between", [from_date, to_date]]
            },
            fields=["attendance_date", "status", "in_time", "out_time"]
        )
        
        total_days = len(attendance_records)
        present_days = len([r for r in attendance_records if r.status == "Present"])
        absent_days = len([r for r in attendance_records if r.status == "Absent"])
        half_days = len([r for r in attendance_records if r.status == "Half Day"])
        
        return {
            "employee_id": employee_id,
            "from_date": from_date,
            "to_date": to_date,
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "half_days": half_days,
            "attendance_percentage": round((present_days / total_days * 100), 2) if total_days > 0 else 0,
            "records": attendance_records
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting attendance summary: {str(e)}")
        return {
            "error": str(e),
            "employee_id": employee_id
        }


def get_kiosk_status(kiosk_id=None):
    """
    Get status information for attendance kiosks
    
    Args:
        kiosk_id (str, optional): Specific kiosk ID
        
    Returns:
        dict: Kiosk status information
    """
    try:
        if kiosk_id:
            # Get specific kiosk status
            kiosk = frappe.get_doc("Attendance Kiosk", kiosk_id)
            return {
                "kiosk_id": kiosk_id,
                "kiosk_name": kiosk.kiosk_name,
                "location": kiosk.location,
                "is_active": kiosk.is_active,
                "timezone": kiosk.timezone,
                "last_updated": kiosk.modified
            }
        else:
            # Get all kiosks status
            kiosks = frappe.db.get_all(
                "Attendance Kiosk",
                fields=["name", "kiosk_name", "location", "is_active", "timezone"],
                order_by="kiosk_name"
            )
            
            return {
                "total_kiosks": len(kiosks),
                "active_kiosks": len([k for k in kiosks if k.is_active]),
                "kiosks": kiosks
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting kiosk status: {str(e)}")
        return {
            "error": str(e),
            "kiosk_id": kiosk_id
        }


def format_employee_name(employee_id):
    """
    Get formatted employee name for display
    
    Args:
        employee_id (str): Employee ID
        
    Returns:
        str: Formatted employee name
    """
    try:
        employee = frappe.get_value(
            "Employee", 
            employee_id, 
            ["employee_name", "first_name", "last_name"]
        )
        
        if employee:
            return employee[0] or f"{employee[1] or ''} {employee[2] or ''}".strip()
        return employee_id
        
    except Exception:
        return employee_id


def get_system_health():
    """
    Get overall system health status
    
    Returns:
        dict: System health information
    """
    try:
        # Basic system health checks
        total_employees = frappe.db.count("Employee", {"status": "Active"})
        biometric_employees = frappe.db.count("Employee", {"biometric_enabled": 1})
        active_kiosks = frappe.db.count("Attendance Kiosk", {"is_active": 1})
        
        # Recent attendance activity
        today_attendance = frappe.db.count(
            "Employee Attendance", 
            {"attendance_date": frappe.utils.today()}
        )
        
        health_score = 100
        status = "healthy"
        
        # Simple health scoring
        if biometric_employees == 0:
            health_score -= 30
            status = "warning"
        
        if active_kiosks == 0:
            health_score -= 40
            status = "critical"
        
        return {
            "status": status,
            "health_score": health_score,
            "total_employees": total_employees,
            "biometric_employees": biometric_employees,
            "active_kiosks": active_kiosks,
            "today_attendance": today_attendance,
            "last_check": now_datetime()
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting system health: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }