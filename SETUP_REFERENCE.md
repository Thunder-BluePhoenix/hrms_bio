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
