package gateway

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/example/regional-health-platform/services/go/iot-gateway/internal/device"
)

func TestHealthEndpoint(t *testing.T) {
	server := NewServer(device.NewRegistry())

	req := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	rec := httptest.NewRecorder()

	server.Handler().ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", rec.Code)
	}

	if !strings.Contains(rec.Body.String(), `"status":"ok"`) {
		t.Fatalf("expected health payload, got %q", rec.Body.String())
	}
}

func TestRegisterEndpoint(t *testing.T) {
	registry := device.NewRegistry()
	server := NewServer(registry)

	body := bytes.NewBufferString(`{"id":"device-100","site_id":"site-100"}`)
	req := httptest.NewRequest(http.MethodPost, "/devices/register", body)
	rec := httptest.NewRecorder()

	server.Handler().ServeHTTP(rec, req)

	if rec.Code != http.StatusCreated {
		t.Fatalf("expected status 201, got %d", rec.Code)
	}

	if got, ok := registry.Get("device-100"); !ok {
		t.Fatal("expected device to be registered")
	} else if got.Status != device.StatusOnline {
		t.Fatalf("expected default online status, got %q", got.Status)
	}
}

func TestRegisterEndpointRejectsInvalidPayload(t *testing.T) {
	server := NewServer(device.NewRegistry())

	req := httptest.NewRequest(http.MethodPost, "/devices/register", bytes.NewBufferString(`{"site_id":"site-100"}`))
	rec := httptest.NewRecorder()

	server.Handler().ServeHTTP(rec, req)

	if rec.Code != http.StatusBadRequest {
		t.Fatalf("expected status 400, got %d", rec.Code)
	}
}
