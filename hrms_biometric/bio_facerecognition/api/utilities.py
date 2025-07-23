# hrms_biometric/bio_facerecognition/api/utilities.py

import frappe
from frappe import _
import json
import csv
import io
from datetime import datetime, timedelta
import calendar
import shutil
import os
from functools import wraps
import base64

# ================================
# DATE AND TIME HELPERS
# ================================

def get_working_days_in_period(start_date, end_date, include_weekends=False):
    """Get number of working days in a period"""
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        working_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if include_weekends or current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                working_days.append(current_date)
            current_date += timedelta(days=1)
        
        return working_days
        
    except Exception as e:
        frappe.log_error(f"Working days calculation error: {str(e)}")
        return []

def calculate_time_difference(start_time, end_time):
    """Calculate time difference in hours"""
    try:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        
        time_diff = end_time - start_time
        hours = time_diff.total_seconds() / 3600
        
        return round(hours, 2)
        
    except Exception as e:
        frappe.log_error(f"Time difference calculation error: {str(e)}")
        return 0

def format_duration(seconds):
    """Format duration in human readable format"""
    try:
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
        
    except:
        return "0s"

def get_pay_period_dates(month, year):
    """Get start and end dates for a pay period"""
    try:
        start_date = datetime(int(year), int(month), 1).date()
        _, last_day = calendar.monthrange(int(year), int(month))
        end_date = datetime(int(year), int(month), last_day).date()
        
        return start_date, end_date
        
    except Exception as e:
        frappe.log_error(f"Pay period calculation error: {str(e)}")
        return None, None

def get_current_fiscal_year():
    """Get current fiscal year based on company settings"""
    try:
        # Default to April-March fiscal year for India
        today = datetime.now().date()
        if today.month >= 4:
            return f"{today.year}-{today.year + 1}"
        else:
            return f"{today.year - 1}-{today.year}"
    except:
        return str(datetime.now().year)

def convert_timezone(dt, from_tz="UTC", to_tz="Asia/Kolkata"):
    """Convert datetime between timezones"""
    try:
        import pytz
        
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # Localize if naive datetime
        if dt.tzinfo is None:
            dt = from_timezone.localize(dt)
        
        # Convert to target timezone
        converted_dt = dt.astimezone(to_timezone)
        
        return converted_dt
        
    except Exception as e:
        frappe.log_error(f"Timezone conversion error: {str(e)}")
        return dt

# ================================
# FILE OPERATIONS
# ================================

def export_to_csv_helper(data, filename=None):
    """Export data to CSV format"""
    try:
        if not data:
            return {"success": False, "message": "No data to export"}
        
        output = io.StringIO()
        
        # Get field names from first record
        fieldnames = list(data[0].keys()) if data else []
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            # Convert datetime objects to strings
            formatted_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    formatted_row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_row[key] = value
            writer.writerow(formatted_row)
        
        csv_content = output.getvalue()
        output.close()
        
        # Save as file
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": csv_content,
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

def export_to_json_helper(data, filename=None):
    """Export data to JSON format"""
    try:
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        json_content = json.dumps(data, indent=2, default=str)
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": json_content,
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "filename": filename,
            "records_exported": len(data) if isinstance(data, list) else 1
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

def save_file_from_base64(base64_data, filename, is_private=1):
    """Save file from base64 data"""
    try:
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        file_content = base64.b64decode(base64_data)
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": file_content,
            "is_private": is_private
        })
        file_doc.insert(ignore_permissions=True)
        
        return file_doc
        
    except Exception as e:
        frappe.log_error(f"File save error: {str(e)}")
        return None

# ================================
# PERFORMANCE HELPERS
# ================================

