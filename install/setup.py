# hrms_biometric/install/setup.py

import frappe
from frappe import _
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
        
        # Step 4: Create sample data (optional)
        create_sample_data()
        
        # Step 5: Setup custom fields
        setup_custom_fields()
        
        # Step 6: Create default kiosk
        create_default_kiosk()
        
        # Step 7: Setup notification channels
        setup_notification_channels()
        
        print("✅ HRMS Biometric setup completed successfully!")
        
        return {"success": True, "message": "Setup completed successfully"}
        
    except Exception as e:
        frappe.log_error(f"Setup error: {str(e)}")
        print(f"❌ Setup failed: {str(e)}")
        return {"success": False, "message": str(e)}

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
            settings.max_concurrent_recognitions = 2
            settings.camera_resolution = "1280x720"
            
            settings.save(ignore_permissions=True)
            print("✅ Default settings created")
        else:
            print("ℹ️ Settings already exist")
        
    except Exception as e:
        frappe.log_error(f"Default settings creation error: {str(e)}")
        print(f"❌ Failed to create default settings: {str(e)}")

def setup_permissions():
    """Setup role permissions for biometric system"""
    try:
        print("🔐 Setting up permissions...")
        
        # Create custom roles if they don't exist
        roles_to_create = [
            {
                "role_name": "Biometric Administrator",
                "desk_access": 1,
                "home_page": "biometric-dashboard"
            },
            {
                "role_name": "Attendance Manager", 
                "desk_access": 1,
                "home_page": "attendance-overview"
            },
            {
                "role_name": "Kiosk User",
                "desk_access": 0,
                "home_page": "kiosk-interface"
            }
        ]
        
        for role_data in roles_to_create:
            if not frappe.db.exists("Role", role_data["role_name"]):
                role = frappe.new_doc("Role")
                role.role_name = role_data["role_name"]
                role.desk_access = role_data["desk_access"]
                role.home_page = role_data.get("home_page")
                role.save(ignore_permissions=True)
                print(f"✅ Created role: {role_data['role_name']}")
        
        # Setup doctype permissions
        setup_doctype_permissions()
        
        print("✅ Permissions setup completed")
        
    except Exception as e:
        frappe.log_error(f"Permissions setup error: {str(e)}")
        print(f"❌ Failed to setup permissions: {str(e)}")

def setup_doctype_permissions():
    """Setup permissions for biometric doctypes"""
    permission_configs = [
        {
            "doctype": "Employee Face Recognition",
            "role": "Biometric Administrator",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1
        },
        {
            "doctype": "Employee Face Recognition", 
            "role": "Attendance Manager",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0
        },
        {
            "doctype": "Employee Attendance",
            "role": "Biometric Administrator", 
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1
        },
        {
            "doctype": "Employee Attendance",
            "role": "Attendance Manager",
            "permlevel": 0, 
            "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0
        },
        {
            "doctype": "Attendance Kiosk",
            "role": "Biometric Administrator",
            "permlevel": 0,
            "read": 1, "write": 1, "create": 1, "delete": 1
        },
        {
            "doctype": "Face Recognition Settings",
            "role": "Biometric Administrator", 
            "permlevel": 0,
            "read": 1, "write": 1
        }
    ]
    
    for perm in permission_configs:
        if not frappe.db.exists("Custom DocPerm", {
            "parent": perm["doctype"],
            "role": perm["role"], 
            "permlevel": perm["permlevel"]
        }):
            doc_perm = frappe.new_doc("Custom DocPerm")
            doc_perm.update(perm)
            doc_perm.save(ignore_permissions=True)

def create_sample_data():
    """Create sample data for testing (optional)"""
    try:
        print("📝 Creating sample data...")
        
        # Create sample employees (for testing only)
        sample_employees = [
            {
                "employee_id": "EMP001",
                "employee_name": "John Doe",
                "department": "IT",
                "designation": "Software Engineer",
                "email": "john.doe@company.com",
                "mobile": "+919876543210",
                "status": "Active"
            },
            {
                "employee_id": "EMP002", 
                "employee_name": "Jane Smith",
                "department": "HR",
                "designation": "HR Manager",
                "email": "jane.smith@company.com",
                "mobile": "+919876543211",
                "status": "Active"
            }
        ]
        
        for emp_data in sample_employees:
            if not frappe.db.exists("Employee Face Recognition", emp_data["employee_id"]):
                emp = frappe.new_doc("Employee Face Recognition")
                emp.update(emp_data)
                # Note: Face images would need to be added manually
                emp.save(ignore_permissions=True)
                print(f"✅ Created sample employee: {emp_data['employee_name']}")
        
        print("✅ Sample data created")
        
    except Exception as e:
        frappe.log_error(f"Sample data creation error: {str(e)}")
        print(f"⚠️ Warning: Could not create sample data: {str(e)}")

