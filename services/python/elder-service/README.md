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

Run locally:

```bash
PYTHONPATH=src python3 -m elder_service
```
