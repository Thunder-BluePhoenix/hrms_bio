# hrms_biometric/install/setup.py - CORRECTED VERSION with missing functions

import frappe
from frappe import _
from frappe.utils import getdate, add_days
import os
import subprocess
import sys


def run_complete_setup():
    """Run complete setup for HRMS Biometric app"""
    try:
        print("🚀 Starting HRMS Biometric Setup...")
        
        # Step 1: Install system dependencies
        install_system_dependencies()
        
        # Step 2: Create default settings
        create_default_settings()
        
        # Step 3: Setup permissions
        setup_permissions()
        
        # Step 4: Setup custom fields
        setup_custom_fields()
        
        # Step 5: Create default kiosk
        create_default_kiosk()
        
        # Step 6: Setup notification channels
        setup_notification_channels()
        
        # Step 7: Create sample data (optional)
        create_sample_data()
        
        print("✅ HRMS Biometric setup completed successfully!")
        
        return {"success": True, "message": "Setup completed successfully"}
        
    except Exception as e:
        frappe.log_error(f"Setup error: {str(e)}")
        print(f"❌ Setup failed: {str(e)}")
        return {"success": False, "message": str(e)}


def setup_custom_fields():
    """Setup custom fields for Employee doctype - STANDALONE VERSION"""
    try:
        print("📝 Setting up custom fields...")
        
        # Custom fields for Employee
        custom_fields = [
            {
                "dt": "Employee",
                "fieldname": "biometric_section",
                "label": "Biometric Information",
                "fieldtype": "Section Break",
                "insert_after": "personal_details",
                "collapsible": 1
            },
            {
                "dt": "Employee", 
                "fieldname": "biometric_enabled",
                "label": "Enable Biometric Attendance",
                "fieldtype": "Check",
                "insert_after": "biometric_section",
                "default": 0
            },
            {
                "dt": "Employee",
                "fieldname": "face_recognition_id",
                "label": "Face Recognition ID", 
                "fieldtype": "Data",
                "insert_after": "biometric_enabled",
                "read_only": 1
            },
            {
                "dt": "Employee",
                "fieldname": "notification_preferences",
                "label": "Notification Preferences",
                "fieldtype": "Small Text",
                "insert_after": "face_recognition_id"
            }
        ]
        
        for field in custom_fields:
            field_name = f"{field['dt']}-{field['fieldname']}"
            if not frappe.db.exists("Custom Field", field_name):
                custom_field = frappe.new_doc("Custom Field")
                custom_field.update(field)
                custom_field.save(ignore_permissions=True)
                print(f"✅ Created custom field: {field['fieldname']}")
        
        frappe.db.commit()
        print("✅ Custom fields setup completed")
        
    except Exception as e:
        frappe.log_error(f"Custom fields setup error: {str(e)}")
        print(f"❌ Failed to setup custom fields: {str(e)}")


def setup_permissions():
    """Setup default permissions for biometric system - STANDALONE VERSION"""
    try:
        print("🔐 Setting up permissions...")
        
        # Define role permissions
        doctypes = [
            "Employee Face Recognition",
            "Face Recognition Settings", 
            "Attendance Kiosk"
        ]
        
        role_permissions = {
            "HR Manager": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1},
            "HR User": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0},
            "Employee": {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0},
            "System Manager": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1}
        }
        
        for doctype in doctypes:
            if frappe.db.exists("DocType", doctype):
                for role, perms in role_permissions.items():
                    # Check if permission already exists
                    existing_perm = frappe.db.exists("Custom DocPerm", {
                        "parent": doctype, 
                        "role": role,
                        "parenttype": "DocType"
                    })
                    
                    if not existing_perm:
                        doc_perm = frappe.new_doc("Custom DocPerm")
                        doc_perm.parent = doctype
                        doc_perm.parenttype = "DocType"
                        doc_perm.parentfield = "permissions"
                        doc_perm.role = role
                        doc_perm.read = perms["read"]
                        doc_perm.write = perms["write"]
                        doc_perm.create = perms["create"]
                        doc_perm.delete = perms["delete"]
                        doc_perm.submit = perms["submit"]
                        doc_perm.cancel = perms["cancel"]
                        doc_perm.save(ignore_permissions=True)
                        print(f"✅ Created permission for {role} on {doctype}")
        
        frappe.db.commit()
        print("✅ Permissions setup completed")
        
    except Exception as e:
        frappe.log_error(f"Permissions setup error: {str(e)}")
        print(f"❌ Failed to setup permissions: {str(e)}")


