import frappe
import cv2
import face_recognition
import base64
import numpy as np
import json
from datetime import datetime, timedelta
import os
from PIL import Image
from io import BytesIO
import logging
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@frappe.whitelist()
def process_face_encoding_on_save(doc, method=None):
    """Process and store face encodings when Employee Face Recognition doc is saved."""
    try:
        encodings = []
        image_fields = ['face_image_1', 'face_image_2', 'face_image_3', 'face_image_4', 'face_image_5']
        
        for field in image_fields:
            if doc.get(field):
                try:
                    # Get file content
                    file_path = doc.get(field)
                    if file_path:
                        file_doc = frappe.get_doc("File", {"file_url": file_path})
                        if file_doc:
                            image_content = file_doc.get_content()
                            if image_content:
                                # Process the image
                                encoding = extract_face_encoding(image_content)
                                if encoding is not None:
                                    encodings.append(encoding.tolist())
                except Exception as e:
                    logger.error(f"Error processing {field}: {str(e)}")
                    continue
        
        if encodings:
            # Store encodings as JSON
            doc.encoding_data = json.dumps(encodings)
            logger.info(f"Stored {len(encodings)} face encodings for employee {doc.employee_id}")
        else:
            frappe.throw("No valid face encodings could be extracted from the uploaded images.")
            
    except Exception as e:
        logger.error(f"Error in process_face_encoding_on_save: {str(e)}")
        frappe.throw(f"Error processing face encodings: {str(e)}")

def extract_face_encoding(image_data):
    """Extract face encoding from image data with enhanced accuracy."""
    try:
        # Handle different image data formats
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                # Base64 with data URI
                image_data = base64.b64decode(image_data.split(',')[1])
            else:
                # Try to decode as base64
                try:
                    image_data = base64.b64decode(image_data)
                except:
                    # If not base64, treat as file path or raw data
                    pass
        
        # Convert to numpy array
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.error("Could not decode image")
            return None
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Enhance image quality
        rgb_image = enhance_image_quality(rgb_image)
        
        # Find face locations with multiple models for better accuracy
        face_locations = face_recognition.face_locations(
            rgb_image, 
            model="cnn",  # Use CNN model for better accuracy
            number_of_times_to_upsample=2  # Upsample for better detection
        )
        
        if not face_locations:
            # Try with HOG model if CNN fails
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
        
        if not face_locations:
            logger.warning("No face detected in image")
            return None
        
        # Get face encodings with enhanced parameters
        face_encodings = face_recognition.face_encodings(
            rgb_image,
            face_locations,
            num_jitters=100,  # More jitters for better accuracy
            model="large"     # Use large model for better accuracy
        )
        
        if face_encodings:
            return face_encodings[0]
        else:
            logger.warning("Could not generate face encoding")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting face encoding: {str(e)}")
        return None

# def enhance_image_quality(image):
#     """Enhance image quality for better face recognition."""
#     try:
#         # Convert to grayscale and back to RGB for contrast enhancement
#         gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
#         # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
#         clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#         enhanced_gray = clahe.apply(gray)
        
#         # Convert back to RGB
#         enhanced_rgb = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
        
#         # Blend with original image
#         alpha = 0.7  # Weight for original image
#         beta = 0.3   # Weight for enhanced image
#         blended = cv2.addWeighted(image, alpha, enhanced_rgb, beta, 0)
        
#         return blended
#     except:
#         return image

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

@frappe.whitelist()
def recognize_face_from_camera(captured_image, kiosk_name=None):
    """Recognize face from camera capture with enhanced accuracy."""
    try:
        if not captured_image:
            return {"success": False, "message": "No image provided"}
        
        # Decode captured image
        captured_face_encoding = extract_face_encoding(captured_image)
        
        if captured_face_encoding is None:
            return {"success": False, "message": "No face detected in captured image. Please ensure your face is clearly visible."}
        
        # Get all active employees with face encodings
        employees = frappe.get_all(
            "Employee Face Recognition",
            filters={"status": "Active", "encoding_data": ["!=", ""]},
            fields=["name", "employee_id", "employee_name", "department", "designation", "encoding_data"]
        )
        
        if not employees:
            return {"success": False, "message": "No employees registered for face recognition"}
        
        best_match = None
        best_distance = float('inf')
        min_confidence_threshold = 0.4  # Lower is better for face_recognition library
        
        for employee in employees:
            try:
                if not employee.encoding_data:
                    continue
                    
                stored_encodings = json.loads(employee.encoding_data)
                
                for encoding_data in stored_encodings:
                    if not encoding_data:
                        continue
                        
                    stored_encoding = np.array(encoding_data)
                    
                    # Calculate face distance
                    distance = face_recognition.face_distance([stored_encoding], captured_face_encoding)[0]
                    
                    # Check if this is the best match so far
                    if distance < best_distance and distance < min_confidence_threshold:
                        best_distance = distance
                        best_match = employee
                        
            except Exception as e:
                logger.error(f"Error comparing with employee {employee.employee_id}: {str(e)}")
                continue
        
        if best_match:
            # Calculate confidence percentage (convert distance to confidence)
            confidence = max(0, (1 - best_distance) * 100)
            
            # Log attendance
            attendance_result = log_attendance(
                best_match, 
                captured_image, 
                confidence, 
                kiosk_name
            )
            
            return {
                "success": True,
                "employee": {
                    "employee_id": best_match.employee_id,
                    "employee_name": best_match.employee_name,
                    "department": best_match.department,
                    "designation": best_match.designation
                },
                "confidence": round(confidence, 2),
                "attendance": attendance_result,
                "message": f"Welcome {best_match.employee_name}!"
            }
        else:
            return {
                "success": False, 
                "message": "Face not recognized. Please ensure you are registered in the system."
            }
            
    except Exception as e:
        logger.error(f"Error in recognize_face_from_camera: {str(e)}")
        return {"success": False, "message": f"System error: {str(e)}"}

