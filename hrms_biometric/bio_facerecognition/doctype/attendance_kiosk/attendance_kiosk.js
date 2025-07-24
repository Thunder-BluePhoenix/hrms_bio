// Clean Attendance Kiosk JS - Fixed dialog issues and removed duplicates

frappe.ui.form.on('Attendance Kiosk', {
    refresh: function(frm) {
        frm.add_custom_button(__('Launch Kiosk (New Window)'), function() {
            launchKioskInterface(frm);
        });
        
        frm.add_custom_button(__('Show Embedded Kiosk'), function() {
            showEmbeddedKiosk(frm);
        });
        
        frm.add_custom_button(__('Test Camera'), function() {
            testCameraAccess();
        });
        
        frm.add_custom_button(__('Reset Interface'), function() {
            resetKioskInterface(frm);
        });
        
        // Show instructions instead of setting HTML content
        frm.set_df_property('attendance_interface', 'description', 
            'Use the buttons above to launch or test the kiosk interface. ' +
            'The kiosk can be launched in a new window for standalone use, or embedded within this page.'
        );
    }
});

function getAttendanceKioskHTML() {
    return '<!DOCTYPE html>' +
        '<html>' +
        '<head>' +
            '<title>Attendance Kiosk</title>' +
            '<meta charset="utf-8">' +
            '<meta name="viewport" content="width=device-width, initial-scale=1">' +
            '<meta name="csrf-token" content="">' +
            '<style>' +
                '.kiosk-container {' +
                    'display: flex;' +
                    'flex-direction: column;' +
                    'align-items: center;' +
                    'padding: 30px;' +
                    'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);' +
                    'min-height: 100vh;' +
                    'font-family: Arial, sans-serif;' +
                    'color: white;' +
                '}' +
                '.kiosk-header {' +
                    'text-align: center;' +
                    'margin-bottom: 40px;' +
                '}' +
                '.kiosk-header h1 {' +
                    'font-size: 2.5em;' +
                    'margin-bottom: 10px;' +
                    'text-shadow: 2px 2px 4px rgba(0,0,0,0.3);' +
                '}' +
                '.kiosk-main {' +
                    'display: flex;' +
                    'gap: 40px;' +
                    'max-width: 1200px;' +
                    'width: 100%;' +
                '}' +
                '.camera-section {' +
                    'flex: 2;' +
                    'background: rgba(255,255,255,0.1);' +
                    'border-radius: 20px;' +
                    'padding: 30px;' +
                '}' +
                '#kiosk-video {' +
                    'width: 100%;' +
                    'height: 400px;' +
                    'object-fit: cover;' +
                    'border-radius: 15px;' +
                    'background: #000;' +
                '}' +
                '.status-display {' +
                    'background: rgba(255,255,255,0.2);' +
                    'border-radius: 10px;' +
                    'padding: 20px;' +
                    'text-align: center;' +
                    'margin: 20px 0;' +
                '}' +
                '.employee-display {' +
                    'background: rgba(76, 175, 80, 0.2);' +
                    'border-radius: 10px;' +
                    'padding: 20px;' +
                    'text-align: center;' +
                    'display: none;' +
                    'margin-bottom: 20px;' +
                '}' +
                '.employee-display.show { display: block; }' +
                '.control-buttons {' +
                    'display: flex;' +
                    'gap: 15px;' +
                    'justify-content: center;' +
                    'flex-wrap: wrap;' +
                '}' +
                '.kiosk-btn {' +
                    'padding: 15px 30px;' +
                    'border: none;' +
                    'border-radius: 25px;' +
                    'font-size: 1.1em;' +
                    'font-weight: 600;' +
                    'cursor: pointer;' +
                    'background: rgba(255,255,255,0.2);' +
                    'color: white;' +
                    'min-width: 150px;' +
                '}' +
                '.kiosk-btn.primary {' +
                    'background: linear-gradient(45deg, #4CAF50, #45a049);' +
                '}' +
                '.info-section {' +
                    'flex: 1;' +
                    'display: flex;' +
                    'flex-direction: column;' +
                    'gap: 30px;' +
                '}' +
                '.clock-widget {' +
                    'background: rgba(255,255,255,0.1);' +
                    'border-radius: 20px;' +
                    'padding: 30px;' +
                    'text-align: center;' +
                '}' +
                '.digital-time {' +
                    'font-size: 3em;' +
                    'font-weight: bold;' +
                    'margin-bottom: 10px;' +
                '}' +
                '@media (max-width: 768px) {' +
                    '.kiosk-main { flex-direction: column; }' +
                '}' +
            '</style>' +
        '</head>' +
        '<body style="margin: 0; padding: 0;">' +
            '<div class="kiosk-container">' +
                '<div class="kiosk-header">' +
                    '<h1>🏢 Employee Attendance System</h1>' +
                    '<p>Position your face in front of the camera for automatic check-in/check-out</p>' +
                '</div>' +
                
                '<div class="kiosk-main">' +
                    '<div class="camera-section">' +
                        '<video id="kiosk-video" autoplay muted playsinline></video>' +
                        
                        '<div id="status-display" class="status-display">' +
                            '<div style="font-size: 2em; margin-bottom: 10px;">📷</div>' +
                            '<div>Click "Start Camera" to begin</div>' +
                        '</div>' +
                        
                        '<div id="employee-display" class="employee-display">' +
                            '<h3 id="emp-name">Employee Name</h3>' +
                            '<div style="margin-top: 10px;">' +
                                '<div><strong>ID:</strong> <span id="emp-id">-</span></div>' +
                                '<div><strong>Department:</strong> <span id="emp-dept">-</span></div>' +
                                '<div><strong>Time:</strong> <span id="emp-time">-</span></div>' +
                                '<div><strong>Status:</strong> <span id="emp-status">-</span></div>' +
                            '</div>' +
                        '</div>' +
                        
                        '<div class="control-buttons">' +
                            '<button id="start-camera-btn" class="kiosk-btn primary">Start Camera</button>' +
                            '<button id="stop-camera-btn" class="kiosk-btn" style="display: none;">Stop Camera</button>' +
                            '<button id="test-recognition-btn" class="kiosk-btn">Test Recognition</button>' +
                        '</div>' +
                    '</div>' +
                    
                    '<div class="info-section">' +
                        '<div class="clock-widget">' +
                            '<div id="digital-time-display" class="digital-time">--:--:--</div>' +
                            '<div id="digital-date-display">Loading...</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            
            '<script>' +
                'var kioskData = {' +
                    'stream: null,' +
                    'canvas: null,' +
                    'isProcessing: false,' +
                    'lastRecognition: 0,' +
                    'interval: null,' +
                    'clockInterval: null' +
                '};' +
                
                'function initKiosk() {' +
                    'setTimeout(setupKiosk, 100);' +
                '}' +
                
                'function setupKiosk() {' +
                    'var video = document.getElementById("kiosk-video");' +
                    'var startBtn = document.getElementById("start-camera-btn");' +
                    'var stopBtn = document.getElementById("stop-camera-btn");' +
                    'var testBtn = document.getElementById("test-recognition-btn");' +
                    
                    'if (!video || !startBtn) {' +
                        'setTimeout(setupKiosk, 100);' +
                        'return;' +
                    '}' +
                    
                    'kioskData.canvas = document.createElement("canvas");' +
                    
                    'startBtn.addEventListener("click", startCamera);' +
                    'stopBtn.addEventListener("click", stopCamera);' +
                    'testBtn.addEventListener("click", testRecognition);' +
                    
                    'startClock();' +
                '}' +
                
                'function startCamera() {' +
                    'updateStatus("📷", "Starting camera...");' +
                    
                    'navigator.mediaDevices.getUserMedia({' +
                        'video: { width: { ideal: 640 }, height: { ideal: 480 } }' +
                    '}).then(function(stream) {' +
                        'kioskData.stream = stream;' +
                        'var video = document.getElementById("kiosk-video");' +
                        'video.srcObject = stream;' +
                        
                        'video.onloadedmetadata = function() {' +
                            'video.play();' +
                            'kioskData.canvas.width = video.videoWidth;' +
                            'kioskData.canvas.height = video.videoHeight;' +
                            
                            'updateStatus("✅", "Camera active");' +
                            'document.getElementById("start-camera-btn").style.display = "none";' +
                            'document.getElementById("stop-camera-btn").style.display = "inline-block";' +
                            
                            'startRecognition();' +
                        '};' +
                    '}).catch(function(error) {' +
                        'updateStatus("❌", "Camera failed");' +
                    '});' +
                '}' +
                
                'function stopCamera() {' +
                    'if (kioskData.stream) {' +
                        'kioskData.stream.getTracks().forEach(function(track) {' +
                            'track.stop();' +
                        '});' +
                        'kioskData.stream = null;' +
                    '}' +
                    'if (kioskData.interval) {' +
                        'clearInterval(kioskData.interval);' +
                    '}' +
                    'var video = document.getElementById("kiosk-video");' +
                    'if (video) video.srcObject = null;' +
                    
                    'updateStatus("📷", "Camera stopped");' +
                    'document.getElementById("start-camera-btn").style.display = "inline-block";' +
                    'document.getElementById("stop-camera-btn").style.display = "none";' +
                    'hideEmployee();' +
                '}' +
                
                'function startRecognition() {' +
                    'kioskData.interval = setInterval(function() {' +
                        'if (!kioskData.isProcessing && kioskData.stream) {' +
                            'performRecognition();' +
                        '}' +
                    '}, 3000);' +
                '}' +
                
                'function performRecognition() {' +
                    'var currentTime = Date.now();' +
                    'if (currentTime - kioskData.lastRecognition < 5000) return;' +
                    
                    'try {' +
                        'kioskData.isProcessing = true;' +
                        'kioskData.lastRecognition = currentTime;' +
                        
                        'var video = document.getElementById("kiosk-video");' +
                        'if (!video || !kioskData.canvas) return;' +
                        
                        'var ctx = kioskData.canvas.getContext("2d");' +
                        'ctx.drawImage(video, 0, 0, kioskData.canvas.width, kioskData.canvas.height);' +
                        'var imageData = kioskData.canvas.toDataURL("image/jpeg", 0.8);' +
                        
                        'updateStatus("🔍", "Analyzing...");' +
                        
                        'var headers = { "Content-Type": "application/json" };' +
                        'var metaToken = document.querySelector("meta[name=csrf-token]");' +
                        'if (metaToken) {' +
                            'headers["X-Frappe-CSRF-Token"] = metaToken.getAttribute("content");' +
                        '}' +
                        
                        'fetch("/api/method/hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.recognize_face_from_camera", {' +
                            'method: "POST",' +
                            'headers: headers,' +
                            'body: JSON.stringify({' +
                                'captured_image: imageData,' +
                                'kiosk_name: "Standalone_Kiosk"' +
                            '})' +
                        '}).then(function(response) {' +
                            'return response.json();' +
                        '}).then(function(data) {' +
                            'var result = data.message || data;' +
                            'if (result.success) {' +
                                'showEmployee(result);' +
                                'updateStatus("✅", "Success");' +
                                'setTimeout(function() {' +
                                    'hideEmployee();' +
                                    'updateStatus("🔍", "Ready");' +
                                '}, 4000);' +
                            '} else {' +
                                'updateStatus("👤", "Try again");' +
                            '}' +
                        '}).catch(function() {' +
                            'updateStatus("❌", "Failed");' +
                        '}).finally(function() {' +
                            'kioskData.isProcessing = false;' +
                        '});' +
                    '} catch (error) {' +
                        'kioskData.isProcessing = false;' +
                    '}' +
                '}' +
                
                'function testRecognition() {' +
                    'if (!kioskData.stream) {' +
                        'updateStatus("⚠️", "Start camera first");' +
                        'return;' +
                    '}' +
                    'updateStatus("🧪", "Testing...");' +
                    'performRecognition();' +
                '}' +
                
                'function updateStatus(icon, message) {' +
                    'var status = document.getElementById("status-display");' +
                    'if (status) {' +
                        'status.innerHTML = ' +
                            '"<div style=\\"font-size: 2em; margin-bottom: 10px;\\">" + icon + "</div>" +' +
                            '"<div>" + message + "</div>";' +
                    '}' +
                '}' +
                
                'function showEmployee(result) {' +
                    'var empDisplay = document.getElementById("employee-display");' +
                    'if (empDisplay) empDisplay.classList.add("show");' +
                    
                    'var empName = document.getElementById("emp-name");' +
                    'var empId = document.getElementById("emp-id");' +
                    'var empTime = document.getElementById("emp-time");' +
                    
                    'if (empName) empName.textContent = result.employee.employee_name;' +
                    'if (empId) empId.textContent = result.employee.employee_id;' +
                    'if (empTime) empTime.textContent = new Date().toLocaleTimeString();' +
                '}' +
                
                'function hideEmployee() {' +
                    'var empDisplay = document.getElementById("employee-display");' +
                    'if (empDisplay) empDisplay.classList.remove("show");' +
                '}' +
                
                'function startClock() {' +
                    'function updateTime() {' +
                        'var now = new Date();' +
                        'var timeDisplay = document.getElementById("digital-time-display");' +
                        'var dateDisplay = document.getElementById("digital-date-display");' +
                        
                        'if (timeDisplay) {' +
                            'var h = now.getHours().toString().padStart(2, "0");' +
                            'var m = now.getMinutes().toString().padStart(2, "0");' +
                            'var s = now.getSeconds().toString().padStart(2, "0");' +
                            'timeDisplay.textContent = h + ":" + m + ":" + s;' +
                        '}' +
                        
                        'if (dateDisplay) {' +
                            'dateDisplay.textContent = now.toLocaleDateString();' +
                        '}' +
                    '}' +
                    'updateTime();' +
                    'kioskData.clockInterval = setInterval(updateTime, 1000);' +
                '}' +
                
                'function cleanup() {' +
                    'if (kioskData.stream) {' +
                        'kioskData.stream.getTracks().forEach(function(track) {' +
                            'track.stop();' +
                        '});' +
                    '}' +
                    'if (kioskData.interval) clearInterval(kioskData.interval);' +
                    'if (kioskData.clockInterval) clearInterval(kioskData.clockInterval);' +
                '}' +
                
                'document.addEventListener("DOMContentLoaded", initKiosk);' +
                'window.addEventListener("beforeunload", cleanup);' +
            '</script>' +
        '</body>' +
        '</html>';
}

