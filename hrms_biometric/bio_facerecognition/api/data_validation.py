# hrms_biometric/bio_facerecognition/api/data_validation.py

import frappe
from frappe import _
import json
import hashlib
import re
from datetime import datetime, timedelta
import calendar

def validate_employee_data(employee_data):
    """Validate employee data before saving"""
    errors = []
    
    # Required fields
    required_fields = ['employee_id', 'employee_name']
    for field in required_fields:
        if not employee_data.get(field):
            errors.append(f"{field} is required")
    
    # Employee ID format
    if employee_data.get('employee_id'):
        emp_id = employee_data['employee_id']
        if not emp_id.startswith('EMP') or len(emp_id) < 6:
            errors.append("Employee ID must start with 'EMP' and be at least 6 characters")
    
    # Email validation
    if employee_data.get('email'):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, employee_data['email']):
            errors.append("Invalid email format")
    
    # Mobile number validation
    if employee_data.get('mobile'):
        mobile = employee_data['mobile'].replace('-', '').replace(' ', '').replace('+', '')
        if not mobile.isdigit() or len(mobile) < 10:
            errors.append("Invalid mobile number format")
    
    return errors

def validate_attendance_data(attendance_data):
    """Validate attendance data"""
    errors = []
    
    # Required fields
    required_fields = ['employee_id', 'attendance_date', 'attendance_type']
    for field in required_fields:
        if not attendance_data.get(field):
            errors.append(f"{field} is required")
    
    # Date validation
    if attendance_data.get('attendance_date'):
        try:
            att_date = datetime.strptime(str(attendance_data['attendance_date']), "%Y-%m-%d").date()
            today = datetime.now().date()
            if att_date > today:
                errors.append("Attendance date cannot be in the future")
        except:
            errors.append("Invalid attendance date format")
    
    # Time validation
    if attendance_data.get('check_in_time') and attendance_data.get('check_out_time'):
        try:
            check_in = datetime.fromisoformat(str(attendance_data['check_in_time']))
            check_out = datetime.fromisoformat(str(attendance_data['check_out_time']))
            if check_out <= check_in:
                errors.append("Check-out time must be after check-in time")
        except:
            errors.append("Invalid time format")
    
    return errors

def sanitize_input_data(data):
    """Sanitize input data to prevent injection attacks"""
    try:
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                sanitized[key] = sanitize_input_data(value)
            return sanitized
        elif isinstance(data, list):
            return [sanitize_input_data(item) for item in data]
        elif isinstance(data, str):
            # Remove potentially dangerous characters
            # Remove script tags
            data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
            # Remove SQL injection patterns
            dangerous_patterns = ['union', 'select', 'insert', 'update', 'delete', 'drop', 'exec']
            for pattern in dangerous_patterns:
                data = re.sub(f'\\b{pattern}\\b', '', data, flags=re.IGNORECASE)
            return data.strip()
        else:
            return data
            
    except Exception as e:
        frappe.log_error(f"Data sanitization error: {str(e)}")
        return data

def generate_secure_hash(data):
    """Generate secure hash for data integrity"""
    try:
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        elif not isinstance(data, str):
            data = str(data)
        
        return hashlib.sha256(data.encode()).hexdigest()
        
    except Exception as e:
        frappe.log_error(f"Hash generation error: {str(e)}")
        return None

def verify_data_integrity(data, expected_hash):
    """Verify data integrity using hash"""
    try:
        current_hash = generate_secure_hash(data)
        return current_hash == expected_hash
        
    except Exception as e:
        frappe.log_error(f"Data integrity verification error: {str(e)}")
        return False

def validate_phone_number(phone, country_code="IN"):
    """Validate and format phone number"""
    try:
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        if country_code == "IN":
            # Indian phone number validation
            if phone.startswith('91'):
                phone = phone[2:]
            elif phone.startswith('0'):
                phone = phone[1:]
            
            if len(phone) == 10 and phone[0] in '6789':
                return {"valid": True, "formatted": f"+91{phone}", "local": phone}
        
        elif country_code == "US":
            # US phone number validation
            if phone.startswith('1'):
                phone = phone[1:]
            
            if len(phone) == 10:
                return {"valid": True, "formatted": f"+1{phone}", "local": phone}
        
        return {"valid": False, "reason": "Invalid phone number format"}
        
    except Exception as e:
        return {"valid": False, "reason": f"Validation error: {str(e)}"}

def validate_working_hours_data(hours_data):
    """Validate working hours configuration"""
    errors = []
    
    try:
        start_time = datetime.strptime(hours_data.get('start_time', '09:00'), '%H:%M').time()
        end_time = datetime.strptime(hours_data.get('end_time', '18:00'), '%H:%M').time()
        
        if start_time >= end_time:
            errors.append("Start time must be before end time")
        
        # Check if working hours are reasonable (minimum 4 hours, maximum 16 hours)
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        total_minutes = end_minutes - start_minutes
        
        if total_minutes < 240:  # Less than 4 hours
            errors.append("Working hours must be at least 4 hours")
        elif total_minutes > 960:  # More than 16 hours
            errors.append("Working hours cannot exceed 16 hours")
            
    except ValueError:
        errors.append("Invalid time format. Use HH:MM format")
    
    return errors

