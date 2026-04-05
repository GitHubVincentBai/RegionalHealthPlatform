from dataclasses import dataclass, field
from datetime import date


VALID_CHECK_IN_STATUSES = {"pre_admission", "checked_in", "discharged"}


def _normalize_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_optional_iso_date(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""

    try:
        date.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc

    return normalized


@dataclass(slots=True)
class FamilyContact:
    family_name: str
    relation_type: str
    phone: str
    is_primary_contact: bool = False

    def __post_init__(self) -> None:
        self.family_name = _normalize_text(self.family_name, "family_name")
        self.relation_type = _normalize_text(self.relation_type, "relation_type")
        self.phone = _normalize_text(self.phone, "phone")

    def to_dict(self) -> dict[str, object]:
        return {
            "family_name": self.family_name,
            "relation_type": self.relation_type,
            "phone": self.phone,
            "is_primary_contact": self.is_primary_contact,
        }


@dataclass(slots=True)
class StayInfo:
    check_in_status: str = "pre_admission"
    room_id: str = ""
    bed_id: str = ""
    check_in_date: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        self.check_in_status = _normalize_text(self.check_in_status, "check_in_status")
        self.room_id = self.room_id.strip()
        self.bed_id = self.bed_id.strip()
        self.check_in_date = _normalize_optional_iso_date(
            self.check_in_date, "check_in_date"
        )
        self.notes = self.notes.strip()

        if self.check_in_status not in VALID_CHECK_IN_STATUSES:
            raise ValueError(
                f"check_in_status must be one of {', '.join(sorted(VALID_CHECK_IN_STATUSES))}"
            )

        if self.bed_id and not self.room_id:
            raise ValueError("room_id is required when bed_id is provided")

    def to_dict(self) -> dict[str, object]:
        return {
            "check_in_status": self.check_in_status,
            "room_id": self.room_id,
            "bed_id": self.bed_id,
            "check_in_date": self.check_in_date,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ElderProfile:
    elder_id: str
    elder_code: str
    full_name: str
    gender: str
    age: int
    risk_level: str
    birth_date: str = ""
    phone: str = ""
    id_card: str = ""
    status: str = "active"
    station_id: str = ""
    stay_info: StayInfo = field(default_factory=StayInfo)
    family_contacts: list[FamilyContact] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.elder_id = _normalize_text(self.elder_id, "elder_id")
        self.elder_code = _normalize_text(self.elder_code, "elder_code")
        self.full_name = _normalize_text(self.full_name, "full_name")
        self.gender = _normalize_text(self.gender, "gender")
        if self.age < 0:
            raise ValueError("age must be non-negative")
        self.birth_date = _normalize_optional_iso_date(self.birth_date, "birth_date")
        self.phone = self.phone.strip()
        self.id_card = self.id_card.strip()
        self.risk_level = _normalize_text(self.risk_level, "risk_level")
        self.status = _normalize_text(self.status, "status")
        self.station_id = _normalize_text(self.station_id, "station_id")
        if not isinstance(self.stay_info, StayInfo):
            raise TypeError("stay_info must be a StayInfo instance")
        self.family_contacts = [
            contact if isinstance(contact, FamilyContact) else FamilyContact(**contact)
            for contact in self.family_contacts
        ]

        primary_contacts = [
            contact for contact in self.family_contacts if contact.is_primary_contact
        ]
        if self.family_contacts and not primary_contacts:
            raise ValueError(
                "family_contacts must include one primary contact when contacts are provided"
            )
        if len(primary_contacts) > 1:
            raise ValueError("family_contacts can include only one primary contact")

    def is_high_risk(self) -> bool:
        return self.risk_level.lower() in {"high", "critical"}

    def to_dict(self) -> dict[str, object]:
        return {
            "elder_id": self.elder_id,
            "elder_code": self.elder_code,
            "full_name": self.full_name,
            "gender": self.gender,
            "age": self.age,
            "birth_date": self.birth_date,
            "phone": self.phone,
            "id_card": self.id_card,
            "risk_level": self.risk_level,
            "status": self.status,
            "station_id": self.station_id,
            "stay_info": self.stay_info.to_dict(),
            "family_contacts": [contact.to_dict() for contact in self.family_contacts],
        }