def install_system_dependencies():
    """Install required system dependencies"""
    try:
        print("📦 Installing system dependencies...")
        
        # Check if we're on a supported system
        import platform
        system = platform.system().lower()
        
        if system == "linux":
            # Try to detect package manager
            if os.path.exists("/usr/bin/apt-get"):
                install_debian_dependencies()
            elif os.path.exists("/usr/bin/yum"):
                install_redhat_dependencies()
            else:
                print("⚠️ Unknown Linux distribution. Please install dependencies manually.")
        
        elif system == "darwin":  # macOS
            install_macos_dependencies()
        
        else:
            print("⚠️ Unsupported operating system. Please install dependencies manually.")
        
        print("✅ System dependencies installation completed")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not install system dependencies: {str(e)}")


def install_debian_dependencies():
    """Install dependencies for Debian/Ubuntu systems"""
    packages = [
        "build-essential", "cmake", "pkg-config",
        "libopencv-dev", "libgl1-mesa-glx", "libglib2.0-0",
        "libsm6", "libxext6", "libxrender-dev", "libgomp1",
        "libboost-all-dev", "libgtk-3-dev", "libavcodec-dev",
        "libavformat-dev", "libswscale-dev", "libv4l-dev",
        "libxvidcore-dev", "libx264-dev", "libopenblas-dev",
        "liblapack-dev", "libatlas-base-dev", "gfortran",
        "python3-dev", "python3-setuptools", "libjpeg-dev",
        "libpng-dev", "libtiff-dev", "libwebp-dev",
        "libfreetype6-dev", "libharfbuzz-dev", "libfribidi-dev"
    ]
    
    cmd = ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y"] + packages
    try:
        subprocess.run(" ".join(cmd), shell=True, check=True)
        print("✅ Debian/Ubuntu dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to install some packages: {str(e)}")


def install_redhat_dependencies():
    """Install dependencies for RedHat/CentOS systems"""
    packages = [
        "gcc", "gcc-c++", "cmake", "make", "opencv-devel",
        "mesa-libGL", "libSM", "libXext", "libXrender",
        "boost-devel", "gtk3-devel", "openblas-devel",
        "lapack-devel", "atlas-devel", "python3-devel",
        "python3-setuptools", "libjpeg-devel", "libpng-devel",
        "libtiff-devel", "libwebp-devel", "freetype-devel"
    ]
    
    cmd = ["sudo", "yum", "install", "-y"] + packages
    try:
        subprocess.run(cmd, check=True)
        print("✅ RedHat/CentOS dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to install some packages: {str(e)}")


def install_macos_dependencies():
    """Install dependencies for macOS using Homebrew"""
    packages = [
        "cmake", "pkg-config", "opencv", "boost", "dlib",
        "jpeg", "libpng", "libtiff", "webp", "freetype", "harfbuzz"
    ]
    
    # Check if Homebrew is installed
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ Homebrew not found. Please install Homebrew first.")
        return
    
    cmd = ["brew", "install"] + packages
    try:
        subprocess.run(cmd, check=True)
        print("✅ macOS dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to install some packages: {str(e)}")


