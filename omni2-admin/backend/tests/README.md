# Test Scripts Directory

This directory contains reusable test scripts for the Omni2 Admin Dashboard.

## Available Test Scripts

### Database Inspection
- **check_tables.py** - List all tables in the database
- **check_mcp_servers.py** - Inspect mcp_servers table structure and data
- **check_audit_logs.py** - Inspect audit_logs table structure

### Metrics Testing
- **test_dashboard_metrics.py** - Test dashboard metrics API and explain counters
- **simulate_activity.py** - Create test audit log entries (WIP - has ARRAY type issues)

## Usage

All scripts can be run inside the Docker container:

```bash
docker exec omni2-admin-api python tests/<script_name>.py
```

## Development Guidelines

**HARD RULE**: Before creating any new test script, check this directory first to see if:
1. An existing script can be reused
2. An existing script can be modified/extended
3. The functionality already exists

This prevents duplication and keeps tests organized.

## Adding New Tests

When adding new test scripts:
1. Place them in this `tests/` directory
2. Update this README with a brief description
3. Follow the naming convention: `test_<feature>.py` or `check_<component>.py`
4. Include helpful output with emojis for readability
