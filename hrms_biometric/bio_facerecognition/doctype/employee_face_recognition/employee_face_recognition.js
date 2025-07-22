frappe.ui.form.on('Employee Face Recognition', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Capture Face Images'), function() {
            openFaceCaptureDialog(frm);
        });
        
        frm.add_custom_button(__('Test Recognition'), function() {
            testEmployeeFaceRecognition(frm);
        });
        
        frm.add_custom_button(__('View Attendance'), function() {
            frappe.route_options = {
                "employee_id": frm.doc.employee_id
            };
            frappe.set_route("List", "Employee Attendance");
        });
        
        // Show encoding status
        if (frm.doc.encoding_data) {
            frm.dashboard.add_indicator(__('Face Encodings: Ready'), 'green');
        } else {
            frm.dashboard.add_indicator(__('Face Encodings: Not Generated'), 'red');
        }
    },
    
    before_save: function(frm) {
        // Validate that all required images are uploaded
        let requiredImages = ['face_image_1', 'face_image_2', 'face_image_3'];
        let missingImages = [];
        
        requiredImages.forEach(function(field) {
            if (!frm.doc[field]) {
                missingImages.push(field.replace('face_image_', 'Image '));
            }
        });
        
        if (missingImages.length > 0) {
            frappe.throw(__('Please upload all required face images: {0}', [missingImages.join(', ')]));
        }
    },
    
    employee_id: function(frm) {
        if (frm.doc.employee_id) {
            // Auto-generate employee name if not set
            if (!frm.doc.employee_name) {
                frm.set_value('employee_name', frm.doc.employee_id + ' Employee');
            }
        }
    }
});

function openFaceCaptureDialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Capture Face Images'),
        fields: [
            {
                fieldname: 'instructions',
                fieldtype: 'HTML',
                options: `
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                        <h4 style="color: #333; margin-bottom: 15px;">📸 Face Capture Instructions</h4>
                        <ul style="text-align: left; color: #666; line-height: 1.6;">
                            <li>Look directly at the camera</li>
                            <li>Ensure good lighting on your face</li>
                            <li>Keep a neutral expression</li>
                            <li>Remove glasses if possible</li>
                            <li>Capture from slightly different angles</li>
                        </ul>
                    </div>
                `
            },
            {
                fieldname: 'camera_section',
                fieldtype: 'Section Break',
                label: 'Camera'
            },
            {
                fieldname: 'camera_feed',
                fieldtype: 'HTML',
                options: `
                    <div style="text-align: center;">
                        <video id="capture-video" width="400" height="300" autoplay muted playsinline style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></video>
                        <div style="margin-top: 15px;">
                            <button id="start-capture-camera" class="btn btn-primary btn-sm" style="margin-right: 10px;">Start Camera</button>
                            <button id="capture-image" class="btn btn-success btn-sm" disabled>Capture Image</button>
                            <button id="stop-capture-camera" class="btn btn-secondary btn-sm" style="margin-left: 10px;" disabled>Stop Camera</button>
                        </div>
                        <div id="capture-status" style="margin-top: 10px; font-weight: 500;"></div>
                    </div>
                `
            },
            {
                fieldname: 'captured_images_section',
                fieldtype: 'Section Break',
                label: 'Captured Images'
            },
            {
                fieldname: 'captured_images',
                fieldtype: 'HTML',
                options: `
                    <div id="captured-images-container" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <div class="image-slot" data-slot="1">
                            <div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">
                                Image 1<br>Not Captured
                            </div>
                        </div>
                        <div class="image-slot" data-slot="2">
                            <div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">
                                Image 2<br>Not Captured
                            </div>
                        </div>
                        <div class="image-slot" data-slot="3">
                            <div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">
                                Image 3<br>Not Captured
                            </div>
                        </div>
                        <div class="image-slot" data-slot="4">
                            <div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">
                                Image 4<br>Optional
                            </div>
                        </div>
                        <div class="image-slot" data-slot="5">
                            <div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">
                                Image 5<br>Optional
                            </div>
                        </div>
                    </div>
                `
            }
        ],
        size: 'large',
        primary_action_label: __('Save Images'),
        primary_action: function(dialog) {
            saveCapturedImages(frm, dialog);
        },
        secondary_action_label: __('Cancel'),
        secondary_action: function(dialog) {
            stopCaptureCamera();
            dialog.hide();
        }
    });

    d.show();
    initializeCaptureInterface(d);
}

