# hrms_biometric/patches/v0_0/optimize_database_indexes.py

import frappe
from frappe import _


def execute():
    """Optimize database indexes for biometric system performance"""
    try:
        print("⚡ Optimizing database indexes via patch...")
        
        # Create indexes for Employee Face Recognition
        optimize_face_recognition_indexes()
        
        # Create indexes for Employee Attendance
        optimize_attendance_indexes()
        
        # Create indexes for Notification Activity Log
        optimize_notification_indexes()
        
        # Create indexes for Multi Location Sync Log
        optimize_sync_log_indexes()
        
        # Create indexes for Payroll Summary
        optimize_payroll_indexes()
        
        # Create composite indexes for performance
        create_composite_indexes()
        
        # Analyze tables for better performance
        analyze_tables()
        
        # Final commit
        frappe.db.commit()
        print("✅ Database indexes optimization completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Database indexes optimization patch error: {str(e)}")
        print(f"❌ Database indexes optimization patch failed: {str(e)}")


def optimize_face_recognition_indexes():
    """Create indexes for Employee Face Recognition table"""
    try:
        print("👤 Optimizing Employee Face Recognition indexes...")
        
        if not frappe.db.exists("DocType", "Employee Face Recognition"):
            print("ℹ️ Employee Face Recognition doctype not found, skipping...")
            return
        
        indexes = [
            {
                "name": "idx_face_recognition_employee_id",
                "table": "`tabEmployee Face Recognition`",
                "columns": "(employee_id)"
            },
            {
                "name": "idx_face_recognition_status_employee",
                "table": "`tabEmployee Face Recognition`",
                "columns": "(status, employee_id)"
            },
            {
                "name": "idx_face_recognition_creation",
                "table": "`tabEmployee Face Recognition`",
                "columns": "(creation)"
            },
            {
                "name": "idx_face_recognition_modified",
                "table": "`tabEmployee Face Recognition`",
                "columns": "(modified)"
            },
            {
                "name": "idx_face_recognition_status",
                "table": "`tabEmployee Face Recognition`",
                "columns": "(status)"
            }
        ]
        
        create_indexes(indexes)
        
    except Exception as e:
        frappe.log_error(f"Face recognition indexes error: {str(e)}")
        print(f"⚠️ Face recognition indexes warning: {str(e)}")


def optimize_attendance_indexes():
    """Create indexes for Employee Attendance table"""
    try:
        print("📅 Optimizing Employee Attendance indexes...")
        
        if not frappe.db.exists("DocType", "Employee Attendance"):
            print("ℹ️ Employee Attendance doctype not found, skipping...")
            return
        
        indexes = [
            {
                "name": "idx_attendance_employee_date",
                "table": "`tabEmployee Attendance`",
                "columns": "(employee_id, attendance_date)"
            },
            {
                "name": "idx_attendance_date_status",
                "table": "`tabEmployee Attendance`",
                "columns": "(attendance_date, status)"
            },
            {
                "name": "idx_attendance_verification_status",
                "table": "`tabEmployee Attendance`",
                "columns": "(verification_status)"
            },
            {
                "name": "idx_attendance_confidence_score",
                "table": "`tabEmployee Attendance`",
                "columns": "(confidence_score)"
            },
            {
                "name": "idx_attendance_creation",
                "table": "`tabEmployee Attendance`",
                "columns": "(creation)"
            },
            {
                "name": "idx_attendance_modified",
                "table": "`tabEmployee Attendance`",
                "columns": "(modified)"
            }
        ]
        
        create_indexes(indexes)
        
    except Exception as e:
        frappe.log_error(f"Attendance indexes error: {str(e)}")
        print(f"⚠️ Attendance indexes warning: {str(e)}")