function launchKioskInterface(frm) {
    var kioskWindow = window.open('', '_blank', 'fullscreen=yes,scrollbars=no,menubar=no,toolbar=no');
    
    if (kioskWindow) {
        var htmlContent = getAttendanceKioskHTML();
        
        // Add CSRF token to the HTML
        if (frappe.csrf_token) {
            htmlContent = htmlContent.replace(
                '<meta name="csrf-token" content="">',
                '<meta name="csrf-token" content="' + frappe.csrf_token + '">'
            );
        }
        
        kioskWindow.document.write(htmlContent);
        kioskWindow.document.close();
        
        frappe.show_alert({
            message: 'Kiosk interface launched in new window',
            indicator: 'green'
        });
    } else {
        frappe.show_alert({
            message: 'Could not open kiosk window. Please check popup settings.',
            indicator: 'red'
        });
    }
}

// Embedded Kiosk (Separate namespace to avoid conflicts)
function showEmbeddedKiosk(frm) {
    var embeddedKioskDialog = new frappe.ui.Dialog({
        title: __('Attendance Kiosk Interface'),
        fields: [
            {
                fieldname: 'kiosk_interface',
                fieldtype: 'HTML',
                options: getEmbeddedKioskHTML()
            }
        ],
        size: 'extra-large',
        primary_action_label: __('Close Kiosk'),
        primary_action: function() {
            if (window.cleanupEmbeddedKiosk) {
                window.cleanupEmbeddedKiosk();
            }
            embeddedKioskDialog.hide();
        },
        onhide: function() {
            if (window.cleanupEmbeddedKiosk) {
                window.cleanupEmbeddedKiosk();
            }
        }
    });
    
    embeddedKioskDialog.show();
    setTimeout(function() {
        initializeEmbeddedKiosk();
    }, 500);
}