function initializeCaptureInterface(dialog) {
    let stream = null;
    let currentSlot = 1;
    let capturedImages = {};
    
    // Get DOM elements
    const video = document.getElementById('capture-video');
    const startBtn = document.getElementById('start-capture-camera');
    const captureBtn = document.getElementById('capture-image');
    const stopBtn = document.getElementById('stop-capture-camera');
    const status = document.getElementById('capture-status');
    
    // Event listeners
    startBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            video.srcObject = stream;
            startBtn.disabled = true;
            captureBtn.disabled = false;
            stopBtn.disabled = false;
            status.textContent = '✅ Camera started - Ready to capture';
            status.style.color = 'green';
            
        } catch (error) {
            console.error('Camera error:', error);
            status.textContent = '❌ Camera access denied';
            status.style.color = 'red';
        }
    });
    
    captureBtn.addEventListener('click', () => {
        captureImage();
    });
    
    stopBtn.addEventListener('click', () => {
        stopCamera();
    });
    
    function captureImage() {
        if (!stream || currentSlot > 5) return;
        
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        capturedImages[currentSlot] = imageData;
        
        // Update UI
        const slot = document.querySelector(`[data-slot="${currentSlot}"]`);
        if (slot) {
            const placeholder = slot.querySelector('.image-placeholder');
            placeholder.innerHTML = '<img src="' + imageData + '" style="width: 150px; height: 120px; object-fit: cover; border-radius: 8px;">';
            placeholder.style.border = '2px solid #28a745';
        }
        
        status.textContent = 'Image ' + currentSlot + ' captured successfully';
        status.style.color = 'green';
        
        currentSlot++;
        
        if (currentSlot > 3) {
            status.textContent = 'Required images captured. You can capture ' + (5 - currentSlot + 1) + ' more optional images.';
        }
        
        if (currentSlot > 5) {
            captureBtn.disabled = true;
            status.textContent = 'All image slots filled';
        }
    }
    
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        video.srcObject = null;
        startBtn.disabled = false;
        captureBtn.disabled = true;
        stopBtn.disabled = true;
        status.textContent = '📷 Camera stopped';
        status.style.color = '#666';
    }
    
    // Store references for cleanup
    dialog.capturedImages = capturedImages;
    dialog.stopCamera = stopCamera;
}

async function saveCapturedImages(frm, dialog) {
    const capturedImages = dialog.capturedImages || {};
    
    // Check if minimum required images are captured
    if (!capturedImages[1] || !capturedImages[2] || !capturedImages[3]) {
        frappe.throw(__('Please capture at least the first 3 face images'));
        return;
    }
    
    try {
        frappe.show_alert({
            message: 'Saving images...',
            indicator: 'blue'
        });
        
        // Save each captured image
        for (let slot = 1; slot <= 5; slot++) {
            if (capturedImages[slot]) {
                const fieldName = 'face_image_' + slot;
                const fileName = frm.doc.employee_id + '_face_' + slot + '_' + Date.now() + '.jpg';
                
                // Convert base64 to file and upload
                const fileDoc = await uploadBase64Image(capturedImages[slot], fileName);
                if (fileDoc) {
                    frm.set_value(fieldName, fileDoc.file_url);
                }
            }
        }
        
        // Stop camera and close dialog
        if (dialog.stopCamera) {
            dialog.stopCamera();
        }
        dialog.hide();
        
        frappe.show_alert({
            message: 'Face images saved successfully!',
            indicator: 'green'
        });
        
        // Trigger save to generate encodings
        frm.save();
        
    } catch (error) {
        console.error('Error saving images:', error);
        frappe.show_alert({
            message: 'Error saving images: ' + error.message,
            indicator: 'red'
        });
    }
}

