import frappe
from frappe import _
from frappe.utils import get_dates_between, getdate, add_days
from datetime import datetime, timedelta
import json
import calendar
import io
import csv
import base64

# Add these imports for Excel export
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

@frappe.whitelist()
def get_attendance_analytics(period="monthly", start_date=None, end_date=None):
    """Generate comprehensive attendance analytics"""
    try:
        if not start_date or not end_date:
            # Default to current month
            today = datetime.now()
            start_date = today.replace(day=1).date()
            end_date = today.date()
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        analytics = {}
        
        # 1. Daily Attendance Trends
        analytics["daily_trends"] = get_daily_attendance_trends(start_date, end_date)
        
        # 2. Peak Hours Analysis
        analytics["peak_hours"] = get_peak_hours_analysis(start_date, end_date)
        
        # 3. Department-wise Attendance
        analytics["department_stats"] = get_department_attendance_stats(start_date, end_date)
        
        # 4. Recognition Accuracy Metrics
        analytics["accuracy_metrics"] = get_recognition_accuracy_metrics(start_date, end_date)
        
        # 5. Employee Attendance Patterns
        analytics["employee_patterns"] = get_employee_attendance_patterns(start_date, end_date)
        
        # 6. Location-wise Statistics
        analytics["location_stats"] = get_location_attendance_stats(start_date, end_date)
        
        # 7. Late Arrivals and Early Departures
        analytics["punctuality_stats"] = get_punctuality_statistics(start_date, end_date)
        
        # 8. Overtime Analysis
        analytics["overtime_stats"] = get_overtime_analysis(start_date, end_date)
        
        return {
            "success": True,
            "period": {"start": start_date, "end": end_date},
            "analytics": analytics
        }
        
    except Exception as e:
        frappe.log_error(f"Analytics generation error: {str(e)}")
        return {"success": False, "message": str(e)}

def get_daily_attendance_trends(start_date, end_date):
    """Get daily attendance trends"""
    try:
        trends = frappe.db.sql("""
            SELECT 
                DATE(attendance_date) as date,
                COUNT(DISTINCT employee_id) as unique_employees,
                COUNT(*) as total_records,
                SUM(CASE WHEN attendance_type = 'Check In' THEN 1 ELSE 0 END) as check_ins,
                SUM(CASE WHEN attendance_type = 'Check Out' THEN 1 ELSE 0 END) as check_outs,
                AVG(confidence_score) as avg_confidence,
                DAYNAME(attendance_date) as day_name
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
            GROUP BY DATE(attendance_date)
            ORDER BY date
        """, (start_date, end_date), as_dict=True)
        
        # Calculate attendance percentage for each day
        total_employees = frappe.db.count("Employee Face Recognition", {"status": "Active"})
        
        for trend in trends:
            trend["attendance_percentage"] = round(
                (trend["unique_employees"] / total_employees) * 100, 2
            ) if total_employees > 0 else 0
        
        return trends
        
    except Exception as e:
        frappe.log_error(f"Daily trends error: {str(e)}")
        return []

def get_peak_hours_analysis(start_date, end_date):
    """Analyze peak check-in and check-out hours"""
    try:
        peak_hours = frappe.db.sql("""
            SELECT 
                HOUR(check_in_time) as hour,
                COUNT(*) as check_in_count,
                'Check In' as type
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND check_in_time IS NOT NULL
            AND docstatus = 1
            GROUP BY HOUR(check_in_time)
            
            UNION ALL
            
            SELECT 
                HOUR(check_out_time) as hour,
                COUNT(*) as count,
                'Check Out' as type
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND check_out_time IS NOT NULL
            AND docstatus = 1
            GROUP BY HOUR(check_out_time)
            
            ORDER BY hour
        """, (start_date, end_date, start_date, end_date), as_dict=True)
        
        # Process data for better visualization
        hourly_data = {}
        for hour in range(24):
            hourly_data[hour] = {"check_in": 0, "check_out": 0}
        
        for record in peak_hours:
            hour = record["hour"]
            if record["type"] == "Check In":
                hourly_data[hour]["check_in"] = record.get("check_in_count", record.get("count", 0))
            else:
                hourly_data[hour]["check_out"] = record.get("count", 0)
        
        return [
            {
                "hour": f"{hour:02d}:00",
                "check_in_count": data["check_in"],
                "check_out_count": data["check_out"],
                "total_activity": data["check_in"] + data["check_out"]
            }
            for hour, data in hourly_data.items()
        ]
        
    except Exception as e:
        frappe.log_error(f"Peak hours analysis error: {str(e)}")
        return []

