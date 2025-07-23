// Complete Fixed Employee Face Recognition JS for Frappe v15

frappe.ui.form.on('Employee Face Recognition', {
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Capture Face Images'), function() {
            openFaceCaptureDialog(frm);
        });
        
        frm.add_custom_button(__('Test Camera'), function() {
            testCameraAccess();
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
        var requiredImages = ['face_image_1', 'face_image_2', 'face_image_3'];
        var missingImages = [];
        
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
    // First ensure the document is saved
    if (!frm.doc.name) {
        frappe.msgprint({
            title: __('Document Not Saved'),
            message: __('Please save the Employee Face Recognition document first, then try capturing images.'),
            indicator: 'red'
        });
        return;
    }
    
    if (!frm.doc.employee_id) {
        frappe.msgprint({
            title: __('Employee ID Required'),
            message: __('Please set the Employee ID field first.'),
            indicator: 'red'
        });
        return;
    }
    
    var d = new frappe.ui.Dialog({
        title: __('Capture Face Images'),
        fields: [
            {
                fieldname: 'instructions',
                fieldtype: 'HTML',
                options: '<div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">' +
                    '<h4 style="color: #333; margin-bottom: 15px;">📸 Face Capture Instructions</h4>' +
                    '<ul style="text-align: left; color: #666; line-height: 1.6;">' +
                        '<li>Look directly at the camera</li>' +
                        '<li>Ensure good lighting on your face</li>' +
                        '<li>Keep a neutral expression</li>' +
                        '<li>Remove glasses if possible</li>' +
                        '<li>Capture from slightly different angles</li>' +
                    '</ul>' +
                '</div>'
            },
            {
                fieldname: 'camera_section',
                fieldtype: 'Section Break',
                label: 'Camera'
            },
            {
                fieldname: 'camera_feed',
                fieldtype: 'HTML',
                options: '<div style="text-align: center;">' +
                    '<video id="capture-video" width="400" height="300" autoplay muted playsinline style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></video>' +
                    '<div style="margin-top: 15px;">' +
                        '<button id="start-capture-camera" class="btn btn-primary btn-sm" style="margin-right: 10px;">Start Camera</button>' +
                        '<button id="capture-image" class="btn btn-success btn-sm" disabled>Capture Image</button>' +
                        '<button id="stop-capture-camera" class="btn btn-secondary btn-sm" style="margin-left: 10px;" disabled>Stop Camera</button>' +
                    '</div>' +
                    '<div id="capture-status" style="margin-top: 10px; font-weight: 500;"></div>' +
                '</div>'
            },
            {
                fieldname: 'images_section',
                fieldtype: 'Section Break',
                label: 'Captured Images'
            },
            {
                fieldname: 'images_grid',
                fieldtype: 'HTML',
                options: '<div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; padding: 20px;">' +
                    '<div class="image-slot" data-slot="1">' +
                        '<div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">' +
                            'Image 1<br>Required' +
                        '</div>' +
                    '</div>' +
                    '<div class="image-slot" data-slot="2">' +
                        '<div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">' +
                            'Image 2<br>Required' +
                        '</div>' +
                    '</div>' +
                    '<div class="image-slot" data-slot="3">' +
                        '<div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">' +
                            'Image 3<br>Required' +
                        '</div>' +
                    '</div>' +
                    '<div class="image-slot" data-slot="4">' +
                        '<div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">' +
                            'Image 4<br>Optional' +
                        '</div>' +
                    '</div>' +
                    '<div class="image-slot" data-slot="5">' +
                        '<div class="image-placeholder" style="width: 150px; height: 120px; border: 2px dashed #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px; text-align: center;">' +
                            'Image 5<br>Optional' +
                        '</div>' +
                    '</div>' +
                '</div>'
            }
        ],
        size: 'large',
        primary_action_label: __('Save Images'),
        primary_action: function(dialog) {
            saveCapturedImages(frm, dialog);
        },
        secondary_action_label: __('Cancel'),
        secondary_action: function(dialog) {
            stopCaptureCamera(dialog);
            dialog.hide();
        },
        onhide: function(dialog) {
            stopCaptureCamera(dialog);
        }
    });

    d.show();
    
    // Add delay to ensure DOM is ready
    setTimeout(function() {
        initializeCaptureInterface(d, frm);
    }, 500);
}

function initializeCaptureInterface(dialog, frm) {
    var stream = null;
    var currentSlot = 1;
    var capturedImages = {};
    
    function waitForElements() {
        var video = document.getElementById('capture-video');
        var startBtn = document.getElementById('start-capture-camera');
        var captureBtn = document.getElementById('capture-image');
        var stopBtn = document.getElementById('stop-capture-camera');
        var status = document.getElementById('capture-status');
        
        if (!video || !startBtn || !captureBtn || !stopBtn || !status) {
            console.log('Waiting for DOM elements...');
            setTimeout(waitForElements, 100);
            return;
        }
        
        setupEventListeners(video, startBtn, captureBtn, stopBtn, status);
    }
    
    function setupEventListeners(video, startBtn, captureBtn, stopBtn, status) {
        // Start camera button
        startBtn.addEventListener('click', function() {
            navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            }).then(function(mediaStream) {
                stream = mediaStream;
                video.srcObject = stream;
                startBtn.disabled = true;
                captureBtn.disabled = false;
                stopBtn.disabled = false;
                status.textContent = '✅ Camera started - Ready to capture';
                status.style.color = 'green';
            }).catch(function(error) {
                console.error('Camera error:', error);
                status.textContent = '❌ Camera access denied';
                status.style.color = 'red';
            });
        });
        
        // Capture image button
        captureBtn.addEventListener('click', function() {
            captureImage();
        });
        
        // Stop camera button
        stopBtn.addEventListener('click', function() {
            stopCamera();
        });
        
        function captureImage() {
            if (!stream || currentSlot > 5) return;
            
            var canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            var imageData = canvas.toDataURL('image/jpeg', 0.8);
            capturedImages[currentSlot] = imageData;
            
            // Update UI
            var slot = document.querySelector('[data-slot="' + currentSlot + '"]');
            if (slot) {
                var placeholder = slot.querySelector('.image-placeholder');
                placeholder.innerHTML = '<img src="' + imageData + '" style="width: 150px; height: 120px; object-fit: cover; border-radius: 8px;">';
                placeholder.style.border = '2px solid #28a745';
            }
            
            status.textContent = 'Image ' + currentSlot + ' captured successfully';
            status.style.color = 'green';
            
            currentSlot++;
            
            if (currentSlot > 3) {
                status.textContent = 'Required images captured. You can capture ' + (5 - currentSlot + 1) + ' more optional images.';
            }
        }
        
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(function(track) {
                    track.stop();
                });
                stream = null;
            }
            
            video.srcObject = null;
            startBtn.disabled = false;
            captureBtn.disabled = true;
            stopBtn.disabled = true;
            status.textContent = '📷 Camera stopped';
            status.style.color = '#666';
        }
        
        // Store cleanup function and data on dialog
        dialog.stopCaptureCamera = stopCamera;
        dialog.capturedImages = capturedImages;
        dialog.captureStream = stream;
    }
    
    waitForElements();
}

