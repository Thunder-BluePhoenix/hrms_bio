import frappe
from frappe import _
import json
import base64
import cv2
import numpy as np
from datetime import datetime, timedelta
import calendar
import os
import hashlib

# ================================
# IMAGE PROCESSING HELPERS
# ================================

def enhance_image_quality(image):
    """Enhanced image processing for better face recognition"""
    try:
        # Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to color if original was color
        if len(image.shape) == 3:
            enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
            # Blend with original
            alpha = 0.7
            beta = 0.3
            enhanced = cv2.addWeighted(image, alpha, enhanced, beta, 0)
        else:
            enhanced = enhanced_gray
        
        # Apply Gaussian blur to reduce noise
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Sharpen the image
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
        
    except Exception as e:
        frappe.log_error(f"Image enhancement error: {str(e)}")
        return image

def validate_face_image_quality(image_data):
    """Validate face image quality before storing"""
    try:
        # Decode image
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = base64.b64decode(image_data.split(',')[1])
            else:
                image_data = base64.b64decode(image_data)
        
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"valid": False, "reason": "Invalid image format"}
        
        # Check image dimensions
        height, width = image.shape[:2]
        if width < 200 or height < 200:
            return {"valid": False, "reason": "Image too small (minimum 200x200)"}
        
        if width > 2000 or height > 2000:
            return {"valid": False, "reason": "Image too large (maximum 2000x2000)"}
        
        # Check for face presence
        import face_recognition
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return {"valid": False, "reason": "No face detected in image"}
        
        if len(face_locations) > 1:
            return {"valid": False, "reason": "Multiple faces detected. Please use single face image"}
        
        # Check face size relative to image
        top, right, bottom, left = face_locations[0]
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        image_area = width * height
        face_ratio = face_area / image_area
        
        if face_ratio < 0.1:
            return {"valid": False, "reason": "Face too small in image"}
        
        # Check image blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if blur_score < 100:
            return {"valid": False, "reason": "Image is too blurry"}
        
        # Check brightness
        brightness = np.mean(gray)
        if brightness < 50:
            return {"valid": False, "reason": "Image too dark"}
        if brightness > 200:
            return {"valid": False, "reason": "Image too bright"}
        
        return {
            "valid": True,
            "quality_score": min(100, (blur_score / 500) * 100),
            "face_ratio": face_ratio,
            "brightness": brightness
        }
        
    except Exception as e:
        return {"valid": False, "reason": f"Error validating image: {str(e)}"}

def compress_image_for_storage(image_data, quality=85):
    """Compress image for efficient storage"""
    try:
        # Decode image
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = base64.b64decode(image_data.split(',')[1])
            else:
                image_data = base64.b64decode(image_data)
        
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        # Resize if too large
        height, width = image.shape[:2]
        max_dimension = 800
        
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Compress image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, compressed_image = cv2.imencode('.jpg', image, encode_param)
        
        # Convert back to base64
        compressed_base64 = base64.b64encode(compressed_image.tobytes()).decode('utf-8')
        
        return f"data:image/jpeg;base64,{compressed_base64}"
        
    except Exception as e:
        frappe.log_error(f"Image compression error: {str(e)}")
        return image_data

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

# ================================
# DATA VALIDATION HELPERS
# ================================

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
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
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

# ================================
# SECURITY HELPERS
# ================================

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
            import re
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

# ================================
# NOTIFICATION HELPERS
# ================================

def format_notification_message(template, data):
    """Format notification message with data"""
    try:
        # Replace placeholders in template
        message = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))
        
        return message
        
    except Exception as e:
        frappe.log_error(f"Message formatting error: {str(e)}")
        return template

def get_notification_recipients(employee_id, notification_type):
    """Get notification recipients based on type"""
    try:
        recipients = []
        
        # Get employee settings
        settings = frappe.get_value(
            "Employee Notification Settings",
            employee_id,
            ["email_enabled", "sms_enabled", "push_enabled", "whatsapp_enabled"],
            as_dict=True
        )
        
        if not settings:
            return recipients
        
        # Get employee contact info
        employee = frappe.get_doc("Employee Face Recognition", employee_id)
        
        # Add based on enabled channels
        if settings.get('email_enabled') and employee.email:
            recipients.append({
                "type": "email",
                "address": employee.email,
                "name": employee.employee_name
            })
        
        if settings.get('sms_enabled') and employee.mobile:
            recipients.append({
                "type": "sms",
                "address": employee.mobile,
                "name": employee.employee_name
            })
        
        if settings.get('whatsapp_enabled') and employee.mobile:
            recipients.append({
                "type": "whatsapp",
                "address": employee.mobile,
                "name": employee.employee_name
            })
        
        return recipients
        
    except Exception as e:
        frappe.log_error(f"Recipients lookup error: {str(e)}")
        return []