async function uploadBase64Image(base64Data, fileName) {
    try {
        // Remove data URL prefix
        const base64 = base64Data.split(',')[1];
        
        // Convert base64 to blob
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {type: 'image/jpeg'});
        
        // Create form data
        const formData = new FormData();
        formData.append('file', blob, fileName);
        formData.append('is_private', 1);
        formData.append('folder', 'Home');
        
        // Upload file
        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': frappe.csrf_token
            },
            body: formData
        });
        
        const result = await response.json();
        if (result.message) {
            return result.message;
        } else {
            throw new Error('Upload failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

function testEmployeeFaceRecognition(frm) {
    if (!frm.doc.employee_id) {
        frappe.throw(__('Please save the employee record first'));
        return;
    }
    
    if (!frm.doc.encoding_data) {
        frappe.throw(__('No face encodings found. Please upload face images and save the record first.'));
        return;
    }
    
    let testDialog = new frappe.ui.Dialog({
        title: __('Test Face Recognition'),
        fields: [
            {
                fieldname: 'test_instructions',
                fieldtype: 'HTML',
                options: `
                    <div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 8px; margin-bottom: 20px;">
                        <h4 style="color: #1976d2; margin-bottom: 15px;">🧪 Recognition Test</h4>
                        <p style="color: #666; margin-bottom: 0;">Position your face in front of the camera to test recognition accuracy</p>
                    </div>
                `
            },
            {
                fieldname: 'test_camera_feed',
                fieldtype: 'HTML',
                options: `
                    <div style="text-align: center;">
                        <video id="test-video" width="400" height="300" autoplay muted playsinline style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></video>
                        <div style="margin-top: 15px;">
                            <button id="start-test-camera" class="btn btn-primary btn-sm">Start Camera</button>
                            <button id="test-recognition" class="btn btn-success btn-sm" disabled>Test Recognition</button>
                            <button id="stop-test-camera" class="btn btn-secondary btn-sm" disabled>Stop Camera</button>
                        </div>
                        <div id="test-status" style="margin-top: 15px; padding: 10px; border-radius: 5px; display: none;"></div>
                        <div id="test-results" style="margin-top: 15px; display: none;"></div>
                    </div>
                `
            }
        ],
        size: 'large',
        primary_action_label: __('Close'),
        primary_action: function(dialog) {
            stopTestCamera();
            dialog.hide();
        }
    });
    
    testDialog.show();
    initializeTestInterface(frm, testDialog);
}

function initializeTestInterface(frm, dialog) {
    let testStream = null;
    
    const video = document.getElementById('test-video');
    const startBtn = document.getElementById('start-test-camera');
    const testBtn = document.getElementById('test-recognition');
    const stopBtn = document.getElementById('stop-test-camera');
    const status = document.getElementById('test-status');
    const results = document.getElementById('test-results');
    
    startBtn.addEventListener('click', async () => {
        try {
            testStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            video.srcObject = testStream;
            startBtn.disabled = true;
            testBtn.disabled = false;
            stopBtn.disabled = false;
            
            showTestStatus('✅ Camera ready for testing', 'success');
            
        } catch (error) {
            showTestStatus('❌ Camera access denied', 'error');
        }
    });
    
    testBtn.addEventListener('click', async () => {
        await performRecognitionTest(frm, video);
    });
    
    stopBtn.addEventListener('click', () => {
        stopTestCamera();
    });
    
    function stopTestCamera() {
        if (testStream) {
            testStream.getTracks().forEach(track => track.stop());
            testStream = null;
        }
        
        video.srcObject = null;
        startBtn.disabled = false;
        testBtn.disabled = true;
        stopBtn.disabled = true;
        showTestStatus('📷 Camera stopped', 'info');
    }
    
    function showTestStatus(message, type) {
        status.style.display = 'block';
        status.textContent = message;
        status.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'}`;
    }
    
    dialog.stopTestCamera = stopTestCamera;
}

async function performRecognitionTest(frm, video) {
    try {
        document.getElementById('test-status').textContent = '🔍 Testing recognition...';
        document.getElementById('test-status').className = 'alert alert-info';
        
        // Capture image
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Call recognition API
        const response = await fetch('/api/method/bio_facerecognition.bio_facerecognition.api.enhanced_face_recognition.recognize_face_from_camera', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            },
            body: JSON.stringify({
                captured_image: imageData,
                kiosk_name: 'Test'
            })
        });
        
        const data = await response.json();
        const result = data.message || data;
        
        displayTestResults(result, frm.doc.employee_id);
        
    } catch (error) {
        console.error('Recognition test error:', error);
        document.getElementById('test-status').textContent = '❌ Test failed: ' + error.message;
        document.getElementById('test-status').className = 'alert alert-danger';
    }
}

