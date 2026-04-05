import unittest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from fastapi.testclient import TestClient

    from elder_service.http.examples import (
        ELDER_PROFILE_RESPONSE_FIELDS,
        ELDER_PROFILE_CREATE_EXAMPLE,
        ELDER_PROFILE_LIST_EXAMPLE,
        ELDER_PROFILE_LIST_RESPONSE_FIELDS,
        ELDER_PROFILE_RESPONSE_EXAMPLE,
        FAMILY_CONTACT_RESPONSE_FIELDS,
        STAY_INFO_RESPONSE_FIELDS,
    )
    from elder_service.http.server import create_app
except ModuleNotFoundError as exc:
    TestClient = None
    create_app = None
    ELDER_PROFILE_CREATE_EXAMPLE = None
    ELDER_PROFILE_LIST_EXAMPLE = None
    ELDER_PROFILE_LIST_RESPONSE_FIELDS = set()
    ELDER_PROFILE_RESPONSE_EXAMPLE = None
    ELDER_PROFILE_RESPONSE_FIELDS = set()
    FAMILY_CONTACT_RESPONSE_FIELDS = set()
    STAY_INFO_RESPONSE_FIELDS = set()
    FASTAPI_IMPORT_ERROR = exc
else:
    FASTAPI_IMPORT_ERROR = None


@unittest.skipIf(FASTAPI_IMPORT_ERROR is not None, f"fastapi runtime unavailable: {FASTAPI_IMPORT_ERROR}")
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

    def test_missing_profile_returns_404(self) -> None:
        response = self.client.get("/elders/does-not-exist")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])

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
                "stay_info": {"check_in_status": "checked_in"},
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
                "stay_info": {"check_in_status": "checked_in"},
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
        self.assertEqual(body["items"][0]["stay_info"]["bed_id"], "")

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
        self.assertEqual(request_schema["example"]["stay_info"]["room_id"], "3B")
        self.assertEqual(request_schema["example"]["stay_info"]["bed_id"], "3B-08")
        self.assertEqual(len(request_schema["example"]["family_contacts"]), 2)
        self.assertEqual(response_schema["example"], ELDER_PROFILE_RESPONSE_EXAMPLE)
        self.assertEqual(list_schema["example"], ELDER_PROFILE_LIST_EXAMPLE)


if __name__ == "__main__":
    unittest.main()
