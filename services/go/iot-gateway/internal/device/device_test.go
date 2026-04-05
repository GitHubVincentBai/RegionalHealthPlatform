package device

import "testing"

func TestRegistryRegisterAndGet(t *testing.T) {
	registry := NewRegistry()
	if err := registry.Register(Device{
		ID:     "device-001",
		SiteID: "site-001",
		Status: StatusOnline,
	}); err != nil {
		t.Fatalf("register should succeed: %v", err)
	}

	if registry.Count() != 1 {
		t.Fatalf("expected registry count to be 1, got %d", registry.Count())
	}

	got, ok := registry.Get("device-001")
	if !ok {
		t.Fatal("expected registered device to be retrievable")
	}

	if got.Status != StatusOnline {
		t.Fatalf("expected status %q, got %q", StatusOnline, got.Status)
	}
}

func TestRegistryRejectsInvalidDevice(t *testing.T) {
	registry := NewRegistry()

	if err := registry.Register(Device{SiteID: "site-001"}); err == nil {
		t.Fatal("expected missing id to fail")
	}

	if err := registry.Register(Device{ID: "device-002"}); err == nil {
		t.Fatal("expected missing site id to fail")
	}
}

func TestRegistryDefaultsStatusToOnline(t *testing.T) {
	registry := NewRegistry()
	if err := registry.Register(Device{
		ID:     "device-003",
		SiteID: "site-001",
	}); err != nil {
		t.Fatalf("register should succeed: %v", err)
	}

	got, ok := registry.Get("device-003")
	if !ok {
		t.Fatal("expected device to be stored")
	}

	if got.Status != StatusOnline {
		t.Fatalf("expected default status %q, got %q", StatusOnline, got.Status)
	}
}
