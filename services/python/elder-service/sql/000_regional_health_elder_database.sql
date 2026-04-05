-- Create the regional_health_elder database if it does not already exist.
-- Run this file from a maintenance database such as postgres:
--   psql -h 127.0.0.1 -p 5432 -d postgres -f sql/000_regional_health_elder_database.sql

SELECT format(
    'CREATE DATABASE regional_health_elder WITH OWNER %I ENCODING ''UTF8'' TEMPLATE template0',
    current_user
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = 'regional_health_elder'
)
\gexec
