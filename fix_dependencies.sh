#!/bin/bash

# Comprehensive Frappe HRMS Biometric Dependencies Fix Script
# Run this script from your frappe-bench directory

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

# Check if running from bench directory
check_bench_directory() {
    if [[ ! -f "sites/apps.txt" || ! -d "apps" ]]; then
        print_error "This script must be run from your frappe-bench directory!"
        print_info "Navigate to your bench directory first: cd /path/to/frappe-bench"
        exit 1
    fi
    print_success "Running from frappe-bench directory"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            OS="ubuntu"
            print_info "Detected Ubuntu/Debian system"
        elif command -v yum >/dev/null 2>&1; then
            OS="centos"
            print_info "Detected CentOS/RHEL system"
        elif command -v dnf >/dev/null 2>&1; then
            OS="fedora"
            print_info "Detected Fedora system"
        else
            OS="unknown"
            print_warning "Unknown Linux distribution"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Detected macOS system"
    else
        OS="unknown"
        print_warning "Unsupported operating system"
    fi
}

# Install system dependencies for Ubuntu/Debian
install_ubuntu_deps() {
    print_header "Installing Ubuntu/Debian System Dependencies"
    
    # Update package lists
    print_info "Updating package lists..."
    sudo apt-get update -qq
    
    # Install essential build tools
    print_info "Installing build essentials..."
    sudo apt-get install -y \
        build-essential \
        cmake \
        pkg-config \
        git \
        curl \
        wget
    
    # Install Python development packages
    print_info "Installing Python development packages..."
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-setuptools \
        python3-wheel
    
    # Install OpenCV and computer vision dependencies
    print_info "Installing OpenCV dependencies..."
    sudo apt-get install -y \
        libopencv-dev \
        python3-opencv \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1
    
    # Install image processing libraries
    print_info "Installing image processing libraries..."
    sudo apt-get install -y \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libwebp-dev \
        libopenjp2-7-dev
    
    # Install math and scientific computing libraries
    print_info "Installing scientific computing libraries..."
    sudo apt-get install -y \
        libboost-all-dev \
        libopenblas-dev \
        liblapack-dev \
        libatlas-base-dev \
        libeigen3-dev
    
    # Install GUI and system libraries
    print_info "Installing GUI libraries..."
    sudo apt-get install -y \
        libx11-dev \
        libgtk-3-dev \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev
    
    # Install additional development tools
    print_info "Installing additional development tools..."
    sudo apt-get install -y \
        libtool \
        autoconf \
        automake \
        make \
        gcc \
        g++ \
        gfortran
    
    print_success "Ubuntu/Debian dependencies installed successfully"
}

# Install system dependencies for CentOS/RHEL
install_centos_deps() {
    print_header "Installing CentOS/RHEL System Dependencies"
    
    # Enable EPEL repository
    print_info "Enabling EPEL repository..."
    sudo yum install -y epel-release
    
    # Install development tools
    print_info "Installing development tools..."
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y cmake3 pkg-config git curl wget
    
    # Create cmake symlink if needed
    if [[ ! -f /usr/bin/cmake && -f /usr/bin/cmake3 ]]; then
        sudo ln -sf /usr/bin/cmake3 /usr/bin/cmake
    fi
    
    # Install Python development packages
    print_info "Installing Python development packages..."
    sudo yum install -y \
        python3-devel \
        python3-pip \
        python3-setuptools \
        python3-wheel
    
    # Install OpenCV and dependencies
    print_info "Installing OpenCV dependencies..."
    sudo yum install -y \
        opencv-devel \
        mesa-libGL \
        libSM \
        libXext \
        libXrender
    
    # Install image processing libraries
    print_info "Installing image processing libraries..."
    sudo yum install -y \
        libjpeg-devel \
        libpng-devel \
        libtiff-devel \
        libwebp-devel
    
    # Install math libraries
    print_info "Installing math libraries..."
    sudo yum install -y \
        boost-devel \
        openblas-devel \
        lapack-devel \
        atlas-devel
    
    print_success "CentOS/RHEL dependencies installed successfully"
}

# Install system dependencies for macOS
install_macos_deps() {
    print_header "Installing macOS System Dependencies"
    
    # Check if Homebrew is installed
    if ! command -v brew >/dev/null 2>&1; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Update Homebrew
    print_info "Updating Homebrew..."
    brew update
    
    # Install dependencies
    print_info "Installing dependencies via Homebrew..."
    brew install \
        cmake \
        pkg-config \
        opencv \
        boost \
        dlib \
        jpeg \
        libpng \
        libtiff \
        webp \
        openblas \
        lapack
    
    print_success "macOS dependencies installed successfully"
}

# Clean and prepare Python environment
prepare_python_env() {
    print_header "Preparing Python Environment"
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source env/bin/activate
    
    # Upgrade pip and setuptools
    print_info "Upgrading pip, setuptools, and wheel..."
    pip install --upgrade pip setuptools wheel
    
    # Install build dependencies
    print_info "Installing Python build dependencies..."
    pip install --upgrade \
        cython \
        numpy \
        cmake \
        scikit-build \
        pybind11
    
    print_success "Python environment prepared"
}