def optimize_notification_indexes():
    """Create indexes for Notification Activity Log table"""
    try:
        print("📧 Optimizing Notification Activity Log indexes...")
        
        if not frappe.db.exists("DocType", "Notification Activity Log"):
            print("ℹ️ Notification Activity Log doctype not found, skipping...")
            return
        
        indexes = [
            {
                "name": "idx_notification_employee_timestamp",
                "table": "`tabNotification Activity Log`",
                "columns": "(employee_id, timestamp)"
            },
            {
                "name": "idx_notification_status_timestamp",
                "table": "`tabNotification Activity Log`",
                "columns": "(notification_status, timestamp)"
            },
            {
                "name": "idx_notification_event_type",
                "table": "`tabNotification Activity Log`",
                "columns": "(event_type, timestamp)"
            },
            {
                "name": "idx_notification_priority_timestamp",
                "table": "`tabNotification Activity Log`",
                "columns": "(priority_level, timestamp)"
            },
            {
                "name": "idx_notification_batch_id",
                "table": "`tabNotification Activity Log`",
                "columns": "(batch_id)"
            },
            {
                "name": "idx_notification_timestamp",
                "table": "`tabNotification Activity Log`",
                "columns": "(timestamp)"
            }
        ]
        
        create_indexes(indexes)
        
    except Exception as e:
        frappe.log_error(f"Notification indexes error: {str(e)}")
        print(f"⚠️ Notification indexes warning: {str(e)}")


def optimize_sync_log_indexes():
    """Create indexes for Multi Location Sync Log table"""
    try:
        print("🔄 Optimizing Multi Location Sync Log indexes...")
        
        if not frappe.db.exists("DocType", "Multi Location Sync Log"):
            print("ℹ️ Multi Location Sync Log doctype not found, skipping...")
            return
        
        indexes = [
            {
                "name": "idx_sync_log_date_status",
                "table": "`tabMulti Location Sync Log`",
                "columns": "(sync_date, status)"
            },
            {
                "name": "idx_sync_log_type_date",
                "table": "`tabMulti Location Sync Log`",
                "columns": "(sync_type, sync_date)"
            },
            {
                "name": "idx_sync_log_initiated_by",
                "table": "`tabMulti Location Sync Log`",
                "columns": "(initiated_by, sync_date)"
            },
            {
                "name": "idx_sync_log_next_scheduled",
                "table": "`tabMulti Location Sync Log`",
                "columns": "(next_sync_scheduled)"
            },
            {
                "name": "idx_sync_log_creation",
                "table": "`tabMulti Location Sync Log`",
                "columns": "(creation)"
            }
        ]
        
        create_indexes(indexes)
        
    except Exception as e:
        frappe.log_error(f"Sync log indexes error: {str(e)}")
        print(f"⚠️ Sync log indexes warning: {str(e)}")


def optimize_payroll_indexes():
    """Create indexes for Payroll Summary table"""
    try:
        print("💰 Optimizing Payroll Summary indexes...")
        
        if not frappe.db.exists("DocType", "Payroll Summary"):
            print("ℹ️ Payroll Summary doctype not found, skipping...")
            return
        
        indexes = [
            {
                "name": "idx_payroll_month_year",
                "table": "`tabPayroll Summary`",
                "columns": "(month, year)"
            },
            {
                "name": "idx_payroll_generation_date",
                "table": "`tabPayroll Summary`",
                "columns": "(generation_date)"
            },
            {
                "name": "idx_payroll_status_year",
                "table": "`tabPayroll Summary`",
                "columns": "(status, year)"
            },
            {
                "name": "idx_payroll_approved_by",
                "table": "`tabPayroll Summary`",
                "columns": "(approved_by, approval_date)"
            },
            {
                "name": "idx_payroll_creation",
                "table": "`tabPayroll Summary`",
                "columns": "(creation)"
            }
        ]
        
        create_indexes(indexes)
        
    except Exception as e:
        frappe.log_error(f"Payroll indexes error: {str(e)}")
        print(f"⚠️ Payroll indexes warning: {str(e)}")


