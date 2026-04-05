import unittest

from elder_service.application.repository import InMemoryElderProfileRepository
from elder_service.application.service import ElderService, ElderProfileNotFoundError
from elder_service.domain.models import FamilyContact, StayInfo
from elder_service.service import create_elder_profile


class ElderServiceTest(unittest.TestCase):
    def test_create_profile_defaults_to_medium_risk(self) -> None:
        profile = create_elder_profile(
            elder_id="E-001",
            full_name="张三",
            age=78,
        )

        self.assertEqual(profile.elder_code, "E-001")
        self.assertEqual(profile.risk_level, "medium")
        self.assertFalse(profile.is_high_risk())

    def test_repository_round_trip(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())
        created = service.create_profile(
            elder_id="E-002",
            elder_code="EC-002",
            full_name="李四",
            age=81,
            risk_level="high",
            stay_info=StayInfo(
                check_in_status="checked_in",
                room_id="2A",
                bed_id="2A-03",
                check_in_date="2026-04-05",
                notes="near elevator",
            ),
            family_contacts=[
                FamilyContact(
                    family_name="李家属",
                    relation_type="child",
                    phone="13800000000",
                    is_primary_contact=True,
                )
            ],
        )

        self.assertTrue(created.is_high_risk())
        self.assertEqual(service.get_profile("E-002").full_name, "李四")
        self.assertEqual(len(service.list_profiles()), 1)
        self.assertEqual(service.get_profile("E-002").elder_code, "EC-002")
        self.assertEqual(service.get_profile("E-002").stay_info.room_id, "2A")
        self.assertEqual(service.get_profile("E-002").family_contacts[0].family_name, "李家属")

    def test_get_missing_profile_raises(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())

        with self.assertRaises(ElderProfileNotFoundError):
            service.get_profile("missing")

    def test_negative_age_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="E-003",
                full_name="王五",
                age=-1,
            )


if __name__ == "__main__":
    unittest.main()
