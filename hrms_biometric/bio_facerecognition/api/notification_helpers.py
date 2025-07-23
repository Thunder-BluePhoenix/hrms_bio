# hrms_biometric/bio_facerecognition/api/notification_helpers.py

import frappe
from frappe import _
import json
from datetime import datetime, timedelta


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
            'hrms_biometric.bio_facerecognition.api.mobile_notifications.send_attendance_notification',
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

def get_notification_templates():
    """Get notification templates for different events"""
    templates = {
        "check_in": {
            "email": {
                "subject": "✅ Check-In Confirmed - {employee_name}",
                "body": """
                Hello {employee_name}!
                
                Your check-in has been successfully recorded.
                
                Details:
                📍 Location: {location}
                🕐 Time: {time}
                👤 Employee ID: {employee_id}
                🏢 Department: {department}
                
                Have a productive day!
                """
            },
            "sms": "✅ Check-In confirmed at {time} from {location}. Have a great day! - {company}",
            "whatsapp": """
🔐 *Attendance Check-In Confirmed*

Hello {employee_name}! ✅

Your check-in has been recorded:
📍 *Location:* {location}
🕐 *Time:* {time}
👤 *Employee ID:* {employee_id}

Have a productive day! 💪
            """
        },
        "check_out": {
            "email": {
                "subject": "🚪 Check-Out Confirmed - {employee_name}",
                "body": """
                Goodbye {employee_name}!
                
                Your check-out has been successfully recorded.
                
                Details:
                📍 Location: {location}
                🕐 Time: {time}
                👤 Employee ID: {employee_id}
                🏢 Department: {department}
                
                Thank you for your hard work today!
                """
            },
            "sms": "🚪 Check-Out recorded at {time} from {location}. Thank you for your work today! - {company}",
            "whatsapp": """
🚪 *Attendance Check-Out Recorded*

Goodbye {employee_name}! 👋

Your check-out has been recorded:
📍 *Location:* {location}
🕐 *Time:* {time}
👤 *Employee ID:* {employee_id}

Thank you for your hard work today! 🌟
            """
        },
        "late_arrival": {
            "email": {
                "subject": "⚠️ Late Arrival Alert - {employee_name}",
                "body": """
                Hello {employee_name},
                
                This is to inform you that you arrived late today.
                
                Details:
                📍 Location: {location}
                🕐 Arrival Time: {time}
                ⏰ Expected Time: {expected_time}
                ⏱️ Late By: {late_by} minutes
                
                Please ensure punctuality in future.
                """
            },
            "sms": "⚠️ Late arrival recorded at {time}. Expected: {expected_time}. Please be punctual. - {company}",
            "whatsapp": """
⚠️ *Late Arrival Alert*

Hello {employee_name},

You arrived late today:
🕐 *Arrival Time:* {time}
⏰ *Expected Time:* {expected_time}
⏱️ *Late By:* {late_by} minutes

Please ensure punctuality. 🙏
            """
        },
        "missed_checkout": {
            "email": {
                "subject": "❗ Missed Check-Out Alert - {employee_name}",
                "body": """
                Hello {employee_name},
                
                You forgot to check out today.
                
                Details:
                📅 Date: {date}
                🕐 Check-In Time: {check_in_time}
                📍 Location: {location}
                
                Please contact HR to update your attendance.
                """
            },
            "sms": "❗ You forgot to check out today. Check-in was at {check_in_time}. Contact HR. - {company}",
            "whatsapp": """
❗ *Missed Check-Out Alert*

Hello {employee_name},

You forgot to check out today:
📅 *Date:* {date}
🕐 *Check-In Time:* {check_in_time}
📍 *Location:* {location}

Please contact HR to update your attendance. 📞
            """
        },
        "overtime_alert": {
            "email": {
                "subject": "⏰ Overtime Alert - {employee_name}",
                "body": """
                Hello {employee_name},
                
                You are currently working overtime.
                
                Details:
                🕐 Current Time: {current_time}
                ⏰ Normal End Time: {normal_end_time}
                ⏱️ Overtime Hours: {overtime_hours}
                
                Please ensure you get adequate rest.
                """
            },
            "sms": "⏰ You're working overtime. Current time: {current_time}. Overtime: {overtime_hours} hrs. - {company}",
            "whatsapp": """
⏰ *Overtime Alert*

Hello {employee_name},

You are working overtime:
🕐 *Current Time:* {current_time}
⏰ *Normal End Time:* {normal_end_time}
⏱️ *Overtime Hours:* {overtime_hours}

Please ensure adequate rest! 😴
            """
        },
        "weekly_summary": {
            "email": {
                "subject": "📊 Weekly Attendance Summary - {employee_name}",
                "body": """
                Hello {employee_name},
                
                Here's your weekly attendance summary:
                
                📅 Week: {week_start} to {week_end}
                📊 Days Present: {days_present}/{total_days}
                ⏰ Total Hours: {total_hours}
                ⏱️ Average Daily Hours: {avg_daily_hours}
                🎯 Punctuality Rate: {punctuality_rate}%
                
                {performance_message}
                """
            },
            "sms": "📊 Weekly Summary: {days_present}/{total_days} days, {total_hours}hrs total. Punctuality: {punctuality_rate}% - {company}",
            "whatsapp": """
📊 *Weekly Attendance Summary*

Hello {employee_name}! 📅

*Week:* {week_start} to {week_end}
📊 *Days Present:* {days_present}/{total_days}
⏰ *Total Hours:* {total_hours}
⏱️ *Avg Daily Hours:* {avg_daily_hours}
🎯 *Punctuality:* {punctuality_rate}%

{performance_message} 🌟
            """
        }
    }
    
    return templates

