import unittest
import sys
from datetime import date
from pathlib import Path
import tomllib

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from elder_service.application.repository import InMemoryElderProfileRepository
from elder_service.application.service import (
    ElderProfileAlreadyExistsError,
    ElderProfileNotFoundError,
    ElderService,
)
from elder_service.domain.models import FamilyContact, StayInfo
from elder_service.service import create_elder_profile

SERVICE_DIR = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = SERVICE_DIR / "pyproject.toml"


class ElderServiceTest(unittest.TestCase):
    def test_create_list_and_fetch_profile_smoke(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())

        created = service.create_profile(
            elder_id="E-100",
            elder_code="EC-100",
            full_name="赵六",
            gender="male",
            age=78,
            birth_date="1947-08-16",
            phone="13900000001",
            id_card="210102194708160011",
            risk_level="critical",
            status="active",
            station_id="station-heping-001",
            stay_info=StayInfo(
                check_in_status="checked_in",
                room_id="3B",
                bed_id="3B-08",
                check_in_date="2026-04-05",
                notes="corner bed",
            ),
            family_contacts=[
                FamilyContact(
                    family_name="赵家属",
                    relation_type="child",
                    phone="13900000000",
                    is_primary_contact=True,
                )
            ],
        )

        items, total = service.list_profiles()
        fetched = service.get_profile("E-100")

        self.assertEqual(created.elder_id, "E-100")
        self.assertEqual(total, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].elder_id, "E-100")
        self.assertEqual(items[0].station_id, "station-heping-001")
        self.assertEqual(items[0].stay_info.check_in_status, "checked_in")
        self.assertEqual(fetched.full_name, "赵六")
        self.assertEqual(fetched.gender, "male")
        self.assertEqual(fetched.birth_date, "1947-08-16")
        self.assertEqual(fetched.stay_info.room_id, "3B")
        self.assertEqual(fetched.family_contacts[0].family_name, "赵家属")

    def test_create_profile_defaults_to_medium_risk(self) -> None:
        profile = create_elder_profile(
            elder_id="E-001",
            full_name="张三",
            age=78,
            station_id="station-heping-001",
        )

        self.assertEqual(profile.elder_code, "E-001")
        self.assertEqual(profile.gender, "unknown")
        self.assertEqual(profile.risk_level, "medium")
        self.assertEqual(profile.status, "active")
        self.assertFalse(profile.is_high_risk())

    def test_create_profile_accepts_birth_date_without_age(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())

        created = service.create_profile(
            elder_id="E-001A",
            elder_code="EC-001A",
            full_name="生日建档",
            gender="female",
            birth_date="1940-01-01",
            station_id="station-heping-001",
            stay_info=StayInfo(
                check_in_status="checked_in",
                room_id="A-101",
                bed_id="A-101-02",
                check_in_date="2026-04-05",
            ),
            family_contacts=[
                FamilyContact(
                    family_name="王家属",
                    relation_type="daughter",
                    phone="13800000008",
                    is_primary_contact=True,
                )
            ],
        )

        today = date.today()
        expected_age = today.year - 1940 - ((today.month, today.day) < (1, 1))
        self.assertEqual(created.birth_date, "1940-01-01")
        self.assertEqual(created.age, expected_age)
        self.assertEqual(created.stay_info.room_id, "A-101")
        self.assertEqual(created.family_contacts[0].family_name, "王家属")

    def test_invalid_birth_date_format_is_rejected_even_when_age_is_present(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())

        with self.assertRaisesRegex(ValueError, "birth_date must use YYYY-MM-DD format"):
            service.create_profile(
                elder_id="E-001B",
                elder_code="EC-001B",
                full_name="生日格式错误",
                gender="female",
                age=80,
                birth_date="1940/01/01",
                station_id="station-heping-001",
            )

    def test_invalid_check_in_date_format_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "check_in_date must use YYYY-MM-DD format"):
            StayInfo(
                check_in_status="checked_in",
                room_id="A-101",
                bed_id="A-101-02",
                check_in_date="2026/04/05",
            )

    def test_checked_in_profile_allows_minimal_stay_info_fields(self) -> None:
        stay_info = StayInfo(check_in_status="checked_in")

        self.assertEqual(stay_info.check_in_status, "checked_in")
        self.assertEqual(stay_info.room_id, "")
        self.assertEqual(stay_info.bed_id, "")
        self.assertEqual(stay_info.check_in_date, "")

    def test_repository_round_trip(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())
        created = service.create_profile(
            elder_id="E-002",
            elder_code="EC-002",
            full_name="李四",
            gender="male",
            age=81,
            risk_level="high",
            status="active",
            station_id="station-heping-002",
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
        items, total = service.list_profiles()
        self.assertEqual(total, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(service.get_profile("E-002").elder_code, "EC-002")
        self.assertEqual(service.get_profile("E-002").stay_info.room_id, "2A")
        self.assertEqual(service.get_profile("E-002").station_id, "station-heping-002")
        self.assertEqual(service.get_profile("E-002").family_contacts[0].family_name, "李家属")

    def test_duplicate_profile_rejected(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())
        service.create_profile(
            elder_id="E-101",
            elder_code="EC-101",
            full_name="重复长者",
            gender="female",
            age=75,
            risk_level="medium",
            status="active",
            station_id="station-heping-001",
            stay_info=StayInfo(check_in_status="pre_admission"),
        )

        with self.assertRaises(ElderProfileAlreadyExistsError):
            service.create_profile(
                elder_id="E-101",
                elder_code="EC-101",
                full_name="重复长者",
                gender="female",
                age=75,
                risk_level="medium",
                status="active",
                station_id="station-heping-001",
                stay_info=StayInfo(check_in_status="pre_admission"),
            )

    def test_get_missing_profile_raises(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())

        with self.assertRaises(ElderProfileNotFoundError):
            service.get_profile("missing")

    def test_required_fields_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="",
                full_name="缺失编号",
                age=80,
                station_id="station-heping-001",
            )

        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="E-102",
                full_name="",
                age=80,
                station_id="station-heping-001",
            )

    def test_negative_age_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="E-003",
                full_name="王五",
                age=-1,
                station_id="station-heping-001",
            )

    def test_age_or_birth_date_is_required(self) -> None:
        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="E-003A",
                full_name="王五",
                station_id="station-heping-001",
            )

    def test_station_id_is_required(self) -> None:
        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="E-004",
                full_name="王六",
                age=81,
                station_id="",
            )

    def test_family_contacts_require_exactly_one_primary_contact(self) -> None:
        with self.assertRaises(ValueError):
            create_elder_profile(
                elder_id="E-004A",
                full_name="无主联系人",
                age=81,
                station_id="station-heping-001",
                family_contacts=[
                    FamilyContact(
                        family_name="张家属",
                        relation_type="child",
                        phone="13800000001",
                        is_primary_contact=False,
                    )
                ],
            )

    def test_stay_info_requires_room_when_bed_is_provided(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())
        created = service.create_profile(
            elder_id="E-020",
            elder_code="EC-020",
            full_name="入住缺房间",
            gender="female",
            age=78,
            station_id="station-heping-001",
            stay_info=StayInfo(check_in_status="checked_in"),
        )

        self.assertEqual(created.stay_info.check_in_status, "checked_in")
        self.assertEqual(created.stay_info.room_id, "")
        self.assertEqual(created.stay_info.bed_id, "")

        with self.assertRaisesRegex(ValueError, "room_id is required when bed_id is provided"):
            StayInfo(check_in_status="pre_admission", bed_id="A-101-02")

    def test_family_contacts_require_single_primary_contact(self) -> None:
        with self.assertRaisesRegex(ValueError, "must include one primary contact"):
            create_elder_profile(
                elder_id="E-021",
                full_name="无主联系人",
                age=80,
                station_id="station-heping-001",
                family_contacts=[
                    FamilyContact(
                        family_name="家属甲",
                        relation_type="daughter",
                        phone="13800000001",
                        is_primary_contact=False,
                    )
                ],
            )

        with self.assertRaisesRegex(ValueError, "only one primary contact"):
            create_elder_profile(
                elder_id="E-022",
                full_name="双主联系人",
                age=82,
                station_id="station-heping-001",
                family_contacts=[
                    FamilyContact(
                        family_name="家属甲",
                        relation_type="daughter",
                        phone="13800000001",
                        is_primary_contact=True,
                    ),
                    FamilyContact(
                        family_name="家属乙",
                        relation_type="son",
                        phone="13800000002",
                        is_primary_contact=True,
                    ),
                ],
            )

    def test_list_profiles_supports_filters_and_pagination(self) -> None:
        service = ElderService(InMemoryElderProfileRepository())
        service.create_profile(
            elder_id="E-010",
            elder_code="EC-010",
            full_name="张阿姨",
            gender="female",
            age=76,
            risk_level="medium",
            status="active",
            station_id="station-heping-001",
            stay_info=StayInfo(check_in_status="pre_admission"),
        )
        service.create_profile(
            elder_id="E-011",
            elder_code="EC-011",
            full_name="李爷爷",
            gender="male",
            age=84,
            risk_level="high",
            status="active",
            station_id="station-heping-001",
            stay_info=StayInfo(
                check_in_status="checked_in",
                room_id="A-201",
                bed_id="A-201-01",
                check_in_date="2026-04-05",
            ),
        )
        service.create_profile(
            elder_id="E-012",
            elder_code="EC-012",
            full_name="王奶奶",
            gender="female",
            age=88,
            risk_level="high",
            status="inactive",
            station_id="station-heping-002",
            stay_info=StayInfo(
                check_in_status="checked_in",
                room_id="B-301",
                bed_id="B-301-02",
                check_in_date="2026-04-06",
            ),
        )

        filtered_items, filtered_total = service.list_profiles(
            search="李",
            risk_level="high",
            check_in_status="checked_in",
        )
        self.assertEqual(filtered_total, 1)
        self.assertEqual(len(filtered_items), 1)
        self.assertEqual(filtered_items[0].elder_id, "E-011")

        paged_items, paged_total = service.list_profiles(
            risk_level="high",
            page=2,
            page_size=1,
        )
        self.assertEqual(paged_total, 2)
        self.assertEqual(len(paged_items), 1)
        self.assertEqual(paged_items[0].elder_id, "E-012")

    def test_pyproject_keeps_http_runtime_and_test_dependencies_in_sync(self) -> None:
        with PYPROJECT_PATH.open("rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)

        project = pyproject["project"]
        runtime_dependencies = set(project["dependencies"])
        test_dependencies = set(project["optional-dependencies"]["test"])
        expected_dependencies = {
            "fastapi>=0.115,<1",
            "httpx>=0.27,<1",
            "uvicorn>=0.30,<1",
        }

        self.assertEqual(project["requires-python"], ">=3.11")
        self.assertTrue(expected_dependencies.issubset(runtime_dependencies))
        self.assertEqual(test_dependencies, expected_dependencies)


if __name__ == "__main__":
    unittest.main()