def log_attendance(employee, captured_image, confidence, kiosk_name):
    """Log attendance for recognized employee."""
    try:
        current_time = datetime.now()
        current_date = current_time.date()
        
        # Check if there's already an attendance record for today
        existing_attendance = frappe.get_all(
            "Employee Attendance",
            filters={
                "employee_id": employee.employee_id,
                "attendance_date": current_date
            },
            fields=["name", "check_in_time", "check_out_time", "attendance_type"],
            order_by="creation desc",
            limit=1
        )
        
        attendance_type = "Check In"
        doc_name = None
        
        if existing_attendance:
            last_record = existing_attendance[0]
            if last_record.check_in_time and not last_record.check_out_time:
                # Employee has checked in but not checked out
                attendance_type = "Check Out"
                doc_name = last_record.name
        
        if doc_name:
            # Update existing record with check out
            doc = frappe.get_doc("Employee Attendance", doc_name)
            doc.check_out_time = current_time
            doc.attendance_type = "Check Out"
            
            # Calculate total hours
            if doc.check_in_time:
                time_diff = current_time - doc.check_in_time
                doc.total_hours = round(time_diff.total_seconds() / 3600, 2)
            
            doc.save(ignore_permissions=True)
        else:
            # Create new attendance record
            doc = frappe.new_doc("Employee Attendance")
            doc.employee_id = employee.employee_id
            doc.employee_name = employee.employee_name
            doc.department = employee.department
            doc.attendance_date = current_date
            doc.check_in_time = current_time
            doc.attendance_type = "Check In"
            doc.kiosk_location = kiosk_name or "Unknown"
            doc.confidence_score = confidence
            doc.verification_status = "Verified"
            doc.created_by_system = 1
            
            # Save captured image
            if captured_image:
                try:
                    # Save the captured image as attachment
                    file_doc = save_captured_image(captured_image, employee.employee_id, current_time)
                    if file_doc:
                        doc.face_image_captured = file_doc.file_url
                except Exception as e:
                    logger.error(f"Error saving captured image: {str(e)}")
            
            doc.save(ignore_permissions=True)
            doc.submit()
        
        frappe.db.commit()
        
        return {
            "type": attendance_type,
            "time": current_time.strftime("%H:%M:%S"),
            "date": current_date.strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        logger.error(f"Error logging attendance: {str(e)}")
        frappe.db.rollback()
        return {"error": str(e)}

def save_captured_image(image_data, employee_id, timestamp):
    """Save captured image as file attachment."""
    try:
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # Generate filename
        filename = f"attendance_{employee_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
        
        # Create file doc
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": image_bytes,
            "is_private": 1
        })
        file_doc.save(ignore_permissions=True)
        
        return file_doc
        
    except Exception as e:
        logger.error(f"Error saving captured image: {str(e)}")
        return None

@frappe.whitelist()
def get_attendance_stats(employee_id=None):
    """Get attendance statistics."""
    try:
        filters = {}
        if employee_id:
            filters["employee_id"] = employee_id
            
        # Get today's attendance count
        today_count = frappe.db.count(
            "Employee Attendance",
            filters={**filters, "attendance_date": datetime.now().date()}
        )
        
        # Get this week's attendance count
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        week_count = frappe.db.count(
            "Employee Attendance",
            filters={
                **filters,
                "attendance_date": ["between", [week_start, datetime.now().date()]]
            }
        )
        
        # Get this month's attendance count
        month_start = datetime.now().replace(day=1).date()
        month_count = frappe.db.count(
            "Employee Attendance",
            filters={
                **filters,
                "attendance_date": ["between", [month_start, datetime.now().date()]]
            }
        )
        
        return {
            "today": today_count,
            "this_week": week_count,
            "this_month": month_count
        }
        
    except Exception as e:
        logger.error(f"Error getting attendance stats: {str(e)}")
        return {"today": 0, "this_week": 0, "this_month": 0}