def get_department_attendance_stats(start_date, end_date):
    """Get department-wise attendance statistics"""
    try:
        dept_stats = frappe.db.sql("""
            SELECT 
                COALESCE(department, 'Unknown') as department,
                COUNT(DISTINCT employee_id) as unique_employees,
                COUNT(*) as total_records,
                AVG(confidence_score) as avg_confidence,
                SUM(CASE WHEN TIME(check_in_time) > '09:30:00' THEN 1 ELSE 0 END) as late_arrivals,
                SUM(CASE WHEN TIME(check_out_time) < '17:30:00' THEN 1 ELSE 0 END) as early_departures,
                AVG(total_hours) as avg_working_hours
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
            GROUP BY department
            ORDER BY unique_employees DESC
        """, (start_date, end_date), as_dict=True)
        
        # Calculate additional metrics
        for dept in dept_stats:
            dept["punctuality_rate"] = round(
                ((dept["total_records"] - dept["late_arrivals"]) / dept["total_records"]) * 100, 2
            ) if dept["total_records"] > 0 else 0
            
            dept["avg_confidence"] = round(dept["avg_confidence"] or 0, 2)
            dept["avg_working_hours"] = round(dept["avg_working_hours"] or 0, 2)
        
        return dept_stats
        
    except Exception as e:
        frappe.log_error(f"Department stats error: {str(e)}")
        return []

def get_recognition_accuracy_metrics(start_date, end_date):
    """Get face recognition accuracy metrics"""
    try:
        accuracy_metrics = frappe.db.sql("""
            SELECT 
                DATE(creation) as date,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN verification_status = 'Verified' THEN 1 ELSE 0 END) as successful_recognitions,
                SUM(CASE WHEN verification_status = 'Failed' THEN 1 ELSE 0 END) as failed_recognitions,
                AVG(confidence_score) as avg_confidence,
                MIN(confidence_score) as min_confidence,
                MAX(confidence_score) as max_confidence,
                STDDEV(confidence_score) as confidence_stddev
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            GROUP BY DATE(creation)
            ORDER BY date
        """, (start_date, end_date), as_dict=True)
        
        # Calculate success rates
        for metric in accuracy_metrics:
            metric["success_rate"] = round(
                (metric["successful_recognitions"] / metric["total_attempts"]) * 100, 2
            ) if metric["total_attempts"] > 0 else 0
            
            metric["avg_confidence"] = round(metric["avg_confidence"] or 0, 2)
            metric["confidence_stddev"] = round(metric["confidence_stddev"] or 0, 2)
        
        # Overall accuracy summary
        total_attempts = sum([m["total_attempts"] for m in accuracy_metrics])
        total_successful = sum([m["successful_recognitions"] for m in accuracy_metrics])
        
        overall_accuracy = {
            "total_attempts": total_attempts,
            "successful_recognitions": total_successful,
            "overall_success_rate": round((total_successful / total_attempts) * 100, 2) if total_attempts > 0 else 0,
            "daily_metrics": accuracy_metrics
        }
        
        return overall_accuracy
        
    except Exception as e:
        frappe.log_error(f"Accuracy metrics error: {str(e)}")
        return {}

def get_employee_attendance_patterns(start_date, end_date):
    """Analyze individual employee attendance patterns"""
    try:
        patterns = frappe.db.sql("""
            SELECT 
                employee_id,
                employee_name,
                department,
                COUNT(DISTINCT attendance_date) as days_present,
                AVG(TIME_TO_SEC(TIME(check_in_time)) / 3600) as avg_check_in_hour,
                AVG(TIME_TO_SEC(TIME(check_out_time)) / 3600) as avg_check_out_hour,
                AVG(total_hours) as avg_daily_hours,
                STDDEV(total_hours) as hours_consistency,
                SUM(CASE WHEN TIME(check_in_time) > '09:30:00' THEN 1 ELSE 0 END) as late_days,
                MIN(attendance_date) as first_attendance,
                MAX(attendance_date) as last_attendance
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND check_in_time IS NOT NULL
            AND check_out_time IS NOT NULL
            AND docstatus = 1
            GROUP BY employee_id
            HAVING days_present > 0
            ORDER BY days_present DESC
        """, (start_date, end_date), as_dict=True)
        
        # Calculate additional pattern metrics
        total_working_days = len([d for d in get_dates_between(start_date, end_date) 
                                 if getdate(d).weekday() < 5])  # Weekdays only
        
        for pattern in patterns:
            pattern["attendance_rate"] = round(
                (pattern["days_present"] / total_working_days) * 100, 2
            ) if total_working_days > 0 else 0
            
            pattern["punctuality_rate"] = round(
                ((pattern["days_present"] - pattern["late_days"]) / pattern["days_present"]) * 100, 2
            ) if pattern["days_present"] > 0 else 0
            
            pattern["avg_check_in_time"] = f"{int(pattern['avg_check_in_hour'] or 9):02d}:{int(((pattern['avg_check_in_hour'] or 9) % 1) * 60):02d}"
            pattern["avg_check_out_time"] = f"{int(pattern['avg_check_out_hour'] or 18):02d}:{int(((pattern['avg_check_out_hour'] or 18) % 1) * 60):02d}"
            pattern["avg_daily_hours"] = round(pattern["avg_daily_hours"] or 0, 2)
            pattern["hours_consistency"] = round(pattern["hours_consistency"] or 0, 2)
        
        return patterns
        
    except Exception as e:
        frappe.log_error(f"Employee patterns error: {str(e)}")
        return []

