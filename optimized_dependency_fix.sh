#!/bin/bash

# Optimized Dependency Fix for HRMS Biometric
# This script preserves your existing project structure and just fixes the dependencies

set -e

echo "🔧 Optimized HRMS Biometric Dependency Fix"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${YELLOW}⏳ $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Step 1: Install system dependencies for CMake/dlib
print_status "Installing system dependencies for dlib compilation..."
if command -v apt-get >/dev/null 2>&1; then
    # Ubuntu/Debian
    sudo apt-get update -qq
    sudo apt-get install -y build-essential cmake pkg-config \
        libboost-all-dev libopenblas-dev liblapack-dev \
        libx11-dev libgtk-3-dev python3-dev libjpeg-dev \
        libpng-dev libtiff-dev libatlas-base-dev
elif command -v yum >/dev/null 2>&1; then
    # CentOS/RHEL
    sudo yum install -y gcc gcc-c++ cmake3 boost-devel \
        openblas-devel lapack-devel python3-devel \
        libjpeg-devel atlas-devel
    sudo ln -sf /usr/bin/cmake3 /usr/bin/cmake 2>/dev/null || true
elif command -v brew >/dev/null 2>&1; then
    # macOS
    brew install cmake boost openblas dlib
else
    print_error "Unsupported system. Please install cmake, boost, and development tools manually."
    exit 1
fi
print_success "System dependencies installed"

# Step 2: Setup Python environment
print_status "Setting up Python build environment..."
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install --upgrade cmake cython numpy

# Set environment variables for compilation
export CMAKE_BUILD_PARALLEL_LEVEL=4
export DLIB_NO_GUI_SUPPORT=1
print_success "Python environment ready"

# Step 3: Create missing __init__.py files (preserving your structure)
print_status "Creating missing __init__.py files..."
cd apps/hrms_biometric

mkdir -p hrms_biometric/patches/v0_0
mkdir -p hrms_biometric/install

# Create minimal __init__.py files
echo '# Patches module' > hrms_biometric/patches/__init__.py
echo '# v0.0 patches' > hrms_biometric/patches/v0_0/__init__.py
echo '# Install module' > hrms_biometric/install/__init__.py

print_success "Missing files created"

# Go back to bench directory
cd ../..

# Step 4: Install dlib separately (this is usually the problematic package)
print_status "Installing dlib separately with optimized settings..."
pip install --no-cache-dir dlib==19.24.0 --verbose

# Step 5: Install your project with [full] dependencies
print_status "Installing hrms_biometric with full dependencies..."
pip install -e apps/hrms_biometric[full]

# Step 6: Test critical imports
print_status "Testing imports..."
python3 -c "
try:
    import cv2
    import face_recognition
    import dlib
    import numpy
    print('✅ All critical packages imported successfully!')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

print_success "All dependencies installed successfully!"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Your project structure has been preserved."
echo "Next steps:"
echo "  1. bench migrate"
echo "  2. bench restart"
echo "  3. bench install-app hrms_biometric (if not already installed)"