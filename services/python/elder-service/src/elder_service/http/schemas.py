from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from elder_service.domain.models import ElderProfile, FamilyContact, StayInfo
from elder_service.http.examples import (
    ELDER_PROFILE_CREATE_EXAMPLE,
    ELDER_PROFILE_LIST_EXAMPLE,
    ELDER_PROFILE_RESPONSE_EXAMPLE,
)


class FamilyContactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": ELDER_PROFILE_CREATE_EXAMPLE},
    )

    elder_id: str = Field(min_length=1)
    elder_code: str | None = Field(default=None, min_length=1)
    full_name: str = Field(min_length=1)
    gender: str = Field(default="unknown", min_length=1)
    age: int = Field(ge=0)
    birth_date: str = ""
    phone: str = ""
    id_card: str = ""
    risk_level: str = Field(default="medium", min_length=1)
    status: str = Field(default="active", min_length=1)
    station_id: str = Field(min_length=1)
    stay_info: StayInfoRequest = Field(default_factory=StayInfoRequest)
    family_contacts: list[FamilyContactRequest] = Field(default_factory=list)


class ElderProfileResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": ELDER_PROFILE_RESPONSE_EXAMPLE})

    elder_id: str
    elder_code: str
    full_name: str
    gender: str
    age: int
    birth_date: str
    phone: str
    id_card: str
    risk_level: str
    status: str
    station_id: str
    stay_info: StayInfoResponse
    family_contacts: list[FamilyContactResponse]

    @classmethod
    def from_domain(cls, profile: ElderProfile) -> "ElderProfileResponse":
        return cls(
            elder_id=profile.elder_id,
            elder_code=profile.elder_code,
            full_name=profile.full_name,
            gender=profile.gender,
            age=profile.age,
            birth_date=profile.birth_date,
            phone=profile.phone,
            id_card=profile.id_card,
            risk_level=profile.risk_level,
            status=profile.status,
            station_id=profile.station_id,
            stay_info=StayInfoResponse.from_domain(profile.stay_info),
            family_contacts=[
                FamilyContactResponse.from_domain(contact)
                for contact in profile.family_contacts
            ],
        )


class ElderProfileListResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": ELDER_PROFILE_LIST_EXAMPLE})

    items: list[ElderProfileResponse]
    total: int
    page: int
    page_size: int
