from elder_service.application.repository import InMemoryElderProfileRepository
from elder_service.application.service import ElderService
from elder_service.domain.models import ElderProfile, FamilyContact, StayInfo


def create_default_service() -> ElderService:
    return ElderService(InMemoryElderProfileRepository())


def create_elder_profile(
    elder_id: str,
    full_name: str,
    age: int,
    station_id: str,
    risk_level: str = "medium",
    gender: str = "unknown",
    birth_date: str = "",
    phone: str = "",
    id_card: str = "",
    status: str = "active",
    elder_code: str | None = None,
    stay_info: StayInfo | None = None,
    family_contacts: list[FamilyContact] | None = None,
) -> ElderProfile:
    service = create_default_service()
    return service.create_profile(
        elder_id=elder_id,
        elder_code=elder_code,
        full_name=full_name,
        gender=gender,
        age=age,
        birth_date=birth_date,
        phone=phone,
        id_card=id_card,
        risk_level=risk_level,
        status=status,
        station_id=station_id,
        stay_info=stay_info,
        family_contacts=family_contacts,
    )
