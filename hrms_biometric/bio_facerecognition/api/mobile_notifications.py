import frappe
from frappe import _
import requests
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def send_attendance_notification(employee_id, attendance_type, attendance_time, kiosk_location):
    """Send attendance notification via multiple channels"""
    try:
        # Get employee details
        employee = frappe.get_doc("Employee Face Recognition", employee_id)
        
        # Get notification preferences
        notification_settings = get_employee_notification_settings(employee_id)
        
        notifications_sent = []
        
        # Send Email Notification
        if notification_settings.get("email_enabled", True) and employee.email:
            email_result = send_email_notification(
                employee, attendance_type, attendance_time, kiosk_location
            )
            notifications_sent.append({"type": "email", "status": email_result})
        
        # Send SMS Notification
        if notification_settings.get("sms_enabled", False) and employee.mobile:
            sms_result = send_sms_notification(
                employee, attendance_type, attendance_time, kiosk_location
            )
            notifications_sent.append({"type": "sms", "status": sms_result})
        
        # Send Push Notification (if mobile app is integrated)
        if notification_settings.get("push_enabled", False):
            push_result = send_push_notification(
                employee, attendance_type, attendance_time, kiosk_location
            )
            notifications_sent.append({"type": "push", "status": push_result})
        
        # Send WhatsApp Notification (if configured)
        if notification_settings.get("whatsapp_enabled", False) and employee.mobile:
            whatsapp_result = send_whatsapp_notification(
                employee, attendance_type, attendance_time, kiosk_location
            )
            notifications_sent.append({"type": "whatsapp", "status": whatsapp_result})
        
        # Log notification activity
        log_notification_activity(employee_id, attendance_type, notifications_sent)
        
        return {
            "success": True,
            "notifications_sent": notifications_sent
        }
        
    except Exception as e:
        frappe.log_error(f"Notification error: {str(e)}")
        return {"success": False, "message": str(e)}