function getEmbeddedKioskHTML() {
    return '<div style="padding: 0; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; min-height: 500px;">' +
        '<div style="text-align: center; padding: 20px; color: white;">' +
            '<h2>🏢 Employee Attendance Kiosk</h2>' +
            '<p>Position your face in front of the camera for automatic check-in/check-out</p>' +
        '</div>' +
        
        '<div style="display: flex; gap: 20px; padding: 0 20px 20px; color: white;">' +
            '<div style="flex: 2; background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px;">' +
                '<video id="embedded-video" width="100%" height="300" autoplay muted playsinline style="border-radius: 10px; background: #000;"></video>' +
                
                '<div id="embedded-status" style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 15px; text-align: center; margin: 15px 0;">' +
                    '<div style="font-size: 1.5em; margin-bottom: 5px;">📷</div>' +
                    '<div>Click "Start Camera" to begin</div>' +
                '</div>' +
                
                '<div id="embedded-employee" style="background: rgba(76, 175, 80, 0.2); border-radius: 8px; padding: 15px; text-align: center; display: none; margin-bottom: 15px;">' +
                    '<h4 id="embedded-emp-name">Employee Name</h4>' +
                    '<div><strong>ID:</strong> <span id="embedded-emp-id">-</span></div>' +
                    '<div><strong>Time:</strong> <span id="embedded-emp-time">-</span></div>' +
                '</div>' +
                
                '<div style="text-align: center;">' +
                    '<button id="embedded-start" class="btn btn-primary" style="margin-right: 10px;">Start Camera</button>' +
                    '<button id="embedded-stop" class="btn btn-secondary" style="display: none;">Stop Camera</button>' +
                    '<button id="embedded-test" class="btn btn-success" style="margin-left: 10px;">Test Recognition</button>' +
                '</div>' +
            '</div>' +
            
            '<div style="flex: 1; background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; text-align: center;">' +
                '<h4>🕒 Current Time</h4>' +
                '<div id="embedded-time" style="font-size: 2em; font-weight: bold;">--:--:--</div>' +
                '<div id="embedded-date">Loading...</div>' +
            '</div>' +
        '</div>' +
    '</div>';
}

