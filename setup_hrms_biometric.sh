#!/bin/bash

# HRMS Biometric App - Complete Setup Script
# Save this file as: setup_hrms_biometric.sh
# Run from your bench directory with: bash setup_hrms_biometric.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🚀 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️ $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "apps" ]; then
    print_error "Please run this script from your bench directory (where 'apps' folder exists)"
    exit 1
fi

# Check if hrms_biometric app exists
if [ ! -d "apps/hrms_biometric" ]; then
    print_error "hrms_biometric app directory not found in apps/"
    print_info "Please ensure the app is cloned first: bench get-app [repository-url]"
    exit 1
fi

print_status "Setting up HRMS Biometric App file structure..."

# Navigate to app directory
cd apps/hrms_biometric/

# Create root level files
print_status "Creating root level files..."
touch setup.py
touch MANIFEST.in
print_success "Root files created"

# Create patches directory structure
print_status "Creating patches directory structure..."
mkdir -p hrms_biometric/patches/v0_0
print_success "Patches directory structure created"

# Create __init__.py files for patches
print_status "Creating __init__.py files for patches..."
touch hrms_biometric/patches/__init__.py
touch hrms_biometric/patches/v0_0/__init__.py
print_success "Patch __init__.py files created"

# Create patch files
print_status "Creating patch files..."
touch hrms_biometric/patches/v0_0/initial_setup.py
touch hrms_biometric/patches/v0_0/create_default_settings.py
touch hrms_biometric/patches/v0_0/setup_custom_fields.py
touch hrms_biometric/patches/v0_0/create_default_roles_and_permissions.py
touch hrms_biometric/patches/v0_0/migrate_existing_attendance_data.py
touch hrms_biometric/patches/v0_0/cleanup_orphaned_records.py
touch hrms_biometric/patches/v0_0/optimize_database_indexes.py
print_success "Patch files created"

# Create permissions.py file
print_status "Creating permissions.py..."
touch hrms_biometric/permissions.py
print_success "Permissions file created"

# Create optional directories for future use
print_status "Creating optional directories for future features..."
mkdir -p hrms_biometric/public/css
mkdir -p hrms_biometric/public/js
mkdir -p hrms_biometric/public/icons
mkdir -p hrms_biometric/templates/pages
mkdir -p hrms_biometric/templates/emails
mkdir -p hrms_biometric/www/biometric-kiosk
mkdir -p hrms_biometric/fixtures
mkdir -p hrms_biometric/translations
mkdir -p hrms_biometric/tests
print_success "Optional directories created"

# Create placeholder files for optional directories
print_status "Creating placeholder files..."
touch hrms_biometric/public/css/.gitkeep
touch hrms_biometric/public/js/.gitkeep
touch hrms_biometric/public/icons/.gitkeep
touch hrms_biometric/templates/pages/.gitkeep
touch hrms_biometric/templates/emails/.gitkeep
touch hrms_biometric/www/biometric-kiosk/.gitkeep
touch hrms_biometric/fixtures/.gitkeep
touch hrms_biometric/translations/.gitkeep
touch hrms_biometric/tests/__init__.py
print_success "Placeholder files created"

# Set proper permissions
print_status "Setting file permissions..."
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
print_success "File permissions set"

# Create a quick reference file
print_status "Creating quick reference file..."
cat > SETUP_REFERENCE.md << 'EOF'
# HRMS Biometric Setup Reference

## Files Created by Setup Script

### Root Level Files:
- setup.py (NEW)
- MANIFEST.in (NEW)

### App Module Files:
- hrms_biometric/permissions.py (NEW)

### Patch Files (7 migration patches):
- hrms_biometric/patches/__init__.py (NEW)
- hrms_biometric/patches/v0_0/__init__.py (NEW)
- hrms_biometric/patches/v0_0/initial_setup.py (NEW) - Database setup and indexes
- hrms_biometric/patches/v0_0/create_default_settings.py (NEW) - Default configuration
- hrms_biometric/patches/v0_0/setup_custom_fields.py (NEW) - Employee custom fields
- hrms_biometric/patches/v0_0/create_default_roles_and_permissions.py (NEW) - Security setup
- hrms_biometric/patches/v0_0/migrate_existing_attendance_data.py (NEW) - Data migration
- hrms_biometric/patches/v0_0/cleanup_orphaned_records.py (NEW) - Data cleanup
- hrms_biometric/patches/v0_0/optimize_database_indexes.py (NEW) - Performance optimization

## Files to Update:
- pyproject.toml (UPDATE)
- hrms_biometric/hooks.py (UPDATE)
- hrms_biometric/patches.txt (UPDATE)
- hrms_biometric/install/setup.py (UPDATE)

## Next Steps:
1. Copy content from Claude artifacts into each file
2. Update existing files with corrected versions
3. Run: bench migrate
4. Run: bench restart

## Installation Commands:
```bash
bench install-app hrms_biometric
bench migrate
bench restart
```
EOF
print_success "Setup reference file created"

# Verify structure
print_status "Verifying file structure..."
echo ""
print_info "📋 Patch files created:"
find . -name "*.py" -path "./hrms_biometric/patches/*" -type f | sort

echo ""
print_info "📋 Root files:"
if ls setup.py MANIFEST.in >/dev/null 2>&1; then
    ls -la setup.py MANIFEST.in
else
    print_warning "Some root files missing"
fi

echo ""
print_info "📋 Permissions file:"
if ls hrms_biometric/permissions.py >/dev/null 2>&1; then
    ls -la hrms_biometric/permissions.py
else
    print_warning "Permissions file missing"
fi

echo ""
print_info "📋 Directory structure:"
tree hrms_biometric/ -I '__pycache__|*.pyc' || find hrms_biometric/ -type d | head -10

echo ""
print_success "🎉 File structure setup completed successfully!"

echo ""
print_info "📝 Next steps:"
echo "1. Copy the content from Claude artifacts into each file"
echo "2. Update existing files (hooks.py, pyproject.toml, patches.txt, install/setup.py)"
echo "3. Run: bench migrate"
echo "4. Run: bench restart"

echo ""
print_info "🔧 Installation commands:"
echo "   bench install-app hrms_biometric"
echo "   bench migrate"
echo "   bench restart"

echo ""
print_info "📖 Check SETUP_REFERENCE.md for detailed file list and instructions"

print_success "Setup script completed! 🚀"