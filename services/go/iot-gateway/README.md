# IoT Gateway Skeleton

This is the initial Go service skeleton for device registration and gateway flows.

Current goals:

- provide a minimal executable service under `cmd/iot-gateway`
- define an internal device model with basic registration behavior
- expose native `go test` and `go build` workflows without extra dependencies

Current HTTP endpoints:

- `GET /healthz`
- `POST /devices/register`

The service listens on `:8080` by default. Set `IOT_GATEWAY_ADDR` to override it.