def create_composite_indexes():
    """Create composite indexes for complex queries"""
    try:
        print("🔗 Creating composite indexes...")
        
        # Composite index for attendance reports using correct field names
        if frappe.db.exists("DocType", "Employee Attendance"):
            composite_indexes = [
                {
                    "name": "idx_attendance_composite_report",
                    "table": "`tabEmployee Attendance`",
                    "columns": "(attendance_date, status, employee_id)"
                },
                {
                    "name": "idx_attendance_biometric_composite",
                    "table": "`tabEmployee Attendance`",
                    "columns": "(verification_status, confidence_score, attendance_date)"
                },
                {
                    "name": "idx_attendance_employee_status",
                    "table": "`tabEmployee Attendance`",
                    "columns": "(employee_id, status, attendance_date)"
                }
            ]
            
            create_indexes(composite_indexes)
        
        # Composite index for face recognition queries using correct field names
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            face_composite_indexes = [
                {
                    "name": "idx_face_recognition_composite",
                    "table": "`tabEmployee Face Recognition`",
                    "columns": "(employee_id, status)"
                },
                {
                    "name": "idx_face_recognition_status_creation",
                    "table": "`tabEmployee Face Recognition`",
                    "columns": "(status, creation)"
                }
            ]
            
            create_indexes(face_composite_indexes)
        
        # Composite indexes for notification logs
        if frappe.db.exists("DocType", "Notification Activity Log"):
            notification_composite_indexes = [
                {
                    "name": "idx_notification_composite",
                    "table": "`tabNotification Activity Log`",
                    "columns": "(employee_id, event_type, timestamp)"
                },
                {
                    "name": "idx_notification_status_priority",
                    "table": "`tabNotification Activity Log`",
                    "columns": "(notification_status, priority_level, timestamp)"
                }
            ]
            
            create_indexes(notification_composite_indexes)
        
    except Exception as e:
        frappe.log_error(f"Composite indexes error: {str(e)}")
        print(f"⚠️ Composite indexes warning: {str(e)}")


def create_indexes(indexes):
    """Helper function to create database indexes"""
    for index in indexes:
        try:
            # Check if table exists first
            table_name = index['table'].strip('`')
            table_check = frappe.db.sql(f"SHOW TABLES LIKE '{table_name}'")
            if not table_check:
                print(f"ℹ️ Table {index['table']} does not exist, skipping index {index['name']}")
                continue
            
            # Check if index already exists
            existing_indexes = frappe.db.sql(f"""
                SHOW INDEX FROM {index['table']} 
                WHERE Key_name = '{index['name']}'
            """)
            
            if not existing_indexes:
                # Create the index
                frappe.db.sql(f"""
                    CREATE INDEX {index['name']} 
                    ON {index['table']} {index['columns']}
                """)
                print(f"✅ Created index: {index['name']}")
            else:
                print(f"ℹ️ Index already exists: {index['name']}")
                
        except Exception as e:
            print(f"⚠️ Error creating index {index['name']}: {str(e)}")
            continue


def analyze_tables():
    """Analyze tables for better query planning"""
    try:
        print("📊 Analyzing tables for query optimization...")
        
        tables_to_analyze = [
            "`tabEmployee Face Recognition`",
            "`tabEmployee Attendance`",
            "`tabNotification Activity Log`",
            "`tabMulti Location Sync Log`",
            "`tabPayroll Summary`",
            "`tabEmployee Notification Settings`",
            "`tabAttendance Kiosk`"
        ]
        
        analyzed_count = 0
        for table in tables_to_analyze:
            try:
                # Check if table exists first
                table_name = table.strip('`')
                table_check = frappe.db.sql(f"SHOW TABLES LIKE '{table_name}'")
                if table_check:
                    frappe.db.sql(f"ANALYZE TABLE {table}")
                    print(f"✅ Analyzed table: {table}")
                    analyzed_count += 1
                else:
                    print(f"ℹ️ Table {table} does not exist, skipping analysis")
            except Exception as e:
                print(f"⚠️ Error analyzing {table}: {str(e)}")
                continue
        
        print(f"✅ Analyzed {analyzed_count} tables")
        
    except Exception as e:
        frappe.log_error(f"Table analysis error: {str(e)}")
        print(f"⚠️ Table analysis warning: {str(e)}")