def get_location_attendance_stats(start_date, end_date):
    """Get location-wise attendance statistics"""
    try:
        location_stats = frappe.db.sql("""
            SELECT 
                kiosk_location,
                COUNT(DISTINCT employee_id) as unique_employees,
                COUNT(*) as total_records,
                COUNT(DISTINCT attendance_date) as active_days,
                AVG(confidence_score) as avg_confidence,
                MIN(creation) as first_usage,
                MAX(creation) as last_usage
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND kiosk_location IS NOT NULL
            AND docstatus = 1
            GROUP BY kiosk_location
            ORDER BY total_records DESC
        """, (start_date, end_date), as_dict=True)
        
        # Calculate utilization metrics
        for location in location_stats:
            location["avg_records_per_day"] = round(
                location["total_records"] / location["active_days"], 2
            ) if location["active_days"] > 0 else 0
            
            location["avg_confidence"] = round(location["avg_confidence"] or 0, 2)
        
        return location_stats
        
    except Exception as e:
        frappe.log_error(f"Location stats error: {str(e)}")
        return []

def get_punctuality_statistics(start_date, end_date):
    """Analyze punctuality patterns"""
    try:
        punctuality_stats = frappe.db.sql("""
            SELECT 
                DATE(attendance_date) as date,
                COUNT(*) as total_check_ins,
                SUM(CASE WHEN TIME(check_in_time) <= '09:00:00' THEN 1 ELSE 0 END) as early_arrivals,
                SUM(CASE WHEN TIME(check_in_time) BETWEEN '09:01:00' AND '09:30:00' THEN 1 ELSE 0 END) as on_time_arrivals,
                SUM(CASE WHEN TIME(check_in_time) > '09:30:00' THEN 1 ELSE 0 END) as late_arrivals,
                AVG(TIME_TO_SEC(TIMEDIFF(check_in_time, CONCAT(DATE(check_in_time), ' 09:00:00'))) / 60) as avg_lateness_minutes
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND check_in_time IS NOT NULL
            AND docstatus = 1
            GROUP BY DATE(attendance_date)
            ORDER BY date
        """, (start_date, end_date), as_dict=True)
        
        # Calculate percentages
        for stat in punctuality_stats:
            total = stat["total_check_ins"]
            if total > 0:
                stat["early_percentage"] = round((stat["early_arrivals"] / total) * 100, 2)
                stat["on_time_percentage"] = round((stat["on_time_arrivals"] / total) * 100, 2)
                stat["late_percentage"] = round((stat["late_arrivals"] / total) * 100, 2)
            else:
                stat["early_percentage"] = stat["on_time_percentage"] = stat["late_percentage"] = 0
            
            stat["avg_lateness_minutes"] = round(stat["avg_lateness_minutes"] or 0, 2)
        
        return punctuality_stats
        
    except Exception as e:
        frappe.log_error(f"Punctuality stats error: {str(e)}")
        return []

def get_overtime_analysis(start_date, end_date):
    """Analyze overtime patterns"""
    try:
        overtime_stats = frappe.db.sql("""
            SELECT 
                employee_id,
                employee_name,
                department,
                COUNT(*) as working_days,
                SUM(CASE WHEN total_hours > 9 THEN (total_hours - 9) ELSE 0 END) as total_overtime_hours,
                AVG(CASE WHEN total_hours > 9 THEN (total_hours - 9) ELSE 0 END) as avg_overtime_per_day,
                MAX(total_hours) as max_hours_single_day,
                SUM(CASE WHEN total_hours > 9 THEN 1 ELSE 0 END) as overtime_days
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND total_hours IS NOT NULL
            AND total_hours > 0
            AND docstatus = 1
            GROUP BY employee_id
            HAVING total_overtime_hours > 0
            ORDER BY total_overtime_hours DESC
        """, (start_date, end_date), as_dict=True)
        
        # Calculate overtime metrics
        for stat in overtime_stats:
            stat["overtime_frequency"] = round(
                (stat["overtime_days"] / stat["working_days"]) * 100, 2
            ) if stat["working_days"] > 0 else 0
            
            stat["total_overtime_hours"] = round(stat["total_overtime_hours"], 2)
            stat["avg_overtime_per_day"] = round(stat["avg_overtime_per_day"], 2)
            stat["max_hours_single_day"] = round(stat["max_hours_single_day"], 2)
        
        return overtime_stats
        
    except Exception as e:
        frappe.log_error(f"Overtime analysis error: {str(e)}")
        return []