@frappe.whitelist()
def test_face_recognition_system():
    """Test endpoint for face recognition system."""
    try:
        # Count registered employees
        employee_count = frappe.db.count("Employee Face Recognition", {"status": "Active"})
        
        # Count attendance records today
        today_attendance = frappe.db.count(
            "Employee Attendance", 
            {"attendance_date": datetime.now().date()}
        )
        
        return {
            "success": True,
            "system_status": "Active",
            "registered_employees": employee_count,
            "today_attendance": today_attendance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    




# ANALYSIS: Potential Issues & Improvements for Check-in/Check-out Logic

"""
CURRENT SYSTEM ANALYSIS:
Your current log_attendance() function has good basic logic but could be enhanced
"""

# ISSUE 1: Same Day Multiple Check-ins
# Current logic only looks for latest record, but what if:
# - Employee checks in at 9 AM
# - Goes for lunch break at 1 PM (should be check-out)  
# - Returns from lunch at 2 PM (should be check-in again)
# - Leaves office at 6 PM (final check-out)

def enhanced_log_attendance(employee, captured_image, confidence, kiosk_name):
    """Enhanced attendance logging with better logic"""
    try:
        current_time = datetime.now()
        current_date = current_time.date()
        
        # Get ALL attendance records for today (not just latest)
        existing_attendance = frappe.get_all(
            "Employee Attendance",
            filters={
                "employee_id": employee.employee_id,
                "attendance_date": current_date
            },
            fields=["name", "check_in_time", "check_out_time", "attendance_type", "creation"],
            order_by="check_in_time desc"  # Order by actual check-in time
        )
        
        # IMPROVED LOGIC: Determine check-in vs check-out based on pattern
        attendance_type = determine_attendance_type(existing_attendance, current_time)
        
        # IMPROVEMENT: Minimum time gap between check-ins (prevent accidental double-taps)
        if not validate_minimum_time_gap(existing_attendance, current_time):
            return {
                "success": False,
                "message": "Please wait at least 5 minutes between check-ins"
            }
        
        # IMPROVEMENT: Handle break times
        if attendance_type == "Check Out":
            # Update the latest incomplete record
            incomplete_record = get_incomplete_attendance_record(existing_attendance)
            if incomplete_record:
                update_checkout_record(incomplete_record, current_time, captured_image, confidence)
            else:
                return {"success": False, "message": "No active check-in found"}
                
        else:  # Check In
            create_checkin_record(employee, current_time, captured_image, confidence, kiosk_name)
            
        # IMPROVEMENT: Send contextual notifications
        # send_smart_notification(employee, attendance_type, current_time, existing_attendance)
        
        return {
            "success": True,
            "attendance_type": attendance_type,
            "time": current_time,
            "message": f"{attendance_type} recorded successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Enhanced attendance logging error: {str(e)}")
        return {"success": False, "message": str(e)}

def determine_attendance_type(existing_records, current_time):
    """Smarter logic to determine if this should be check-in or check-out"""
    
    if not existing_records:
        return "Check In"  # First entry of the day
    
    # Find the most recent incomplete record
    for record in existing_records:
        if record.check_in_time and not record.check_out_time:
            # There's an active check-in without check-out
            return "Check Out"
    
    # All records are complete (have both check-in and check-out)
    # This could be returning from break/lunch
    return "Check In"

def validate_minimum_time_gap(existing_records, current_time, min_gap_minutes=5):
    """Prevent accidental double-taps by enforcing minimum time gap"""
    
    if not existing_records:
        return True
    
    latest_record = existing_records[0]
    
    # Check against latest check-in time
    if latest_record.check_in_time:
        time_diff = current_time - latest_record.check_in_time
        if time_diff.total_seconds() < (min_gap_minutes * 60):
            return False
    
    # Check against latest check-out time if exists
    if latest_record.check_out_time:
        time_diff = current_time - latest_record.check_out_time
        if time_diff.total_seconds() < (min_gap_minutes * 60):
            return False
    
    return True

def get_incomplete_attendance_record(existing_records):
    """Find the most recent attendance record without check-out"""
    for record in existing_records:
        if record.check_in_time and not record.check_out_time:
            return frappe.get_doc("Employee Attendance", record.name)
    return None

def update_checkout_record(doc, current_time, captured_image, confidence):
    """Update existing record with check-out information"""
    doc.check_out_time = current_time
    doc.attendance_type = "Check Out"
    
    # Calculate working hours
    if doc.check_in_time:
        time_diff = current_time - doc.check_in_time
        doc.total_hours = round(time_diff.total_seconds() / 3600, 2)
    
    # Add check-out image if needed
    if captured_image:
        doc.face_image_captured = captured_image
    
    doc.confidence_score = confidence
    doc.save(ignore_permissions=True)

def create_checkin_record(employee, current_time, captured_image, confidence, kiosk_name):
    """Create new check-in record"""
    doc = frappe.new_doc("Employee Attendance")
    doc.employee_id = employee.employee_id
    doc.employee_name = employee.employee_name
    doc.department = employee.department
    doc.attendance_date = current_time.date()
    doc.check_in_time = current_time
    doc.attendance_type = "Check In"
    doc.kiosk_location = kiosk_name or "Unknown"
    doc.confidence_score = confidence
    doc.verification_status = "Verified"
    doc.created_by_system = 1
    
    if captured_image:
        doc.face_image_captured = captured_image
    
    doc.insert(ignore_permissions=True)

def send_smart_notification(employee, attendance_type, current_time, existing_records):
    """Send contextual notifications based on attendance patterns"""
    
    # Check if this is late arrival (after 9:30 AM for example)
    if attendance_type == "Check In" and current_time.time() > time(9, 30):
        send_late_arrival_notification(employee, current_time)
    
    # Check if this is early departure (before 5:30 PM for example)
    elif attendance_type == "Check Out" and current_time.time() < time(17, 30):
        send_early_departure_notification(employee, current_time)
    
    # Check for overtime (after 7 PM for example)
    elif attendance_type == "Check Out" and current_time.time() > time(19, 0):
        send_overtime_notification(employee, current_time, existing_records)

# ISSUE 2: Handling Multiple Locations
def validate_location_consistency(employee_id, current_location, current_date):
    """Ensure employee isn't checking in from multiple locations simultaneously"""
    
    active_checkins = frappe.get_all(
        "Employee Attendance",
        filters={
            "employee_id": employee_id,
            "attendance_date": current_date,
            "check_in_time": ["is", "set"],
            "check_out_time": ["is", "not set"]
        },
        fields=["kiosk_location", "check_in_time"]
    )
    
    for checkin in active_checkins:
        if checkin.kiosk_location != current_location:
            return False, f"You are still checked in at {checkin.kiosk_location}"
    
    return True, "Location validation passed"

# ISSUE 3: Break Time Handling
def detect_break_patterns(existing_records, current_time):
    """Detect if this might be a break check-out/check-in"""
    
    if not existing_records:
        return False
    
    latest_checkin = None
    for record in existing_records:
        if record.check_in_time and not record.check_out_time:
            latest_checkin = record.check_in_time
            break
    
    if latest_checkin:
        time_since_checkin = current_time - latest_checkin
        # If it's been 3-5 hours since check-in, might be lunch break
        if 3 <= time_since_checkin.total_seconds() / 3600 <= 5:
            return True
    
    return False

# ISSUE 4: Overnight Shift Handling
def handle_overnight_shifts(employee, current_time, existing_records):
    """Handle employees working overnight shifts"""
    
    # Check if employee has overnight shift pattern
    shift_settings = get_employee_shift_settings(employee.employee_id)
    
    if shift_settings and shift_settings.is_overnight_shift:
        # For overnight shifts, attendance date should be the shift start date
        # not the current date
        return calculate_overnight_attendance_date(current_time, shift_settings)
    
    return current_time.date()

def get_employee_shift_settings(employee_id):
    """Get employee's shift configuration"""
    # This would integrate with ERPNext's Shift Management
    return frappe.get_value("Employee", employee_id, 
                          ["shift_type", "default_shift"], as_dict=True)

# ISSUE 5: Data Integrity Checks
def validate_attendance_data_integrity(employee_id, attendance_date):
    """Ensure attendance data is consistent"""
    
    records = frappe.get_all(
        "Employee Attendance",
        filters={
            "employee_id": employee_id,
            "attendance_date": attendance_date
        },
        fields=["check_in_time", "check_out_time", "total_hours"],
        order_by="check_in_time"
    )
    
    issues = []
    
    for i, record in enumerate(records):
        # Check for overlapping times
        if i > 0:
            prev_record = records[i-1]
            if (prev_record.check_out_time and record.check_in_time and 
                record.check_in_time < prev_record.check_out_time):
                issues.append(f"Overlapping attendance times detected")
        
        # Validate total hours calculation
        if record.check_in_time and record.check_out_time:
            calculated_hours = (record.check_out_time - record.check_in_time).total_seconds() / 3600
            if abs(calculated_hours - (record.total_hours or 0)) > 0.1:
                issues.append(f"Total hours mismatch in record")
    
    return issues