function saveCapturedImages(frm, dialog) {
    var capturedImages = dialog.capturedImages || {};
    
    if (Object.keys(capturedImages).length < 3) {
        frappe.msgprint(__('Please capture at least 3 images before saving.'));
        return;
    }
    
    // Show progress dialog
    var progressDialog = frappe.msgprint({
        title: __('Uploading Images'),
        message: __('Uploading captured images... Please wait.'),
        indicator: 'blue'
    });
    
    var uploadedCount = 0;
    var totalImages = Object.keys(capturedImages).length;
    var errors = [];
    
    // Upload images one by one
    uploadNextImage(Object.keys(capturedImages), 0);
    
    function uploadNextImage(slots, index) {
        if (index >= slots.length) {
            // All uploads complete
            progressDialog.hide();
            
            if (uploadedCount > 0) {
                frappe.show_alert({
                    message: 'Successfully uploaded ' + uploadedCount + ' image(s)!',
                    indicator: 'green'
                });
                
                // Save the document
                frm.save().then(function() {
                    frappe.show_alert({
                        message: 'Document saved with face images!',
                        indicator: 'green'
                    });
                });
            }
            
            if (errors.length > 0) {
                frappe.show_alert({
                    message: errors.length + ' image(s) failed to upload',
                    indicator: 'orange'
                });
            }
            
            // Close dialog
            stopCaptureCamera(dialog);
            dialog.hide();
            return;
        }
        
        var slot = slots[index];
        var imageData = capturedImages[slot];
        var fieldName = 'face_image_' + slot;
        
        // Update progress
        progressDialog.$wrapper.find('.msgprint-text').text(
            'Uploading image ' + (index + 1) + ' of ' + totalImages + '...'
        );
        
        // Upload using Frappe's file upload API
        uploadImageToField(imageData, fieldName, frm, slot).then(function(result) {
            if (result.success) {
                uploadedCount++;
                frm.set_value(fieldName, result.file_url);
            } else {
                errors.push('Image ' + slot + ': ' + result.error);
            }
            
            // Upload next image after a short delay
            setTimeout(function() {
                uploadNextImage(slots, index + 1);
            }, 500);
        }).catch(function(error) {
            errors.push('Image ' + slot + ': ' + error.message);
            setTimeout(function() {
                uploadNextImage(slots, index + 1);
            }, 500);
        });
    }
}