function initializeEmbeddedKiosk() {
    var embeddedStream = null;
    var embeddedCanvas = null;
    var isEmbeddedProcessing = false;
    var embeddedInterval = null;
    var embeddedClockInterval = null;
    
    setTimeout(function() {
        setupEmbeddedElements();
    }, 100);
    
    function setupEmbeddedElements() {
        var video = document.getElementById('embedded-video');
        var startBtn = document.getElementById('embedded-start');
        var stopBtn = document.getElementById('embedded-stop');
        var testBtn = document.getElementById('embedded-test');
        
        if (!video || !startBtn || !stopBtn || !testBtn) {
            setTimeout(setupEmbeddedElements, 100);
            return;
        }
        
        embeddedCanvas = document.createElement('canvas');
        
        startBtn.addEventListener('click', startEmbeddedCamera);
        stopBtn.addEventListener('click', stopEmbeddedCamera);
        testBtn.addEventListener('click', testEmbeddedRecognition);
        
        startEmbeddedClock();
    }
    
    function startEmbeddedCamera() {
        updateEmbeddedStatus('📷', 'Starting camera...');
        
        navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        }).then(function(stream) {
            embeddedStream = stream;
            var video = document.getElementById('embedded-video');
            video.srcObject = stream;
            
            video.onloadedmetadata = function() {
                video.play();
                embeddedCanvas.width = video.videoWidth;
                embeddedCanvas.height = video.videoHeight;
                
                updateEmbeddedStatus('✅', 'Camera active - Position your face');
                document.getElementById('embedded-start').style.display = 'none';
                document.getElementById('embedded-stop').style.display = 'inline-block';
                
                startEmbeddedRecognition();
            };
        }).catch(function(error) {
            updateEmbeddedStatus('❌', 'Camera access denied');
        });
    }
    
    function stopEmbeddedCamera() {
        if (embeddedStream) {
            embeddedStream.getTracks().forEach(function(track) { track.stop(); });
            embeddedStream = null;
        }
        if (embeddedInterval) {
            clearInterval(embeddedInterval);
        }
        
        var video = document.getElementById('embedded-video');
        if (video) video.srcObject = null;
        
        updateEmbeddedStatus('📷', 'Camera stopped');
        document.getElementById('embedded-start').style.display = 'inline-block';
        document.getElementById('embedded-stop').style.display = 'none';
        hideEmbeddedEmployee();
    }
    
    function startEmbeddedRecognition() {
        embeddedInterval = setInterval(function() {
            if (!isEmbeddedProcessing && embeddedStream) {
                performEmbeddedRecognition();
            }
        }, 3000);
    }
    
    function performEmbeddedRecognition() {
        try {
            isEmbeddedProcessing = true;
            
            var video = document.getElementById('embedded-video');
            if (!video || !embeddedCanvas) return;
            
            var ctx = embeddedCanvas.getContext('2d');
            ctx.drawImage(video, 0, 0, embeddedCanvas.width, embeddedCanvas.height);
            var imageData = embeddedCanvas.toDataURL('image/jpeg', 0.8);
            
            updateEmbeddedStatus('🔍', 'Analyzing face...');
            
            frappe.call({
                method: 'hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.recognize_face_from_camera',
                args: {
                    captured_image: imageData,
                    kiosk_name: 'Embedded_Kiosk'
                },
                callback: function(response) {
                    var result = response.message;
                    if (result && result.success) {
                        showEmbeddedEmployee(result);
                        updateEmbeddedStatus('✅', 'Attendance marked successfully');
                        
                        setTimeout(function() {
                            hideEmbeddedEmployee();
                            updateEmbeddedStatus('🔍', 'Ready for next employee');
                        }, 4000);
                    } else {
                        updateEmbeddedStatus('👤', 'Position your face clearly');
                    }
                    isEmbeddedProcessing = false;
                },
                error: function(error) {
                    updateEmbeddedStatus('❌', 'Recognition failed');
                    isEmbeddedProcessing = false;
                }
            });
            
        } catch (error) {
            isEmbeddedProcessing = false;
        }
    }
    
    function testEmbeddedRecognition() {
        if (!embeddedStream) {
            frappe.show_alert({ message: 'Please start the camera first', indicator: 'orange' });
            return;
        }
        updateEmbeddedStatus('🧪', 'Testing recognition...');
        performEmbeddedRecognition();
    }
    
    function updateEmbeddedStatus(icon, message) {
        var status = document.getElementById('embedded-status');
        if (status) {
            status.innerHTML = '<div style="font-size: 1.5em; margin-bottom: 5px;">' + icon + '</div><div>' + message + '</div>';
        }
    }
    
    function showEmbeddedEmployee(result) {
        var empDisplay = document.getElementById('embedded-employee');
        var empName = document.getElementById('embedded-emp-name');
        var empId = document.getElementById('embedded-emp-id');
        var empTime = document.getElementById('embedded-emp-time');
        
        if (empDisplay) empDisplay.style.display = 'block';
        if (empName) empName.textContent = result.employee.employee_name;
        if (empId) empId.textContent = result.employee.employee_id;
        if (empTime) empTime.textContent = new Date().toLocaleTimeString();
    }
    
    function hideEmbeddedEmployee() {
        var empDisplay = document.getElementById('embedded-employee');
        if (empDisplay) empDisplay.style.display = 'none';
    }
    
    function startEmbeddedClock() {
        function updateTime() {
            var now = new Date();
            var timeDisplay = document.getElementById('embedded-time');
            var dateDisplay = document.getElementById('embedded-date');
            
            if (timeDisplay) {
                var timeStr = now.getHours().toString().padStart(2, '0') + ':' +
                             now.getMinutes().toString().padStart(2, '0') + ':' +
                             now.getSeconds().toString().padStart(2, '0');
                timeDisplay.textContent = timeStr;
            }
            
            if (dateDisplay) {
                var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                dateDisplay.textContent = now.toLocaleDateString('en-US', options);
            }
        }
        
        updateTime();
        embeddedClockInterval = setInterval(updateTime, 1000);
    }
    
    function cleanupEmbedded() {
        if (embeddedStream) {
            embeddedStream.getTracks().forEach(function(track) { track.stop(); });
        }
        if (embeddedInterval) clearInterval(embeddedInterval);
        if (embeddedClockInterval) clearInterval(embeddedClockInterval);
    }
    
    window.cleanupEmbeddedKiosk = cleanupEmbedded;
}

function testCameraAccess() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            stream.getTracks().forEach(function(track) { track.stop(); });
            frappe.show_alert({ message: 'Camera access successful!', indicator: 'green' });
        })
        .catch(function(error) {
            frappe.show_alert({ message: 'Camera access failed: ' + error.message, indicator: 'red' });
        });
}

function resetKioskInterface(frm) {
    if (window.cleanupStandaloneKiosk) {
        window.cleanupStandaloneKiosk();
    }
    if (window.cleanupEmbeddedKiosk) {
        window.cleanupEmbeddedKiosk();
    }
    
    frappe.show_alert({ 
        message: 'Kiosk interface reset successfully. Camera streams have been stopped.', 
        indicator: 'green' 
    });
}
