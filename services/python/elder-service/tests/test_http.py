import unittest
import sys
from pathlib import Path
from datetime import date

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from fastapi.testclient import TestClient

    from elder_service.http.examples import (
        ELDER_PROFILE_CREATE_REQUEST_FIELDS,
        ELDER_PROFILE_RESPONSE_FIELDS,
        ELDER_PROFILE_CREATE_EXAMPLE,
        ELDER_PROFILE_LIST_EXAMPLE,
        ELDER_PROFILE_LIST_RESPONSE_FIELDS,
        ELDER_PROFILE_RESPONSE_EXAMPLE,
        FAMILY_CONTACT_REQUEST_FIELDS,
        FAMILY_CONTACT_RESPONSE_FIELDS,
        PRIMARY_FAMILY_CONTACT_EXAMPLE,
        STAY_INFO_REQUEST_FIELDS,
        STAY_INFO_RESPONSE_FIELDS,
        STAY_INFO_EXAMPLE,
    )
    from elder_service.http.server import create_app
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "elder-service HTTP tests require FastAPI runtime dependencies. "
        "Install the service with `python3 -m pip install -e \".[test]\"` "
        "or use `bash scripts/run_python_elder_checks.sh test`."
    ) from exc


class ElderHttpApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_create_list_and_fetch_profile(self) -> None:
        create_response = self.client.post(
            "/elders",
            json=ELDER_PROFILE_CREATE_EXAMPLE,
        )

        self.assertEqual(create_response.status_code, 201)
        body = create_response.json()
        self.assertEqual(body, ELDER_PROFILE_RESPONSE_EXAMPLE)
        self.assertEqual(set(body), ELDER_PROFILE_RESPONSE_FIELDS)
        self.assertEqual(set(body["stay_info"]), STAY_INFO_RESPONSE_FIELDS)
        self.assertEqual(set(body["family_contacts"][0]), FAMILY_CONTACT_RESPONSE_FIELDS)

        list_response = self.client.get("/elders")
        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        self.assertEqual(list_body, ELDER_PROFILE_LIST_EXAMPLE)
        self.assertEqual(set(list_body), ELDER_PROFILE_LIST_RESPONSE_FIELDS)
        self.assertEqual(set(list_body["items"][0]), ELDER_PROFILE_RESPONSE_FIELDS)
        self.assertEqual(
            set(list_body["items"][0]["family_contacts"][1]),
            FAMILY_CONTACT_RESPONSE_FIELDS,
        )

        fetch_response = self.client.get("/elders/E-100")
        self.assertEqual(fetch_response.status_code, 200)
        fetch_body = fetch_response.json()
        self.assertEqual(fetch_body, ELDER_PROFILE_RESPONSE_EXAMPLE)
        self.assertEqual(set(fetch_body), ELDER_PROFILE_RESPONSE_FIELDS)
        self.assertEqual(set(fetch_body["stay_info"]), STAY_INFO_RESPONSE_FIELDS)

    def test_duplicate_profile_returns_409(self) -> None:
        payload = {
            "elder_id": "E-101",
            "elder_code": "EC-101",
            "full_name": "重复长者",
            "gender": "female",
            "age": 75,
            "risk_level": "medium",
            "status": "active",
            "station_id": "station-heping-001",
            "stay_info": {"check_in_status": "pre_admission"},
            "family_contacts": [],
        }

        first_response = self.client.post("/elders", json=payload)
        duplicate_response = self.client.post("/elders", json=payload)

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(duplicate_response.status_code, 409)
        self.assertIn("already exists", duplicate_response.json()["detail"])

    def test_missing_required_fields_return_422(self) -> None:
        missing_elder_id_response = self.client.post(
            "/elders",
            json={
                "elder_id": "",
                "elder_code": "EC-102",
                "full_name": "缺失编号",
                "gender": "female",
                "age": 80,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "pre_admission"},
                "family_contacts": [],
            },
        )
        missing_full_name_response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-102",
                "elder_code": "EC-102",
                "full_name": "",
                "gender": "female",
                "age": 80,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "pre_admission"},
                "family_contacts": [],
            },
        )

        self.assertEqual(missing_elder_id_response.status_code, 422)
        self.assertEqual(missing_full_name_response.status_code, 422)

    def test_create_profile_accepts_birth_date_without_age(self) -> None:
        payload = {
            "elder_id": "E-103",
            "elder_code": "EC-103",
            "full_name": "仅生日建档",
            "gender": "female",
            "birth_date": "1940-01-01",
            "risk_level": "medium",
            "status": "active",
            "station_id": "station-heping-001",
            "stay_info": {
                "check_in_status": "checked_in",
                "room_id": "A-101",
                "bed_id": "A-101-02",
                "check_in_date": "2026-04-05",
            },
            "family_contacts": [
                {
                    "family_name": "王家属",
                    "relation_type": "daughter",
                    "phone": "13800000008",
                    "is_primary_contact": True,
                }
            ],
        }

        response = self.client.post("/elders", json=payload)

        self.assertEqual(response.status_code, 201)
        body = response.json()
        today = date.today()
        expected_age = today.year - 1940 - ((today.month, today.day) < (1, 1))
        self.assertEqual(body["birth_date"], "1940-01-01")
        self.assertEqual(body["age"], expected_age)
        self.assertEqual(body["stay_info"]["room_id"], "A-101")
        self.assertEqual(body["stay_info"]["bed_id"], "A-101-02")
        self.assertEqual(body["family_contacts"][0]["family_name"], "王家属")

    def test_invalid_birth_date_returns_422_even_when_age_is_present(self) -> None:
        response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-103C",
                "elder_code": "EC-103C",
                "full_name": "非法生日HTTP",
                "gender": "female",
                "age": 80,
                "birth_date": "1940/01/01",
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "pre_admission"},
                "family_contacts": [],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("birth_date must use YYYY-MM-DD format", response.json()["detail"])

    def test_invalid_check_in_date_returns_422(self) -> None:
        response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-103D",
                "elder_code": "EC-103D",
                "full_name": "非法入住日期HTTP",
                "gender": "male",
                "age": 82,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {
                    "check_in_status": "checked_in",
                    "room_id": "A-101",
                    "bed_id": "A-101-02",
                    "check_in_date": "2026/04/05",
                },
                "family_contacts": [],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("check_in_date must use YYYY-MM-DD format", response.json()["detail"])

    def test_create_profile_accepts_checked_in_without_room_or_bed(self) -> None:
        response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-103A",
                "elder_code": "EC-103A",
                "full_name": "最小入住HTTP",
                "gender": "male",
                "age": 82,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "checked_in"},
                "family_contacts": [],
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["stay_info"]["check_in_status"], "checked_in")
        self.assertEqual(body["stay_info"]["room_id"], "")
        self.assertEqual(body["stay_info"]["bed_id"], "")
        self.assertEqual(body["stay_info"]["check_in_date"], "")

    def test_unknown_fields_return_422(self) -> None:
        extra_top_level_response = self.client.post(
            "/elders",
            json={
                **ELDER_PROFILE_CREATE_EXAMPLE,
                "unexpected_field": "not-allowed",
            },
        )
        extra_nested_response = self.client.post(
            "/elders",
            json={
                **ELDER_PROFILE_CREATE_EXAMPLE,
                "stay_info": {
                    **ELDER_PROFILE_CREATE_EXAMPLE["stay_info"],
                    "unexpected_field": "not-allowed",
                },
            },
        )

        self.assertEqual(extra_top_level_response.status_code, 422)
        self.assertEqual(extra_nested_response.status_code, 422)

    def test_invalid_family_contacts_return_422(self) -> None:
        response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-103B",
                "elder_code": "EC-103B",
                "full_name": "无主联系人HTTP",
                "gender": "female",
                "age": 80,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "pre_admission"},
                "family_contacts": [
                    {
                        "family_name": "李家属",
                        "relation_type": "child",
                        "phone": "13800000010",
                        "is_primary_contact": False,
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("primary contact", response.json()["detail"])

    def test_missing_profile_returns_404(self) -> None:
        response = self.client.get("/elders/does-not-exist")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])

    def test_invalid_stay_info_returns_422_with_readable_detail(self) -> None:
        response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-120",
                "elder_code": "EC-120",
                "full_name": "入住缺床位",
                "gender": "female",
                "age": 79,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {
                    "check_in_status": "pre_admission",
                    "room_id": "",
                    "bed_id": "A-101-02",
                },
                "family_contacts": [],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("room_id is required", response.json()["detail"])

    def test_invalid_family_contacts_return_422_with_readable_detail(self) -> None:
        response = self.client.post(
            "/elders",
            json={
                "elder_id": "E-121",
                "elder_code": "EC-121",
                "full_name": "无主联系人",
                "gender": "female",
                "age": 77,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "pre_admission"},
                "family_contacts": [
                    {
                        "family_name": "家属甲",
                        "relation_type": "daughter",
                        "phone": "13800000001",
                        "is_primary_contact": False,
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("primary contact", response.json()["detail"])

    def test_list_endpoint_supports_filters_and_pagination(self) -> None:
        payloads = [
            {
                "elder_id": "E-201",
                "elder_code": "EC-201",
                "full_name": "孙阿姨",
                "gender": "female",
                "age": 71,
                "risk_level": "medium",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {"check_in_status": "pre_admission"},
                "family_contacts": [],
            },
            {
                "elder_id": "E-202",
                "elder_code": "EC-202",
                "full_name": "周爷爷",
                "gender": "male",
                "age": 83,
                "risk_level": "high",
                "status": "active",
                "station_id": "station-heping-001",
                "stay_info": {
                    "check_in_status": "checked_in",
                    "room_id": "A-201",
                    "bed_id": "A-201-01",
                    "check_in_date": "2026-04-05",
                },
                "family_contacts": [],
            },
            {
                "elder_id": "E-203",
                "elder_code": "EC-203",
                "full_name": "吴奶奶",
                "gender": "female",
                "age": 86,
                "risk_level": "high",
                "status": "inactive",
                "station_id": "station-heping-002",
                "stay_info": {
                    "check_in_status": "checked_in",
                    "room_id": "B-301",
                    "bed_id": "B-301-02",
                    "check_in_date": "2026-04-06",
                },
                "family_contacts": [],
            },
        ]

        for payload in payloads:
            response = self.client.post("/elders", json=payload)
            self.assertEqual(response.status_code, 201)

        response = self.client.get(
            "/elders",
            params={
                "risk_level": "high",
                "check_in_status": "checked_in",
                "page": 1,
                "page_size": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total"], 2)
        self.assertEqual(body["page"], 1)
        self.assertEqual(body["page_size"], 1)
        self.assertEqual(len(body["items"]), 1)
        self.assertEqual(body["items"][0]["elder_id"], "E-202")
        self.assertEqual(body["items"][0]["stay_info"]["bed_id"], "A-201-01")

        search_response = self.client.get("/elders", params={"search": "吴"})
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.json()["total"], 1)
        self.assertEqual(search_response.json()["items"][0]["elder_id"], "E-203")
        self.assertEqual(search_response.json()["items"][0]["station_id"], "station-heping-002")
        self.assertEqual(search_response.json()["items"][0]["stay_info"]["check_in_status"], "checked_in")

    def test_openapi_schema_exposes_stable_create_example(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        schemas = response.json()["components"]["schemas"]
        request_schema = schemas["ElderProfileCreateRequest"]
        response_schema = schemas["ElderProfileResponse"]
        list_schema = schemas["ElderProfileListResponse"]
        stay_info_request_schema = schemas["StayInfoRequest"]
        family_contact_request_schema = schemas["FamilyContactRequest"]
        self.assertEqual(
            set(request_schema["properties"]),
            ELDER_PROFILE_CREATE_REQUEST_FIELDS,
        )
        self.assertNotIn("age", request_schema["required"])
        self.assertEqual(
            set(stay_info_request_schema["properties"]),
            STAY_INFO_REQUEST_FIELDS,
        )
        self.assertEqual(
            set(family_contact_request_schema["properties"]),
            FAMILY_CONTACT_REQUEST_FIELDS,
        )
        self.assertEqual(stay_info_request_schema["example"], STAY_INFO_EXAMPLE)
        self.assertEqual(
            family_contact_request_schema["example"],
            PRIMARY_FAMILY_CONTACT_EXAMPLE,
        )
        self.assertEqual(request_schema["example"]["stay_info"]["room_id"], "3B")
        self.assertEqual(request_schema["example"]["stay_info"]["bed_id"], "3B-08")
        self.assertEqual(len(request_schema["example"]["family_contacts"]), 2)
        self.assertEqual(response_schema["example"], ELDER_PROFILE_RESPONSE_EXAMPLE)
        self.assertEqual(list_schema["example"], ELDER_PROFILE_LIST_EXAMPLE)


if __name__ == "__main__":
    unittest.main()