function uploadImageToField(imageData, fieldName, frm, slot) {
    return new Promise(function(resolve, reject) {
        try {
            // Convert base64 to blob
            var base64Data = imageData.split(',')[1];
            var byteCharacters = atob(base64Data);
            var byteNumbers = new Array(byteCharacters.length);
            
            for (var i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            
            var byteArray = new Uint8Array(byteNumbers);
            var blob = new Blob([byteArray], { type: 'image/jpeg' });
            
            // Generate unique filename
            var timestamp = new Date().getTime();
            var filename = 'face_' + slot + '_' + frm.doc.employee_id + '_' + timestamp + '.jpg';
            
            // Create FormData
            var formData = new FormData();
            formData.append('file', blob, filename);
            formData.append('is_private', 0);
            formData.append('folder', 'Home/Attachments');
            formData.append('doctype', frm.doc.doctype);
            formData.append('docname', frm.doc.name);
            
            // Upload file
            fetch('/api/method/upload_file', {
                method: 'POST',
                headers: {
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                },
                body: formData
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                if (data.message && data.message.file_url) {
                    resolve({
                        success: true,
                        file_url: data.message.file_url,
                        file_name: data.message.file_name
                    });
                } else {
                    resolve({
                        success: false,
                        error: 'Upload failed - no file URL returned'
                    });
                }
            }).catch(function(error) {
                resolve({
                    success: false,
                    error: error.message
                });
            });
            
        } catch (error) {
            resolve({
                success: false,
                error: error.message
            });
        }
    });
}

function testEmployeeFaceRecognition(frm) {
    if (!frm.doc.face_image_1 || !frm.doc.face_image_2 || !frm.doc.face_image_3) {
        frappe.msgprint(__('Please upload face images and save the record first.'));
        return;
    }
    
    var testDialog = new frappe.ui.Dialog({
        title: __('Test Face Recognition'),
        fields: [
            {
                fieldname: 'test_instructions',
                fieldtype: 'HTML',
                options: '<div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 8px; margin-bottom: 20px;">' +
                    '<h4 style="color: #1976d2; margin-bottom: 15px;">🧪 Recognition Test</h4>' +
                    '<p style="color: #666; margin-bottom: 0;">Position your face in front of the camera to test recognition accuracy</p>' +
                '</div>'
            },
            {
                fieldname: 'test_camera_feed',
                fieldtype: 'HTML',
                options: '<div style="text-align: center;">' +
                    '<video id="test-video" width="400" height="300" autoplay muted playsinline style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></video>' +
                    '<div style="margin-top: 15px;">' +
                        '<button id="start-test-camera" class="btn btn-primary btn-sm">Start Camera</button>' +
                        '<button id="test-recognition" class="btn btn-success btn-sm" disabled>Test Recognition</button>' +
                        '<button id="stop-test-camera" class="btn btn-secondary btn-sm" disabled>Stop Camera</button>' +
                    '</div>' +
                    '<div id="test-status" style="margin-top: 15px; padding: 10px; border-radius: 5px; display: none;"></div>' +
                    '<div id="test-results" style="margin-top: 15px; display: none;"></div>' +
                '</div>'
            }
        ],
        size: 'large',
        primary_action_label: __('Close'),
        primary_action: function(dialog) {
            stopTestCamera(dialog);
            dialog.hide();
        },
        onhide: function(dialog) {
            stopTestCamera(dialog);
        }
    });
    
    testDialog.show();
    
    setTimeout(function() {
        initializeTestInterface(frm, testDialog);
    }, 500);
}

function initializeTestInterface(frm, dialog) {
    var testStream = null;
    
    function waitForTestElements() {
        var video = document.getElementById('test-video');
        var startBtn = document.getElementById('start-test-camera');
        var testBtn = document.getElementById('test-recognition');
        var stopBtn = document.getElementById('stop-test-camera');
        var status = document.getElementById('test-status');
        var results = document.getElementById('test-results');
        
        if (!video || !startBtn || !testBtn || !stopBtn || !status || !results) {
            console.log('Waiting for test DOM elements...');
            setTimeout(waitForTestElements, 100);
            return;
        }
        
        setupTestEventListeners(video, startBtn, testBtn, stopBtn, status, results);
    }
    
    function setupTestEventListeners(video, startBtn, testBtn, stopBtn, status, results) {
        startBtn.addEventListener('click', function() {
            navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            }).then(function(stream) {
                testStream = stream;
                video.srcObject = testStream;
                startBtn.disabled = true;
                testBtn.disabled = false;
                stopBtn.disabled = false;
                
                showTestStatus('✅ Camera ready for testing', 'success');
            }).catch(function(error) {
                showTestStatus('❌ Camera access denied', 'error');
            });
        });
        
        testBtn.addEventListener('click', function() {
            performRecognitionTest(frm, video);
        });
        
        stopBtn.addEventListener('click', function() {
            stopTestCameraInternal();
        });
        
        function stopTestCameraInternal() {
            if (testStream) {
                testStream.getTracks().forEach(function(track) {
                    track.stop();
                });
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
            status.className = 'alert alert-' + (type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info');
        }
        
        dialog.stopTestCamera = stopTestCameraInternal;
        dialog.testStream = testStream;
    }
    
    waitForTestElements();
}

function performRecognitionTest(frm, video) {
    try {
        document.getElementById('test-status').textContent = '🔍 Testing recognition...';
        document.getElementById('test-status').className = 'alert alert-info';
        
        // Capture image
        var canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        var imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Call recognition API
        fetch('/api/method/hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.recognize_face_from_camera', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token
            },
            body: JSON.stringify({
                captured_image: imageData,
                kiosk_name: 'Test'
            })
        }).then(function(response) {
            return response.json();
        }).then(function(data) {
            var result = data.message || data;
            displayTestResults(result, frm.doc.employee_id);
        }).catch(function(error) {
            console.error('Recognition test error:', error);
            document.getElementById('test-status').textContent = '❌ Test failed: ' + error.message;
            document.getElementById('test-status').className = 'alert alert-danger';
        });
    } catch (error) {
        console.error('Recognition test error:', error);
        document.getElementById('test-status').textContent = '❌ Test failed: ' + error.message;
        document.getElementById('test-status').className = 'alert alert-danger';
    }
}