def setup_custom_fields():
    """Setup custom fields in standard doctypes"""
    try:
        print("🔧 Setting up custom fields...")
        
        # Add biometric fields to Employee doctype
        custom_fields = [
            {
                "doctype": "Employee",
                "fieldname": "biometric_enabled",
                "label": "Biometric Enabled",
                "fieldtype": "Check",
                "insert_after": "status",
                "default": 1,
                "description": "Enable biometric attendance for this employee"
            },
            {
                "doctype": "Employee",
                "fieldname": "face_recognition_id",
                "label": "Face Recognition ID", 
                "fieldtype": "Data",
                "insert_after": "biometric_enabled",
                "read_only": 1,
                "description": "Linked Face Recognition record ID"
            },
            {
                "doctype": "Employee",
                "fieldname": "biometric_section",
                "label": "Biometric Settings",
                "fieldtype": "Section Break",
                "insert_after": "face_recognition_id"
            },
            {
                "doctype": "Employee", 
                "fieldname": "notification_preferences",
                "label": "Notification Preferences",
                "fieldtype": "Link",
                "options": "Employee Notification Settings",
                "insert_after": "biometric_section"
            }
        ]
        
        for field in custom_fields:
            if not frappe.db.exists("Custom Field", {
                "dt": field["doctype"],
                "fieldname": field["fieldname"]
            }):
                custom_field = frappe.new_doc("Custom Field")
                custom_field.update(field)
                custom_field.save(ignore_permissions=True)
                print(f"✅ Created custom field: {field['fieldname']}")
        
        print("✅ Custom fields setup completed")
        
    except Exception as e:
        frappe.log_error(f"Custom fields setup error: {str(e)}")
        print(f"❌ Failed to setup custom fields: {str(e)}")

def create_default_kiosk():
    """Create a default attendance kiosk"""
    try:
        print("🖥️ Creating default kiosk...")
        
        if not frappe.db.exists("Attendance Kiosk", "Default Kiosk"):
            kiosk = frappe.new_doc("Attendance Kiosk")
            kiosk.kiosk_name = "Default Kiosk"
            kiosk.location = "Main Office"
            kiosk.is_active = 1
            kiosk.timezone = "Asia/Kolkata"
            kiosk.save(ignore_permissions=True)
            print("✅ Default kiosk created")
        else:
            print("ℹ️ Default kiosk already exists")
        
    except Exception as e:
        frappe.log_error(f"Default kiosk creation error: {str(e)}")
        print(f"❌ Failed to create default kiosk: {str(e)}")

def setup_notification_channels():
    """Setup default notification channel settings"""
    try:
        print("📱 Setting up notification channels...")
        
        # Create SMS Settings
        if not frappe.db.exists("SMS Settings", "SMS Settings"):
            sms_settings = frappe.new_doc("SMS Settings")
            sms_settings.sms_gateway_url = ""
            sms_settings.username = ""
            sms_settings.sender_name = "ATTEND"
            sms_settings.is_enabled = 0
            sms_settings.save(ignore_permissions=True)
            print("✅ SMS Settings created")
        
        # Create WhatsApp Settings
        if not frappe.db.exists("WhatsApp Settings", "WhatsApp Settings"):
            whatsapp_settings = frappe.new_doc("WhatsApp Settings")
            whatsapp_settings.whatsapp_provider = "Meta Business API"
            whatsapp_settings.api_url = "https://graph.facebook.com"
            whatsapp_settings.api_version = "v18.0"
            whatsapp_settings.is_enabled = 0
            whatsapp_settings.save(ignore_permissions=True)
            print("✅ WhatsApp Settings created")
        
        print("✅ Notification channels setup completed")
        
    except Exception as e:
        frappe.log_error(f"Notification channels setup error: {str(e)}")
        print(f"❌ Failed to setup notification channels: {str(e)}")

def cleanup_data():
    """Cleanup data during uninstall"""
    try:
        print("🧹 Cleaning up biometric data...")
        
        # List of doctypes to clean
        doctypes_to_clean = [
            "Employee Face Recognition",
            "Employee Attendance", 
            "Attendance Kiosk",
            "Employee Notification Settings",
            "Notification Activity Log",
            "Multi Location Sync Log",
            "Attendance Conflict Log",
            "Payroll Summary",
            "Attendance Report"
        ]
        
        for doctype in doctypes_to_clean:
            if frappe.db.exists("DocType", doctype):
                records = frappe.get_all(doctype)
                for record in records:
                    try:
                        frappe.delete_doc(doctype, record.name, ignore_permissions=True)
                    except:
                        pass
                print(f"✅ Cleaned {doctype}")
        
        # Clean settings
        settings_to_clean = [
            "Face Recognition Settings",
            "SMS Settings", 
            "WhatsApp Settings"
        ]
        
        for setting in settings_to_clean:
            if frappe.db.exists(setting, setting):
                try:
                    frappe.delete_doc(setting, setting, ignore_permissions=True)
                    print(f"✅ Cleaned {setting}")
                except:
                    pass
        
        frappe.db.commit()
        print("✅ Data cleanup completed")
        
    except Exception as e:
        frappe.log_error(f"Cleanup error: {str(e)}")
        print(f"❌ Cleanup failed: {str(e)}")

def remove_custom_fields():
    """Remove custom fields during uninstall"""
    try:
        print("🗑️ Removing custom fields...")
        
        # Remove custom fields from Employee
        custom_fields_to_remove = [
            {"dt": "Employee", "fieldname": "biometric_enabled"},
            {"dt": "Employee", "fieldname": "face_recognition_id"},
            {"dt": "Employee", "fieldname": "biometric_section"},
            {"dt": "Employee", "fieldname": "notification_preferences"}
        ]
        
        for field in custom_fields_to_remove:
            if frappe.db.exists("Custom Field", field):
                frappe.delete_doc("Custom Field", field, ignore_permissions=True)
                print(f"✅ Removed custom field: {field['fieldname']}")
        
        frappe.db.commit()
        print("✅ Custom fields removal completed")
        
    except Exception as e:
        frappe.log_error(f"Custom fields removal error: {str(e)}")
        print(f"❌ Custom fields removal failed: {str(e)}")

# Bench commands
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
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✅ Installed: {dep}")
        
        print("✅ Python dependencies installation completed")
        
    except Exception as e:
        print(f"❌ Failed to install Python dependencies: {str(e)}")

if __name__ == "__main__":
    # This can be run directly for testing
    run_complete_setup()