-- Elder MVP schema
-- Source of truth for elder profile + family contact persistence.

CREATE TABLE IF NOT EXISTS elder_profiles (
    elder_id TEXT PRIMARY KEY,
    elder_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    age INTEGER NOT NULL,
    birth_date TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    id_card TEXT NOT NULL DEFAULT '',
    risk_level TEXT NOT NULL,
    status TEXT NOT NULL,
    station_id TEXT NOT NULL,
    admission_id TEXT NOT NULL DEFAULT '',
    check_in_status TEXT NOT NULL,
    room_id TEXT NOT NULL DEFAULT '',
    bed_id TEXT NOT NULL DEFAULT '',
    check_in_date TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    CONSTRAINT elder_profiles_check_in_status_chk
        CHECK (check_in_status IN ('pre_admission', 'checked_in', 'discharged')),
    CONSTRAINT elder_profiles_bed_requires_room_chk
        CHECK (bed_id = '' OR room_id <> '')
);

CREATE TABLE IF NOT EXISTS elder_family_contacts (
    id BIGSERIAL PRIMARY KEY,
    elder_id TEXT NOT NULL REFERENCES elder_profiles(elder_id) ON DELETE CASCADE,
    family_name TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    phone TEXT NOT NULL,
    is_primary_contact BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS elder_family_contacts_primary_contact_uidx
ON elder_family_contacts (elder_id)
WHERE is_primary_contact;

CREATE INDEX IF NOT EXISTS elder_profiles_station_status_idx
ON elder_profiles (station_id, status);

CREATE INDEX IF NOT EXISTS elder_profiles_risk_level_idx
ON elder_profiles (risk_level);

CREATE INDEX IF NOT EXISTS elder_profiles_check_in_status_idx
ON elder_profiles (check_in_status);

CREATE UNIQUE INDEX IF NOT EXISTS elder_profiles_checked_in_bed_uidx
ON elder_profiles (bed_id)
WHERE bed_id <> '' AND check_in_status = 'checked_in';