def validate_recognition_settings(settings):
    """Validate face recognition settings"""
    errors = []
    
    # Tolerance validation
    tolerance = settings.get('recognition_tolerance', 0.4)
    if not isinstance(tolerance, (int, float)) or tolerance < 0.1 or tolerance > 1.0:
        errors.append("Recognition tolerance must be between 0.1 and 1.0")
    
    # Num jitters validation
    num_jitters = settings.get('num_jitters', 100)
    if not isinstance(num_jitters, int) or num_jitters < 1 or num_jitters > 200:
        errors.append("Number of jitters must be between 1 and 200")
    
    # Confidence threshold validation
    confidence_threshold = settings.get('confidence_threshold', 70)
    if not isinstance(confidence_threshold, (int, float)) or confidence_threshold < 0 or confidence_threshold > 100:
        errors.append("Confidence threshold must be between 0 and 100")
    
    # Model validation
    recognition_model = settings.get('recognition_model', 'large')
    if recognition_model not in ['small', 'large']:
        errors.append("Recognition model must be 'small' or 'large'")
    
    detection_model = settings.get('face_detection_model', 'cnn')
    if detection_model not in ['hog', 'cnn']:
        errors.append("Face detection model must be 'hog' or 'cnn'")
    
    return errors

def validate_payroll_data(payroll_data):
    """Validate payroll calculation data"""
    errors = []
    
    # Required fields
    required_fields = ['employee_id', 'month', 'year', 'working_hours']
    for field in required_fields:
        if field not in payroll_data:
            errors.append(f"{field} is required")
    
    # Validate month
    month = payroll_data.get('month')
    if month and (not isinstance(month, int) or month < 1 or month > 12):
        errors.append("Month must be between 1 and 12")
    
    # Validate year
    year = payroll_data.get('year')
    current_year = datetime.now().year
    if year and (not isinstance(year, int) or year < 2020 or year > current_year + 1):
        errors.append(f"Year must be between 2020 and {current_year + 1}")
    
    # Validate working hours
    working_hours = payroll_data.get('working_hours', 0)
    if not isinstance(working_hours, (int, float)) or working_hours < 0 or working_hours > 744:  # Max hours in a month
        errors.append("Working hours must be between 0 and 744")
    
    # Validate hourly rate
    hourly_rate = payroll_data.get('hourly_rate', 0)
    if not isinstance(hourly_rate, (int, float)) or hourly_rate < 0:
        errors.append("Hourly rate must be a positive number")
    
    return errors

def validate_notification_data(notification_data):
    """Validate notification data"""
    errors = []
    
    # Required fields
    required_fields = ['employee_id', 'event_type']
    for field in required_fields:
        if not notification_data.get(field):
            errors.append(f"{field} is required")
    
    # Validate event type
    valid_event_types = ['Check In', 'Check Out', 'Late Arrival', 'Missed Check Out', 'Overtime Alert', 'Weekly Summary']
    if notification_data.get('event_type') not in valid_event_types:
        errors.append(f"Event type must be one of: {', '.join(valid_event_types)}")
    
    # Validate priority level
    priority_level = notification_data.get('priority_level', 'Normal')
    valid_priorities = ['Low', 'Normal', 'High', 'Urgent']
    if priority_level not in valid_priorities:
        errors.append(f"Priority level must be one of: {', '.join(valid_priorities)}")
    
    return errors

def format_currency(amount, currency="INR"):
    """Format currency amount"""
    try:
        if currency == "INR":
            return f"₹{amount:,.2f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except:
        return str(amount)

def validate_kiosk_data(kiosk_data):
    """Validate attendance kiosk data"""
    errors = []
    
    # Required fields
    required_fields = ['kiosk_name', 'location']
    for field in required_fields:
        if not kiosk_data.get(field):
            errors.append(f"{field} is required")
    
    # Validate kiosk name format
    kiosk_name = kiosk_data.get('kiosk_name', '')
    if kiosk_name and not re.match(r'^[A-Za-z0-9_\-\s]+$', kiosk_name):
        errors.append("Kiosk name can only contain letters, numbers, spaces, hyphens and underscores")
    
    # Validate timezone
    timezone = kiosk_data.get('timezone', '')
    valid_timezones = [
        'Asia/Kolkata', 'America/New_York', 'Europe/London', 
        'Asia/Tokyo', 'Australia/Sydney', 'America/Los_Angeles'
    ]
    if timezone and timezone not in valid_timezones:
        errors.append(f"Timezone must be one of: {', '.join(valid_timezones)}")
    
    return errors