function displayTestResults(result, expectedEmployeeId) {
    var resultsDiv = document.getElementById('test-results');
    var statusDiv = document.getElementById('test-status');
    
    if (result.success) {
        var isCorrect = result.employee.employee_id === expectedEmployeeId;
        var statusClass = isCorrect ? 'success' : 'warning';
        var statusIcon = isCorrect ? '✅' : '⚠️';
        
        statusDiv.textContent = statusIcon + ' Recognition ' + (isCorrect ? 'Successful' : 'Incorrect');
        statusDiv.className = 'alert alert-' + statusClass;
        
        resultsDiv.innerHTML = '<div class="alert alert-' + statusClass + '" style="text-align: left;">' +
            '<h5>' + statusIcon + ' Recognition Results</h5>' +
            '<p><strong>Detected Employee:</strong> ' + result.employee.employee_name + ' (' + result.employee.employee_id + ')</p>' +
            '<p><strong>Confidence Score:</strong> ' + result.confidence + '%</p>' +
            '<p><strong>Department:</strong> ' + (result.employee.department || 'N/A') + '</p>' +
            '<p><strong>Expected Employee:</strong> ' + expectedEmployeeId + '</p>' +
            '<p><strong>Match Status:</strong> ' + (isCorrect ? 'Correct Match ✅' : 'Incorrect Match ⚠️') + '</p>' +
        '</div>';
    } else {
        statusDiv.textContent = '❌ Recognition Failed';
        statusDiv.className = 'alert alert-danger';
        
        resultsDiv.innerHTML = '<div class="alert alert-danger" style="text-align: left;">' +
            '<h5>❌ Recognition Failed</h5>' +
            '<p><strong>Error:</strong> ' + result.message + '</p>' +
            '<p><strong>Suggestions:</strong></p>' +
            '<ul>' +
                '<li>Ensure your face is clearly visible</li>' +
                '<li>Check lighting conditions</li>' +
                '<li>Make sure face images were uploaded correctly</li>' +
                '<li>Try capturing additional face images</li>' +
            '</ul>' +
        '</div>';
    }
    
    resultsDiv.style.display = 'block';
}

