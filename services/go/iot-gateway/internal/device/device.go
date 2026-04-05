package device

import (
	"errors"
	"strings"
	"sync"
)

type Status string

const (
	StatusOnline  Status = "online"
	StatusOffline Status = "offline"
)

type Device struct {
	ID     string
	SiteID string
	Status Status
}

type Registry struct {
	mu      sync.RWMutex
	devices map[string]Device
}

func NewRegistry() *Registry {
	return &Registry{
		devices: map[string]Device{},
	}
}

func (r *Registry) Register(d Device) error {
	if strings.TrimSpace(d.ID) == "" {
		return errors.New("device id is required")
	}
	if strings.TrimSpace(d.SiteID) == "" {
		return errors.New("site id is required")
	}
	if d.Status == "" {
		d.Status = StatusOnline
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	r.devices[d.ID] = d
	return nil
}

func (r *Registry) Count() int {
	r.mu.RLock()
	defer r.mu.RUnlock()

	return len(r.devices)
}

func (r *Registry) Get(id string) (Device, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	d, ok := r.devices[id]
	return d, ok
}

func (r *Registry) List() []Device {
	r.mu.RLock()
	defer r.mu.RUnlock()

	devices := make([]Device, 0, len(r.devices))
	for _, d := range r.devices {
		devices = append(devices, d)
	}

	return devices
}