def measure_performance(func):
    """Decorator to measure function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        # Log performance if it takes too long
        if execution_time > 5:  # More than 5 seconds
            frappe.log_error(f"Slow function: {func.__name__} took {execution_time:.2f} seconds")
        
        return result
    return wrapper

def optimize_database_query(doctype, filters, fields, limit=None):
    """Optimize database queries for better performance"""
    try:
        # Add index hints for common queries
        query_optimizations = {
            "Employee Attendance": {
                "index_fields": ["employee_id", "attendance_date", "creation"],
                "order_by": "creation desc"
            },
            "Employee Face Recognition": {
                "index_fields": ["employee_id", "status"],
                "order_by": "modified desc"
            }
        }
        
        optimization = query_optimizations.get(doctype, {})
        
        # Build optimized query
        query_params = {
            "doctype": doctype,
            "filters": filters,
            "fields": fields or ["*"]
        }
        
        if limit:
            query_params["limit"] = limit
        
        if optimization.get("order_by"):
            query_params["order_by"] = optimization["order_by"]
        
        return frappe.get_all(**query_params)
        
    except Exception as e:
        frappe.log_error(f"Query optimization error: {str(e)}")
        # Fallback to standard query
        return frappe.get_all(doctype, filters=filters, fields=fields, limit=limit)

def cache_expensive_operation(key, operation, timeout=3600):
    """Cache expensive operations"""
    try:
        # Try to get from cache first
        cached_result = frappe.cache().get_value(key)
        if cached_result:
            return json.loads(cached_result)
        
        # Execute operation and cache result
        result = operation()
        frappe.cache().set_value(key, json.dumps(result, default=str), timeout)
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Cache operation error: {str(e)}")
        # Execute operation without caching
        return operation()

# ================================
# SYSTEM HEALTH HELPERS
# ================================

def check_system_dependencies():
    """Check if all system dependencies are available"""
    try:
        dependencies = {
            "face_recognition": False,
            "cv2": False,
            "numpy": False,
            "PIL": False
        }
        
        # Check face_recognition
        try:
            import face_recognition
            dependencies["face_recognition"] = True
        except ImportError:
            pass
        
        # Check OpenCV
        try:
            import cv2
            dependencies["cv2"] = True
        except ImportError:
            pass
        
        # Check NumPy
        try:
            import numpy
            dependencies["numpy"] = True
        except ImportError:
            pass
        
        # Check PIL
        try:
            from PIL import Image
            dependencies["PIL"] = True
        except ImportError:
            pass
        
        return dependencies
        
    except Exception as e:
        frappe.log_error(f"Dependency check error: {str(e)}")
        return {}

def cleanup_old_files(file_type="attendance_images", days_old=30):
    """Cleanup old files to free up space"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        if file_type == "attendance_images":
            # Find old attendance images
            old_files = frappe.get_all(
                "File",
                filters={
                    "creation": ["<", cutoff_date],
                    "file_name": ["like", "%attendance%"]
                },
                fields=["name", "file_url", "file_size"]
            )
        else:
            # Find old files of specified type
            old_files = frappe.get_all(
                "File",
                filters={
                    "creation": ["<", cutoff_date],
                    "file_name": ["like", f"%{file_type}%"]
                },
                fields=["name", "file_url", "file_size"]
            )
        
        deleted_count = 0
        total_size_freed = 0
        
        for file_record in old_files:
            try:
                frappe.delete_doc("File", file_record.name, ignore_permissions=True)
                deleted_count += 1
                total_size_freed += file_record.get("file_size", 0)
            except Exception as e:
                frappe.log_error(f"Error deleting file {file_record.name}: {str(e)}")
        
        frappe.db.commit()
        
        return {
            "success": True,
            "deleted_files": deleted_count,
            "size_freed_mb": round(total_size_freed / (1024 * 1024), 2)
        }
        
    except Exception as e:
        frappe.log_error(f"File cleanup error: {str(e)}")
        return {"success": False, "message": str(e)}

