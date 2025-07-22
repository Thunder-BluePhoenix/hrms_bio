import frappe
from frappe import _
import json

@frappe.whitelist()
def get_face_recognition_settings():
    """Get current face recognition settings"""
    try:
        settings = frappe.get_single("Face Recognition Settings")
        return {
            "success": True,
            "settings": {
                "recognition_tolerance": settings.recognition_tolerance,
                "recognition_model": settings.recognition_model,
                "num_jitters": settings.num_jitters,
                "face_detection_model": settings.face_detection_model,
                "upsample_times": settings.upsample_times,
                "confidence_threshold": settings.confidence_threshold,
                "recognition_cooldown": settings.recognition_cooldown,
                "max_face_images": settings.max_face_images,
                "image_quality_threshold": settings.image_quality_threshold,
                "auto_cleanup_days": settings.auto_cleanup_days,
                "enable_face_enhancement": settings.enable_face_enhancement,
                "enable_anti_spoofing": settings.enable_anti_spoofing,
                "working_hours_start": settings.working_hours_start,
                "working_hours_end": settings.working_hours_end,
                "default_hourly_rate": settings.default_hourly_rate,
                "overtime_multiplier": settings.overtime_multiplier,
                "late_arrival_threshold": settings.late_arrival_threshold,
                "early_departure_threshold": settings.early_departure_threshold
            }
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def update_face_recognition_settings(settings_data):
    """Update face recognition settings"""
    try:
        settings = frappe.get_single("Face Recognition Settings")
        
        # Parse settings data if it's a string
        if isinstance(settings_data, str):
            settings_data = json.loads(settings_data)
        
        # Update settings
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.save(ignore_permissions=True)
        
        # Clear cache to apply new settings
        frappe.clear_cache()
        
        return {
            "success": True,
            "message": "Settings updated successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Settings update error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def test_recognition_accuracy(test_type="current_settings"):
    """Test face recognition accuracy with current or modified settings"""
    try:
        if test_type == "current_settings":
            # Test with current settings
            test_results = run_accuracy_test()
        else:
            # Test with modified settings (for optimization)
            test_results = run_optimization_test()
        
        return {
            "success": True,
            "test_results": test_results
        }
        
    except Exception as e:
        frappe.log_error(f"Accuracy test error: {str(e)}")
        return {"success": False, "message": str(e)}

def run_accuracy_test():
    """Run accuracy test with current settings"""
    try:
        # Get recent recognition attempts for analysis
        recent_attempts = frappe.get_all(
            "Employee Attendance",
            filters={
                "creation": [">=", frappe.utils.add_days(frappe.utils.nowdate(), -7)],
                "confidence_score": [">", 0]
            },
            fields=["confidence_score", "verification_status", "employee_id"],
            limit=100
        )
        
        if not recent_attempts:
            return {"message": "No recent recognition attempts found for testing"}
        
        # Calculate accuracy metrics
        total_attempts = len(recent_attempts)
        successful_recognitions = len([a for a in recent_attempts if a.verification_status == "Verified"])
        failed_recognitions = total_attempts - successful_recognitions
        
        # Confidence score analysis
        confidence_scores = [a.confidence_score for a in recent_attempts if a.confidence_score]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        min_confidence = min(confidence_scores) if confidence_scores else 0
        max_confidence = max(confidence_scores) if confidence_scores else 0
        
        # Score distribution
        high_confidence = len([s for s in confidence_scores if s >= 90])
        medium_confidence = len([s for s in confidence_scores if 70 <= s < 90])
        low_confidence = len([s for s in confidence_scores if s < 70])
        
        # Get current settings for context
        current_settings = frappe.get_single("Face Recognition Settings")
        
        return {
            "total_attempts": total_attempts,
            "successful_recognitions": successful_recognitions,
            "failed_recognitions": failed_recognitions,
            "success_rate": round((successful_recognitions / total_attempts) * 100, 2) if total_attempts > 0 else 0,
            "confidence_stats": {
                "average": round(avg_confidence, 2),
                "minimum": round(min_confidence, 2),
                "maximum": round(max_confidence, 2),
                "distribution": {
                    "high_confidence": high_confidence,
                    "medium_confidence": medium_confidence,
                    "low_confidence": low_confidence
                }
            },
            "current_settings": {
                "recognition_tolerance": current_settings.recognition_tolerance,
                "num_jitters": current_settings.num_jitters,
                "recognition_model": current_settings.recognition_model,
                "face_detection_model": current_settings.face_detection_model,
                "confidence_threshold": current_settings.confidence_threshold
            },
            "performance_metrics": {
                "estimated_processing_time": calculate_estimated_processing_time(current_settings),
                "accuracy_grade": get_accuracy_grade(successful_recognitions, total_attempts),
                "confidence_grade": get_confidence_grade(avg_confidence)
            },
            "recommendations": generate_accuracy_recommendations(avg_confidence, successful_recognitions, total_attempts),
            "test_timestamp": frappe.utils.now(),
            "data_period": "Last 7 days"
        }
        
    except Exception as e:
        frappe.log_error(f"Accuracy test error: {str(e)}")
        return {"error": str(e)}

def get_accuracy_grade(successful, total):
    """Get accuracy grade based on success rate"""
    try:
        if total == 0:
            return "No Data"
        
        success_rate = (successful / total) * 100
        
        if success_rate >= 95:
            return "Excellent (A+)"
        elif success_rate >= 90:
            return "Very Good (A)"
        elif success_rate >= 85:
            return "Good (B+)"
        elif success_rate >= 80:
            return "Acceptable (B)"
        elif success_rate >= 70:
            return "Needs Improvement (C)"
        else:
            return "Poor (D)"
            
    except:
        return "Unknown"

def get_confidence_grade(avg_confidence):
    """Get confidence grade based on average confidence score"""
    try:
        if avg_confidence >= 95:
            return "Excellent (A+)"
        elif avg_confidence >= 90:
            return "Very Good (A)"
        elif avg_confidence >= 85:
            return "Good (B+)"
        elif avg_confidence >= 80:
            return "Acceptable (B)"
        elif avg_confidence >= 70:
            return "Needs Improvement (C)"
        else:
            return "Poor (D)"
            
    except:
        return "Unknown"

def run_optimization_test():
    """Run optimization test with modified settings to find optimal parameters"""
    try:
        # Get current settings for baseline
        current_settings = frappe.get_single("Face Recognition Settings")
        
        # Get recent recognition attempts for testing
        test_data = frappe.get_all(
            "Employee Attendance",
            filters={
                "creation": [">=", frappe.utils.add_days(frappe.utils.nowdate(), -7)],
                "confidence_score": [">", 0]
            },
            fields=["confidence_score", "verification_status", "employee_id"],
            limit=50  # Use smaller sample for optimization testing
        )
        
        if not test_data:
            return {"message": "No recent recognition data available for optimization testing"}
        
        # Define test parameter variations
        test_variations = [
            {
                "name": "Higher Accuracy",
                "tolerance": max(0.3, current_settings.recognition_tolerance - 0.1),
                "jitters": min(150, current_settings.num_jitters + 25),
                "model": "large"
            },
            {
                "name": "Faster Processing", 
                "tolerance": min(0.6, current_settings.recognition_tolerance + 0.1),
                "jitters": max(50, current_settings.num_jitters - 25),
                "model": "small"
            },
            {
                "name": "Balanced",
                "tolerance": 0.45,
                "jitters": 75,
                "model": "large"
            },
            {
                "name": "Strict Matching",
                "tolerance": 0.35,
                "jitters": 125,
                "model": "large"
            }
        ]
        
        optimization_results = []
        
        # Current baseline results
        baseline_successful = len([t for t in test_data if t.verification_status == "Verified"])
        baseline_avg_confidence = sum([t.confidence_score for t in test_data]) / len(test_data)
        baseline_success_rate = (baseline_successful / len(test_data)) * 100
        
        baseline_result = {
            "name": "Current Settings",
            "tolerance": current_settings.recognition_tolerance,
            "jitters": current_settings.num_jitters,
            "model": current_settings.recognition_model,
            "success_rate": round(baseline_success_rate, 2),
            "avg_confidence": round(baseline_avg_confidence, 2),
            "estimated_processing_time": calculate_estimated_processing_time(current_settings),
            "recommendation": "baseline"
        }
        optimization_results.append(baseline_result)
        
        # Test each variation
        for variation in test_variations:
            # Simulate results based on parameter changes
            simulated_results = simulate_recognition_results(test_data, variation)
            
            variation_result = {
                "name": variation["name"],
                "tolerance": variation["tolerance"],
                "jitters": variation["jitters"],
                "model": variation["model"],
                "success_rate": simulated_results["success_rate"],
                "avg_confidence": simulated_results["avg_confidence"],
                "estimated_processing_time": simulated_results["processing_time"],
                "recommendation": simulated_results["recommendation"]
            }
            optimization_results.append(variation_result)
        
        # Find best performing variation
        best_variation = max(optimization_results[1:], key=lambda x: x["success_rate"])
        
        # Generate recommendations
        recommendations = generate_optimization_recommendations(optimization_results, baseline_result)
        
        return {
            "baseline": baseline_result,
            "test_variations": optimization_results[1:],
            "best_variation": best_variation,
            "recommendations": recommendations,
            "improvement_potential": round(best_variation["success_rate"] - baseline_success_rate, 2)
        }
        
    except Exception as e:
        frappe.log_error(f"Optimization test error: {str(e)}")
        return {"error": str(e)}

def simulate_recognition_results(test_data, variation_params):
    """Simulate recognition results based on parameter variations"""
    try:
        # Current baseline metrics
        baseline_successful = len([t for t in test_data if t.verification_status == "Verified"])
        baseline_success_rate = (baseline_successful / len(test_data)) * 100
        baseline_avg_confidence = sum([t.confidence_score for t in test_data]) / len(test_data)
        
        # Simulate changes based on parameter adjustments
        current_settings = frappe.get_single("Face Recognition Settings")
        
        # Tolerance effect: Lower tolerance = higher accuracy but potentially lower success rate
        tolerance_diff = variation_params["tolerance"] - current_settings.recognition_tolerance
        tolerance_effect = -tolerance_diff * 5  # Lower tolerance increases accuracy
        
        # Jitters effect: More jitters = higher accuracy but slower processing
        jitters_diff = variation_params["jitters"] - current_settings.num_jitters
        jitters_effect = (jitters_diff / 25) * 2  # More jitters slightly increase accuracy
        
        # Model effect: Large model = higher accuracy
        model_effect = 3 if variation_params["model"] == "large" and current_settings.recognition_model == "small" else 0
        model_effect = -3 if variation_params["model"] == "small" and current_settings.recognition_model == "large" else model_effect
        
        # Calculate simulated metrics
        accuracy_improvement = tolerance_effect + jitters_effect + model_effect
        simulated_success_rate = min(100, max(0, baseline_success_rate + accuracy_improvement))
        simulated_confidence = min(100, max(0, baseline_avg_confidence + (accuracy_improvement * 0.5)))
        
        # Processing time estimation
        processing_time = calculate_estimated_processing_time_for_params(variation_params)
        
        # Generate recommendation
        recommendation = generate_variation_recommendation(
            simulated_success_rate, 
            baseline_success_rate, 
            processing_time
        )
        
        return {
            "success_rate": round(simulated_success_rate, 2),
            "avg_confidence": round(simulated_confidence, 2),
            "processing_time": processing_time,
            "recommendation": recommendation
        }
        
    except Exception as e:
        frappe.log_error(f"Simulation error: {str(e)}")
        return {
            "success_rate": 0,
            "avg_confidence": 0,
            "processing_time": 5.0,
            "recommendation": "error"
        }

def calculate_estimated_processing_time(settings):
    """Calculate estimated processing time based on settings"""
    try:
        base_time = 2.0  # Base processing time in seconds
        
        # Model effect
        if settings.recognition_model == "large":
            base_time += 0.5
        
        # Jitters effect  
        jitter_time = (settings.num_jitters - 50) / 100  # Additional time per jitter
        base_time += max(0, jitter_time)
        
        # Detection model effect
        if settings.face_detection_model == "cnn":
            base_time += 0.3
        
        return round(base_time, 2)
        
    except:
        return 3.0  # Default fallback

def calculate_estimated_processing_time_for_params(params):
    """Calculate estimated processing time for specific parameters"""
    try:
        base_time = 2.0
        
        # Model effect
        if params["model"] == "large":
            base_time += 0.5
        
        # Jitters effect
        jitter_time = (params["jitters"] - 50) / 100
        base_time += max(0, jitter_time)
        
        # Assume CNN model for optimization tests
        base_time += 0.3
        
        return round(base_time, 2)
        
    except:
        return 3.0

def generate_variation_recommendation(simulated_rate, baseline_rate, processing_time):
    """Generate recommendation for a parameter variation"""
    try:
        improvement = simulated_rate - baseline_rate
        
        if improvement > 5 and processing_time < 4:
            return "highly_recommended"
        elif improvement > 2 and processing_time < 5:
            return "recommended"
        elif improvement > 0:
            return "marginal_improvement"
        elif improvement < -2:
            return "not_recommended"
        else:
            return "neutral"
            
    except:
        return "unknown"

def generate_optimization_recommendations(results, baseline):
    """Generate comprehensive optimization recommendations"""
    try:
        recommendations = []
        
        # Find best accuracy
        best_accuracy = max(results, key=lambda x: x["success_rate"])
        if best_accuracy["success_rate"] > baseline["success_rate"] + 2:
            recommendations.append({
                "type": "accuracy",
                "message": f"Switch to '{best_accuracy['name']}' settings for {best_accuracy['success_rate'] - baseline['success_rate']:.1f}% better accuracy",
                "action": "update_settings",
                "settings": {
                    "recognition_tolerance": best_accuracy["tolerance"],
                    "num_jitters": best_accuracy["jitters"],
                    "recognition_model": best_accuracy["model"]
                }
            })
        
        # Find best speed
        fastest = min(results, key=lambda x: x["estimated_processing_time"])
        if fastest["estimated_processing_time"] < baseline["estimated_processing_time"] - 0.5:
            recommendations.append({
                "type": "performance",
                "message": f"Use '{fastest['name']}' settings for {baseline['estimated_processing_time'] - fastest['estimated_processing_time']:.1f}s faster processing",
                "action": "update_settings",
                "settings": {
                    "recognition_tolerance": fastest["tolerance"],
                    "num_jitters": fastest["jitters"],
                    "recognition_model": fastest["model"]
                }
            })
        
        # General recommendations
        if baseline["success_rate"] < 85:
            recommendations.append({
                "type": "warning",
                "message": "Current accuracy is below 85%. Consider updating face images or adjusting settings.",
                "action": "review_images"
            })
        
        if baseline["estimated_processing_time"] > 5:
            recommendations.append({
                "type": "performance",
                "message": "Processing time is slow. Consider reducing jitters or using small model.",
                "action": "optimize_speed"
            })
        
        return recommendations
        
    except Exception as e:
        frappe.log_error(f"Recommendation generation error: {str(e)}")
        return []

def generate_accuracy_recommendations(avg_confidence, successful, total):
    """Generate recommendations based on accuracy test results"""
    recommendations = []
    
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    if success_rate < 85:
        recommendations.append({
            "type": "critical",
            "message": "Success rate is below 85%. Consider lowering recognition tolerance for stricter matching.",
            "action": "Lower tolerance from current value to 0.4 or below"
        })
    
    if avg_confidence < 80:
        recommendations.append({
            "type": "warning",
            "message": "Average confidence is low. Consider requesting employees to update face images.",
            "action": "Initiate face image refresh campaign"
        })
    
    if success_rate > 95 and avg_confidence > 90:
        recommendations.append({
            "type": "success",
            "message": "Excellent performance! System is working optimally.",
            "action": "Maintain current settings"
        })
    
    return recommendations

@frappe.whitelist()
def optimize_recognition_settings():
    """Automatically optimize recognition settings based on historical data"""
    try:
        # Analyze historical performance
        performance_data = analyze_historical_performance()
        
        if not performance_data["success"]:
            return performance_data
        
        # Generate optimal settings
        optimal_settings = calculate_optimal_settings(performance_data["data"])
        
        # Create optimization report
        optimization_report = {
            "current_performance": performance_data["data"],
            "recommended_settings": optimal_settings,
            "expected_improvement": calculate_expected_improvement(performance_data["data"], optimal_settings)
        }
        
        return {
            "success": True,
            "optimization_report": optimization_report
        }
        
    except Exception as e:
        frappe.log_error(f"Settings optimization error: {str(e)}")
        return {"success": False, "message": str(e)}

def analyze_historical_performance():
    """Analyze historical recognition performance"""
    try:
        # Get performance data from last 30 days
        performance_stats = frappe.db.sql("""
            SELECT 
                DATE(creation) as date,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN verification_status = 'Verified' THEN 1 ELSE 0 END) as successful,
                AVG(confidence_score) as avg_confidence,
                MIN(confidence_score) as min_confidence,
                MAX(confidence_score) as max_confidence,
                STDDEV(confidence_score) as confidence_stddev
            FROM `tabEmployee Attendance`
            WHERE creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND confidence_score > 0
            GROUP BY DATE(creation)
            ORDER BY date DESC
        """, as_dict=True)
        
        if not performance_stats:
            return {"success": False, "message": "Insufficient historical data"}
        
        # Calculate overall metrics
        total_attempts = sum([s["total_attempts"] for s in performance_stats])
        total_successful = sum([s["successful"] for s in performance_stats])
        overall_success_rate = (total_successful / total_attempts) * 100 if total_attempts > 0 else 0
        
        # Calculate average confidence
        total_confidence = sum([s["avg_confidence"] * s["total_attempts"] for s in performance_stats])
        overall_avg_confidence = total_confidence / total_attempts if total_attempts > 0 else 0
        
        return {
            "success": True,
            "data": {
                "daily_stats": performance_stats,
                "overall_metrics": {
                    "total_attempts": total_attempts,
                    "success_rate": round(overall_success_rate, 2),
                    "avg_confidence": round(overall_avg_confidence, 2),
                    "days_analyzed": len(performance_stats)
                }
            }
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

def calculate_optimal_settings(performance_data):
    """Calculate optimal settings based on performance data"""
    try:
        current_settings = frappe.get_single("Face Recognition Settings")
        overall_metrics = performance_data["overall_metrics"]
        
        optimal_settings = {}
        
        # Optimize tolerance based on success rate
        if overall_metrics["success_rate"] < 85:
            # Lower tolerance for stricter matching
            optimal_settings["recognition_tolerance"] = max(0.3, current_settings.recognition_tolerance - 0.1)
        elif overall_metrics["success_rate"] > 98:
            # Slightly increase tolerance for faster processing
            optimal_settings["recognition_tolerance"] = min(0.6, current_settings.recognition_tolerance + 0.05)
        else:
            optimal_settings["recognition_tolerance"] = current_settings.recognition_tolerance
        
        # Optimize num_jitters based on confidence
        if overall_metrics["avg_confidence"] < 80:
            # Increase jitters for better accuracy
            optimal_settings["num_jitters"] = min(150, current_settings.num_jitters + 25)
        elif overall_metrics["avg_confidence"] > 95:
            # Reduce jitters for faster processing
            optimal_settings["num_jitters"] = max(50, current_settings.num_jitters - 25)
        else:
            optimal_settings["num_jitters"] = current_settings.num_jitters
        
        # Optimize face detection model
        if overall_metrics["success_rate"] < 90:
            optimal_settings["face_detection_model"] = "cnn"  # More accurate but slower
        else:
            optimal_settings["face_detection_model"] = current_settings.face_detection_model
        
        # Optimize recognition model
        if overall_metrics["avg_confidence"] < 85:
            optimal_settings["recognition_model"] = "large"  # More accurate
        else:
            optimal_settings["recognition_model"] = current_settings.recognition_model
        
        return optimal_settings
        
    except Exception as e:
        frappe.log_error(f"Optimal settings calculation error: {str(e)}")
        return {}

def calculate_expected_improvement(current_data, optimal_settings):
    """Calculate expected improvement with optimal settings"""
    try:
        current_settings = frappe.get_single("Face Recognition Settings")
        improvements = {}
        
        # Estimate success rate improvement
        if optimal_settings.get("recognition_tolerance", current_settings.recognition_tolerance) < current_settings.recognition_tolerance:
            improvements["success_rate"] = "+2-5%"
        elif optimal_settings.get("recognition_tolerance", current_settings.recognition_tolerance) > current_settings.recognition_tolerance:
            improvements["success_rate"] = "Maintained with faster processing"
        else:
            improvements["success_rate"] = "No change expected"
        
        # Estimate confidence improvement
        if optimal_settings.get("num_jitters", current_settings.num_jitters) > current_settings.num_jitters:
            improvements["confidence"] = "+3-7 points"
        elif optimal_settings.get("num_jitters", current_settings.num_jitters) < current_settings.num_jitters:
            improvements["confidence"] = "Maintained with faster processing"
        else:
            improvements["confidence"] = "No change expected"
        
        # Estimate processing speed impact
        if optimal_settings.get("face_detection_model") == "cnn" and current_settings.face_detection_model != "cnn":
            improvements["processing_speed"] = "-10-20% (more accurate)"
        elif optimal_settings.get("num_jitters", current_settings.num_jitters) < current_settings.num_jitters:
            improvements["processing_speed"] = "+15-25% faster"
        else:
            improvements["processing_speed"] = "No significant change"
        
        return improvements
        
    except Exception as e:
        return {"error": str(e)}

# Face Recognition Settings DocType
def create_face_recognition_settings_doctype():
    """Create Face Recognition Settings DocType"""
    
    settings_doctype = {
        "doctype": "DocType",
        "name": "Face Recognition Settings",
        "module": "Bio Facerecognition",
        "issingle": 1,
        "fields": [
            # Recognition Parameters
            {"fieldname": "recognition_section", "fieldtype": "Section Break", "label": "Recognition Parameters"},
            {"fieldname": "recognition_tolerance", "fieldtype": "Float", "label": "Recognition Tolerance", 
             "default": 0.4, "precision": 2, "description": "Lower values = stricter matching (0.3-0.6)"},
            {"fieldname": "recognition_model", "fieldtype": "Select", "label": "Recognition Model",
             "options": "small\nlarge", "default": "large", "description": "Large model = more accurate"},
            {"fieldname": "num_jitters", "fieldtype": "Int", "label": "Number of Jitters",
             "default": 100, "description": "Higher values = more accurate but slower (50-150)"},
            {"fieldname": "column_break_1", "fieldtype": "Column Break"},
            {"fieldname": "face_detection_model", "fieldtype": "Select", "label": "Face Detection Model",
             "options": "hog\ncnn", "default": "cnn", "description": "CNN = more accurate but slower"},
            {"fieldname": "upsample_times", "fieldtype": "Int", "label": "Upsample Times",
             "default": 2, "description": "Higher values = better detection of small faces (1-3)"},
            {"fieldname": "confidence_threshold", "fieldtype": "Float", "label": "Minimum Confidence Threshold",
             "default": 70.0, "precision": 1, "description": "Minimum confidence score to accept recognition"},
            
            # Performance Settings
            {"fieldname": "performance_section", "fieldtype": "Section Break", "label": "Performance Settings"},
            {"fieldname": "recognition_cooldown", "fieldtype": "Int", "label": "Recognition Cooldown (ms)",
             "default": 3000, "description": "Minimum time between recognitions for same person"},
            {"fieldname": "max_face_images", "fieldtype": "Int", "label": "Max Face Images per Employee",
             "default": 5, "description": "Maximum number of face images to store"},
            {"fieldname": "image_quality_threshold", "fieldtype": "Float", "label": "Image Quality Threshold",
             "default": 0.8, "precision": 2, "description": "Minimum quality score for face images"},
            {"fieldname": "column_break_2", "fieldtype": "Column Break"},
            {"fieldname": "auto_cleanup_days", "fieldtype": "Int", "label": "Auto Cleanup Days",
             "default": 30, "description": "Days to keep captured face images"},
            {"fieldname": "enable_face_enhancement", "fieldtype": "Check", "label": "Enable Face Enhancement",
             "default": 1, "description": "Enhance image quality before recognition"},
            {"fieldname": "enable_anti_spoofing", "fieldtype": "Check", "label": "Enable Anti-Spoofing",
             "default": 0, "description": "Detect fake faces (experimental)"},
            
            # Working Hours Settings
            {"fieldname": "working_hours_section", "fieldtype": "Section Break", "label": "Working Hours Settings"},
            {"fieldname": "working_hours_start", "fieldtype": "Time", "label": "Working Hours Start",
             "default": "09:00:00"},
            {"fieldname": "working_hours_end", "fieldtype": "Time", "label": "Working Hours End",
             "default": "18:00:00"},
            {"fieldname": "late_arrival_threshold", "fieldtype": "Time", "label": "Late Arrival Threshold",
             "default": "09:30:00"},
            {"fieldname": "column_break_3", "fieldtype": "Column Break"},
            {"fieldname": "early_departure_threshold", "fieldtype": "Time", "label": "Early Departure Threshold",
             "default": "17:30:00"},
            {"fieldname": "lunch_break_hours", "fieldtype": "Float", "label": "Lunch Break Hours",
             "default": 1.0, "precision": 1},
            
            # Payroll Integration
            {"fieldname": "payroll_section", "fieldtype": "Section Break", "label": "Payroll Integration"},
            {"fieldname": "default_hourly_rate", "fieldtype": "Currency", "label": "Default Hourly Rate",
             "default": 50.0},
            {"fieldname": "overtime_multiplier", "fieldtype": "Float", "label": "Overtime Multiplier",
             "default": 1.5, "precision": 1},
            {"fieldname": "late_penalty_minutes", "fieldtype": "Int", "label": "Late Penalty (minutes)",
             "default": 30, "description": "Minutes deducted per late arrival"},
            
            # System Settings
            {"fieldname": "system_section", "fieldtype": "Section Break", "label": "System Settings"},
            {"fieldname": "enable_logging", "fieldtype": "Check", "label": "Enable Detailed Logging",
             "default": 1},
            {"fieldname": "log_retention_days", "fieldtype": "Int", "label": "Log Retention Days",
             "default": 90},
            {"fieldname": "enable_backup", "fieldtype": "Check", "label": "Enable Automatic Backup",
             "default": 1},
            {"fieldname": "column_break_4", "fieldtype": "Column Break"},
            {"fieldname": "backup_frequency", "fieldtype": "Select", "label": "Backup Frequency",
             "options": "Daily\nWeekly\nMonthly", "default": "Weekly"},
            {"fieldname": "max_concurrent_recognitions", "fieldtype": "Int", "label": "Max Concurrent Recognitions",
             "default": 2, "description": "Maximum parallel recognition processes"},
            
            # Advanced Settings
            {"fieldname": "advanced_section", "fieldtype": "Section Break", "label": "Advanced Settings"},
            {"fieldname": "custom_recognition_params", "fieldtype": "Long Text", "label": "Custom Recognition Parameters",
             "description": "JSON format for advanced parameters"},
            {"fieldname": "integration_settings", "fieldtype": "Long Text", "label": "Integration Settings",
             "description": "Settings for external system integrations"},
            {"fieldname": "alert_settings", "fieldtype": "Long Text", "label": "Alert Settings",
             "description": "Configuration for system alerts and notifications"}
        ]
    }
    
    return settings_doctype

@frappe.whitelist()
def backup_face_recognition_data():
    """Create backup of face recognition data"""
    try:
        backup_data = {}
        
        # Backup employee face data
        employees = frappe.get_all(
            "Employee Face Recognition",
            fields=["*"]
        )
        backup_data["employees"] = employees
        
        # Backup attendance data (last 30 days)
        recent_attendance = frappe.get_all(
            "Employee Attendance",
            filters={"creation": [">=", frappe.utils.add_days(frappe.utils.nowdate(), -30)]},
            fields=["*"]
        )
        backup_data["attendance"] = recent_attendance
        
        # Backup settings
        settings = frappe.get_single("Face Recognition Settings")
        backup_data["settings"] = settings.as_dict()
        
        # Save backup file
        backup_content = json.dumps(backup_data, indent=2, default=str)
        
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"face_recognition_backup_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.json",
            "content": backup_content,
            "is_private": 1
        })
        file_doc.insert()
        
        # Log backup activity
        backup_log = frappe.new_doc("System Backup Log")
        backup_log.backup_type = "Face Recognition Data"
        backup_log.backup_date = frappe.utils.nowdate()
        backup_log.file_path = file_doc.file_url
        backup_log.data_size = len(backup_content)
        backup_log.status = "Completed"
        backup_log.insert()
        
        return {
            "success": True,
            "backup_file": file_doc.file_url,
            "backup_size": len(backup_content),
            "records_backed_up": {
                "employees": len(employees),
                "attendance_records": len(recent_attendance)
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Backup error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def restore_face_recognition_data(backup_file_url):
    """Restore face recognition data from backup"""
    try:
        # Get backup file
        file_doc = frappe.get_doc("File", {"file_url": backup_file_url})
        backup_content = file_doc.get_content()
        
        if isinstance(backup_content, bytes):
            backup_content = backup_content.decode('utf-8')
        
        backup_data = json.loads(backup_content)
        
        restored_count = {"employees": 0, "attendance": 0}
        
        # Restore employee data
        for emp_data in backup_data.get("employees", []):
            try:
                if not frappe.db.exists("Employee Face Recognition", emp_data["name"]):
                    emp_doc = frappe.new_doc("Employee Face Recognition")
                    emp_doc.update(emp_data)
                    emp_doc.insert(ignore_permissions=True)
                    restored_count["employees"] += 1
            except Exception as e:
                frappe.log_error(f"Employee restore error: {str(e)}")
        
        # Restore settings
        if "settings" in backup_data:
            try:
                settings = frappe.get_single("Face Recognition Settings")
                settings.update(backup_data["settings"])
                settings.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Settings restore error: {str(e)}")
        
        frappe.db.commit()
        
        return {
            "success": True,
            "restored_records": restored_count,
            "message": "Data restored successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Restore error: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_system_health_status():
    """Get comprehensive system health status"""
    try:
        health_status = {}
        
        # Database health
        health_status["database"] = check_database_health()
        
        # Recognition accuracy health
        health_status["accuracy"] = check_recognition_accuracy()
        
        # System performance health
        health_status["performance"] = check_system_performance()
        
        # Storage health
        health_status["storage"] = check_storage_health()
        
        # Overall health score
        health_status["overall_score"] = calculate_overall_health_score(health_status)
        
        return {
            "success": True,
            "health_status": health_status,
            "timestamp": frappe.utils.now()
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

def check_database_health():
    """Check database health metrics"""
    try:
        # Table sizes
        table_stats = frappe.db.sql("""
            SELECT 
                table_name,
                table_rows,
                ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'size_mb'
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name LIKE 'tabEmployee%%'
            OR table_name LIKE '%%Attendance%%'
        """, (frappe.conf.db_name,), as_dict=True)
        
        # Recent activity
        recent_records = frappe.db.count(
            "Employee Attendance",
            {"creation": [">=", frappe.utils.add_days(frappe.utils.nowdate(), -1)]}
        )
        
        return {
            "status": "healthy",
            "table_stats": table_stats,
            "recent_activity": recent_records,
            "total_employees": frappe.db.count("Employee Face Recognition"),
            "total_attendance_records": frappe.db.count("Employee Attendance")
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_recognition_accuracy():
    """Check recognition accuracy health"""
    try:
        # Recent accuracy stats
        recent_stats = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN verification_status = 'Verified' THEN 1 ELSE 0 END) as successful,
                AVG(confidence_score) as avg_confidence
            FROM `tabEmployee Attendance`
            WHERE creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            AND confidence_score > 0
        """, as_dict=True)[0]
        
        success_rate = (recent_stats["successful"] / recent_stats["total_attempts"]) * 100 if recent_stats["total_attempts"] > 0 else 0
        
        status = "healthy" if success_rate >= 90 else "warning" if success_rate >= 80 else "critical"
        
        return {
            "status": status,
            "success_rate": round(success_rate, 2),
            "avg_confidence": round(recent_stats["avg_confidence"] or 0, 2),
            "total_attempts_24h": recent_stats["total_attempts"]
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_system_performance():
    """Check system performance metrics"""
    try:
        # Average recognition time (estimated)
        avg_recognition_time = 2.5  # seconds (placeholder)
        
        # System load indicators
        active_kiosks = frappe.db.count("Attendance Kiosk", {"is_active": 1})
        
        status = "healthy" if avg_recognition_time <= 3 else "warning" if avg_recognition_time <= 5 else "critical"
        
        return {
            "status": status,
            "avg_recognition_time": avg_recognition_time,
            "active_kiosks": active_kiosks,
            "memory_usage": "Normal",  # Placeholder
            "cpu_usage": "Normal"      # Placeholder
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_storage_health():
    """Check storage health and usage"""
    try:
        # Count face images
        total_face_images = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabFile`
            WHERE file_name LIKE '%%face%%'
            OR file_name LIKE '%%attendance%%'
        """, as_dict=True)[0]["count"]
        
        # Estimate storage usage (placeholder calculation)
        estimated_storage_mb = total_face_images * 0.5  # Assuming 0.5MB per image
        
        status = "healthy" if estimated_storage_mb < 1000 else "warning" if estimated_storage_mb < 5000 else "critical"
        
        return {
            "status": status,
            "total_face_images": total_face_images,
            "estimated_storage_mb": round(estimated_storage_mb, 2),
            "cleanup_needed": estimated_storage_mb > 2000
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def calculate_overall_health_score(health_status):
    """Calculate overall health score"""
    try:
        scores = {
            "healthy": 100,
            "warning": 70,
            "critical": 30,
            "error": 0
        }
        
        weights = {
            "database": 0.25,
            "accuracy": 0.35,
            "performance": 0.25,
            "storage": 0.15
        }
        
        total_score = 0
        for component, weight in weights.items():
            component_score = scores.get(health_status[component]["status"], 0)
            total_score += component_score * weight
        
        return round(total_score, 1)
        
    except:
        return 0