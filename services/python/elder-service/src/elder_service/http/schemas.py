from __future__ import annotations

from pydantic import BaseModel, Field

from elder_service.domain.models import ElderProfile, FamilyContact, StayInfo


class FamilyContactRequest(BaseModel):
    family_name: str = Field(min_length=1)
    relation_type: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    is_primary_contact: bool = False

    def to_domain(self) -> FamilyContact:
        return FamilyContact(
            family_name=self.family_name,
            relation_type=self.relation_type,
            phone=self.phone,
            is_primary_contact=self.is_primary_contact,
        )


class FamilyContactResponse(BaseModel):
    family_name: str
    relation_type: str
    phone: str
    is_primary_contact: bool

    @classmethod
    def from_domain(cls, contact: FamilyContact) -> "FamilyContactResponse":
        return cls(
            family_name=contact.family_name,
            relation_type=contact.relation_type,
            phone=contact.phone,
            is_primary_contact=contact.is_primary_contact,
        )


class StayInfoRequest(BaseModel):
    check_in_status: str = Field(default="pre_admission", min_length=1)
    room_id: str = ""
    bed_id: str = ""
    check_in_date: str = ""
    notes: str = ""

    def to_domain(self) -> StayInfo:
        return StayInfo(
            check_in_status=self.check_in_status,
            room_id=self.room_id,
            bed_id=self.bed_id,
            check_in_date=self.check_in_date,
            notes=self.notes,
        )


class StayInfoResponse(BaseModel):
    check_in_status: str
    room_id: str
    bed_id: str
    check_in_date: str
    notes: str

    @classmethod
    def from_domain(cls, stay_info: StayInfo) -> "StayInfoResponse":
        return cls(
            check_in_status=stay_info.check_in_status,
            room_id=stay_info.room_id,
            bed_id=stay_info.bed_id,
            check_in_date=stay_info.check_in_date,
            notes=stay_info.notes,
        )


class ElderProfileCreateRequest(BaseModel):
    elder_id: str = Field(min_length=1)
    elder_code: str | None = Field(default=None, min_length=1)
    full_name: str = Field(min_length=1)
    age: int = Field(ge=0)
    risk_level: str = Field(default="medium", min_length=1)
    stay_info: StayInfoRequest = Field(default_factory=StayInfoRequest)
    family_contacts: list[FamilyContactRequest] = Field(default_factory=list)


class ElderProfileResponse(BaseModel):
    elder_id: str
    elder_code: str
    full_name: str
    age: int
    risk_level: str
    is_high_risk: bool
    stay_info: StayInfoResponse
    family_contacts: list[FamilyContactResponse]
    current_stay_status: str

    @classmethod
    def from_domain(cls, profile: ElderProfile) -> "ElderProfileResponse":
        return cls(
            elder_id=profile.elder_id,
            elder_code=profile.elder_code,
            full_name=profile.full_name,
            age=profile.age,
            risk_level=profile.risk_level,
            is_high_risk=profile.is_high_risk(),
            stay_info=StayInfoResponse.from_domain(profile.stay_info),
            family_contacts=[
                FamilyContactResponse.from_domain(contact)
                for contact in profile.family_contacts
            ],
            current_stay_status=profile.stay_info.check_in_status,
        )


class ElderProfileListResponse(BaseModel):
    items: list[ElderProfileResponse]
    total: int
    page: int
    page_size: int