def get_system_storage_info():
    """Get system storage information"""
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage("/")
        
        # Get file counts
        total_files = frappe.db.count("File")
        attendance_images = frappe.db.count("File", {"file_name": ["like", "%attendance%"]})
        face_images = frappe.db.count("File", {"file_name": ["like", "%face%"]})
        
        return {
            "disk_usage": {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percentage": round((used / total) * 100, 2)
            },
            "file_counts": {
                "total_files": total_files,
                "attendance_images": attendance_images,
                "face_images": face_images
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Storage info error: {str(e)}")
        return {"error": str(e)}

# ================================
# CONFIGURATION HELPERS
# ================================

def get_system_configuration():
    """Get current system configuration"""
    try:
        config = frappe.get_single("Face Recognition Settings")
        
        return {
            "recognition_params": {
                "tolerance": config.recognition_tolerance,
                "model": config.recognition_model,
                "jitters": config.num_jitters,
                "detection_model": config.face_detection_model
            },
            "working_hours": {
                "start": config.working_hours_start,
                "end": config.working_hours_end,
                "late_threshold": config.late_arrival_threshold
            },
            "payroll": {
                "hourly_rate": config.default_hourly_rate,
                "overtime_multiplier": config.overtime_multiplier
            },
            "system": {
                "logging_enabled": config.enable_logging,
                "backup_enabled": config.enable_backup,
                "max_concurrent": config.max_concurrent_recognitions
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Configuration retrieval error: {str(e)}")
        return {}

def update_system_configuration(config_updates):
    """Update system configuration"""
    try:
        settings = frappe.get_single("Face Recognition Settings")
        
        for section, updates in config_updates.items():
            for key, value in updates.items():
                field_name = f"{section}_{key}" if section != "system" else key
                if hasattr(settings, field_name):
                    setattr(settings, field_name, value)
        
        settings.save(ignore_permissions=True)
        
        # Clear cache to apply new settings
        frappe.clear_cache()
        
        return {"success": True, "message": "Configuration updated successfully"}
        
    except Exception as e:
        frappe.log_error(f"Configuration update error: {str(e)}")
        return {"success": False, "message": str(e)}

# ================================
# REPORTING HELPERS
# ================================

def generate_report_summary(data, report_type):
    """Generate summary statistics for reports"""
    try:
        summary = {
            "total_records": len(data),
            "date_range": {
                "start": None,
                "end": None
            },
            "key_metrics": {}
        }
        
        if not data:
            return summary
        
        # Extract date range
        if report_type == "attendance":
            dates = [item.get('attendance_date') for item in data if item.get('attendance_date')]
            if dates:
                summary["date_range"]["start"] = min(dates)
                summary["date_range"]["end"] = max(dates)
            
            # Calculate attendance metrics
            unique_employees = len(set([item.get('employee_id') for item in data if item.get('employee_id')]))
            avg_hours = sum([item.get('total_hours', 0) for item in data]) / len(data) if data else 0
            late_arrivals = len([item for item in data if item.get('status') == 'Late'])
            
            summary["key_metrics"] = {
                "unique_employees": unique_employees,
                "average_hours": round(avg_hours, 2),
                "late_arrivals": late_arrivals,
                "punctuality_rate": round((len(data) - late_arrivals) / len(data) * 100, 2) if data else 0
            }
        
        return summary
        
    except Exception as e:
        frappe.log_error(f"Report summary generation error: {str(e)}")
        return {"total_records": 0, "error": str(e)}

def format_number_for_display(number, format_type="decimal"):
    """Format numbers for display"""
    try:
        if format_type == "decimal":
            return f"{number:,.2f}"
        elif format_type == "integer":
            return f"{int(number):,}"
        elif format_type == "percentage":
            return f"{number:.1f}%"
        elif format_type == "currency":
            return f"₹{number:,.2f}"
        else:
            return str(number)
    except:
        return str(number)

def get_color_code_for_status(status):
    """Get color codes for different statuses"""
    color_mapping = {
        "success": "#28a745",
        "warning": "#ffc107", 
        "danger": "#dc3545",
        "info": "#17a2b8",
        "primary": "#007bff",
        "Present": "#28a745",
        "Absent": "#dc3545",
        "Late": "#ffc107",
        "Half Day": "#17a2b8",
        "Active": "#28a745",
        "Inactive": "#6c757d",
        "Verified": "#28a745",
        "Failed": "#dc3545",
        "Pending": "#ffc107"
    }
    
    return color_mapping.get(status, "#6c757d")

def calculate_percentage(part, total):
    """Calculate percentage with error handling"""
    try:
        if total == 0:
            return 0
        return round((part / total) * 100, 2)
    except:
        return 0

def get_unique_filename(base_name, extension):
    """Generate unique filename to avoid conflicts"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{base_name}_{timestamp}.{extension}"
    except:
        return f"{base_name}.{extension}"