# Web App Skeleton

This is the initial Vue 3 + Vite web application skeleton for the Regional Health Platform.

Current goals:

- provide a stable frontend workspace under `apps/web`
- expose a lightweight Vue 3 + Vite app structure
- keep the shell easy to extend for future elder profile and入住 flows
- keep the first route set focused on `总览`、`长者档案`、`入住办理`

Current entry pages:

- `dashboard` for the console overview
- `elder-list` for elder archive browsing and drill-down
- `elder-detail` for elder profile and check-in detail viewing
- `elder-intake` for intake draft creation

Elder intake/list/detail now use the front-end adapter layer under `src/api/adapters/elder-service/`:

- `httpClient.js` wraps `elder-service` `GET /elders`、`GET /elders/{elder_id}`、`POST /elders`
- `mapper.js` maps API payloads to page view models and create payloads
- `archiveService.js` coordinates `create/list/get` and keeps explicit mock fallback warnings visible in the UI
- `flow.spec.mjs` covers the minimal `create -> list -> get` call chain to reduce drift from the Python service contract
