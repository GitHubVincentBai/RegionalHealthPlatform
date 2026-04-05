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

    def list_profiles(
        self,
        *,
        search: str | None = None,
        risk_level: str | None = None,
        check_in_status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ElderProfile], int]:
        profiles = self._repository.list_all()

        if search:
            normalized_search = search.strip().lower()
            profiles = [
                profile
                for profile in profiles
                if normalized_search in profile.elder_id.lower()
                or normalized_search in profile.elder_code.lower()
                or normalized_search in profile.full_name.lower()
            ]

        if risk_level:
            normalized_risk_level = risk_level.strip().lower()
            profiles = [
                profile
                for profile in profiles
                if profile.risk_level.lower() == normalized_risk_level
            ]

        if check_in_status:
            normalized_check_in_status = check_in_status.strip().lower()
            profiles = [
                profile
                for profile in profiles
                if profile.stay_info.check_in_status.lower() == normalized_check_in_status
            ]

        profiles.sort(key=lambda profile: profile.elder_id)

        total = len(profiles)
        start = (page - 1) * page_size
        end = start + page_size
        return profiles[start:end], total