# Fix CMake issues
fix_cmake_issues() {
    print_header "Fixing CMake Issues"
    
    # Clear CMake cache
    print_info "Clearing CMake cache..."
    find . -name "CMakeCache.txt" -type f -delete 2>/dev/null || true
    find . -name "CMakeFiles" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Set CMake environment variables
    print_info "Setting CMake environment variables..."
    export CMAKE_BUILD_PARALLEL_LEVEL=$(nproc 2>/dev/null || echo 4)
    export CMAKE_INSTALL_PREFIX="$PWD/env"
    
    # For macOS, set additional variables
    if [[ "$OS" == "macos" ]]; then
        export CMAKE_OSX_DEPLOYMENT_TARGET=10.15
        export MACOSX_DEPLOYMENT_TARGET=10.15
    fi
    
    print_success "CMake issues fixed"
}

# Install problematic packages individually
install_problematic_packages() {
    print_header "Installing Problematic Packages Individually"
    
    # Activate virtual environment
    source env/bin/activate
    
    # Install packages that commonly fail
    print_info "Installing dlib with specific settings..."
    pip install --no-cache-dir dlib==19.24.0 \
        --verbose \
        --global-option=build_ext \
        --global-option="-j$(nproc 2>/dev/null || echo 4)"
    
    print_info "Installing face-recognition..."
    pip install --no-cache-dir face-recognition>=1.3.0
    
    print_info "Installing OpenCV packages..."
    pip install --no-cache-dir opencv-python>=4.8.0
    pip install --no-cache-dir opencv-contrib-python>=4.8.0
    
    print_success "Problematic packages installed successfully"
}

# Install remaining Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    # Activate virtual environment
    source env/bin/activate
    
    # Install from requirements.txt if it exists
    if [[ -f "apps/hrms_biometric/requirements.txt" ]]; then
        print_info "Installing from requirements.txt..."
        pip install --no-cache-dir -r apps/hrms_biometric/requirements.txt
    else
        print_info "Installing core dependencies..."
        pip install --no-cache-dir \
            numpy>=1.24.0 \
            Pillow>=10.0.0 \
            scikit-image>=0.21.0 \
            imutils>=0.5.4 \
            pandas>=2.0.0 \
            scipy>=1.11.0
    fi
    
    print_success "Python dependencies installed successfully"
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    # Activate virtual environment
    source env/bin/activate
    
    # Test imports
    print_info "Testing critical imports..."
    
    python3 -c "
import sys
import importlib

packages = [
    'cv2',
    'face_recognition', 
    'numpy',
    'PIL',
    'dlib'
]

failed = []

for pkg in packages:
    try:
        importlib.import_module(pkg)
        print(f'✅ {pkg} - OK')
    except ImportError as e:
        print(f'❌ {pkg} - FAILED: {str(e)}')
        failed.append(pkg)

if failed:
    print(f'\n❌ Failed packages: {failed}')
    sys.exit(1)
else:
    print('\n✅ All critical packages imported successfully!')
"
    
    if [[ $? -eq 0 ]]; then
        print_success "Installation verification completed successfully"
    else
        print_error "Some packages failed to import"
        return 1
    fi
}

# Fix app-specific issues
fix_app_issues() {
    print_header "Fixing App-Specific Issues"
    
    # Navigate to app directory
    cd apps/hrms_biometric
    
    # Create missing directories
    print_info "Creating missing directories..."
    mkdir -p hrms_biometric/install
    mkdir -p hrms_biometric/patches/v0_0
    
    # Create missing __init__.py files
    print_info "Creating missing __init__.py files..."
    touch hrms_biometric/install/__init__.py
    touch hrms_biometric/patches/__init__.py
    touch hrms_biometric/patches/v0_0/__init__.py
    
    # Fix file permissions
    print_info "Fixing file permissions..."
    find . -type f -name "*.py" -exec chmod 644 {} \;
    find . -type d -exec chmod 755 {} \;
    
    # Return to bench directory
    cd ../..
    
    print_success "App-specific issues fixed"
}

# Main execution
main() {
    print_header "FRAPPE HRMS BIOMETRIC DEPENDENCIES FIX"
    
    # Check prerequisites
    check_bench_directory
    detect_os
    
    # Install system dependencies based on OS
    case $OS in
        "ubuntu")
            install_ubuntu_deps
            ;;
        "centos")
            install_centos_deps
            ;;
        "macos")
            install_macos_deps
            ;;
        *)
            print_error "Unsupported operating system. Please install dependencies manually."
            exit 1
            ;;
    esac
    
    # Fix app issues
    fix_app_issues
    
    # Prepare Python environment
    prepare_python_env
    
    # Fix CMake issues
    fix_cmake_issues
    
    # Install problematic packages individually
    install_problematic_packages
    
    # Install remaining dependencies
    install_python_deps
    
    # Verify installation
    verify_installation
    
    print_header "INSTALLATION COMPLETED SUCCESSFULLY"
    print_success "All dependencies have been installed and verified!"
    print_info "Next steps:"
    echo "  1. Run: bench migrate"
    echo "  2. Run: bench restart"
    echo "  3. Run: bench install-app hrms_biometric (if not already installed)"
}

# Run main function
main "$@"