def send_email_notification(employee, attendance_type, attendance_time, kiosk_location):
    """Send email notification"""
    try:
        # Email templates
        templates = {
            "Check In": {
                "subject": "✅ Check-In Confirmed - {employee_name}",
                "template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; color: white;">
                        <h2>🔐 Attendance Confirmed</h2>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa;">
                        <h3>Hello {employee_name}!</h3>
                        <p>Your check-in has been successfully recorded.</p>
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <strong>Details:</strong><br>
                            📍 Location: {kiosk_location}<br>
                            🕐 Time: {attendance_time}<br>
                            👤 Employee ID: {employee_id}<br>
                            🏢 Department: {department}
                        </div>
                        <p style="color: #666;">Have a productive day!</p>
                    </div>
                </div>
                """
            },
            "Check Out": {
                "subject": "🚪 Check-Out Confirmed - {employee_name}",
                "template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; text-align: center; color: white;">
                        <h2>🚪 Check-Out Recorded</h2>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa;">
                        <h3>Goodbye {employee_name}!</h3>
                        <p>Your check-out has been successfully recorded.</p>
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <strong>Details:</strong><br>
                            📍 Location: {kiosk_location}<br>
                            🕐 Time: {attendance_time}<br>
                            👤 Employee ID: {employee_id}<br>
                            🏢 Department: {department}
                        </div>
                        <p style="color: #666;">Thank you for your hard work today!</p>
                    </div>
                </div>
                """
            }
        }
        
        template = templates.get(attendance_type, templates["Check In"])
        
        subject = template["subject"].format(
            employee_name=employee.employee_name
        )
        
        message = template["template"].format(
            employee_name=employee.employee_name,
            employee_id=employee.employee_id,
            department=employee.department or "N/A",
            kiosk_location=kiosk_location,
            attendance_time=attendance_time.strftime("%H:%M:%S on %B %d, %Y")
        )
        
        frappe.sendmail(
            recipients=[employee.email],
            subject=subject,
            message=message,
            header=["Face Recognition Attendance System", "#667eea"]
        )
        
        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_sms_notification(employee, attendance_type, attendance_time, kiosk_location):
    """Send SMS notification using configured SMS gateway"""
    try:
        # Get SMS settings
        sms_settings = frappe.get_single("SMS Settings")
        
        if not sms_settings or not sms_settings.sms_gateway_url:
            return {"success": False, "error": "SMS gateway not configured"}
        
        # SMS templates
        templates = {
            "Check In": "✅ Check-In confirmed at {time} from {location}. Have a great day! - {company}",
            "Check Out": "🚪 Check-Out recorded at {time} from {location}. Thank you for your work today! - {company}"
        }
        
        message = templates.get(attendance_type, templates["Check In"]).format(
            time=attendance_time.strftime("%H:%M"),
            location=kiosk_location,
            company=frappe.defaults.get_defaults().get("company", "Company")
        )
        
        # Format phone number
        phone = employee.mobile
        if phone.startswith("+"):
            phone = phone[1:]
        elif phone.startswith("0"):
            phone = "91" + phone[1:]  # Assuming Indian numbers
        
        # Send SMS via configured gateway
        payload = {
            "username": sms_settings.username,
            "password": sms_settings.get_password("password"),
            "to": phone,
            "text": message,
            "from": sms_settings.sender_name or "ATTEND"
        }
        
        response = requests.post(
            sms_settings.sms_gateway_url,
            data=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return {"success": True, "message": "SMS sent successfully"}
        else:
            return {"success": False, "error": f"SMS gateway error: {response.text}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_push_notification(employee, attendance_type, attendance_time, kiosk_location):
    """Send push notification to mobile app"""
    try:
        # Get FCM settings
        fcm_settings = frappe.get_single("FCM Settings")
        
        if not fcm_settings or not fcm_settings.server_key:
            return {"success": False, "error": "FCM not configured"}
        
        # Get employee's device tokens
        device_tokens = frappe.get_all(
            "Employee Device Token",
            filters={"employee_id": employee.employee_id, "is_active": 1},
            pluck="device_token"
        )
        
        if not device_tokens:
            return {"success": False, "error": "No device tokens found"}
        
        # Push notification payload
        notification_data = {
            "title": f"Attendance {attendance_type}",
            "body": f"{attendance_type} recorded at {attendance_time.strftime('%H:%M')} from {kiosk_location}",
            "icon": "attendance_icon",
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "sound": "default"
        }
        
        data_payload = {
            "type": "attendance",
            "employee_id": employee.employee_id,
            "attendance_type": attendance_type,
            "timestamp": attendance_time.isoformat(),
            "location": kiosk_location
        }
        
        # Send to all registered devices
        successful_sends = 0
        failed_sends = 0
        
        for token in device_tokens:
            try:
                fcm_payload = {
                    "to": token,
                    "notification": notification_data,
                    "data": data_payload,
                    "priority": "high"
                }
                
                headers = {
                    "Authorization": f"key={fcm_settings.server_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    "https://fcm.googleapis.com/fcm/send",
                    data=json.dumps(fcm_payload),
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    successful_sends += 1
                else:
                    failed_sends += 1
                    
            except Exception as e:
                failed_sends += 1
                frappe.log_error(f"Push notification error for token {token}: {str(e)}")
        
        return {
            "success": successful_sends > 0,
            "successful_sends": successful_sends,
            "failed_sends": failed_sends
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_whatsapp_notification(employee, attendance_type, attendance_time, kiosk_location):
    """Send WhatsApp notification using WhatsApp Business API"""
    try:
        # Get WhatsApp settings
        whatsapp_settings = frappe.get_single("WhatsApp Settings")
        
        if not whatsapp_settings or not whatsapp_settings.api_url:
            return {"success": False, "error": "WhatsApp API not configured"}
        
        # Format phone number for WhatsApp
        phone = employee.mobile
        if phone.startswith("+"):
            phone = phone[1:]
        elif phone.startswith("0"):
            phone = "91" + phone[1:]  # Assuming Indian numbers
        
        # WhatsApp message templates
        templates = {
            "Check In": """
🔐 *Attendance Check-In Confirmed*

Hello {name}! ✅

Your check-in has been recorded:
📍 *Location:* {location}
🕐 *Time:* {time}
👤 *Employee ID:* {emp_id}

Have a productive day! 💪
            """.strip(),
            "Check Out": """
🚪 *Attendance Check-Out Recorded*

Goodbye {name}! 👋

Your check-out has been recorded:
📍 *Location:* {location}
🕐 *Time:* {time}
👤 *Employee ID:* {emp_id}

Thank you for your hard work today! 🌟
            """.strip()
        }
        
        message = templates.get(attendance_type, templates["Check In"]).format(
            name=employee.employee_name,
            location=kiosk_location,
            time=attendance_time.strftime("%H:%M on %B %d, %Y"),
            emp_id=employee.employee_id
        )
        
        # WhatsApp API payload
        payload = {
            "phone": phone,
            "body": message
        }
        
        headers = {
            "Authorization": f"Bearer {whatsapp_settings.api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            whatsapp_settings.api_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return {"success": True, "message": "WhatsApp message sent successfully"}
        else:
            return {"success": False, "error": f"WhatsApp API error: {response.text}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_employee_notification_settings(employee_id):
    """Get notification preferences for employee"""
    try:
        settings = frappe.get_value(
            "Employee Notification Settings",
            employee_id,
            ["email_enabled", "sms_enabled", "push_enabled", "whatsapp_enabled"],
            as_dict=True
        )
        
        if not settings:
            # Default settings if not configured
            return {
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": False,
                "whatsapp_enabled": False
            }
        
        return settings
        
    except:
        # Default fallback
        return {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": False,
            "whatsapp_enabled": False
        }

def log_notification_activity(employee_id, attendance_type, notifications_sent):
    """Log notification activity for tracking"""
    try:
        log_doc = frappe.new_doc("Notification Activity Log")
        log_doc.employee_id = employee_id
        log_doc.event_type = f"Attendance {attendance_type}"
        log_doc.timestamp = datetime.now()
        log_doc.notifications_data = json.dumps(notifications_sent)
        
        # Count successful notifications
        successful_count = sum(1 for n in notifications_sent if n.get("status", {}).get("success", False))
        log_doc.successful_notifications = successful_count
        log_doc.total_notifications = len(notifications_sent)
        
        log_doc.insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Error logging notification activity: {str(e)}")

@frappe.whitelist()
def send_bulk_notifications(message, recipient_type="all", department=None):
    """Send bulk notifications to employees"""
    try:
        filters = {"status": "Active"}
        
        if recipient_type == "department" and department:
            filters["department"] = department
        
        employees = frappe.get_all(
            "Employee Face Recognition",
            filters=filters,
            fields=["employee_id", "employee_name", "email", "mobile", "department"]
        )
        
        notifications_sent = []
        
        for employee in employees:
            if employee.email:
                try:
                    frappe.sendmail(
                        recipients=[employee.email],
                        subject="📢 Important Notification",
                        message=f"""
                        <div style="font-family: Arial, sans-serif; padding: 20px;">
                            <h3>Hello {employee.employee_name}!</h3>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                                {message}
                            </div>
                            <p style="color: #666; font-size: 12px;">
                                This is an automated message from Face Recognition Attendance System.
                            </p>
                        </div>
                        """
                    )
                    notifications_sent.append({
                        "employee_id": employee.employee_id,
                        "type": "email",
                        "status": "sent"
                    })
                except Exception as e:
                    notifications_sent.append({
                        "employee_id": employee.employee_id,
                        "type": "email",
                        "status": "failed",
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "total_employees": len(employees),
            "notifications_sent": len([n for n in notifications_sent if n["status"] == "sent"]),
            "notifications_failed": len([n for n in notifications_sent if n["status"] == "failed"]),
            "details": notifications_sent
        }
        
    except Exception as e:
        frappe.log_error(f"Bulk notification error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def setup_employee_notification_preferences(employee_id, preferences):
    """Setup notification preferences for employee"""
    try:
        # Check if preferences already exist
        existing = frappe.db.exists("Employee Notification Settings", employee_id)
        
        if existing:
            doc = frappe.get_doc("Employee Notification Settings", employee_id)
        else:
            doc = frappe.new_doc("Employee Notification Settings")
            doc.employee_id = employee_id
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.save(ignore_permissions=True)
        
        return {"success": True, "message": "Notification preferences updated"}
        
    except Exception as e:
        return {"success": False, "message": str(e)}

# DocTypes for Notification System
def create_notification_doctypes():
    """Create DocTypes for notification system"""
    
    # Employee Notification Settings DocType
    notification_settings_doctype = {
        "doctype": "DocType",
        "name": "Employee Notification Settings",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "employee_id", "fieldtype": "Link", "options": "Employee Face Recognition",
             "label": "Employee ID", "reqd": 1},
            {"fieldname": "email_enabled", "fieldtype": "Check", "label": "Email Notifications", "default": 1},
            {"fieldname": "sms_enabled", "fieldtype": "Check", "label": "SMS Notifications", "default": 0},
            {"fieldname": "push_enabled", "fieldtype": "Check", "label": "Push Notifications", "default": 0},
            {"fieldname": "whatsapp_enabled", "fieldtype": "Check", "label": "WhatsApp Notifications", "default": 0},
            {"fieldname": "notification_time_start", "fieldtype": "Time", "label": "Notification Start Time", "default": "08:00:00"},
            {"fieldname": "notification_time_end", "fieldtype": "Time", "label": "Notification End Time", "default": "20:00:00"},
            {"fieldname": "weekend_notifications", "fieldtype": "Check", "label": "Weekend Notifications", "default": 0}
        ]
    }
    
    # Employee Device Token DocType (for push notifications)
    device_token_doctype = {
        "doctype": "DocType",
        "name": "Employee Device Token",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "employee_id", "fieldtype": "Link", "options": "Employee Face Recognition",
             "label": "Employee ID", "reqd": 1},
            {"fieldname": "device_token", "fieldtype": "Data", "label": "Device Token", "reqd": 1},
            {"fieldname": "device_type", "fieldtype": "Select", "label": "Device Type",
             "options": "Android\niOS\nWeb", "reqd": 1},
            {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": 1},
            {"fieldname": "last_used", "fieldtype": "Datetime", "label": "Last Used"}
        ]
    }
    
    # Notification Activity Log DocType
    activity_log_doctype = {
        "doctype": "DocType",
        "name": "Notification Activity Log",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "employee_id", "fieldtype": "Link", "options": "Employee Face Recognition",
             "label": "Employee ID", "reqd": 1},
            {"fieldname": "event_type", "fieldtype": "Data", "label": "Event Type", "reqd": 1},
            {"fieldname": "timestamp", "fieldtype": "Datetime", "label": "Timestamp", "reqd": 1},
            {"fieldname": "successful_notifications", "fieldtype": "Int", "label": "Successful Notifications"},
            {"fieldname": "total_notifications", "fieldtype": "Int", "label": "Total Notifications"},
            {"fieldname": "notifications_data", "fieldtype": "Long Text", "label": "Notifications Data"}
        ]
    }
    
    # SMS Settings DocType
    sms_settings_doctype = {
        "doctype": "DocType",
        "name": "SMS Settings",
        "module": "Bio Facerecognition",
        "issingle": 1,
        "fields": [
            {"fieldname": "sms_gateway_url", "fieldtype": "Data", "label": "SMS Gateway URL"},
            {"fieldname": "username", "fieldtype": "Data", "label": "Username"},
            {"fieldname": "password", "fieldtype": "Password", "label": "Password"},
            {"fieldname": "sender_name", "fieldtype": "Data", "label": "Sender Name"},
            {"fieldname": "is_enabled", "fieldtype": "Check", "label": "Enable SMS", "default": 0}
        ]
    }
    
    # FCM Settings DocType
    fcm_settings_doctype = {
        "doctype": "DocType",
        "name": "FCM Settings",
        "module": "Bio Facerecognition",
        "issingle": 1,
        "fields": [
            {"fieldname": "server_key", "fieldtype": "Password", "label": "FCM Server Key"},
            {"fieldname": "project_id", "fieldtype": "Data", "label": "Firebase Project ID"},
            {"fieldname": "is_enabled", "fieldtype": "Check", "label": "Enable Push Notifications", "default": 0}
        ]
    }
    
    # WhatsApp Settings DocType
    whatsapp_settings_doctype = {
        "doctype": "DocType",
        "name": "WhatsApp Settings",
        "module": "Bio Facerecognition",
        "issingle": 1,
        "fields": [
            {"fieldname": "api_url", "fieldtype": "Data", "label": "WhatsApp API URL"},
            {"fieldname": "api_token", "fieldtype": "Password", "label": "API Token"},
            {"fieldname": "phone_number_id", "fieldtype": "Data", "label": "Phone Number ID"},
            {"fieldname": "is_enabled", "fieldtype": "Check", "label": "Enable WhatsApp", "default": 0}
        ]
    }
    
    return [
        notification_settings_doctype,
        device_token_doctype,
        activity_log_doctype,
        sms_settings_doctype,
        fcm_settings_doctype,
        whatsapp_settings_doctype
    ]