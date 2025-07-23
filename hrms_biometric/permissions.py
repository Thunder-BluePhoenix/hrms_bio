# hrms_biometric/permissions.py

import frappe
from frappe import _


def get_employee_face_recognition_permission_query(user):
    """Permission query for Employee Face Recognition doctype"""
    if not user:
        user = frappe.session.user
    
    # System Manager and Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user):
        return ""
    
    # HR Manager has full access
    if "HR Manager" in frappe.get_roles(user):
        return ""
    
    # HR User can see all but with restrictions
    if "HR User" in frappe.get_roles(user):
        return ""
    
    # Employee can only see their own records
    if "Employee" in frappe.get_roles(user):
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee:
            return f"(`tabEmployee Face Recognition`.employee = '{employee}')"
    
    # Default: no access
    return "1=0"


def has_employee_face_recognition_permission(doc, user):
    """Check if user has permission for Employee Face Recognition document"""
    if not user:
        user = frappe.session.user
    
    # System Manager and Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user):
        return True
    
    # HR Manager has full access
    if "HR Manager" in frappe.get_roles(user):
        return True
    
    # HR User has read access
    if "HR User" in frappe.get_roles(user):
        return True
    
    # Employee can only access their own records
    if "Employee" in frappe.get_roles(user):
        if hasattr(doc, 'employee'):
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
            return doc.employee == employee
    
    return False


def get_employee_attendance_permission_query(user):
    """Permission query for Employee Attendance doctype"""
    if not user:
        user = frappe.session.user
    
    # System Manager and Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user):
        return ""
    
    # HR Manager has full access
    if "HR Manager" in frappe.get_roles(user):
        return ""
    
    # HR User can see all
    if "HR User" in frappe.get_roles(user):
        return ""
    
    # Employee can only see their own attendance
    if "Employee" in frappe.get_roles(user):
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if employee:
            return f"(`tabEmployee Attendance`.employee = '{employee}')"
    
    # Default: no access
    return "1=0"


def has_employee_attendance_permission(doc, user):
    """Check if user has permission for Employee Attendance document"""
    if not user:
        user = frappe.session.user
    
    # System Manager and Administrator have full access
    if "System Manager" in frappe.get_roles(user) or "Administrator" in frappe.get_roles(user):
        return True
    
    # HR Manager has full access
    if "HR Manager" in frappe.get_roles(user):
        return True
    
    # HR User has read access
    if "HR User" in frappe.get_roles(user):
        return True
    
    # Employee can only access their own attendance
    if "Employee" in frappe.get_roles(user):
        if hasattr(doc, 'employee'):
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
            return doc.employee == employee
    
    return False


def get_kiosk_permission_query(user):
    """Permission query for Attendance Kiosk"""
    if not user:
        user = frappe.session.user
    
    # System Manager, Administrator, and HR roles have access
    user_roles = frappe.get_roles(user)
    allowed_roles = ["System Manager", "Administrator", "HR Manager", "HR User"]
    
    if any(role in user_roles for role in allowed_roles):
        return ""
    
    # Default: no access
    return "1=0"


def has_kiosk_permission(doc, user):
    """Check if user has permission for Attendance Kiosk"""
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    allowed_roles = ["System Manager", "Administrator", "HR Manager", "HR User"]
    
    return any(role in user_roles for role in allowed_roles)


def can_create_face_recognition_record(user=None):
    """Check if user can create Employee Face Recognition records"""
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    allowed_roles = ["System Manager", "Administrator", "HR Manager", "HR User"]
    
    return any(role in user_roles for role in allowed_roles)


def can_modify_biometric_settings(user=None):
    """Check if user can modify biometric settings"""
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    admin_roles = ["System Manager", "Administrator", "HR Manager"]
    
    return any(role in user_roles for role in admin_roles)


def get_user_employee_name(user=None):
    """Get employee name for the current user"""
    if not user:
        user = frappe.session.user
    
    return frappe.db.get_value("Employee", {"user_id": user}, "name")


def validate_biometric_access(employee=None, user=None):
    """Validate if user has access to biometric data for the employee"""
    if not user:
        user = frappe.session.user
    
    if not employee:
        return False
    
    # Admin access
    user_roles = frappe.get_roles(user)
    if any(role in ["System Manager", "Administrator", "HR Manager"] for role in user_roles):
        return True
    
    # Self access
    user_employee = get_user_employee_name(user)
    if user_employee == employee:
        return True
    
    return False