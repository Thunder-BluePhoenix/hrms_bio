# hrms_biometric/bio_facerecognition/api/helper_functions_utilities.py

"""
Main helper functions utilities file that imports and consolidates all helper modules.
This file serves as the central hub for all utility functions.
"""

import frappe
from frappe import _
from datetime import datetime, timedelta

# Import all helper modules
from .image_processing import (
    enhance_image_quality,
    validate_face_image_quality, 
    compress_image_for_storage,
    convert_base64_to_cv2,
    convert_cv2_to_base64,
    detect_anti_spoofing
)

from .data_validation import (
    validate_employee_data,
    validate_attendance_data,
    sanitize_input_data,
    generate_secure_hash,
    verify_data_integrity,
    validate_phone_number,
    validate_working_hours_data,
    validate_recognition_settings,
    validate_payroll_data,
    validate_notification_data,
    validate_kiosk_data,
    format_currency
)

from .utilities import (
    get_working_days_in_period,
    calculate_time_difference,
    format_duration,
    get_pay_period_dates,
    get_current_fiscal_year,
    convert_timezone,
    export_to_csv_helper,
    export_to_json_helper,
    save_file_from_base64,
    measure_performance,
    optimize_database_query,
    cache_expensive_operation,
    check_system_dependencies,
    cleanup_old_files,
    get_system_storage_info,
    get_system_configuration,
    update_system_configuration,
    generate_report_summary,
    format_number_for_display,
    get_color_code_for_status,
    calculate_percentage,
    get_unique_filename
)

from .notification_helpers import (
    format_notification_message,
    get_notification_recipients,
    queue_notification,
    get_notification_templates,
    get_notification_settings_for_employee,
    check_notification_time_window,
    create_notification_channels,
    log_notification_delivery,
    get_notification_statistics
)

# Export all functions for easy importing
__all__ = [
    # Image processing functions
    'enhance_image_quality',
    'validate_face_image_quality',
    'compress_image_for_storage',
    'convert_base64_to_cv2', 
    'convert_cv2_to_base64',
    'detect_anti_spoofing',
    
    # Data validation functions
    'validate_employee_data',
    'validate_attendance_data',
    'sanitize_input_data',
    'generate_secure_hash',
    'verify_data_integrity',
    'validate_phone_number',
    'validate_working_hours_data',
    'validate_recognition_settings',
    'validate_payroll_data',
    'validate_notification_data',
    'validate_kiosk_data',
    'format_currency',
    
    # Utility functions
    'get_working_days_in_period',
    'calculate_time_difference',
    'format_duration',
    'get_pay_period_dates',
    'get_current_fiscal_year',
    'convert_timezone',
    'export_to_csv_helper',
    'export_to_json_helper',
    'save_file_from_base64',
    'measure_performance',
    'optimize_database_query',
    'cache_expensive_operation',
    'check_system_dependencies',
    'cleanup_old_files',
    'get_system_storage_info',
    'get_system_configuration',
    'update_system_configuration',
    'generate_report_summary',
    'format_number_for_display',
    'get_color_code_for_status',
    'calculate_percentage',
    'get_unique_filename',
    
    # Notification functions
    'format_notification_message',
    'get_notification_recipients',
    'queue_notification',
    'get_notification_templates',
    'get_notification_settings_for_employee',
    'check_notification_time_window',
    'create_notification_channels',
    'log_notification_delivery',
    'get_notification_statistics'
]

# Additional consolidated helper functions that combine multiple operations