def get_notification_settings_for_employee(employee_id):
    """Get notification settings for specific employee"""
    try:
        settings = frappe.get_value(
            "Employee Notification Settings",
            employee_id,
            [
                "email_enabled", "sms_enabled", "push_enabled", "whatsapp_enabled",
                "notification_time_start", "notification_time_end", "timezone",
                "weekend_notifications", "holiday_notifications", "urgent_only_after_hours"
            ],
            as_dict=True
        )
        
        if not settings:
            # Return default settings
            return {
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": False,
                "whatsapp_enabled": False,
                "notification_time_start": "08:00:00",
                "notification_time_end": "20:00:00",
                "timezone": "Asia/Kolkata",
                "weekend_notifications": False,
                "holiday_notifications": False,
                "urgent_only_after_hours": True
            }
        
        return settings
        
    except Exception as e:
        frappe.log_error(f"Error getting notification settings: {str(e)}")
        return {}

def check_notification_time_window(employee_id, notification_type="normal"):
    """Check if current time is within notification window for employee"""
    try:
        settings = get_notification_settings_for_employee(employee_id)
        current_time = datetime.now().time()
        
        # Parse notification time window
        start_time = datetime.strptime(str(settings.get("notification_time_start", "08:00:00")), "%H:%M:%S").time()
        end_time = datetime.strptime(str(settings.get("notification_time_end", "20:00:00")), "%H:%M:%S").time()
        
        # Check if current time is within window
        if start_time <= current_time <= end_time:
            return True
        
        # Check for urgent notifications after hours
        if notification_type == "urgent" and settings.get("urgent_only_after_hours"):
            return True
        
        # Check weekend notifications
        if datetime.now().weekday() >= 5:  # Saturday or Sunday
            return settings.get("weekend_notifications", False)
        
        return False
        
    except Exception as e:
        frappe.log_error(f"Time window check error: {str(e)}")
        return True  # Default to allow notifications

