# hrms_biometric/hrms_biometric/permissions.py

import frappe
from frappe import _

def get_employee_face_recognition_permission_query(user):
    """
    Permission query for Employee Face Recognition
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Biometric Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Biometric Administrator" in frappe.get_roles(user):
        return ""
    
    # Attendance Manager can view all
    if "Attendance Manager" in frappe.get_roles(user):
        return ""
    
    # Employees can only see their own records
    if "Employee" in frappe.get_roles(user):
        employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee_id:
            return f"`tabEmployee Face Recognition`.employee_id = '{employee_id}'"
    
    # Default: no access
    return "1=0"

def get_employee_attendance_permission_query(user):
    """
    Permission query for Employee Attendance
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Biometric Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Biometric Administrator" in frappe.get_roles(user):
        return ""
    
    # Attendance Manager can view all
    if "Attendance Manager" in frappe.get_roles(user):
        return ""
    
    # Employees can only see their own attendance
    if "Employee" in frappe.get_roles(user):
        employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee_id:
            return f"`tabEmployee Attendance`.employee_id = '{employee_id}'"
    
    # Default: no access
    return "1=0"

def get_attendance_kiosk_permission_query(user):
    """
    Permission query for Attendance Kiosk
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Biometric Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Biometric Administrator" in frappe.get_roles(user):
        return ""
    
    # Kiosk users can view kiosks
    if "Kiosk User" in frappe.get_roles(user):
        return ""
    
    # Default: no access
    return "1=0"

def has_employee_face_recognition_permission(doc, user):
    """
    Check if user has permission for specific Employee Face Recognition record
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Biometric Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Biometric Administrator" in frappe.get_roles(user):
        return True
    
    # Attendance Manager can access all
    if "Attendance Manager" in frappe.get_roles(user):
        return True
    
    # Employees can only access their own records
    if "Employee" in frappe.get_roles(user):
        employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee_id and doc.employee_id == employee_id:
            return True
    
    return False

def has_employee_attendance_permission(doc, user):
    """
    Check if user has permission for specific Employee Attendance record
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Biometric Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Biometric Administrator" in frappe.get_roles(user):
        return True
    
    # Attendance Manager can access all
    if "Attendance Manager" in frappe.get_roles(user):
        return True
    
    # Employees can only access their own attendance
    if "Employee" in frappe.get_roles(user):
        employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee_id and doc.employee_id == employee_id:
            return True
    
    return False

def has_attendance_kiosk_permission(doc, user):
    """
    Check if user has permission for specific Attendance Kiosk record
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Biometric Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Biometric Administrator" in frappe.get_roles(user):
        return True
    
    # Kiosk users can access kiosks (read-only)
    if "Kiosk User" in frappe.get_roles(user):
        return True
    
    return False

def has_biometric_access(user=None):
    """
    Check if user has general biometric system access
    """
    if not user:
        user = frappe.session.user
    
    # Check if user has any biometric-related roles
    user_roles = frappe.get_roles(user)
    biometric_roles = ["System Manager", "Biometric Administrator", "Attendance Manager", "Kiosk User"]
    
    return any(role in user_roles for role in biometric_roles)

def get_user_employee_id(user=None):
    """
    Get employee ID for a user (helper function)
    """
    if not user:
        user = frappe.session.user
    
    return frappe.db.get_value("Employee", {"user_id": user}, "name")

def can_access_biometric_features(user=None):
    """
    Check if user can access biometric features
    """
    if not user:
        user = frappe.session.user
    
    # Check custom field if it exists
    try:
        biometric_access = frappe.db.get_value("User", user, "biometric_access")
        if biometric_access:
            return True
    except:
        pass
    
    # Fallback to role-based access
    return has_biometric_access(user)