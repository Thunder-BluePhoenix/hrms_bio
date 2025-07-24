### Hrms Biometric

Biometrics like face recognition etc

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app hrms_biometric
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/hrms_biometric
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
# hrms_bio
# HRMS Biometric

![Frappe](https://img.shields.io/badge/Frappe-v15-blue)
![ERPNext](https://img.shields.io/badge/ERPNext-Compatible-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive biometric face recognition attendance system for Frappe ERPNext HRMS v15. This application automates employee attendance tracking using advanced facial recognition technology, providing seamless integration with existing ERPNext HRMS workflows.

## 🌟 Features

### Core Biometric Features
- **🔍 Advanced Face Recognition**: Multi-image face recognition with configurable accuracy
- **📱 Attendance Kiosk**: Interactive web-based kiosk interface for employees
- **📊 Real-time Processing**: Instant face detection and attendance marking
- **📸 Photo Verification**: Automatic capture and storage of attendance photos
- **🔒 Duplicate Prevention**: Smart duplicate check-in prevention
- **🌍 Multi-timezone Support**: Handle attendance across different timezones

### Integration Features
- **🔗 Seamless ERPNext Integration**: Works with existing Employee and Attendance doctypes
- **👥 Employee Management**: Enhanced employee profiles with biometric settings
- **📈 Comprehensive Reporting**: Detailed attendance analytics and reports
- **🔐 Role-based Permissions**: Granular access control for different user types
- **⚙️ Configurable Settings**: Flexible configuration for recognition parameters

### Technical Features
- **🏗️ Scalable Architecture**: Support for multiple kiosk locations
- **🔄 Auto-cleanup**: Automated maintenance and data cleanup
- **📋 Health Monitoring**: System performance and accuracy monitoring
- **🛠️ Migration Support**: Database patches for smooth upgrades
- **🔧 Extensible Design**: Modular architecture for custom extensions

## 📋 Prerequisites

### System Requirements
- **Frappe Framework**: v15.x
- **ERPNext**: v15.x (optional but recommended)
- **Python**: 3.10 or higher
- **Database**: MariaDB 10.6+ or MySQL 8.0+
- **OS**: Linux (Ubuntu 20.04+), macOS 10.15+, or Windows with WSL2

### Hardware Requirements
- **Camera**: USB webcam or integrated camera for kiosk functionality
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 500MB for application + space for attendance photos
- **CPU**: Multi-core processor recommended for face recognition processing

## 🚀 Installation

### Quick Install

```bash
# Navigate to your bench directory
cd /path/to/your/bench

# Get the app
bench get-app https://github.com/yourusername/hrms_biometric.git --branch main

# Install the app
bench install-app hrms_biometric

# Run migrations
bench migrate

# Restart bench
bench restart
```

### Manual Installation

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake pkg-config \
    libopencv-dev libgl1-mesa-glx libglib2.0-0 libsm6 \
    libxext6 libxrender-dev python3-dev libjpeg-dev \
    libpng-dev libtiff-dev libwebp-dev
```

**macOS:**
```bash
brew install cmake pkg-config opencv boost dlib jpeg libpng libtiff webp
```

**CentOS/RHEL:**
```bash
sudo yum install -y gcc gcc-c++ cmake opencv-devel mesa-libGL \
    libSM libXext libXrender boost-devel python3-devel \
    libjpeg-devel libpng-devel
```

#### 2. Install Python Dependencies

```bash
cd apps/hrms_biometric
pip install -r requirements.txt
```

#### 3. Run Setup Script

```bash
chmod +x setup_hrms_biometric.sh
./setup_hrms_biometric.sh
```

#### 4. Complete Installation

```bash
bench install-app hrms_biometric
bench migrate
bench restart
```

## ⚙️ Configuration

### 1. Enable Biometric for Employees

1. Navigate to **Employee** list in ERPNext
2. Open an employee record
3. In the **Biometric Information** section:
   - Enable **"Enable Biometric Attendance"**
   - The system will create a linked **Employee Face Recognition** record
4. Upload 1-5 face images for better accuracy
5. Save the record

### 2. Setup Attendance Kiosk

1. Go to **Attendance Kiosk** list
2. Create a new kiosk:
   ```
   Kiosk Name: Main Entrance Kiosk
   Location: Building A - Ground Floor
   Timezone: Asia/Kolkata
   Is Active: ✓
   ```
3. Save and test camera access

### 3. Configure Recognition Settings

Access face recognition settings to customize:
- **Recognition Tolerance**: 0.4 (lower = stricter matching)
- **Confidence Threshold**: 70% (minimum confidence for recognition)
- **Photo Retention**: 30 days (how long to keep attendance photos)
- **Duplicate Prevention**: 30 minutes (minimum time between check-ins)

## 📱 Usage

### For Employees

1. **Approach the Kiosk**: Stand 2-3 feet from the camera
2. **Face Positioning**: Align your face within the guide circle
3. **Wait for Recognition**: The system will automatically:
   - Detect your face
   - Match against stored face data
   - Mark attendance
   - Display confirmation message
4. **Verification**: Check attendance in ERPNext if needed

### For HR Personnel

1. **Monitor Daily Attendance**:
   ```
   List > Human Resources > Employee Attendance
   ```

2. **Manage Employee Face Data**:
   ```
   List > Human Resources > Employee Face Recognition
   ```

3. **Generate Reports**:
   ```
   Reports > Human Resources > Attendance Reports
   ```

4. **View Attendance Photos**:
   - Each attendance record includes a verification photo
   - Access via the attendance record's attachment section

### For System Administrators

1. **Kiosk Management**:
   ```bash
   # Monitor kiosk status
   bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.get_kiosk_status
   
   # Test face recognition
   bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.test_recognition_system
   ```

2. **System Maintenance**:
   ```bash
   # Cleanup old attendance images
   bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.cleanup_old_attendance_images
   
   # Generate system health report
   bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.generate_system_health_report
   ```

## 🏗️ Architecture

### Directory Structure

```
hrms_biometric/
├── bio_facerecognition/          # Main module
│   ├── api/                      # API endpoints
│   │   ├── enhanced_face_recognition.py
│   │   └── face_recognition_settings.py
│   └── doctype/                  # Custom doctypes
│       ├── attendance_kiosk/
│       └── employee_face_recognition/
├── install/                      # Installation scripts
│   └── setup.py
├── patches/                      # Database migrations
│   └── v0_0/
├── public/                       # Static assets
│   ├── css/
│   ├── js/
│   └── icons/
├── templates/                    # HTML templates
├── www/                          # Web pages
│   └── biometric-kiosk/
├── hooks.py                      # Frappe hooks
├── requirements.txt              # Python dependencies
└── setup.py                     # Package setup
```

### Key Components

#### Face Recognition Engine
- **Location**: `bio_facerecognition/api/enhanced_face_recognition.py`
- **Purpose**: Core face recognition logic, encoding generation, and matching
- **Features**: Multi-image processing, confidence scoring, duplicate prevention

#### Attendance Kiosk Interface
- **Location**: `bio_facerecognition/doctype/attendance_kiosk/`
- **Purpose**: Web-based kiosk interface for employee interaction
- **Features**: Real-time camera feed, face guidance, attendance confirmation

#### Database Schema
- **Employee Face Recognition**: Stores face images and encodings
- **Attendance Kiosk**: Kiosk configuration and management
- **Enhanced Employee Attendance**: Extended with photo verification

## 🔧 API Reference

### Core Functions

#### Face Recognition
```python
# Process face encoding
process_face_encoding_on_save(doc, method)

# Mark attendance via face recognition
mark_attendance_via_face_recognition(employee_id, kiosk_id)

# Test recognition system
test_recognition_system()
```

#### Kiosk Management
```python
# Get kiosk status
get_kiosk_status(kiosk_id)

# Initialize kiosk
initialize_kiosk(kiosk_id)

# Process kiosk attendance
process_kiosk_attendance(image_data, kiosk_id)
```

#### System Maintenance
```python
# Cleanup old images
cleanup_old_attendance_images(days=30)

# Generate health report
generate_system_health_report()

# Optimize database
optimize_face_recognition_database()
```

### REST API Endpoints

```http
# Mark attendance via API
POST /api/method/hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.mark_attendance_via_face_recognition

# Get employee face data
GET /api/method/hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.get_employee_face_data

# Upload face image
POST /api/method/hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.upload_face_image
```

## 🐛 Troubleshooting

### Common Issues

#### Camera Access Issues
```bash
# Check camera permissions
ls -l /dev/video*

# Test camera access
bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.test_camera_access
```

#### Face Recognition Not Working
```bash
# Verify dependencies
python -c "import cv2, face_recognition; print('Dependencies OK')"

# Check face encodings
bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.verify_face_encodings
```

#### Performance Issues
```bash
# Optimize database
bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.optimize_database

# Check system resources
bench execute hrms_biometric.bio_facerecognition.api.enhanced_face_recognition.check_system_resources
```

### Error Messages

| Error | Solution |
|-------|----------|
| `OpenCV not found` | Install opencv-python: `pip install opencv-python` |
| `Face recognition library missing` | Install face-recognition: `pip install face-recognition` |
| `Camera not accessible` | Check camera permissions and connections |
| `Low confidence score` | Re-upload higher quality face images |
| `Database migration failed` | Run `bench migrate --skip-failing` |

## 🔒 Security & Privacy

### Data Protection
- **Face Data Encryption**: Face encodings are stored securely
- **Photo Retention Policy**: Configurable automatic deletion of attendance photos
- **Access Control**: Role-based permissions for sensitive operations
- **GDPR Compliance**: Built-in data protection and user data export features

### Best Practices
- Regular backup of face recognition data
- Use HTTPS for kiosk interfaces
- Implement proper camera access controls
- Regular security audits of attendance data

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/awesome-feature
   ```
3. **Make Changes**
4. **Run Tests**
   ```bash
   bench run-tests hrms_biometric
   ```
5. **Commit Changes**
   ```bash
   git commit -m "Add awesome feature"
   ```
6. **Push to Branch**
   ```bash
   git push origin feature/awesome-feature
   ```
7. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
bench run-tests hrms_biometric --coverage
```

### Code Style
- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Run `pre-commit` before committing
- Include unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Frappe Framework**: For providing the excellent foundation
- **OpenCV Community**: For computer vision capabilities
- **Face Recognition Library**: For facial recognition algorithms
- **ERPNext Community**: For HRMS integration possibilities

## 📞 Support

### Documentation
- [Frappe Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)
- [OpenCV Documentation](https://docs.opencv.org)

### Community Support
- [Frappe Community Forum](https://discuss.frappe.io)
- [GitHub Issues](https://github.com/yourusername/hrms_biometric/issues)
- [Discord Server](https://discord.gg/frappe)

### Commercial Support
For enterprise support, custom development, or implementation services, please contact:
- **Email**: bluephoenix00995@gmail.com
- **Developer**: BluePhoenix

---

**Made with ❤️ for the Frappe/ERPNext Community**

---

## 📊 Project Status

![GitHub last commit](https://img.shields.io/github/last-commit/Thunder-BluePhoenix/hrms_biometric)
![GitHub issues](https://img.shields.io/github/issues/Thunder-BluePhoenix/hrms_biometric)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Thunder-BluePhoenix/hrms_biometric)
![GitHub stars](https://img.shields.io/github/stars/Thunder-BluePhoenix/hrms_biometric)

**Current Version**: 0.0.1  
**Status**: Active Development  
**Compatibility**: Frappe v15, ERPNext v15  
**Last Updated**: 2025
