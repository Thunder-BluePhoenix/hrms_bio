import frappe
from datetime import datetime, timedelta
from frappe import _
import calendar

@frappe.whitelist()
def calculate_working_hours(employee_id, start_date, end_date):
    """Calculate working hours for payroll integration"""
    try:
        attendance_records = frappe.get_all(
            "Employee Attendance",
            filters={
                "employee_id": employee_id,
                "attendance_date": ["between", [start_date, end_date]],
                "docstatus": 1
            },
            fields=[
                "attendance_date", "check_in_time", "check_out_time", 
                "total_hours", "attendance_type", "status"
            ],
            order_by="attendance_date"
        )
        
        total_hours = 0
        total_days = 0
        late_days = 0
        early_departures = 0
        overtime_hours = 0
        
        # Standard work timings (configurable)
        standard_start_time = "09:00:00"
        standard_end_time = "18:00:00"
        standard_hours_per_day = 9
        lunch_break_hours = 1
        
        daily_breakdown = []
        
        for record in attendance_records:
            if record.check_in_time and record.check_out_time:
                # Calculate actual working hours
                actual_hours = record.total_hours or 0
                
                # Check for late arrival
                check_in_time = record.check_in_time.time()
                standard_start = datetime.strptime(standard_start_time, "%H:%M:%S").time()
                is_late = check_in_time > standard_start
                
                # Check for early departure
                check_out_time = record.check_out_time.time()
                standard_end = datetime.strptime(standard_end_time, "%H:%M:%S").time()
                is_early = check_out_time < standard_end
                
                # Calculate overtime
                effective_hours = max(0, actual_hours - lunch_break_hours)
                overtime = max(0, effective_hours - standard_hours_per_day)
                
                total_hours += effective_hours
                total_days += 1
                
                if is_late:
                    late_days += 1
                if is_early:
                    early_departures += 1
                if overtime > 0:
                    overtime_hours += overtime
                
                daily_breakdown.append({
                    "date": record.attendance_date,
                    "check_in": record.check_in_time,
                    "check_out": record.check_out_time,
                    "hours_worked": effective_hours,
                    "is_late": is_late,
                    "is_early": is_early,
                    "overtime": overtime,
                    "status": record.status
                })
        
        # Calculate summary metrics
        average_hours_per_day = total_hours / total_days if total_days > 0 else 0
        attendance_percentage = (total_days / len(attendance_records)) * 100 if attendance_records else 0
        
        return {
            "success": True,
            "employee_id": employee_id,
            "period": {"start": start_date, "end": end_date},
            "summary": {
                "total_hours": round(total_hours, 2),
                "total_days": total_days,
                "average_hours_per_day": round(average_hours_per_day, 2),
                "late_days": late_days,
                "early_departures": early_departures,
                "overtime_hours": round(overtime_hours, 2),
                "attendance_percentage": round(attendance_percentage, 2)
            },
            "daily_breakdown": daily_breakdown
        }
        
    except Exception as e:
        frappe.log_error(f"Working hours calculation error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def generate_payroll_data(month, year):
    """Generate payroll data for all employees for a given month"""
    try:
        # Get all active employees
        employees = frappe.get_all(
            "Employee Face Recognition",
            filters={"status": "Active"},
            fields=["employee_id", "employee_name", "department", "designation"]
        )
        
        # Calculate month boundaries
        start_date = datetime(int(year), int(month), 1).date()
        end_date = datetime(int(year), int(month), calendar.monthrange(int(year), int(month))[1]).date()
        
        payroll_data = []
        
        for employee in employees:
            working_hours_data = calculate_working_hours(
                employee.employee_id, 
                start_date, 
                end_date
            )
            
            if working_hours_data["success"]:
                summary = working_hours_data["summary"]
                
                # Calculate pay components (configurable rates)
                hourly_rate = get_employee_hourly_rate(employee.employee_id)
                overtime_rate = hourly_rate * 1.5  # 1.5x for overtime
                
                basic_pay = summary["total_hours"] * hourly_rate
                overtime_pay = summary["overtime_hours"] * overtime_rate
                
                # Deductions for late arrivals (configurable)
                late_deduction = summary["late_days"] * (hourly_rate * 0.5)  # 30 min deduction per late day
                
                gross_pay = basic_pay + overtime_pay - late_deduction
                
                payroll_record = {
                    "employee_id": employee.employee_id,
                    "employee_name": employee.employee_name,
                    "department": employee.department,
                    "month": month,
                    "year": year,
                    "working_hours": summary["total_hours"],
                    "overtime_hours": summary["overtime_hours"],
                    "late_days": summary["late_days"],
                    "attendance_percentage": summary["attendance_percentage"],
                    "hourly_rate": hourly_rate,
                    "basic_pay": round(basic_pay, 2),
                    "overtime_pay": round(overtime_pay, 2),
                    "late_deduction": round(late_deduction, 2),
                    "gross_pay": round(gross_pay, 2)
                }
                
                payroll_data.append(payroll_record)
        
        # Create payroll summary document
        payroll_summary = frappe.new_doc("Payroll Summary")
        payroll_summary.month = month
        payroll_summary.year = year
        payroll_summary.total_employees = len(payroll_data)
        payroll_summary.total_gross_pay = sum([p["gross_pay"] for p in payroll_data])
        payroll_summary.total_overtime_pay = sum([p["overtime_pay"] for p in payroll_data])
        payroll_summary.total_deductions = sum([p["late_deduction"] for p in payroll_data])
        payroll_summary.payroll_data = frappe.as_json(payroll_data)
        payroll_summary.insert()
        
        return {
            "success": True,
            "payroll_summary_id": payroll_summary.name,
            "payroll_data": payroll_data,
            "summary": {
                "total_employees": len(payroll_data),
                "total_gross_pay": payroll_summary.total_gross_pay,
                "average_attendance": round(sum([p["attendance_percentage"] for p in payroll_data]) / len(payroll_data), 2) if payroll_data else 0
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Payroll generation error: {str(e)}")
        return {"success": False, "message": str(e)}

def get_employee_hourly_rate(employee_id):
    """Get hourly rate for employee (configurable)"""
    try:
        # Check if custom hourly rate is set
        custom_rate = frappe.db.get_value(
            "Employee Face Recognition", 
            employee_id, 
            "hourly_rate"
        )
        
        if custom_rate:
            return custom_rate
        
        # Default rate from settings
        default_rate = frappe.db.get_single_value("Face Recognition Settings", "default_hourly_rate")
        return default_rate or 50.0  # Fallback rate
        
    except:
        return 50.0  # Default fallback

@frappe.whitelist()
def export_payroll_to_external_system(payroll_summary_id, system_type="csv"):
    """Export payroll data to external payroll systems"""
    try:
        payroll_summary = frappe.get_doc("Payroll Summary", payroll_summary_id)
        payroll_data = frappe.parse_json(payroll_summary.payroll_data)
        
        if system_type == "csv":
            # Generate CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'employee_id', 'employee_name', 'department', 'working_hours',
                'overtime_hours', 'late_days', 'basic_pay', 'overtime_pay',
                'late_deduction', 'gross_pay'
            ])
            
            writer.writeheader()
            for record in payroll_data:
                writer.writerow(record)
            
            csv_content = output.getvalue()
            output.close()
            
            # Save as file
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": f"payroll_{payroll_summary.month}_{payroll_summary.year}.csv",
                "content": csv_content,
                "is_private": 1
            })
            file_doc.insert()
            
            return {
                "success": True,
                "file_url": file_doc.file_url,
                "format": "csv"
            }
            
        elif system_type == "json":
            # Generate JSON format for API integration
            json_data = {
                "period": {
                    "month": payroll_summary.month,
                    "year": payroll_summary.year
                },
                "summary": {
                    "total_employees": payroll_summary.total_employees,
                    "total_gross_pay": payroll_summary.total_gross_pay
                },
                "employees": payroll_data
            }
            
            return {
                "success": True,
                "data": json_data,
                "format": "json"
            }
            
    except Exception as e:
        frappe.log_error(f"Payroll export error: {str(e)}")
        return {"success": False, "message": str(e)}

# Payroll Summary DocType
def create_payroll_doctype():
    """Create Payroll Summary DocType"""
    
    payroll_summary_doctype = {
        "doctype": "DocType",
        "name": "Payroll Summary",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "month", "fieldtype": "Select", "label": "Month", "reqd": 1,
             "options": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12"},
            {"fieldname": "year", "fieldtype": "Int", "label": "Year", "reqd": 1},
            {"fieldname": "total_employees", "fieldtype": "Int", "label": "Total Employees"},
            {"fieldname": "total_gross_pay", "fieldtype": "Currency", "label": "Total Gross Pay"},
            {"fieldname": "total_overtime_pay", "fieldtype": "Currency", "label": "Total Overtime Pay"},
            {"fieldname": "total_deductions", "fieldtype": "Currency", "label": "Total Deductions"},
            {"fieldname": "payroll_data", "fieldtype": "Long Text", "label": "Payroll Data JSON"},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status",
             "options": "Draft\nProcessed\nExported", "default": "Draft"},
            {"fieldname": "exported_to", "fieldtype": "Data", "label": "Exported To"},
            {"fieldname": "export_date", "fieldtype": "Datetime", "label": "Export Date"}
        ]
    }
    
    return payroll_summary_doctype