def optimize_general_indexes():
    """Create general performance indexes"""
    try:
        print("🚀 Creating general performance indexes...")
        
        # Standard Frappe table indexes for better performance
        standard_indexes = [
            {
                "name": "idx_employee_status_user",
                "table": "`tabEmployee`",
                "columns": "(status, user_id)"
            },
            {
                "name": "idx_file_attached_to",
                "table": "`tabFile`",
                "columns": "(attached_to_doctype, attached_to_name)"
            }
        ]
        
        create_indexes(standard_indexes)
        
    except Exception as e:
        frappe.log_error(f"General indexes error: {str(e)}")
        print(f"⚠️ General indexes warning: {str(e)}")


def check_index_usage():
    """Check and report on index usage"""
    try:
        print("📈 Checking index usage statistics...")
        
        # Get index usage statistics
        if frappe.db.exists("DocType", "Employee Face Recognition"):
            index_stats = frappe.db.sql("""
                SHOW INDEX FROM `tabEmployee Face Recognition`
            """, as_dict=True)
            
            print(f"📊 Employee Face Recognition has {len(index_stats)} indexes")
        
        if frappe.db.exists("DocType", "Employee Attendance"):
            index_stats = frappe.db.sql("""
                SHOW INDEX FROM `tabEmployee Attendance`
            """, as_dict=True)
            
            print(f"📊 Employee Attendance has {len(index_stats)} indexes")
        
        print("✅ Index usage check completed")
        
    except Exception as e:
        frappe.log_error(f"Index usage check error: {str(e)}")
        print(f"⚠️ Index usage check warning: {str(e)}")


def generate_optimization_summary():
    """Generate summary of optimization operations"""
    try:
        print("📊 Generating optimization summary...")
        
        summary = {
            "optimization_date": frappe.utils.getdate(),
            "tables_optimized": [],
            "indexes_created": 0,
            "tables_analyzed": 0
        }
        
        # Count tables that were processed
        tables_to_check = [
            "Employee Face Recognition",
            "Employee Attendance", 
            "Notification Activity Log",
            "Multi Location Sync Log",
            "Payroll Summary"
        ]
        
        for table in tables_to_check:
            if frappe.db.exists("DocType", table):
                summary["tables_optimized"].append(table)
        
        # Log the summary
        frappe.log_error(
            f"Database Optimization Summary: {summary}",
            "Biometric Database Optimization"
        )
        
        print("✅ Optimization summary generated")
        
    except Exception as e:
        frappe.log_error(f"Optimization summary error: {str(e)}")
        print(f"⚠️ Optimization summary warning: {str(e)}")


# Main execution function with comprehensive optimization
def execute():
    """Main optimization function with comprehensive database optimization"""
    try:
        print("⚡ Optimizing database indexes via patch...")
        
        # Core optimization operations
        optimize_face_recognition_indexes()
        optimize_attendance_indexes()
        optimize_notification_indexes()
        optimize_sync_log_indexes()
        optimize_payroll_indexes()
        create_composite_indexes()
        
        # Additional optimization operations
        optimize_general_indexes()
        analyze_tables()
        check_index_usage()
        
        # Generate summary
        generate_optimization_summary()
        
        # Final commit
        frappe.db.commit()
        print("✅ Database indexes optimization completed via patch")
            
    except Exception as e:
        frappe.log_error(f"Database indexes optimization patch error: {str(e)}")
        print(f"❌ Database indexes optimization patch failed: {str(e)}")