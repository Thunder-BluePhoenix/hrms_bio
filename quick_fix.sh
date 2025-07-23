#!/bin/bash

# Quick Fix Script for HRMS Biometric Migration Issues
# Run from your bench directory: bash quick_fix.sh

echo "🔧 Applying HRMS Biometric fixes..."

cd apps/hrms_biometric/

# Step 1: Create missing install __init__.py
echo "📁 Creating missing install module..."
cat > hrms_biometric/install/__init__.py << 'EOF'
# hrms_biometric/install/__init__.py
"""
Installation module for HRMS Biometric app
"""
__version__ = "0.0.1"
EOF

echo "✅ Created install/__init__.py"

# Step 2: Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install opencv-python>=4.8.0 --quiet
pip install face-recognition>=1.3.0 --quiet
pip install numpy>=1.24.0 --quiet
pip install Pillow>=10.0.0 --quiet

echo "✅ Python dependencies installed"

# Step 3: Backup existing files
echo "💾 Creating backups..."
cp hrms_biometric/hooks.py hrms_biometric/hooks.py.backup
cp hrms_biometric/install/setup.py hrms_biometric/install/setup.py.backup

echo "✅ Backups created"

# Step 4: Apply patches - you need to copy the corrected content manually
echo "📝 Files that need manual content replacement:"
echo "   - hrms_biometric/hooks.py (use corrected hooks.py content)"
echo "   - hrms_biometric/install/setup.py (use corrected install/setup.py content)"
echo "   - hrms_biometric/patches/v0_0/migrate_existing_attendance_data.py"
echo "   - hrms_biometric/patches/v0_0/cleanup_orphaned_records.py"
echo "   - hrms_biometric/patches/v0_0/optimize_database_indexes.py"

echo ""
echo "🎯 Next steps:"
echo "1. Copy the corrected file contents from Claude artifacts"
echo "2. Run: bench migrate"
echo "3. Run: bench restart"

echo ""
echo "✅ Quick fix preparation completed!"