@frappe.whitelist()
def process_employee_registration(employee_data, face_images):
    """Complete employee registration with validation and face processing"""
    try:
        # Validate employee data
        validation_errors = validate_employee_data(employee_data)
        if validation_errors:
            return {"success": False, "errors": validation_errors}
        
        # Validate and process face images
        processed_images = []
        for i, image_data in enumerate(face_images):
            validation_result = validate_face_image_quality(image_data)
            if not validation_result["valid"]:
                return {"success": False, "message": f"Image {i+1}: {validation_result['reason']}"}
            
            # Compress and store image
            compressed_image = compress_image_for_storage(image_data)
            processed_images.append(compressed_image)
        
        return {
            "success": True,
            "processed_images": processed_images,
            "employee_data": sanitize_input_data(employee_data)
        }
        
    except Exception as e:
        frappe.log_error(f"Employee registration processing error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def comprehensive_attendance_validation(attendance_data):
    """Comprehensive validation for attendance data"""
    try:
        # Basic validation
        validation_errors = validate_attendance_data(attendance_data)
        if validation_errors:
            return {"success": False, "errors": validation_errors}
        
        # Check for duplicate attendance
        existing_attendance = frappe.get_all(
            "Employee Attendance",
            filters={
                "employee_id": attendance_data["employee_id"],
                "attendance_date": attendance_data["attendance_date"],
                "attendance_type": attendance_data["attendance_type"]
            },
            limit=1
        )
        
        if existing_attendance:
            return {"success": False, "message": "Duplicate attendance record"}
        
        # Validate working hours if both times present
        if attendance_data.get("check_in_time") and attendance_data.get("check_out_time"):
            hours_worked = calculate_time_difference(
                attendance_data["check_in_time"], 
                attendance_data["check_out_time"]
            )
            
            if hours_worked > 16:  # More than 16 hours
                return {"success": False, "message": "Working hours exceed maximum limit"}
        
        return {"success": True, "validated_data": sanitize_input_data(attendance_data)}
        
    except Exception as e:
        frappe.log_error(f"Attendance validation error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def export_data_to_format(data, format_type, filename=None):
    """Export data to various formats with comprehensive options"""
    try:
        if format_type.lower() == "csv":
            return export_to_csv_helper(data, filename)
        elif format_type.lower() == "json":
            return export_to_json_helper(data, filename)
        elif format_type.lower() == "excel":
            return export_to_excel_helper(data, filename)
        elif format_type.lower() == "pdf":
            return export_to_pdf_helper(data, filename)
        else:
            return {"success": False, "message": f"Unsupported format: {format_type}"}
            
    except Exception as e:
        frappe.log_error(f"Data export error: {str(e)}")
        return {"success": False, "message": str(e)}

def export_to_excel_helper(data, filename=None):
    """Export data to Excel format with formatting"""
    try:
        import xlsxwriter
        import io
        
        if not data:
            return {"success": False, "message": "No data to export"}
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Data")
        
        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })
        
        data_format = workbook.add_format({'border': 1})
        
        # Write headers
        if data:
            headers = list(data[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Write data
            for row_num, record in enumerate(data, 1):
                for col, header in enumerate(headers):
                    value = record.get(header, "")
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    worksheet.write(row_num, col, value, data_format)
        
        workbook.close()
        output.seek(0)
        
        # Save as file
        if not filename:
            filename = get_unique_filename("export", "xlsx")
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": output.getvalue(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "filename": filename,
            "records_exported": len(data)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

def export_to_pdf_helper(data, filename=None):
    """Export data to PDF format"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        import io
        
        if not data:
            return {"success": False, "message": "No data to export"}
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        
        # Prepare data for table
        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            
            for record in data:
                row = []
                for header in headers:
                    value = record.get(header, "")
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    row.append(str(value))
                table_data.append(row)
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            # Build PDF
            elements = [table]
            doc.build(elements)
        
        output.seek(0)
        
        # Save as file
        if not filename:
            filename = get_unique_filename("export", "pdf")
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": output.getvalue(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "filename": filename,
            "records_exported": len(data)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_comprehensive_system_status():
    """Get comprehensive system status combining all health checks"""
    try:
        status = {}
        
        # System dependencies
        status["dependencies"] = check_system_dependencies()
        
        # Storage information
        status["storage"] = get_system_storage_info()
        
        # System configuration
        status["configuration"] = get_system_configuration()
        
        # Recent activity statistics
        status["activity"] = {
            "today_attendance": frappe.db.count("Employee Attendance", {
                "attendance_date": frappe.utils.today()
            }),
            "active_employees": frappe.db.count("Employee Face Recognition", {
                "status": "Active"
            }),
            "active_kiosks": frappe.db.count("Attendance Kiosk", {
                "is_active": 1
            })
        }
        
        # Calculate overall health score
        health_score = calculate_system_health_score(status)
        status["overall_health"] = health_score
        
        return {"success": True, "status": status}
        
    except Exception as e:
        frappe.log_error(f"System status error: {str(e)}")
        return {"success": False, "message": str(e)}

def calculate_system_health_score(status):
    """Calculate overall system health score"""
    try:
        score = 100
        
        # Dependencies check (30% weight)
        deps = status.get("dependencies", {})
        required_deps = ["face_recognition", "cv2", "numpy", "PIL"]
        missing_deps = [dep for dep in required_deps if not deps.get(dep, False)]
        score -= len(missing_deps) * 7.5  # -7.5 points per missing dependency
        
        # Storage check (20% weight)
        storage = status.get("storage", {})
        disk_usage = storage.get("disk_usage", {})
        usage_pct = disk_usage.get("usage_percentage", 0)
        if usage_pct > 90:
            score -= 20
        elif usage_pct > 80:
            score -= 10
        
        # Activity check (30% weight)
        activity = status.get("activity", {})
        if activity.get("active_employees", 0) == 0:
            score -= 30
        elif activity.get("active_kiosks", 0) == 0:
            score -= 15
        
        # Configuration check (20% weight)
        config = status.get("configuration", {})
        if not config:
            score -= 20
        
        return max(0, min(100, score))
        
    except Exception as e:
        frappe.log_error(f"Health score calculation error: {str(e)}")
        return 0

# Convenience functions for common operations
def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        frappe.log_error(f"Safe execution error in {func.__name__}: {str(e)}")
        return None

def batch_process(items, process_func, batch_size=100):
    """Process items in batches to avoid memory issues"""
    try:
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [safe_execute(process_func, item) for item in batch]
            results.extend([r for r in batch_results if r is not None])
        return results
    except Exception as e:
        frappe.log_error(f"Batch processing error: {str(e)}")
        return []