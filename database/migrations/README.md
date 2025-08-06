# Database Migrations

This directory contains database migrations for the Casablanca Insights project.

## Structure

- `up/` - Migration files to apply
- `down/` - Rollback files for each migration
- `checks/` - Validation scripts

## Migrations

1. **001_initial_setup.sql** - Initial database setup with core tables
2. **002_schema_expansion.sql** - Additional tables for advanced features
3. **003_initial_data.sql** - Sample data for development
4. **004_performance_indexes.sql** - Performance optimization indexes

## Usage

### Apply all migrations
```bash
python run_migrations.py up
```

### Rollback specific migration
```bash
python run_migrations.py down 002_schema_expansion
```

### Validate migrations (CI)
```bash
./ci_hook.sh
```

## Development

When creating new migrations:
1. Create both up and down files
2. Test the rollback works correctly
3. Update this README with migration details
