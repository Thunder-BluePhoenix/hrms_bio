#!/bin/bash

# Quick CMake and Dependencies Fix Script
# Run this from your frappe-bench directory

set -e

echo "🔧 Quick Fix for CMake and Dependencies Issues"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${YELLOW}⏳ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Clear all CMake cache and build files
print_status "Clearing CMake cache and build files..."
find . -name "CMakeCache.txt" -type f -delete 2>/dev/null || true
find . -name "CMakeFiles" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "build" -type d -path "*/pip-*" -exec rm -rf {} + 2>/dev/null || true
pip cache purge 2>/dev/null || true
print_success "CMake cache cleared"

# Step 2: Install system dependencies quickly
print_status "Installing critical system dependencies..."
if command -v apt-get >/dev/null 2>&1; then
    # Ubuntu/Debian
    sudo apt-get update -qq
    sudo apt-get install -y build-essential cmake pkg-config python3-dev \
        libopencv-dev libboost-all-dev libopenblas-dev libjpeg-dev libpng-dev
elif command -v yum >/dev/null 2>&1; then
    # CentOS/RHEL
    sudo yum install -y gcc gcc-c++ cmake3 python3-devel opencv-devel boost-devel
    sudo ln -sf /usr/bin/cmake3 /usr/bin/cmake 2>/dev/null || true
elif command -v brew >/dev/null 2>&1; then
    # macOS
    brew install cmake opencv boost dlib
fi
print_success "System dependencies installed"

# Step 3: Set environment variables
print_status "Setting environment variables..."
export CMAKE_BUILD_PARALLEL_LEVEL=4
export CMAKE_INSTALL_PREFIX="$PWD/env"
export DLIB_NO_GUI_SUPPORT=1
export CMAKE_CXX_STANDARD=14
print_success "Environment variables set"

# Step 4: Activate virtual environment and upgrade pip
print_status "Preparing Python environment..."
source env/bin/activate
pip install --upgrade pip setuptools wheel cmake
pip install --upgrade cython numpy
print_success "Python environment prepared"

# Step 5: Install problematic packages one by one
print_status "Installing dlib (this may take a few minutes)..."
pip install --no-cache-dir --verbose dlib==19.24.0
print_success "dlib installed"

print_status "Installing face-recognition..."
pip install --no-cache-dir face-recognition==1.3.0
print_success "face-recognition installed"

print_status "Installing OpenCV packages..."
pip install --no-cache-dir opencv-python==4.8.1.78
pip install --no-cache-dir opencv-contrib-python==4.8.1.78
print_success "OpenCV packages installed"

# Step 6: Install remaining dependencies
print_status "Installing remaining dependencies..."
pip install --no-cache-dir \
    numpy==1.24.3 \
    Pillow==10.0.1 \
    scikit-image==0.21.0 \
    imutils==0.5.4 \
    pandas==2.0.3
print_success "Remaining dependencies installed"

# Step 7: Create missing files in hrms_biometric
print_status "Creating missing app files..."
cd apps/hrms_biometric

# Create missing __init__.py files
mkdir -p hrms_biometric/install
mkdir -p hrms_biometric/patches/v0_0

echo '# Installation module' > hrms_biometric/install/__init__.py
echo '# Patches module' > hrms_biometric/patches/__init__.py
echo '# v0.0 patches' > hrms_biometric/patches/v0_0/__init__.py

# Create minimal patches.txt if missing
if [[ ! -f hrms_biometric/patches.txt ]]; then
    cat > hrms_biometric/patches.txt << 'EOF'
hrms_biometric.patches.v0_0.initial_setup
hrms_biometric.patches.v0_0.create_default_settings
hrms_biometric.patches.v0_0.setup_custom_fields
hrms_biometric.patches.v0_0.create_default_roles_and_permissions
hrms_biometric.patches.v0_0.migrate_existing_attendance_data
hrms_biometric.patches.v0_0.cleanup_orphaned_records
hrms_biometric.patches.v0_0.optimize_database_indexes
EOF
fi

# Fix file permissions
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;

cd ../..
print_success "App files created and permissions fixed"

# Step 8: Test imports
print_status "Testing critical imports..."
python3 -c "
try:
    import cv2
    import face_recognition
    import numpy
    import PIL
    import dlib
    print('✅ All critical packages imported successfully!')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

if [[ $? -eq 0 ]]; then
    print_success "Import test passed"
else
    print_error "Import test failed"
    exit 1
fi

echo ""
echo "🎉 Quick fix completed successfully!"
echo ""
echo "Next steps:"
echo "1. Run: bench migrate"
echo "2. Run: bench restart"
echo "3. If errors persist, run the comprehensive fix script"

exit 0