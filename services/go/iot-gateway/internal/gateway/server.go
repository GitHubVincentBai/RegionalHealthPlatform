package gateway

import (
	"encoding/json"
	"net/http"

	"github.com/example/regional-health-platform/services/go/iot-gateway/internal/device"
)

type Server struct {
	registry *device.Registry
	mux      *http.ServeMux
}

func NewServer(registry *device.Registry) *Server {
	s := &Server{
		registry: registry,
		mux:      http.NewServeMux(),
	}

	s.mux.HandleFunc("/healthz", s.handleHealth)
	s.mux.HandleFunc("/devices/register", s.handleRegister)

	return s
}

func (s *Server) Handler() http.Handler {
	return s.mux
}

func (s *Server) handleHealth(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{
		"status": "ok",
	})
}

func (s *Server) handleRegister(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		ID     string `json:"id"`
		SiteID string `json:"site_id"`
		Status string `json:"status,omitempty"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid json payload", http.StatusBadRequest)
		return
	}

	status := device.Status(req.Status)
	if status == "" {
		status = device.StatusOnline
	}

	registered := device.Device{
		ID:     req.ID,
		SiteID: req.SiteID,
		Status: status,
	}

	if err := s.registry.Register(registered); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	writeJSON(w, http.StatusCreated, registered)
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}
