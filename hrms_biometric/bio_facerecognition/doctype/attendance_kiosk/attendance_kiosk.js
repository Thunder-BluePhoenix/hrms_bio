frappe.ui.form.on('Attendance Kiosk', {
    refresh: function(frm) {
        // Set the HTML content for the attendance interface
        if (frm.doc.is_active) {
            frm.set_value('attendance_interface', getAttendanceKioskHTML());
        }
        
        // Add custom buttons
        frm.add_custom_button(__('Test Camera'), function() {
            testCameraAccess();
        });
        
        frm.add_custom_button(__('View Today\'s Attendance'), function() {
            frappe.route_options = {
                "attendance_date": frappe.datetime.get_today()
            };
            frappe.set_route("List", "Employee Attendance");
        });
        
        frm.add_custom_button(__('Reset Kiosk'), function() {
            resetKioskInterface(frm);
        });
    },
    
    is_active: function(frm) {
        if (frm.doc.is_active) {
            frm.set_value('attendance_interface', getAttendanceKioskHTML());
        } else {
            frm.set_value('attendance_interface', '<div style="text-align: center; padding: 50px; color: #888;"><h3>Kiosk Disabled</h3><p>Enable the kiosk to start face recognition attendance.</p></div>');
        }
    }
});

function getAttendanceKioskHTML() {
    return `
    <div id="attendance-kiosk-container" style="min-height: 600px;">
        <style>
            #attendance-kiosk-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 20px;
                color: white;
                overflow: hidden;
            }
            
            .kiosk-header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .kiosk-header h2 {
                font-size: 2rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            .kiosk-main {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 20px;
                min-height: 500px;
            }
            
            .camera-section {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .info-section {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .camera-container {
                position: relative;
                border-radius: 15px;
                overflow: hidden;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            
            #kiosk-video {
                width: 400px;
                height: 300px;
                object-fit: cover;
                display: block;
            }
            
            .camera-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .face-guide {
                border: 3px dashed rgba(255, 255, 255, 0.7);
                border-radius: 50%;
                width: 200px;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 3rem;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 0.7; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.05); }
                100% { opacity: 0.7; transform: scale(1); }
            }
            
            .status-display {
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                min-height: 80px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            .status-icon {
                font-size: 2rem;
                margin-bottom: 5px;
            }
            
            .employee-display {
                background: rgba(0, 255, 136, 0.2);
                border: 2px solid #00ff88;
                border-radius: 10px;
                padding: 15px;
                display: none;
                animation: slideIn 0.5s ease;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .clock-widget {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            }
            
            .digital-time {
                font-size: 1.8rem;
                font-weight: 700;
                font-family: 'Courier New', monospace;
                margin-bottom: 5px;
            }
            
            .digital-date {
                font-size: 1rem;
                opacity: 0.8;
            }
            
            .analog-clock {
                width: 120px;
                height: 120px;
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                position: relative;
                margin: 15px auto;
                background: rgba(255, 255, 255, 0.1);
            }
            
            .clock-hand {
                position: absolute;
                background: white;
                transform-origin: bottom center;
                border-radius: 2px;
            }
            
            .hour-hand {
                width: 3px;
                height: 35px;
                top: 25px;
                left: 50%;
                margin-left: -1.5px;
            }
            
            .minute-hand {
                width: 2px;
                height: 45px;
                top: 15px;
                left: 50%;
                margin-left: -1px;
            }
            
            .second-hand {
                width: 1px;
                height: 50px;
                top: 10px;
                left: 50%;
                margin-left: -0.5px;
                background: #ff4757;
            }
            
            .clock-center {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 8px;
                height: 8px;
                background: white;
                border-radius: 50%;
                transform: translate(-50%, -50%);
                z-index: 10;
            }
            
            .stats-widget {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
            }
            
            .stats-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 10px;
                text-align: center;
            }
            
            .stat-row {
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .stat-row:last-child {
                border-bottom: none;
            }
            
            .stat-value {
                font-weight: 700;
                color: #00ff88;
            }
            
            .control-buttons {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }
            
            .kiosk-btn {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }
            
            .kiosk-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            
            .kiosk-btn.primary {
                background: #00ff88;
                color: #000;
                border-color: #00ff88;
            }
            
            .kiosk-btn.primary:hover {
                background: #00dd77;
            }
            
            @media (max-width: 768px) {
                .kiosk-main {
                    grid-template-columns: 1fr;
                }
                
                #kiosk-video {
                    width: 100%;
                    max-width: 350px;
                    height: 250px;
                }
            }
        </style>
        
        <div class="kiosk-header">
            <h2>🔐 Face Recognition Attendance Kiosk</h2>
            <p>Position your face in front of the camera for automatic attendance marking</p>
        </div>
        
        <div class="kiosk-main">
            <div class="camera-section">
                <div class="camera-container">
                    <video id="kiosk-video" autoplay muted playsinline></video>
                    <div class="camera-overlay">
                        <div id="face-guide" class="face-guide">👤</div>
                    </div>
                </div>
                
                <div id="status-display" class="status-display">
                    <div class="status-icon">📷</div>
                    <div class="status-text">Click "Start Camera" to begin</div>
                </div>
                
                <div id="employee-display" class="employee-display">
                    <h3 id="emp-name">Employee Name</h3>
                    <div style="margin-top: 10px;">
                        <div><strong>ID:</strong> <span id="emp-id">-</span></div>
                        <div><strong>Department:</strong> <span id="emp-dept">-</span></div>
                        <div><strong>Time:</strong> <span id="emp-time">-</span></div>
                        <div><strong>Status:</strong> <span id="emp-status">-</span></div>
                    </div>
                </div>
                
                <div class="control-buttons">
                    <button id="start-camera-btn" class="kiosk-btn primary">Start Camera</button>
                    <button id="stop-camera-btn" class="kiosk-btn" style="display: none;">Stop Camera</button>
                    <button id="test-recognition-btn" class="kiosk-btn">Test Recognition</button>
                </div>
            </div>
            
            <div class="info-section">
                <div class="clock-widget">
                    <div id="digital-time-display" class="digital-time">--:--:--</div>
                    <div id="digital-date-display" class="digital-date">Loading...</div>
                    
                    <div class="analog-clock">
                        <div id="hour-hand" class="clock-hand hour-hand"></div>
                        <div id="minute-hand" class="clock-hand minute-hand"></div>
                        <div id="second-hand" class="clock-hand second-hand"></div>
                        <div class="clock-center"></div>
                    </div>
                </div>
                
                <div class="stats-widget">
                    <div class="stats-title">📊 Attendance Stats</div>
                    <div class="stat-row">
                        <span>Today:</span>
                        <span id="today-count" class="stat-value">-</span>
                    </div>
                    <div class="stat-row">
                        <span>This Week:</span>
                        <span id="week-count" class="stat-value">-</span>
                    </div>
                    <div class="stat-row">
                        <span>This Month:</span>
                        <span id="month-count" class="stat-value">-</span>
                    </div>
                    <div class="stat-row">
                        <span>System Status:</span>
                        <span id="system-status" class="stat-value">🟢 Ready</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        (function() {
            let kioskStream = null;
            let kioskCanvas = null;
            let kioskCtx = null;
            let isKioskProcessing = false;
            let lastKioskRecognition = 0;
            let kioskInterval = null;
            let clockInterval = null;
            
            function initializeKioskInterface() {
                setupKioskEventListeners();
                startKioskClocks();
                loadKioskStats();
                
                // Create canvas for image capture
                kioskCanvas = document.createElement('canvas');
                kioskCtx = kioskCanvas.getContext('2d');
            }
            
            function setupKioskEventListeners() {
                const startBtn = document.getElementById('start-camera-btn');
                const stopBtn = document.getElementById('stop-camera-btn');
                const testBtn = document.getElementById('test-recognition-btn');
                
                if (startBtn) {
                    startBtn.addEventListener('click', startKioskCamera);
                }
                
                if (stopBtn) {
                    stopBtn.addEventListener('click', stopKioskCamera);
                }
                
                if (testBtn) {
                    testBtn.addEventListener('click', testKioskRecognition);
                }
            }
            
            async function startKioskCamera() {
                try {
                    updateKioskStatus('📷', 'Starting camera...');
                    
                    kioskStream = await navigator.mediaDevices.getUserMedia({
                        video: {
                            width: { ideal: 640 },
                            height: { ideal: 480 },
                            facingMode: 'user'
                        }
                    });
                    
                    const video = document.getElementById('kiosk-video');
                    if (video) {
                        video.srcObject = kioskStream;
                        
                        video.onloadedmetadata = () => {
                            video.play();
                            kioskCanvas.width = video.videoWidth;
                            kioskCanvas.height = video.videoHeight;
                            
                            updateKioskStatus('✅', 'Camera active - Position your face');
                            document.getElementById('start-camera-btn').style.display = 'none';
                            document.getElementById('stop-camera-btn').style.display = 'inline-block';
                            
                            // Start face recognition
                            startKioskFaceRecognition();
                        };
                    }
                    
                } catch (error) {
                    console.error('Kiosk camera error:', error);
                    updateKioskStatus('❌', 'Camera access denied');
                }
            }
            
            function stopKioskCamera() {
                if (kioskStream) {
                    kioskStream.getTracks().forEach(track => track.stop());
                    kioskStream = null;
                }
                
                if (kioskInterval) {
                    clearInterval(kioskInterval);
                    kioskInterval = null;
                }
                
                const video = document.getElementById('kiosk-video');
                if (video) {
                    video.srcObject = null;
                }
                
                updateKioskStatus('📷', 'Camera stopped');
                document.getElementById('start-camera-btn').style.display = 'inline-block';
                document.getElementById('stop-camera-btn').style.display = 'none';
                hideKioskEmployeeInfo();
            }
            
            function startKioskFaceRecognition() {
                kioskInterval = setInterval(() => {
                    if (!isKioskProcessing && kioskStream) {
                        performKioskFaceRecognition();
                    }
                }, 2000); // Check every 2 seconds
            }
            
            async function performKioskFaceRecognition() {
                const currentTime = Date.now();
                if (currentTime - lastKioskRecognition < 5000) {
                    return; // 5 second cooldown
                }
                
                try {
                    isKioskProcessing = true;
                    updateKioskStatus('🔍', 'Analyzing face...');
                    
                    const video = document.getElementById('kiosk-video');
                    if (!video || !video.videoWidth) return;
                    
                    // Capture frame
                    kioskCtx.drawImage(video, 0, 0, kioskCanvas.width, kioskCanvas.height);
                    const imageData = kioskCanvas.toDataURL('image/jpeg', 0.8);
                    
                    // Call recognition API
                    const response = await callKioskRecognitionAPI(imageData);
                    
                    if (response.success) {
                        handleKioskSuccessfulRecognition(response);
                        lastKioskRecognition = currentTime;
                    } else {
                        updateKioskStatus('👤', 'Position your face clearly');
                        hideKioskEmployeeInfo();
                    }
                    
                } catch (error) {
                    console.error('Kiosk recognition error:', error);
                    updateKioskStatus('⚠️', 'Recognition error');
                } finally {
                    isKioskProcessing = false;
                }
            }
            
            async function callKioskRecognitionAPI(imageData) {
                try {
                    const response = await fetch('/api/method/bio_facerecognition.bio_facerecognition.api.enhanced_face_recognition.recognize_face_from_camera', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Frappe-CSRF-Token': frappe.csrf_token
                        },
                        body: JSON.stringify({
                            captured_image: imageData,
                            kiosk_name: cur_frm.doc.kiosk_name || 'Kiosk'
                        })
                    });
                    
                    const data = await response.json();
                    return data.message || data;
                    
                } catch (error) {
                    console.error('Kiosk API error:', error);
                    throw error;
                }
            }
            
            function handleKioskSuccessfulRecognition(response) {
                const { employee, confidence, attendance, message } = response;
                
                updateKioskStatus('✅', message);
                showKioskEmployeeInfo(employee, attendance, confidence);
                loadKioskStats(); // Refresh stats
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    hideKioskEmployeeInfo();
                    updateKioskStatus('👤', 'Position your face for recognition');
                }, 5000);
            }
            
            function showKioskEmployeeInfo(employee, attendance, confidence) {
                const empDisplay = document.getElementById('employee-display');
                if (!empDisplay) return;
                
                document.getElementById('emp-name').textContent = employee.employee_name;
                document.getElementById('emp-id').textContent = employee.employee_id;
                document.getElementById('emp-dept').textContent = employee.department || 'N/A';
                document.getElementById('emp-time').textContent = attendance.time;
                document.getElementById('emp-status').textContent = attendance.type;
                
                empDisplay.style.display = 'block';
            }
            
            function hideKioskEmployeeInfo() {
                const empDisplay = document.getElementById('employee-display');
                if (empDisplay) {
                    empDisplay.style.display = 'none';
                }
            }
            
            function updateKioskStatus(icon, text) {
                const statusIcon = document.querySelector('#status-display .status-icon');
                const statusText = document.querySelector('#status-display .status-text');
                
                if (statusIcon) statusIcon.textContent = icon;
                if (statusText) statusText.textContent = text;
            }
            
            function startKioskClocks() {
                updateKioskClocks();
                clockInterval = setInterval(updateKioskClocks, 1000);
            }
            
            function updateKioskClocks() {
                const now = new Date();
                
                // Digital clock
                const timeString = now.toLocaleTimeString('en-IN', {
                    hour12: false,
                    timeZone: 'Asia/Kolkata'
                });
                const dateString = now.toLocaleDateString('en-IN', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    timeZone: 'Asia/Kolkata'
                });
                
                const timeDisplay = document.getElementById('digital-time-display');
                const dateDisplay = document.getElementById('digital-date-display');
                
                if (timeDisplay) timeDisplay.textContent = timeString;
                if (dateDisplay) dateDisplay.textContent = dateString;
                
                // Analog clock
                const hours = now.getHours() % 12;
                const minutes = now.getMinutes();
                const seconds = now.getSeconds();
                
                const hourAngle = (hours * 30) + (minutes * 0.5);
                const minuteAngle = minutes * 6;
                const secondAngle = seconds * 6;
                
                const hourHand = document.getElementById('hour-hand');
                const minuteHand = document.getElementById('minute-hand');
                const secondHand = document.getElementById('second-hand');
                
                if (hourHand) hourHand.style.transform = 'rotate(' + hourAngle + 'deg)';
                if (minuteHand) minuteHand.style.transform = 'rotate(' + minuteAngle + 'deg)';
                if (secondHand) secondHand.style.transform = 'rotate(' + secondAngle + 'deg)';
            }
            
            async function loadKioskStats() {
                try {
                    const response = await fetch('/api/method/bio_facerecognition.bio_facerecognition.api.enhanced_face_recognition.get_attendance_stats', {
                        method: 'GET',
                        headers: {
                            'X-Frappe-CSRF-Token': frappe.csrf_token
                        }
                    });
                    
                    const data = await response.json();
                    const stats = data.message || { today: 0, this_week: 0, this_month: 0 };
                    
                    const todayCount = document.getElementById('today-count');
                    const weekCount = document.getElementById('week-count');
                    const monthCount = document.getElementById('month-count');
                    const systemStatus = document.getElementById('system-status');
                    
                    if (todayCount) todayCount.textContent = stats.today;
                    if (weekCount) weekCount.textContent = stats.this_week;
                    if (monthCount) monthCount.textContent = stats.this_month;
                    if (systemStatus) systemStatus.textContent = '🟢 Online';
                    
                } catch (error) {
                    console.error('Error loading kiosk stats:', error);
                    const systemStatus = document.getElementById('system-status');
                    if (systemStatus) systemStatus.textContent = '🔴 Error';
                }
            }
            
            async function testKioskRecognition() {
                if (!kioskStream) {
                    frappe.show_alert({
                        message: 'Please start the camera first',
                        indicator: 'orange'
                    });
                    return;
                }
                
                try {
                    updateKioskStatus('🧪', 'Testing recognition...');
                    await performKioskFaceRecognition();
                } catch (error) {
                    frappe.show_alert({
                        message: 'Test failed: ' + error.message,
                        indicator: 'red'
                    });
                }
            }
            
            // Cleanup function
            function cleanupKioskInterface() {
                if (kioskStream) {
                    kioskStream.getTracks().forEach(track => track.stop());
                }
                if (kioskInterval) {
                    clearInterval(kioskInterval);
                }
                if (clockInterval) {
                    clearInterval(clockInterval);
                }
            }
            
            // Initialize when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initializeKioskInterface);
            } else {
                initializeKioskInterface();
            }
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', cleanupKioskInterface);
            
            // Expose cleanup function globally for form refresh
            window.cleanupKioskInterface = cleanupKioskInterface;
        })();
    </script>
    `;
}

function testCameraAccess() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            stream.getTracks().forEach(track => track.stop());
            frappe.show_alert({
                message: 'Camera access successful!',
                indicator: 'green'
            });
        })
        .catch(function(error) {
            frappe.show_alert({
                message: 'Camera access failed: ' + error.message,
                indicator: 'red'
            });
        });
}

function resetKioskInterface(frm) {
    if (window.cleanupKioskInterface) {
        window.cleanupKioskInterface();
    }
    
    setTimeout(() => {
        frm.set_value('attendance_interface', getAttendanceKioskHTML());
        frappe.show_alert({
            message: 'Kiosk interface reset successfully',
            indicator: 'green'
        });
    }, 500);
}