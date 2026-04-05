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

`.[test]` is the expected local entry for the HTTP suite. The service uses
`unittest`, but the runtime dependencies required by `fastapi.testclient`
must already exist in that environment.
For repository-level verification, treat `services/python/elder-service/.venv`
bootstrapped by `bash scripts/run_python_elder_checks.sh test` as the canonical
environment instead of relying on host Python packages.

Run locally:

```bash
PYTHONPATH=src python3 -m elder_service
```

Run tests from either the repository root or the service directory:

```bash
bash scripts/run_python_elder_checks.sh test
cd services/python/elder-service && ./.venv/bin/python -m unittest tests.test_service tests.test_http
```

Running `python3 -m unittest tests.test_service tests.test_http` directly on the
host interpreter is only expected to work after that interpreter has installed
`.[test]`; otherwise the HTTP suite will fail fast on missing `fastapi`.

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
  "age": 78,
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

`POST /elders` accepts `age` or `birth_date`; at least one of the two must be
present. The stable example keeps both fields so FrontAgent can cover
`family_contacts`、`stay_info`、`room_id`、`bed_id` against a complete payload.
For the MVP contract, `stay_info.check_in_status` may be submitted on its own;
`room_id`、`bed_id`、`check_in_date` remain optional fields in the create, list,
and detail payloads.
When present, `birth_date` and `stay_info.check_in_date` must use `YYYY-MM-DD`.

Canonical local verification for this service is:

```bash
bash scripts/run_python_elder_checks.sh test
```

That entry bootstraps and reuses `services/python/elder-service/.venv`, installs
`-e ".[test]"` when the runtime imports are missing, and runs the service plus
HTTP suites from the same isolated environment used by repository-level checks.

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