def create_default_settings():
    """Create default Face Recognition Settings"""
    try:
        print("⚙️ Creating default settings...")
        
        if not frappe.db.exists("Face Recognition Settings", "Face Recognition Settings"):
            settings = frappe.new_doc("Face Recognition Settings")
            
            # Recognition parameters
            settings.recognition_tolerance = 0.4
            settings.recognition_model = "large"
            settings.num_jitters = 100
            settings.face_detection_model = "cnn"
            settings.upsample_times = 2
            settings.confidence_threshold = 70.0
            
            # Performance settings
            settings.recognition_cooldown = 3000
            settings.max_face_images = 5
            settings.image_quality_threshold = 0.8
            settings.auto_cleanup_days = 30
            settings.enable_face_enhancement = 1
            settings.enable_anti_spoofing = 0
            
            # Working hours
            settings.working_hours_start = "09:00:00"
            settings.working_hours_end = "18:00:00"
            settings.late_arrival_threshold = "09:30:00"
            settings.early_departure_threshold = "17:30:00"
            settings.lunch_break_hours = 1.0
            settings.standard_working_hours = 8.0
            
            # Payroll integration
            settings.default_hourly_rate = 50.0
            settings.overtime_multiplier = 1.5
            settings.late_penalty_minutes = 30
            settings.weekend_rate_multiplier = 2.0
            settings.holiday_rate_multiplier = 2.5
            settings.currency = "INR"
            
            # System settings
            settings.enable_logging = 1
            settings.log_retention_days = 90
            settings.enable_backup = 1
            settings.backup_frequency = "Weekly"
            settings.max_concurrent_recognitions = 5
            
            settings.save(ignore_permissions=True)
            print("✅ Face Recognition Settings created")
        
        frappe.db.commit()
        print("✅ Default settings created successfully")
        
    except Exception as e:
        frappe.log_error(f"Default settings creation error: {str(e)}")
        print(f"❌ Failed to create default settings: {str(e)}")


def create_default_kiosk():
    """Create default attendance kiosk"""
    try:
        print("🖥️ Creating default kiosk...")
        
        if frappe.db.exists("DocType", "Attendance Kiosk"):
            if not frappe.db.exists("Attendance Kiosk", "Default Kiosk"):
                kiosk = frappe.new_doc("Attendance Kiosk")
                kiosk.kiosk_name = "Default Kiosk"
                kiosk.location = "Main Office"
                kiosk.is_active = 1
                kiosk.recognition_tolerance = 0.4
                kiosk.confidence_threshold = 70.0
                kiosk.enable_face_enhancement = 1
                kiosk.auto_capture_delay = 3
                kiosk.display_welcome_message = 1
                kiosk.welcome_message = "Welcome! Please look at the camera for attendance."
                kiosk.save(ignore_permissions=True)
                print("✅ Default kiosk created")
        
    except Exception as e:
        frappe.log_error(f"Kiosk creation error: {str(e)}")
        print(f"❌ Failed to create default kiosk: {str(e)}")


def setup_notification_channels():
    """Setup notification channels"""
    try:
        print("📢 Setting up notification channels...")
        
        # Create Email Settings (if not exists)
        if not frappe.db.exists("Email Account", "Biometric Notifications"):
            email_account = frappe.new_doc("Email Account")
            email_account.email_id = "biometric@company.com"
            email_account.email_account_name = "Biometric Notifications"
            email_account.service = "GMail"
            email_account.enable_outgoing = 1
            email_account.enable_incoming = 0
            email_account.save(ignore_permissions=True)
            print("✅ Email settings created")
        
        # Create SMS Settings
        if not frappe.db.exists("SMS Settings", "SMS Settings"):
            sms_settings = frappe.new_doc("SMS Settings")
            sms_settings.sms_gateway_url = "https://api.example.com/sms"
            sms_settings.save(ignore_permissions=True)
            print("✅ SMS Settings created")
        
        print("✅ Notification channels setup completed")
        
    except Exception as e:
        frappe.log_error(f"Notification channels setup error: {str(e)}")
        print(f"❌ Failed to setup notification channels: {str(e)}")