def queue_notification(employee_id, notification_type, data, priority="normal"):
    """Queue notification for processing"""
    try:
        notification_doc = frappe.new_doc("Notification Activity Log")
        notification_doc.employee_id = employee_id
        notification_doc.event_type = notification_type
        notification_doc.priority_level = priority.title()
        notification_doc.notification_status = "Pending"
        notification_doc.notifications_data = json.dumps(data)
        notification_doc.insert(ignore_permissions=True)
        
        # Queue for background processing
        frappe.enqueue(
            'bio_facerecognition.bio_facerecognition.api.mobile_notifications.send_attendance_notification',
            employee_id=employee_id,
            attendance_type=notification_type,
            attendance_time=data.get('timestamp', datetime.now()),
            kiosk_location=data.get('location', 'Unknown'),
            queue='default',
            timeout=300
        )
        
        return notification_doc.name
        
    except Exception as e:
        frappe.log_error(f"Notification queuing error: {str(e)}")
        return None

# ================================
# PERFORMANCE HELPERS
# ================================

def measure_performance(func):
    """Decorator to measure function performance"""
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

def export_data_to_format(data, format_type, filename=None):
    """Export data to various formats"""
    try:
        if format_type.lower() == "csv":
            return export_to_csv_helper(data, filename)
        elif format_type.lower() == "excel":
            return export_to_excel_helper(data, filename)
        elif format_type.lower() == "json":
            return export_to_json_helper(data, filename)
        elif format_type.lower() == "pdf":
            return export_to_pdf_helper(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
            
    except Exception as e:
        frappe.log_error(f"Data export error: {str(e)}")
        return {"success": False, "message": str(e)}

def export_to_csv_helper(data, filename=None):
    """Export data to CSV format"""
    try:
        import csv
        import io
        
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
            "records_exported": len(data)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

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
        import shutil
        
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

# ================================
# SECURITY HELPERS
# ================================

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
            import re
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

# ================================
# NOTIFICATION HELPERS
# ================================

def format_notification_message(template, data):
    """Format notification message with data"""
    try:
        # Replace placeholders in template
        message = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))
        
        return message
        
    except Exception as e:
        frappe.log_error(f"Message formatting error: {str(e)}")
        return template

def get_notification_recipients(employee_id, notification_type):
    """Get notification recipients based on type"""
    try:
        recipients = []
        
        # Get employee settings
        settings = frappe.get_value(
            "Employee Notification Settings",
            employee_id,
            ["email_enabled", "sms_enabled", "push_enabled", "whatsapp_enabled"],
            as_dict=True
        )
        
        if not settings:
            return recipients
        
        # Get employee contact info
        employee = frappe.get_doc("Employee Face Recognition", employee_id)
        
        # Add based on enabled channels
        if settings.get('email_enabled') and employee.email:
            recipients.append({
                "type": "email",
                "address": employee.email,
                "name": employee.employee_name
            })
        
        if settings.get('sms_enabled') and employee.mobile:
            recipients.append({
                "type": "sms",
                "address": employee.mobile,
                "name": employee.employee_name
            })
        
        if settings.get('whatsapp_enabled') and employee.mobile:
            recipients.append({
                "type": "whatsapp",
                "address": employee.mobile,
                "name": employee.employee_name
            })
        
        return recipients
        
    except Exception as e:
        frappe.log_error(f"Recipients lookup error: {str(e)}")
        return []

def queue_notification(employee_id, notification_type, data, priority="normal"):
    """Queue notification for processing"""
    try:
        notification_doc = frappe.new_doc("Notification Activity Log")
        notification_doc.employee_id = employee_id
        notification_doc.event_type = notification_type
        notification_doc.priority_level = priority.title()
        notification_doc.notification_status = "Pending"
        notification_doc.notifications_data = json.dumps(data)
        notification_doc.insert(ignore_permissions=True)
        
        # Queue for background processing
        frappe.enqueue(
            'bio_facerecognition.bio_facerecognition.api.mobile_notifications.send_attendance_notification',
            employee_id=employee_id,
            attendance_type=notification_type,
            attendance_time=data.get('timestamp', datetime.now()),
            kiosk_location=data.get('location', 'Unknown'),
            queue='default',
            timeout=300
        )
        
        return notification_doc.name
        
    except Exception as e:
        frappe.log_error(f"Notification queuing error: {str(e)}")
        return None

# ================================
# PERFORMANCE HELPERS
# ================================

def measure_performance(func):
    """Decorator to measure function performance"""
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

def export_data_to_format(data, format_type, filename=None):
    """Export data to various formats"""
    try:
        if format_type.lower() == "csv":
            return export_to_csv_helper(data, filename)
        elif format_type.lower() == "excel":
            return export_to_excel_helper(data, filename)
        elif format_type.lower() == "json":
            return export_to_json_helper(data, filename)
        elif format_type.lower() == "pdf":
            return export_to_pdf_helper(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
            
    except Exception as e:
        frappe.log_error(f"Data export error: {str(e)}")
        return {"success": False, "message": str(e)}

def export_to_csv_helper(data, filename=None):
    """Export data to CSV format"""
    try:
        import csv
        import io
        
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
            "records_exported": len(data)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

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
        import shutil
        
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