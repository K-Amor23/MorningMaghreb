-- Down Migration: 001_initial_setup
-- Description: Rollback initial database setup

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
DROP FUNCTION IF EXISTS update_updated_at_column();

DROP TABLE IF EXISTS market_data;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS profiles;

DROP TYPE IF EXISTS notification_type;
DROP TYPE IF EXISTS subscription_status;
DROP TYPE IF EXISTS user_tier;
