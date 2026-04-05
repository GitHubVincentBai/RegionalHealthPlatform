-- Elder MVP seed data sourced from the live regional_health_elder database.
-- These rows are intended for local联调 and UI verification.

BEGIN;

INSERT INTO elder_profiles (
    elder_id, elder_code, full_name, gender, age, birth_date, phone, id_card,
    risk_level, status, station_id, admission_id, check_in_status, room_id,
    bed_id, check_in_date, notes
) VALUES
    ('E-9002', 'EC-9002', '区域库联调长者', 'male', 84, '1941-04-18', '13600009999', '210102194104180031', 'medium', 'active', 'station-heping-002', 'ADM-E-9002', 'pre_admission', 'B-902', 'B-902-01', '2026-04-06', 'regional db flow'),
    ('E-9010', 'EC-9010', '脚本联调长者', 'male', 80, '1945-01-01', '13600007777', '210102194501010011', 'medium', 'active', 'station-heping-003', 'ADM-E-9010', 'pre_admission', 'C-901', 'C-901-01', '2026-04-06', 'script flow'),
    ('E-9021', 'EC-9021', '联调老人21', 'female', 79, '1947-04-05', '13600002121', '210102194704052121', 'medium', 'active', 'station-heping-121', 'ADM-E-9021', 'checked_in', 'D-921', 'D-921-01', '2026-04-05', 'manual probe'),
    ('E-9022', 'EC-9022', '联调老人22', 'male', 82, '1944-04-05', '13600002222', '210102194404052222', 'high', 'active', 'station-heping-122', 'ADM-E-9022', 'checked_in', 'D-922', 'D-922-01', '2026-04-05', 'seed via backend api'),
    ('E-9023', 'EC-9023', '联调老人23', 'female', 77, '1949-04-05', '13600002323', '210102194904052323', 'medium', 'active', 'station-heping-123', 'ADM-E-9023', 'pre_admission', 'D-923', 'D-923-01', '2026-04-07', 'seed via backend api'),
    ('E-9024', 'EC-9024', '联调老人24', 'male', 81, '1945-04-05', '13600002424', '210102194504052424', 'high', 'active', 'station-heping-124', 'ADM-E-9024', 'checked_in', 'D-924', 'D-924-01', '2026-04-05', 'seed via backend api'),
    ('E-9025', 'EC-9025', '联调老人25', 'female', 76, '1950-04-05', '13600002525', '210102195004052525', 'medium', 'active', 'station-heping-125', 'ADM-E-9025', 'checked_in', 'D-925', 'D-925-01', '2026-04-05', 'seed via backend api'),
    ('E-9026', 'EC-9026', '联调老人26', 'male', 83, '1943-04-05', '13600002626', '210102194304052626', 'medium', 'active', 'station-heping-126', 'ADM-E-9026', 'pre_admission', 'D-926', 'D-926-01', '2026-04-08', 'seed via backend api'),
    ('E-9027', 'EC-9027', '联调老人27', 'female', 74, '1952-04-05', '13600002727', '210102195204052727', 'low', 'active', 'station-heping-127', 'ADM-E-9027', 'checked_in', 'D-927', 'D-927-01', '2026-04-05', 'seed via backend api'),
    ('E-9028', 'EC-9028', '联调老人28', 'male', 88, '1938-04-05', '13600002828', '210102193804052828', 'high', 'active', 'station-heping-128', 'ADM-E-9028', 'checked_in', 'D-928', 'D-928-01', '2026-04-05', 'seed via backend api'),
    ('E-9029', 'EC-9029', '联调老人29', 'female', 75, '1951-04-05', '13600002929', '210102195104052929', 'medium', 'active', 'station-heping-129', 'ADM-E-9029', 'pre_admission', 'D-929', 'D-929-01', '2026-04-09', 'seed via backend api'),
    ('E-9030', 'EC-9030', '联调老人30', 'male', 84, '1942-04-05', '13600003030', '210102194204053030', 'medium', 'active', 'station-heping-130', 'ADM-E-9030', 'checked_in', 'D-930', 'D-930-01', '2026-04-05', 'seed via backend api'),
    ('E-9031', 'EC-9031', '前端新录入老人31', 'female', 78, '1948-04-05', '13600003131', '210102194804053131', 'high', 'active', 'station-heping-131', 'ADM-E-9031', 'checked_in', 'D-931', 'D-931-01', '2026-04-05', 'created via frontend proxy')
ON CONFLICT (elder_id) DO UPDATE SET
    elder_code = EXCLUDED.elder_code,
    full_name = EXCLUDED.full_name,
    gender = EXCLUDED.gender,
    age = EXCLUDED.age,
    birth_date = EXCLUDED.birth_date,
    phone = EXCLUDED.phone,
    id_card = EXCLUDED.id_card,
    risk_level = EXCLUDED.risk_level,
    status = EXCLUDED.status,
    station_id = EXCLUDED.station_id,
    admission_id = EXCLUDED.admission_id,
    check_in_status = EXCLUDED.check_in_status,
    room_id = EXCLUDED.room_id,
    bed_id = EXCLUDED.bed_id,
    check_in_date = EXCLUDED.check_in_date,
    notes = EXCLUDED.notes;

DELETE FROM elder_family_contacts
WHERE elder_id IN (
    'E-9002', 'E-9010', 'E-9021', 'E-9022', 'E-9023', 'E-9024', 'E-9025',
    'E-9026', 'E-9027', 'E-9028', 'E-9029', 'E-9030', 'E-9031'
);

INSERT INTO elder_family_contacts (
    elder_id, family_name, relation_type, phone, is_primary_contact
) VALUES
    ('E-9002', '区域库家属', 'son', '13800009999', TRUE),
    ('E-9010', '脚本家属', 'son', '13800007777', TRUE),
    ('E-9021', '家属21', 'child', '13800002121', TRUE),
    ('E-9022', '家属22', 'child', '13800002222', TRUE),
    ('E-9023', '家属23', 'daughter', '13800002323', TRUE),
    ('E-9024', '家属24', 'son', '13800002424', TRUE),
    ('E-9025', '家属25', 'spouse', '13800002525', TRUE),
    ('E-9026', '家属26', 'child', '13800002626', TRUE),
    ('E-9027', '家属27', 'daughter', '13800002727', TRUE),
    ('E-9028', '家属28', 'son', '13800002828', TRUE),
    ('E-9029', '家属29', 'spouse', '13800002929', TRUE),
    ('E-9030', '家属30', 'child', '13800003030', TRUE),
    ('E-9031', '家属31', 'daughter', '13800003131', TRUE);

COMMIT;
