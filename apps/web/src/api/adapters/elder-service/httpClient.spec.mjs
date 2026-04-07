import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createElderServiceHttpClient } from "./httpClient.js";

describe("createElderServiceHttpClient", () => {
  it("calls elder-service list/get/create endpoints with JSON defaults", async () => {
    const calls = [];
    const client = createElderServiceHttpClient({
      baseUrl: "http://127.0.0.1:8000/",
      fetchImpl: async (url, init) => {
        calls.push({ url, init });

        return {
          ok: true,
          status: 200,
          statusText: "OK",
          headers: {
            get(name) {
              return name === "content-type" ? "application/json" : null;
            },
          },
          async json() {
            return { ok: true };
          },
        };
      },
    });

    await client.listElders({ page: 2, page_size: 10, search: "张", station_id: "station-heping-001", status: "active" });
    await client.getElder("E-3001");
    await client.createElder({ elder_id: "E-3001", full_name: "张桂兰" });

    assert.equal(calls.length, 3);
    assert.equal(
      calls[0].url,
      "http://127.0.0.1:8000/elders?page=2&page_size=10&search=%E5%BC%A0&station_id=station-heping-001&status=active",
    );
    assert.equal(calls[0].init.method, "GET");
    assert.equal(calls[0].init.headers.Accept, "application/json");
    assert.equal(calls[1].url, "http://127.0.0.1:8000/elders/E-3001");
    assert.equal(calls[2].url, "http://127.0.0.1:8000/elders");
    assert.equal(calls[2].init.method, "POST");
    assert.equal(calls[2].init.headers["Content-Type"], "application/json");
    assert.equal(calls[2].init.body, JSON.stringify({ elder_id: "E-3001", full_name: "张桂兰" }));
  });

  it("surfaces elder-service error details from JSON responses", async () => {
    const client = createElderServiceHttpClient({
      fetchImpl: async () => ({
        ok: false,
        status: 404,
        statusText: "Not Found",
        headers: {
          get(name) {
            return name === "content-type" ? "application/json" : null;
          },
        },
        async json() {
          return { detail: "elder profile missing" };
        },
      }),
    });

    await assert.rejects(() => client.getElder("missing"), /elder-service request failed: elder profile missing/);
  });

  it("uses the Vite proxy base path by default for localhost:5173 integration", async () => {
    const calls = [];
    const client = createElderServiceHttpClient({
      fetchImpl: async (url) => {
        calls.push(url);
        return {
          ok: true,
          status: 200,
          statusText: "OK",
          headers: {
            get(name) {
              return name === "content-type" ? "application/json" : null;
            },
          },
          async json() {
            return { items: [], total: 0, page: 1, page_size: 20 };
          },
        };
      },
    });

    await client.listElders();
    assert.equal(calls[0], "/api/elders");
  });

  it("converts connection failures into network errors so the archive page can fall back to mock", async () => {
    const client = createElderServiceHttpClient({
      fetchImpl: async () => {
        throw new Error("connect ECONNREFUSED 127.0.0.1:8000");
      },
    });

    await assert.rejects(() => client.listElders(), /elder-service network error: connect ECONNREFUSED 127\.0\.0\.1:8000/);
  });

  it("aborts slow requests and reports a timeout for the fallback adapter", async () => {
    const client = createElderServiceHttpClient({
      timeoutMs: 20,
      fetchImpl: (_url, init) =>
        new Promise((_resolve, reject) => {
          init.signal.addEventListener("abort", () => {
            reject(new DOMException("The operation was aborted.", "AbortError"));
          });
        }),
    });

    await assert.rejects(() => client.listElders(), /elder-service request timeout after 20ms/);
  });
});