def create_notification_channels():
    """Create notification channel configurations"""
    channels = {
        "email": {
            "name": "Email",
            "enabled": True,
            "rate_limit": 100,  # per hour
            "retry_attempts": 3,
            "timeout": 30
        },
        "sms": {
            "name": "SMS",
            "enabled": False,
            "rate_limit": 50,  # per hour
            "retry_attempts": 2,
            "timeout": 15
        },
        "whatsapp": {
            "name": "WhatsApp",
            "enabled": False,
            "rate_limit": 80,  # per hour
            "retry_attempts": 3,
            "timeout": 30
        },
        "push": {
            "name": "Push Notification",
            "enabled": False,
            "rate_limit": 200,  # per hour
            "retry_attempts": 2,
            "timeout": 10
        }
    }
    
    return channels

def log_notification_delivery(employee_id, notification_type, channel, status, message=""):
    """Log notification delivery for tracking"""
    try:
        # Update existing notification log or create new one
        log_filters = {
            "employee_id": employee_id,
            "event_type": notification_type,
            "creation": [">=", datetime.now().date()]
        }
        
        existing_log = frappe.get_all("Notification Activity Log", filters=log_filters, limit=1)
        
        if existing_log:
            log_doc = frappe.get_doc("Notification Activity Log", existing_log[0].name)
        else:
            log_doc = frappe.new_doc("Notification Activity Log")
            log_doc.employee_id = employee_id
            log_doc.event_type = notification_type
            log_doc.timestamp = datetime.now()
        
        # Update delivery status
        log_doc.total_notifications = (log_doc.total_notifications or 0) + 1
        
        if status == "success":
            log_doc.successful_notifications = (log_doc.successful_notifications or 0) + 1
            log_doc.notification_status = "Sent"
        else:
            log_doc.failed_notifications = (log_doc.failed_notifications or 0) + 1
            log_doc.notification_status = "Failed"
            log_doc.error_message = message
        
        # Update delivery channels
        channels = log_doc.delivery_channels or ""
        if channel not in channels:
            log_doc.delivery_channels = f"{channels},{channel}" if channels else channel
        
        if existing_log:
            log_doc.save(ignore_permissions=True)
        else:
            log_doc.insert(ignore_permissions=True)
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Notification logging error: {str(e)}")

def get_notification_statistics(employee_id=None, date_range=7):
    """Get notification delivery statistics"""
    try:
        filters = {
            "creation": [">=", datetime.now().date() - timedelta(days=date_range)]
        }
        
        if employee_id:
            filters["employee_id"] = employee_id
        
        logs = frappe.get_all(
            "Notification Activity Log",
            filters=filters,
            fields=[
                "employee_id", "event_type", "total_notifications",
                "successful_notifications", "failed_notifications",
                "delivery_channels", "creation"
            ]
        )
        
        # Calculate statistics
        total_sent = sum([log.get("total_notifications", 0) for log in logs])
        total_successful = sum([log.get("successful_notifications", 0) for log in logs])
        total_failed = sum([log.get("failed_notifications", 0) for log in logs])
        
        success_rate = (total_successful / total_sent * 100) if total_sent > 0 else 0
        
        # Channel breakdown
        channel_stats = {}
        for log in logs:
            channels = (log.get("delivery_channels") or "").split(",")
            for channel in channels:
                if channel.strip():
                    channel_stats[channel.strip()] = channel_stats.get(channel.strip(), 0) + 1
        
        # Event type breakdown
        event_stats = {}
        for log in logs:
            event_type = log.get("event_type", "Unknown")
            event_stats[event_type] = event_stats.get(event_type, 0) + log.get("total_notifications", 0)
        
        return {
            "total_sent": total_sent,
            "successful": total_successful,
            "failed": total_failed,
            "success_rate": round(success_rate, 2),
            "channel_breakdown": channel_stats,
            "event_breakdown": event_stats,
            "date_range_days": date_range
        }
        
    except Exception as e:
        frappe.log_error(f"Notification statistics error: {str(e)}")
        return {
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0,
            "channel_breakdown": {},
            "event_breakdown": {},
            "error": str(e)
        }