@frappe.whitelist()
def generate_attendance_report(report_type="comprehensive", start_date=None, end_date=None, filters=None):
    """Generate comprehensive attendance reports"""
    try:
        if not start_date or not end_date:
            today = datetime.now()
            start_date = today.replace(day=1).date()
            end_date = today.date()
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        filters = filters or {}
        
        report_data = {}
        
        if report_type in ["comprehensive", "summary"]:
            # Executive Summary
            report_data["executive_summary"] = generate_executive_summary(start_date, end_date, filters)
        
        if report_type in ["comprehensive", "detailed"]:
            # Detailed Analytics
            report_data["detailed_analytics"] = get_attendance_analytics("custom", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        if report_type in ["comprehensive", "employee"]:
            # Employee Performance Report
            report_data["employee_performance"] = generate_employee_performance_report(start_date, end_date, filters)
        
        if report_type in ["comprehensive", "operational"]:
            # Operational Insights
            report_data["operational_insights"] = generate_operational_insights(start_date, end_date, filters)
        
        # Save report
        report_doc = frappe.new_doc("Attendance Report")
        report_doc.report_type = report_type
        report_doc.start_date = start_date
        report_doc.end_date = end_date
        report_doc.filters_applied = json.dumps(filters)
        report_doc.report_data = json.dumps(report_data)
        report_doc.generated_by = frappe.session.user
        report_doc.insert()
        
        return {
            "success": True,
            "report_id": report_doc.name,
            "report_data": report_data
        }
        
    except Exception as e:
        frappe.log_error(f"Report generation error: {str(e)}")
        return {"success": False, "message": str(e)}

def generate_employee_performance_report(start_date, end_date, filters):
    """Generate detailed employee performance report"""
    try:
        department_filter = ""
        filter_values = [start_date, end_date]
        
        if filters.get("department"):
            department_filter = "AND department = %s"
            filter_values.append(filters["department"])
        
        employee_performance = frappe.db.sql(f"""
            SELECT 
                employee_id,
                employee_name,
                department,
                COUNT(DISTINCT attendance_date) as total_days,
                AVG(total_hours) as avg_hours_per_day,
                SUM(total_hours) as total_hours_worked,
                MIN(TIME(check_in_time)) as earliest_check_in,
                MAX(TIME(check_out_time)) as latest_check_out,
                SUM(CASE WHEN TIME(check_in_time) > '09:30:00' THEN 1 ELSE 0 END) as late_days,
                SUM(CASE WHEN total_hours > 9 THEN 1 ELSE 0 END) as overtime_days,
                AVG(confidence_score) as avg_recognition_score,
                COUNT(CASE WHEN verification_status = 'Failed' THEN 1 END) as failed_recognitions
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
            {department_filter}
            GROUP BY employee_id
            ORDER BY total_hours_worked DESC
        """, filter_values, as_dict=True)
        
        # Calculate performance metrics
        for emp in employee_performance:
            working_days = len([d for d in get_dates_between(start_date, end_date) 
                               if getdate(d).weekday() < 5])
            
            emp["attendance_percentage"] = round((emp["total_days"] / working_days) * 100, 2) if working_days > 0 else 0
            emp["punctuality_rate"] = round(((emp["total_days"] - emp["late_days"]) / emp["total_days"]) * 100, 2) if emp["total_days"] > 0 else 0
            emp["overtime_frequency"] = round((emp["overtime_days"] / emp["total_days"]) * 100, 2) if emp["total_days"] > 0 else 0
            emp["avg_hours_per_day"] = round(emp["avg_hours_per_day"] or 0, 2)
            emp["total_hours_worked"] = round(emp["total_hours_worked"] or 0, 2)
            emp["avg_recognition_score"] = round(emp["avg_recognition_score"] or 0, 2)
        
        return {
            "employee_details": employee_performance,
            "summary": {
                "total_employees": len(employee_performance),
                "avg_attendance_rate": round(sum([e["attendance_percentage"] for e in employee_performance]) / len(employee_performance), 2) if employee_performance else 0,
                "avg_punctuality_rate": round(sum([e["punctuality_rate"] for e in employee_performance]) / len(employee_performance), 2) if employee_performance else 0,
                "total_hours_all_employees": sum([e["total_hours_worked"] for e in employee_performance])
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Employee performance report error: {str(e)}")
        return {}

def generate_operational_insights(start_date, end_date, filters):
    """Generate operational insights and recommendations"""
    try:
        # System utilization metrics
        system_stats = frappe.db.sql("""
            SELECT 
                COUNT(DISTINCT kiosk_location) as active_locations,
                COUNT(*) as total_transactions,
                AVG(confidence_score) as avg_system_confidence,
                COUNT(CASE WHEN verification_status = 'Failed' THEN 1 END) as system_failures,
                COUNT(DISTINCT DATE(attendance_date)) as active_days
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (start_date, end_date), as_dict=True)[0]
        
        # Peak usage analysis
        peak_usage = frappe.db.sql("""
            SELECT 
                HOUR(creation) as hour,
                COUNT(*) as transaction_count
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
            GROUP BY HOUR(creation)
            ORDER BY transaction_count DESC
            LIMIT 5
        """, (start_date, end_date), as_dict=True)
        
        # Error analysis
        error_patterns = frappe.db.sql("""
            SELECT 
                kiosk_location,
                COUNT(CASE WHEN verification_status = 'Failed' THEN 1 END) as failure_count,
                COUNT(*) as total_attempts,
                ROUND((COUNT(CASE WHEN verification_status = 'Failed' THEN 1 END) / COUNT(*)) * 100, 2) as failure_rate
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            GROUP BY kiosk_location
            HAVING failure_count > 0
            ORDER BY failure_rate DESC
        """, (start_date, end_date), as_dict=True)
        
        # Generate recommendations
        recommendations = []
        
        if system_stats["avg_system_confidence"] < 85:
            recommendations.append({
                "category": "Technical",
                "priority": "High",
                "issue": "Low recognition confidence",
                "recommendation": "Update employee face images and recalibrate recognition system"
            })
        
        failure_rate = (system_stats["system_failures"] / system_stats["total_transactions"]) * 100 if system_stats["total_transactions"] > 0 else 0
        if failure_rate > 5:
            recommendations.append({
                "category": "System Performance",
                "priority": "Medium",
                "issue": f"High failure rate: {failure_rate:.2f}%",
                "recommendation": "Investigate hardware issues and improve lighting conditions"
            })
        
        # Check for locations with high failure rates
        for location in error_patterns:
            if location["failure_rate"] > 10:
                recommendations.append({
                    "category": "Location Specific",
                    "priority": "Medium",
                    "issue": f"High failure rate at {location['kiosk_location']}: {location['failure_rate']}%",
                    "recommendation": f"Inspect hardware and environmental conditions at {location['kiosk_location']}"
                })
        
        return {
            "system_performance": {
                "utilization_stats": system_stats,
                "peak_hours": peak_usage,
                "error_analysis": error_patterns,
                "overall_success_rate": round(100 - failure_rate, 2)
            },
            "recommendations": recommendations,
            "operational_metrics": {
                "avg_transactions_per_day": round(system_stats["total_transactions"] / system_stats["active_days"], 2) if system_stats["active_days"] > 0 else 0,
                "system_uptime": round((system_stats["active_days"] / len(get_dates_between(start_date, end_date))) * 100, 2),
                "location_coverage": system_stats["active_locations"]
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Operational insights error: {str(e)}")
        return {}

def generate_executive_summary(start_date, end_date, filters):
    """Generate executive summary for attendance"""
    try:
        # Key Metrics
        total_employees = frappe.db.count("Employee Face Recognition", {"status": "Active"})
        
        summary_stats = frappe.db.sql("""
            SELECT 
                COUNT(DISTINCT employee_id) as active_employees,
                COUNT(*) as total_attendance_records,
                AVG(total_hours) as avg_working_hours,
                SUM(CASE WHEN TIME(check_in_time) > '09:30:00' THEN 1 ELSE 0 END) as total_late_arrivals,
                AVG(confidence_score) as avg_recognition_confidence
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (start_date, end_date), as_dict=True)[0]
        
        # Calculate key performance indicators
        attendance_rate = round((summary_stats["active_employees"] / total_employees) * 100, 2) if total_employees > 0 else 0
        punctuality_rate = round(((summary_stats["total_attendance_records"] - summary_stats["total_late_arrivals"]) / summary_stats["total_attendance_records"]) * 100, 2) if summary_stats["total_attendance_records"] > 0 else 0
        
        # Productivity insights
        productivity_score = calculate_productivity_score(summary_stats, attendance_rate, punctuality_rate)
        
        # Trend analysis
        previous_period_start = start_date - timedelta(days=(end_date - start_date).days + 1)
        previous_period_end = start_date - timedelta(days=1)
        
        previous_stats = frappe.db.sql("""
            SELECT 
                COUNT(DISTINCT employee_id) as active_employees,
                COUNT(*) as total_attendance_records,
                AVG(total_hours) as avg_working_hours
            FROM `tabEmployee Attendance`
            WHERE attendance_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (previous_period_start, previous_period_end), as_dict=True)[0]
        
        # Calculate trends
        attendance_trend = calculate_trend(summary_stats["active_employees"], previous_stats["active_employees"])
        hours_trend = calculate_trend(summary_stats["avg_working_hours"], previous_stats["avg_working_hours"])
        
        return {
            "period": {"start": start_date, "end": end_date},
            "key_metrics": {
                "total_employees": total_employees,
                "active_employees": summary_stats["active_employees"],
                "attendance_rate": attendance_rate,
                "punctuality_rate": punctuality_rate,
                "avg_working_hours": round(summary_stats["avg_working_hours"] or 0, 2),
                "recognition_confidence": round(summary_stats["avg_recognition_confidence"] or 0, 2),
                "productivity_score": productivity_score
            },
            "trends": {
                "attendance_change": attendance_trend,
                "hours_change": hours_trend
            },
            "insights": generate_insights(summary_stats, attendance_rate, punctuality_rate)
        }
        
    except Exception as e:
        frappe.log_error(f"Executive summary error: {str(e)}")
        return {}

def calculate_productivity_score(stats, attendance_rate, punctuality_rate):
    """Calculate overall productivity score"""
    try:
        # Weighted scoring system
        weights = {
            "attendance": 0.3,
            "punctuality": 0.25,
            "working_hours": 0.25,
            "recognition_confidence": 0.2
        }
        
        # Normalize scores to 0-100 scale
        attendance_score = min(attendance_rate, 100)
        punctuality_score = min(punctuality_rate, 100)
        
        # Working hours score (assuming 8 hours as target)
        avg_hours = stats["avg_working_hours"] or 0
        hours_score = min((avg_hours / 8.0) * 100, 100)
        
        # Recognition confidence score
        confidence_score = stats["avg_recognition_confidence"] or 0
        
        # Calculate weighted average
        productivity_score = (
            attendance_score * weights["attendance"] +
            punctuality_score * weights["punctuality"] +
            hours_score * weights["working_hours"] +
            confidence_score * weights["recognition_confidence"]
        )
        
        return round(productivity_score, 2)
        
    except:
        return 0

def calculate_trend(current_value, previous_value):
    """Calculate trend percentage"""
    try:
        if previous_value == 0:
            return {"change": 0, "direction": "stable"}
        
        change = ((current_value - previous_value) / previous_value) * 100
        direction = "up" if change > 2 else "down" if change < -2 else "stable"
        
        return {
            "change": round(change, 2),
            "direction": direction
        }
        
    except:
        return {"change": 0, "direction": "stable"}

def generate_insights(stats, attendance_rate, punctuality_rate):
    """Generate actionable insights"""
    insights = []
    
    if attendance_rate < 85:
        insights.append({
            "type": "warning",
            "message": f"Attendance rate is below optimal at {attendance_rate}%. Consider reviewing attendance policies."
        })
    
    if punctuality_rate < 80:
        insights.append({
            "type": "alert",
            "message": f"Punctuality needs improvement at {punctuality_rate}%. Implement punctuality incentives."
        })
    
    if (stats["avg_working_hours"] or 0) < 7:
        insights.append({
            "type": "info",
            "message": f"Average working hours are {round(stats['avg_working_hours'] or 0, 2)}. Monitor productivity levels."
        })
    
    if (stats["avg_recognition_confidence"] or 0) < 85:
        insights.append({
            "type": "technical",
            "message": f"Recognition confidence at {round(stats['avg_recognition_confidence'] or 0, 2)}%. Consider updating face images."
        })
    
    return insights

# DocTypes for Analytics
def create_analytics_doctypes():
    """Create DocTypes for analytics system"""
    
    # Attendance Report DocType
    attendance_report_doctype = {
        "doctype": "DocType",
        "name": "Attendance Report",
        "module": "Bio Facerecognition",
        "fields": [
            {"fieldname": "report_type", "fieldtype": "Select", "label": "Report Type",
             "options": "Comprehensive\nSummary\nDetailed\nEmployee\nOperational", "reqd": 1},
            {"fieldname": "start_date", "fieldtype": "Date", "label": "Start Date", "reqd": 1},
            {"fieldname": "end_date", "fieldtype": "Date", "label": "End Date", "reqd": 1},
            {"fieldname": "filters_applied", "fieldtype": "Long Text", "label": "Filters Applied"},
            {"fieldname": "report_data", "fieldtype": "Long Text", "label": "Report Data"},
            {"fieldname": "generated_by", "fieldtype": "Link", "options": "User", "label": "Generated By"},
            {"fieldname": "generation_time", "fieldtype": "Datetime", "label": "Generation Time", "default": "now"},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status",
             "options": "Generated\nScheduled\nFailed", "default": "Generated"}
        ]
    }
    
    # Analytics Dashboard Settings DocType
    dashboard_settings_doctype = {
        "doctype": "DocType",
        "name": "Analytics Dashboard Settings",
        "module": "Bio Facerecognition",
        "issingle": 1,
        "fields": [
            {"fieldname": "auto_refresh_interval", "fieldtype": "Int", "label": "Auto Refresh Interval (minutes)", "default": 5},
            {"fieldname": "default_date_range", "fieldtype": "Select", "label": "Default Date Range",
             "options": "Today\nThis Week\nThis Month\nLast 30 Days", "default": "This Month"},
            {"fieldname": "enable_real_time_updates", "fieldtype": "Check", "label": "Enable Real-time Updates", "default": 1},
            {"fieldname": "dashboard_widgets", "fieldtype": "Long Text", "label": "Dashboard Widgets Configuration"},
            {"fieldname": "alert_thresholds", "fieldtype": "Long Text", "label": "Alert Thresholds"}
        ]
    }
    
    return [attendance_report_doctype, dashboard_settings_doctype]

@frappe.whitelist()
def export_analytics_data(format_type="excel", analytics_data=None):
    """Export analytics data in various formats"""
    try:
        if not analytics_data:
            # Get default analytics for current month
            analytics_result = get_attendance_analytics()
            if not analytics_result["success"]:
                return {"success": False, "message": "Failed to get analytics data"}
            analytics_data = analytics_result["analytics"]
        
        if format_type == "excel":
            return export_to_excel(analytics_data)
        elif format_type == "csv":
            return export_to_csv(analytics_data)
        elif format_type == "pdf":
            return export_to_pdf(analytics_data)
        elif format_type == "json":
            return export_to_json(analytics_data)
        else:
            return {"success": False, "message": "Unsupported format"}
            
    except Exception as e:
        frappe.log_error(f"Analytics export error: {str(e)}")
        return {"success": False, "message": str(e)}

def export_to_csv(analytics_data):
    """Export analytics to CSV format"""
    try:
        output = io.StringIO()
        
        # Export daily trends
        if analytics_data.get("daily_trends"):
            output.write("Daily Attendance Trends\n")
            output.write("Date,Unique Employees,Check-ins,Check-outs,Attendance %,Avg Confidence\n")
            
            for trend in analytics_data["daily_trends"]:
                output.write(f"{trend.get('date', '')},{trend.get('unique_employees', 0)},{trend.get('check_ins', 0)},{trend.get('check_outs', 0)},{trend.get('attendance_percentage', 0)},{trend.get('avg_confidence', 0)}\n")
            
            output.write("\n")
        
        # Export department stats
        if analytics_data.get("department_stats"):
            output.write("Department Statistics\n")
            output.write("Department,Employees,Total Records,Avg Confidence,Late Arrivals,Punctuality %\n")
            
            for dept in analytics_data["department_stats"]:
                output.write(f"{dept.get('department', '')},{dept.get('unique_employees', 0)},{dept.get('total_records', 0)},{dept.get('avg_confidence', 0)},{dept.get('late_arrivals', 0)},{dept.get('punctuality_rate', 0)}\n")
        
        csv_content = output.getvalue()
        output.close()
        
        # Save as file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"attendance_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "content": csv_content.encode(),
            "is_private": 1
        })
        file_doc.insert()
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "format": "csv"
        }
        
    except Exception as e:
        frappe.log_error(f"CSV export error: {str(e)}")
        return {"success": False, "message": str(e)}

def export_to_json(analytics_data):
    """Export analytics to JSON format"""
    try:
        json_content = json.dumps(analytics_data, indent=2, default=str)
        
        # Save as file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"attendance_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "content": json_content.encode(),
            "is_private": 1
        })
        file_doc.insert()
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "format": "json"
        }
        
    except Exception as e:
        frappe.log_error(f"JSON export error: {str(e)}")
        return {"success": False, "message": str(e)}

def export_to_pdf(analytics_data):
    """Export analytics to PDF format"""
    try:
        # This would require a PDF library like ReportLab
        # For now, return a placeholder
        html_content = generate_analytics_html_report(analytics_data)
        
        # Convert HTML to PDF using frappe's built-in PDF generation
        from frappe.utils.pdf import get_pdf
        
        pdf_content = get_pdf(html_content)
        
        # Save as file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"attendance_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "content": pdf_content,
            "is_private": 1
        })
        file_doc.insert()
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "format": "pdf"
        }
        
    except Exception as e:
        frappe.log_error(f"PDF export error: {str(e)}")
        return {"success": False, "message": str(e)}

def generate_analytics_html_report(analytics_data):
    """Generate HTML report for PDF conversion"""
    html = """
    <html>
    <head>
        <title>Attendance Analytics Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Attendance Analytics Report</h1>
        <p>Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    """
    
    # Add daily trends table
    if analytics_data.get("daily_trends"):
        html += """
        <h2>Daily Attendance Trends</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Unique Employees</th>
                <th>Check-ins</th>
                <th>Check-outs</th>
                <th>Attendance %</th>
            </tr>
        """
        
        for trend in analytics_data["daily_trends"]:
            html += f"""
            <tr>
                <td>{trend.get('date', '')}</td>
                <td>{trend.get('unique_employees', 0)}</td>
                <td>{trend.get('check_ins', 0)}</td>
                <td>{trend.get('check_outs', 0)}</td>
                <td>{trend.get('attendance_percentage', 0)}%</td>
            </tr>
            """
        
        html += "</table>"
    
    # Add department stats
    if analytics_data.get("department_stats"):
        html += """
        <h2>Department Statistics</h2>
        <table>
            <tr>
                <th>Department</th>
                <th>Employees</th>
                <th>Total Records</th>
                <th>Punctuality Rate</th>
            </tr>
        """
        
        for dept in analytics_data["department_stats"]:
            html += f"""
            <tr>
                <td>{dept.get('department', '')}</td>
                <td>{dept.get('unique_employees', 0)}</td>
                <td>{dept.get('total_records', 0)}</td>
                <td>{dept.get('punctuality_rate', 0)}%</td>
            </tr>
            """
        
        html += "</table>"
    
    html += """
    </body>
    </html>
    """
    
    return html

def export_to_excel(analytics_data):
    """Export analytics to Excel format"""
    try:
        if not xlsxwriter:
            return {"success": False, "message": "xlsxwriter library not available"}
            
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Create worksheets for different analytics sections
        worksheets = {
            "Summary": workbook.add_worksheet("Executive Summary"),
            "Daily Trends": workbook.add_worksheet("Daily Trends"),
            "Department Stats": workbook.add_worksheet("Department Analysis"),
            "Employee Patterns": workbook.add_worksheet("Employee Patterns"),
            "Peak Hours": workbook.add_worksheet("Peak Hours")
        }
        
        # Format styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })
        
        data_format = workbook.add_format({'border': 1})
        
        # Write data to worksheets
        write_daily_trends_sheet(worksheets["Daily Trends"], analytics_data.get("daily_trends", []), header_format, data_format)
        write_department_stats_sheet(worksheets["Department Stats"], analytics_data.get("department_stats", []), header_format, data_format)
        write_employee_patterns_sheet(worksheets["Employee Patterns"], analytics_data.get("employee_patterns", []), header_format, data_format)
        write_peak_hours_sheet(worksheets["Peak Hours"], analytics_data.get("peak_hours", []), header_format, data_format)
        
        workbook.close()
        output.seek(0)
        
        # Save as file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"attendance_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "content": output.getvalue(),
            "is_private": 1
        })
        file_doc.insert()
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "format": "excel"
        }
        
    except Exception as e:
        frappe.log_error(f"Excel export error: {str(e)}")
        return {"success": False, "message": str(e)}

def write_daily_trends_sheet(worksheet, data, header_format, data_format):
    """Write daily trends data to Excel worksheet"""
    if not data:
        return
    
    headers = ["Date", "Unique Employees", "Check-ins", "Check-outs", "Attendance %", "Avg Confidence"]
    
    # Write headers
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Write data
    for row, record in enumerate(data, 1):
        worksheet.write(row, 0, str(record.get("date", "")), data_format)
        worksheet.write(row, 1, record.get("unique_employees", 0), data_format)
        worksheet.write(row, 2, record.get("check_ins", 0), data_format)
        worksheet.write(row, 3, record.get("check_outs", 0), data_format)
        worksheet.write(row, 4, record.get("attendance_percentage", 0), data_format)
        worksheet.write(row, 5, record.get("avg_confidence", 0), data_format)

def write_department_stats_sheet(worksheet, data, header_format, data_format):
    """Write department stats to Excel worksheet"""
    if not data:
        return
    
    headers = ["Department", "Employees", "Total Records", "Avg Confidence", "Late Arrivals", "Punctuality %"]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    for row, record in enumerate(data, 1):
        worksheet.write(row, 0, record.get("department", ""), data_format)
        worksheet.write(row, 1, record.get("unique_employees", 0), data_format)
        worksheet.write(row, 2, record.get("total_records", 0), data_format)
        worksheet.write(row, 3, record.get("avg_confidence", 0), data_format)
        worksheet.write(row, 4, record.get("late_arrivals", 0), data_format)
        worksheet.write(row, 5, record.get("punctuality_rate", 0), data_format)

def write_employee_patterns_sheet(worksheet, data, header_format, data_format):
    """Write employee patterns to Excel worksheet"""
    if not data:
        return
    
    headers = ["Employee ID", "Name", "Department", "Days Present", "Attendance %", "Avg Hours", "Late Days"]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    for row, record in enumerate(data, 1):
        worksheet.write(row, 0, record.get("employee_id", ""), data_format)
        worksheet.write(row, 1, record.get("employee_name", ""), data_format)
        worksheet.write(row, 2, record.get("department", ""), data_format)
        worksheet.write(row, 3, record.get("days_present", 0), data_format)
        worksheet.write(row, 4, record.get("attendance_rate", 0), data_format)
        worksheet.write(row, 5, record.get("avg_daily_hours", 0), data_format)
        worksheet.write(row, 6, record.get("late_days", 0), data_format)

def write_peak_hours_sheet(worksheet, data, header_format, data_format):
    """Write peak hours data to Excel worksheet"""
    if not data:
        return
    
    headers = ["Hour", "Check-ins", "Check-outs", "Total Activity"]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    for row, record in enumerate(data, 1):
        worksheet.write(row, 0, record.get("hour", ""), data_format)
        worksheet.write(row, 1, record.get("check_in_count", 0), data_format)
        worksheet.write(row, 2, record.get("check_out_count", 0), data_format)
        worksheet.write(row, 3, record.get("total_activity", 0), data_format)