# hrms_biometric/bio_facerecognition/api/image_processing.py

import frappe
import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO
import face_recognition
import logging

logger = logging.getLogger(__name__)

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

def validate_face_image_quality(image_data):
    """Validate face image quality before storing"""
    try:
        # Decode image
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = base64.b64decode(image_data.split(',')[1])
            else:
                image_data = base64.b64decode(image_data)
        
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"valid": False, "reason": "Invalid image format"}
        
        # Check image dimensions
        height, width = image.shape[:2]
        if width < 200 or height < 200:
            return {"valid": False, "reason": "Image too small (minimum 200x200)"}
        
        if width > 2000 or height > 2000:
            return {"valid": False, "reason": "Image too large (maximum 2000x2000)"}
        
        # Check for face presence
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return {"valid": False, "reason": "No face detected in image"}
        
        if len(face_locations) > 1:
            return {"valid": False, "reason": "Multiple faces detected. Please use single face image"}
        
        # Check face size relative to image
        top, right, bottom, left = face_locations[0]
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        image_area = width * height
        face_ratio = face_area / image_area
        
        if face_ratio < 0.1:
            return {"valid": False, "reason": "Face too small in image"}
        
        # Check image blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if blur_score < 100:
            return {"valid": False, "reason": "Image is too blurry"}
        
        # Check brightness
        brightness = np.mean(gray)
        if brightness < 50:
            return {"valid": False, "reason": "Image too dark"}
        if brightness > 200:
            return {"valid": False, "reason": "Image too bright"}
        
        return {
            "valid": True,
            "quality_score": min(100, (blur_score / 500) * 100),
            "face_ratio": face_ratio,
            "brightness": brightness
        }
        
    except Exception as e:
        return {"valid": False, "reason": f"Error validating image: {str(e)}"}

def compress_image_for_storage(image_data, quality=85):
    """Compress image for efficient storage"""
    try:
        # Decode image
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = base64.b64decode(image_data.split(',')[1])
            else:
                image_data = base64.b64decode(image_data)
        
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        # Resize if too large
        height, width = image.shape[:2]
        max_dimension = 800
        
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Compress image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, compressed_image = cv2.imencode('.jpg', image, encode_param)
        
        # Convert back to base64
        compressed_base64 = base64.b64encode(compressed_image.tobytes()).decode('utf-8')
        
        return f"data:image/jpeg;base64,{compressed_base64}"
        
    except Exception as e:
        frappe.log_error(f"Image compression error: {str(e)}")
        return image_data

def convert_base64_to_cv2(base64_string):
    """Convert base64 string to OpenCV image"""
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        return image
        
    except Exception as e:
        frappe.log_error(f"Base64 to CV2 conversion error: {str(e)}")
        return None

def convert_cv2_to_base64(image):
    """Convert OpenCV image to base64 string"""
    try:
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{image_base64}"
        
    except Exception as e:
        frappe.log_error(f"CV2 to Base64 conversion error: {str(e)}")
        return None

def detect_anti_spoofing(image):
    """Basic anti-spoofing detection"""
    try:
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate various metrics
        metrics = {}
        
        # Texture analysis
        gray_laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        metrics['texture_variance'] = np.var(gray_laplacian)
        
        # Color diversity
        metrics['color_std'] = np.std(hsv[:,:,1])  # Saturation standard deviation
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        metrics['edge_density'] = np.sum(edges > 0) / edges.size
        
        # Simple scoring (these thresholds would need tuning)
        live_score = 0
        if metrics['texture_variance'] > 100:
            live_score += 30
        if metrics['color_std'] > 20:
            live_score += 30
        if metrics['edge_density'] > 0.1:
            live_score += 40
        
        return {
            "is_live": live_score > 60,
            "confidence": live_score,
            "metrics": metrics
        }
        
    except Exception as e:
        frappe.log_error(f"Anti-spoofing detection error: {str(e)}")
        return {"is_live": True, "confidence": 50, "metrics": {}}