from elder_service.application.repository import ElderProfileRepository
from elder_service.domain.models import ElderProfile, FamilyContact, StayInfo


class ElderProfileAlreadyExistsError(ValueError):
    pass


class ElderProfileNotFoundError(LookupError):
    pass


class ElderService:
    def __init__(self, repository: ElderProfileRepository) -> None:
        self._repository = repository

    def create_profile(
        self,
        *,
        elder_id: str,
        elder_code: str | None = None,
        full_name: str,
        age: int,
        risk_level: str = "medium",
        stay_info: StayInfo | None = None,
        family_contacts: list[FamilyContact] | None = None,
    ) -> ElderProfile:
        if self._repository.get(elder_id) is not None:
            raise ElderProfileAlreadyExistsError(f"elder profile {elder_id} already exists")

        profile = ElderProfile(
            elder_id=elder_id,
            elder_code=elder_code or elder_id,
            full_name=full_name,
            age=age,
            risk_level=risk_level,
            stay_info=stay_info or StayInfo(),
            family_contacts=family_contacts or [],
        )
        return self._repository.save(profile)

    def get_profile(self, elder_id: str) -> ElderProfile:
        profile = self._repository.get(elder_id)
        if profile is None:
            raise ElderProfileNotFoundError(f"elder profile {elder_id} not found")
        return profile

    def list_profiles(self) -> list[ElderProfile]:
        return self._repository.list_all()
