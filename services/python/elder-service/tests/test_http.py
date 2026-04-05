import unittest

from fastapi.testclient import TestClient

from elder_service.http.server import create_app


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
            json={
                "elder_id": "E-100",
                "elder_code": "EC-100",
                "full_name": "赵六",
                "age": 79,
                "risk_level": "critical",
                "stay_info": {
                    "check_in_status": "checked_in",
                    "room_id": "3B",
                    "bed_id": "3B-08",
                    "check_in_date": "2026-04-05",
                    "notes": "corner bed",
                },
                "family_contacts": [
                    {
                        "family_name": "赵家属",
                        "relation_type": "child",
                        "phone": "13900000000",
                        "is_primary_contact": True,
                    }
                ],
            },
        )

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["elder_id"], "E-100")
        self.assertEqual(create_response.json()["elder_code"], "EC-100")
        self.assertTrue(create_response.json()["is_high_risk"])
        self.assertEqual(create_response.json()["stay_info"]["bed_id"], "3B-08")
        self.assertEqual(create_response.json()["family_contacts"][0]["family_name"], "赵家属")

        list_response = self.client.get("/elders")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()["items"]), 1)
        self.assertEqual(list_response.json()["items"][0]["current_stay_status"], "checked_in")

        fetch_response = self.client.get("/elders/E-100")
        self.assertEqual(fetch_response.status_code, 200)
        self.assertEqual(fetch_response.json()["full_name"], "赵六")
        self.assertEqual(fetch_response.json()["stay_info"]["room_id"], "3B")

    def test_missing_profile_returns_404(self) -> None:
        response = self.client.get("/elders/does-not-exist")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
