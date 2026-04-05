# Elder Service Skeleton

This is the initial Python service skeleton for elder profile management.

Current goals:

- define a basic package and domain model
- expose a FastAPI application entry with elder profile routes
- keep the `domain / application / http` split stable for later expansion
- provide a stable base for later service, workflow, or integration growth

## Current API Surface

- `GET /health`
- `GET /elders`
- `POST /elders`
- `GET /elders/{elder_id}`

## Run

```bash
PYTHONPATH=src python -m elder_service
```

The service uses `uvicorn` behind the `elder_service.http.server:app` entrypoint.

Current HTTP API:

- `GET /health`
- `GET /elders`
- `POST /elders`
- `GET /elders/<elder_id>`

Install runtime and test dependencies:

```bash
python3 -m pip install -e ".[test]"
```

Run locally:

```bash
PYTHONPATH=src python3 -m elder_service
```

Run tests from either the repository root or the service directory:

```bash
python3 -m unittest discover -s services/python/elder-service/tests
cd services/python/elder-service && python3 -m unittest discover -s tests
```

Repository-level verification still uses:

```bash
bash scripts/run_python_elder_checks.sh test
bash scripts/run_python_elder_checks.sh smoke
```

Stable `POST /elders` example payload:

```json
{
  "elder_id": "E-100",
  "elder_code": "EC-100",
  "full_name": "赵六",
  "gender": "male",
  "age": 79,
  "birth_date": "1947-08-16",
  "phone": "13900000001",
  "id_card": "210102194708160011",
  "risk_level": "critical",
  "status": "active",
  "station_id": "station-heping-001",
  "stay_info": {
    "check_in_status": "checked_in",
    "room_id": "3B",
    "bed_id": "3B-08",
    "check_in_date": "2026-04-05",
    "notes": "corner bed"
  },
  "family_contacts": [
    {
      "family_name": "赵家属",
      "relation_type": "child",
      "phone": "13900000000",
      "is_primary_contact": true
    },
    {
      "family_name": "赵配偶",
      "relation_type": "spouse",
      "phone": "13800000009",
      "is_primary_contact": false
    }
  ]
}
```

The code-level source of truth for FrontAgent sample payloads lives in
`src/elder_service/http/examples.py`, including:

- `ELDER_PROFILE_CREATE_EXAMPLE` for `POST /elders`
- `ELDER_PROFILE_RESPONSE_EXAMPLE` for `GET /elders/{elder_id}`
- `ELDER_PROFILE_LIST_EXAMPLE` for `GET /elders`

OpenAPI exposes the same examples through the request and response schemas.

`POST /elders`、`GET /elders` 列表项、`GET /elders/{elder_id}` 详情统一返回以下任务包字段：

- `elder_id`
- `elder_code`
- `full_name`
- `gender`
- `age`
- `birth_date`
- `phone`
- `id_card`
- `risk_level`
- `status`
- `station_id`
- `stay_info.check_in_status`
- `stay_info.room_id`
- `stay_info.bed_id`
- `stay_info.check_in_date`
- `stay_info.notes`
- `family_contacts[].family_name`
- `family_contacts[].relation_type`
- `family_contacts[].phone`
- `family_contacts[].is_primary_contact`
