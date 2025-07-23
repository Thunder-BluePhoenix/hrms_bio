# hrms_biometric/config/desktop.py
import frappe
from frappe import _

def get_data():
    """Desktop configuration for HRMS Biometric"""
    return [
        {
            "module_name": "Bio Facerecognition",
            "category": "Modules",
            "label": _("Biometric Attendance"),
            "color": "#667eea",
            "icon": "/assets/hrms_biometric/images/biometric-icon.svg",
            "type": "module",
            "description": _("Advanced face recognition attendance system with comprehensive analytics and reporting."),
            "onboard_present": True,
            "is_hidden": 0,
            "shortcuts": [
                # Core functionality shortcuts
                {
                    "label": _("Employee Face Recognition"),
                    "name": "Employee Face Recognition",
                    "type": "DocType",
                    "icon": "fa fa-user-circle",
                    "color": "#667eea",
                    "description": _("Manage employee face recognition data")
                },
                {
                    "label": _("Attendance Kiosk"),
                    "name": "Attendance Kiosk", 
                    "type": "DocType",
                    "icon": "fa fa-desktop",
                    "color": "#764ba2",
                    "description": _("Configure and manage attendance kiosks")
                },
                {
                    "label": _("Employee Attendance"),
                    "name": "Employee Attendance",
                    "type": "DocType", 
                    "icon": "fa fa-clock",
                    "color": "#f093fb",
                    "description": _("View and manage attendance records")
                },
                
                # Configuration shortcuts
                {
                    "label": _("Face Recognition Settings"),
                    "name": "Face Recognition Settings",
                    "type": "DocType",
                    "icon": "fa fa-cogs",
                    "color": "#f5576c",
                    "description": _("Configure face recognition parameters")
                },
                {
                    "label": _("Notification Settings"),
                    "name": "Employee Notification Settings",
                    "type": "DocType",
                    "icon": "fa fa-bell",
                    "color": "#4ecdc4",
                    "description": _("Manage employee notification preferences")
                },
                
                # Analytics and reporting shortcuts
                {
                    "label": _("Attendance Analytics"),
                    "name": "attendance-analytics",
                    "type": "Page",
                    "icon": "fa fa-chart-bar",
                    "color": "#45b7d1",
                    "description": _("Comprehensive attendance analytics dashboard")
                },
                {
                    "label": _("Attendance Report"),
                    "name": "Attendance Report",
                    "type": "DocType",
                    "icon": "fa fa-file-alt",
                    "color": "#96ceb4",
                    "description": _("Generate attendance reports")
                },
                {
                    "label": _("Payroll Summary"),
                    "name": "Payroll Summary", 
                    "type": "DocType",
                    "icon": "fa fa-money-bill-wave",
                    "color": "#feca57",
                    "description": _("View payroll calculations")
                },
                
                # System management shortcuts
                {
                    "label": _("Multi Location Sync"),
                    "name": "Multi Location Sync Log",
                    "type": "DocType",
                    "icon": "fa fa-sync",
                    "color": "#ff9ff3",
                    "description": _("Monitor multi-location synchronization")
                },
                {
                    "label": _("Notification Activity"),
                    "name": "Notification Activity Log",
                    "type": "DocType", 
                    "icon": "fa fa-envelope",
                    "color": "#54a0ff",
                    "description": _("Track notification delivery")
                },
                {
                    "label": _("System Health"),
                    "name": "system-health",
                    "type": "Page", 
                    "icon": "fa fa-heartbeat",
                    "color": "#5f27cd",
                    "description": _("Monitor system health and performance")
                }
            ],
            
            # Quick actions for common tasks
            "quick_lists": [
                {
                    "label": _("Today's Attendance"),
                    "name": "Employee Attendance",
                    "type": "DocType",
                    "filters": {"attendance_date": "Today"},
                    "icon": "fa fa-calendar-day"
                },
                {
                    "label": _("Active Employees"),
                    "name": "Employee Face Recognition", 
                    "type": "DocType",
                    "filters": {"status": "Active"},
                    "icon": "fa fa-users"
                },
                {
                    "label": _("Late Arrivals"),
                    "name": "Employee Attendance",
                    "type": "DocType", 
                    "filters": {"status": "Late", "attendance_date": "Today"},
                    "icon": "fa fa-exclamation-triangle"
                },
                {
                    "label": _("Failed Recognitions"),
                    "name": "Employee Attendance",
                    "type": "DocType",
                    "filters": {"verification_status": "Failed", "attendance_date": "Today"},
                    "icon": "fa fa-times-circle"
                }
            ],
            
            # Charts for dashboard
            "charts": [
                {
                    "label": _("Daily Attendance Trend"),
                    "name": "Daily Attendance Trend",
                    "chart_type": "Line",
                    "source": "Attendance Analytics",
                    "color": "#667eea"
                },
                {
                    "label": _("Department Wise Attendance"),
                    "name": "Department Wise Attendance", 
                    "chart_type": "Donut",
                    "source": "Attendance Analytics",
                    "color": "#764ba2"
                },
                {
                    "label": _("Recognition Accuracy"),
                    "name": "Recognition Accuracy",
                    "chart_type": "Percentage",
                    "source": "Attendance Analytics", 
                    "color": "#f093fb"
                }
            ],
            
            # Number cards for key metrics
            "cards": [
                {
                    "label": _("Today's Check-ins"),
                    "name": "todays_checkins",
                    "function": "hrms_biometric.bio_facerecognition.api.analytics_dashboard.get_todays_checkins"
                },
                {
                    "label": _("Active Employees"),
                    "name": "active_employees", 
                    "function": "hrms_biometric.bio_facerecognition.api.analytics_dashboard.get_active_employees_count"
                },
                {
                    "label": _("Recognition Accuracy"),
                    "name": "recognition_accuracy",
                    "function": "hrms_biometric.bio_facerecognition.api.analytics_dashboard.get_recognition_accuracy"
                },
                {
                    "label": _("System Health"),
                    "name": "system_health",
                    "function": "hrms_biometric.bio_facerecognition.api.face_recognition_settings.get_system_health_score"
                }
            ]
        }
    ]