function displayTestResults(result, expectedEmployeeId) {
    const resultsDiv = document.getElementById('test-results');
    const statusDiv = document.getElementById('test-status');
    
    if (result.success) {
        const isCorrect = result.employee.employee_id === expectedEmployeeId;
        const statusClass = isCorrect ? 'success' : 'warning';
        const statusIcon = isCorrect ? '✅' : '⚠️';
        
        statusDiv.textContent = `${statusIcon} Recognition ${isCorrect ? 'Successful' : 'Incorrect'}`;
        statusDiv.className = `alert alert-${statusClass}`;
        
        resultsDiv.innerHTML = `
            <div class="alert alert-${statusClass}" style="text-align: left;">
                <h5>${statusIcon} Recognition Results</h5>
                <p><strong>Detected Employee:</strong> ${result.employee.employee_name} (${result.employee.employee_id})</p>
                <p><strong>Confidence Score:</strong> ${result.confidence}%</p>
                <p><strong>Department:</strong> ${result.employee.department || 'N/A'}</p>
                <p><strong>Expected Employee:</strong> ${expectedEmployeeId}</p>
                <p><strong>Match Status:</strong> ${isCorrect ? 'Correct Match ✅' : 'Incorrect Match ⚠️'}</p>
            </div>
        `;
    } else {
        statusDiv.textContent = '❌ Recognition Failed';
        statusDiv.className = 'alert alert-danger';
        
        resultsDiv.innerHTML = `
            <div class="alert alert-danger" style="text-align: left;">
                <h5>❌ Recognition Failed</h5>
                <p><strong>Error:</strong> ${result.message}</p>
                <p><strong>Suggestions:</strong></p>
                <ul>
                    <li>Ensure your face is clearly visible</li>
                    <li>Check lighting conditions</li>
                    <li>Make sure face images were uploaded correctly</li>
                    <li>Try capturing additional face images</li>
                </ul>
            </div>
        `;
    }
    
    resultsDiv.style.display = 'block';
}

// Cleanup function for when the form is refreshed
frappe.ui.form.on('Employee Face Recognition', {
    onload: function(frm) {
        // Add any initialization code here
    },
    
    before_load: function(frm) {
        // Cleanup any existing camera streams
        if (window.currentCaptureStream) {
            window.currentCaptureStream.getTracks().forEach(track => track.stop());
            window.currentCaptureStream = null;
        }
    }
});

// Helper function to stop any active camera
function stopCaptureCamera() {
    if (window.currentCaptureStream) {
        window.currentCaptureStream.getTracks().forEach(track => track.stop());
        window.currentCaptureStream = null;
    }
}