def create_sample_data():
    """Create sample data for demonstration (optional)"""
    try:
        print("📊 Creating sample data...")
        
        # This is optional and should only be enabled for demo environments
        if frappe.conf.get("create_sample_biometric_data"):
            # Create sample face recognition settings
            # Add sample employees with biometric enabled
            # This should be implemented carefully
            pass
        
        print("✅ Sample data creation completed")
        
    except Exception as e:
        frappe.log_error(f"Sample data creation error: {str(e)}")
        print(f"⚠️ Sample data creation warning: {str(e)}")


# SAFE SCHEDULED TASKS - These don't depend on cv2 or other heavy dependencies
def cleanup_old_logs():
    """Clean up old log files - safe scheduled task"""
    try:
        print("🧹 Cleaning up old logs...")
        
        # Clean old notification logs (older than 90 days)
        old_date = add_days(getdate(), -90)
        
        if frappe.db.exists("DocType", "Notification Activity Log"):
            old_logs = frappe.get_all(
                "Notification Activity Log",
                filters={"timestamp": ["<", old_date]},
                fields=["name"]
            )
            
            count = 0
            for log in old_logs:
                try:
                    frappe.delete_doc("Notification Activity Log", log.name, ignore_permissions=True)
                    count += 1
                except:
                    continue
            
            print(f"✅ Cleaned {count} old notification logs")
        
        # Clean old sync logs (older than 6 months)
        old_sync_date = add_days(getdate(), -180)
        
        if frappe.db.exists("DocType", "Multi Location Sync Log"):
            old_sync_logs = frappe.get_all(
                "Multi Location Sync Log",
                filters={"sync_date": ["<", old_sync_date]},
                fields=["name"]
            )
            
            sync_count = 0
            for log in old_sync_logs:
                try:
                    frappe.delete_doc("Multi Location Sync Log", log.name, ignore_permissions=True)
                    sync_count += 1
                except:
                    continue
            
            print(f"✅ Cleaned {sync_count} old sync logs")
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Log cleanup error: {str(e)}")
        print(f"⚠️ Log cleanup warning: {str(e)}")


def generate_weekly_summary():
    """Generate weekly summary - safe scheduled task"""
    try:
        print("📊 Generating weekly summary...")
        
        # Simple summary without cv2 dependencies
        from frappe.utils import add_days, getdate
        
        start_date = add_days(getdate(), -7)
        end_date = getdate()
        
        if frappe.db.exists("DocType", "Employee Attendance"):
            # Count attendance records for the week
            attendance_count = frappe.db.count(
                "Employee Attendance",
                filters={
                    "attendance_date": ["between", [start_date, end_date]]
                }
            )
            
            print(f"📈 Weekly attendance records: {attendance_count}")
        
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            # Count active face recognition profiles
            active_profiles = frappe.db.count(
                "Employee Face Recognition",
                filters={"status": "Active"}
            )
            
            print(f"👥 Active biometric profiles: {active_profiles}")
        
        # Log the summary
        frappe.log_error(
            f"Weekly Biometric Summary: {attendance_count} attendance records, {active_profiles} active profiles",
            "Biometric Weekly Summary"
        )
        
    except Exception as e:
        frappe.log_error(f"Weekly summary error: {str(e)}")
        print(f"⚠️ Weekly summary warning: {str(e)}")


def install_python_dependencies():
    """Install Python dependencies"""
    try:
        print("🐍 Installing Python dependencies...")
        
        # Install core dependencies
        dependencies = [
            "face-recognition>=1.3.0",
            "opencv-python>=4.8.0", 
            "numpy>=1.24.0",
            "Pillow>=10.0.0",
            "xlsxwriter>=3.1.0",
            "requests>=2.31.0"
        ]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print(f"✅ Installed: {dep}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to install {dep}: {str(e)}")
                continue
        
        print("✅ Python dependencies installation completed")
        
    except Exception as e:
        print(f"❌ Failed to install Python dependencies: {str(e)}")


if __name__ == "__main__":
    # This can be run directly for testing
    run_complete_setup()