def get_workspace_sidebar_items():
    """Get sidebar items for the workspace"""
    return [
        {
            "type": "Card Break",
            "label": _("Employee Management")
        },
        {
            "type": "Link",
            "name": "Employee Face Recognition",
            "label": _("Face Recognition"),
            "icon": "fa fa-user-circle"
        },
        {
            "type": "Link", 
            "name": "Employee Notification Settings",
            "label": _("Notification Settings"),
            "icon": "fa fa-bell"
        },
        
        {
            "type": "Card Break", 
            "label": _("Attendance Management")
        },
        {
            "type": "Link",
            "name": "Employee Attendance",
            "label": _("Attendance Records"), 
            "icon": "fa fa-clock"
        },
        {
            "type": "Link",
            "name": "Attendance Kiosk",
            "label": _("Kiosk Management"),
            "icon": "fa fa-desktop"
        },
        {
            "type": "Link",
            "name": "Attendance Conflict Log", 
            "label": _("Conflict Resolution"),
            "icon": "fa fa-exclamation-triangle"
        },
        
        {
            "type": "Card Break",
            "label": _("Analytics & Reports")
        },
        {
            "type": "Link",
            "name": "attendance-analytics",
            "label": _("Analytics Dashboard"),
            "icon": "fa fa-chart-bar"
        },
        {
            "type": "Link",
            "name": "Attendance Report",
            "label": _("Attendance Reports"),
            "icon": "fa fa-file-alt" 
        },
        {
            "type": "Link",
            "name": "Payroll Summary",
            "label": _("Payroll Summary"),
            "icon": "fa fa-money-bill-wave"
        },
        
        {
            "type": "Card Break",
            "label": _("System Management")
        },
        {
            "type": "Link",
            "name": "Face Recognition Settings", 
            "label": _("System Settings"),
            "icon": "fa fa-cogs"
        },
        {
            "type": "Link",
            "name": "Multi Location Sync Log",
            "label": _("Multi-Location Sync"),
            "icon": "fa fa-sync"
        },
        {
            "type": "Link",
            "name": "Notification Activity Log",
            "label": _("Notification Logs"),
            "icon": "fa fa-envelope"
        },
        {
            "type": "Link",
            "name": "system-health",
            "label": _("System Health"),
            "icon": "fa fa-heartbeat"
        }
    ]