// Helper functions
function stopCaptureCamera(dialog) {
    if (dialog && dialog.stopCaptureCamera) {
        dialog.stopCaptureCamera();
    }
    if (dialog && dialog.captureStream) {
        dialog.captureStream.getTracks().forEach(function(track) {
            track.stop();
        });
    }
}

function stopTestCamera(dialog) {
    if (dialog && dialog.stopTestCamera) {
        dialog.stopTestCamera();
    }
    if (dialog && dialog.testStream) {
        dialog.testStream.getTracks().forEach(function(track) {
            track.stop();
        });
    }
}

function testCameraAccess() {
    frappe.show_alert({
        message: 'Testing camera access...',
        indicator: 'blue'
    });
    
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            stream.getTracks().forEach(function(track) {
                track.stop();
            });
            frappe.show_alert({
                message: '✅ Camera access successful! You can now capture face images.',
                indicator: 'green'
            });
        })
        .catch(function(error) {
            console.error('Camera test error:', error);
            var errorMsg = 'Camera access failed: ';
            
            switch(error.name) {
                case 'NotAllowedError':
                    errorMsg += 'Permission denied. Please allow camera access in your browser.';
                    break;
                case 'NotFoundError':
                    errorMsg += 'No camera found. Please connect a camera device.';
                    break;
                case 'NotReadableError':
                    errorMsg += 'Camera is already in use by another application.';
                    break;
                case 'OverconstrainedError':
                    errorMsg += 'Camera constraints cannot be satisfied.';
                    break;
                default:
                    errorMsg += error.message || 'Unknown error';
            }
            
            frappe.show_alert({
                message: errorMsg,
                indicator: 'red'
            });
        });
}

// Cleanup function for when the form is refreshed
frappe.ui.form.on('Employee Face Recognition', {
    onload: function(frm) {
        // Add any initialization code here
    },
    
    before_load: function(frm) {
        // Cleanup any existing camera streams
        if (window.currentCaptureStream) {
            window.currentCaptureStream.getTracks().forEach(function(track) {
                track.stop();
            });
            window.currentCaptureStream = null;
        }
    }
});
