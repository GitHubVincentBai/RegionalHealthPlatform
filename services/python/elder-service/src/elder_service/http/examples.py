STAY_INFO_REQUEST_EXAMPLE = {
    "check_in_status": "checked_in",
    "room_id": "3B",
    "bed_id": "3B-08",
    "check_in_date": "2026-04-05",
    "notes": "corner bed",
}

STAY_INFO_EXAMPLE = {
    "admission_id": "ADM-E-100",
    **STAY_INFO_REQUEST_EXAMPLE,
}

PRIMARY_FAMILY_CONTACT_EXAMPLE = {
    "family_name": "赵家属",
    "relation_type": "child",
    "phone": "13900000000",
    "is_primary_contact": True,
}

SECONDARY_FAMILY_CONTACT_EXAMPLE = {
    "family_name": "赵配偶",
    "relation_type": "spouse",
    "phone": "13800000009",
    "is_primary_contact": False,
}

ELDER_PROFILE_CREATE_EXAMPLE = {
    "elder_id": "E-100",
    "elder_code": "EC-100",
    "full_name": "赵六",
    "gender": "male",
    "age": 78,
    "birth_date": "1947-08-16",
    "phone": "13900000001",
    "id_card": "210102194708160011",
    "risk_level": "critical",
    "status": "active",
    "station_id": "station-heping-001",
    "stay_info": STAY_INFO_REQUEST_EXAMPLE,
    "family_contacts": [
        PRIMARY_FAMILY_CONTACT_EXAMPLE,
        SECONDARY_FAMILY_CONTACT_EXAMPLE,
    ],
}

ELDER_PROFILE_RESPONSE_EXAMPLE = {
    "elder_id": "E-100",
    "elder_code": "EC-100",
    "full_name": "赵六",
    "gender": "male",
    "age": 78,
    "birth_date": "1947-08-16",
    "phone": "13900000001",
    "id_card": "210102194708160011",
    "risk_level": "critical",
    "status": "active",
    "station_id": "station-heping-001",
    "stay_info": STAY_INFO_EXAMPLE,
    "family_contacts": [
        PRIMARY_FAMILY_CONTACT_EXAMPLE,
        SECONDARY_FAMILY_CONTACT_EXAMPLE,
    ],
}

ELDER_PROFILE_LIST_EXAMPLE = {
    "items": [ELDER_PROFILE_RESPONSE_EXAMPLE],
    "total": 1,
    "page": 1,
    "page_size": 20,
}

ELDER_PROFILE_CREATE_REQUEST_FIELDS = {
    "elder_id",
    "elder_code",
    "full_name",
    "gender",
    "age",
    "birth_date",
    "phone",
    "id_card",
    "risk_level",
    "status",
    "station_id",
    "stay_info",
    "family_contacts",
}

ELDER_PROFILE_RESPONSE_FIELDS = {
    "elder_id",
    "elder_code",
    "full_name",
    "gender",
    "age",
    "birth_date",
    "phone",
    "id_card",
    "risk_level",
    "status",
    "station_id",
    "stay_info",
    "family_contacts",
}

ELDER_PROFILE_LIST_RESPONSE_FIELDS = {
    "items",
    "total",
    "page",
    "page_size",
}

STAY_INFO_RESPONSE_FIELDS = {
    "admission_id",
    "check_in_status",
    "room_id",
    "bed_id",
    "check_in_date",
    "notes",
}

STAY_INFO_REQUEST_FIELDS = STAY_INFO_RESPONSE_FIELDS - {"admission_id"}

FAMILY_CONTACT_RESPONSE_FIELDS = {
    "family_name",
    "relation_type",
    "phone",
    "is_primary_contact",
}

FAMILY_CONTACT_REQUEST_FIELDS = set(FAMILY_CONTACT_RESPONSE_FIELDS)
