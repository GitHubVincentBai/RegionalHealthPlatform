package main

import (
	"log"
	"net/http"
	"os"

	"github.com/example/regional-health-platform/services/go/iot-gateway/internal/device"
	"github.com/example/regional-health-platform/services/go/iot-gateway/internal/gateway"
)

func main() {
	registry := device.NewRegistry()
	server := gateway.NewServer(registry)

	addr := os.Getenv("IOT_GATEWAY_ADDR")
	if addr == "" {
		addr = ":8080"
	}

	log.Printf("iot-gateway listening on %s", addr)
	if err := http.ListenAndServe(addr, server.Handler()); err != nil {
		log.Fatal(err)
	}
}
