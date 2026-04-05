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

    await client.listElders({ page: 2, page_size: 10, search: "张" });
    await client.getElder("E-3001");
    await client.createElder({ elder_id: "E-3001", full_name: "张桂兰" });

    assert.equal(calls.length, 3);
    assert.equal(calls[0].url, "http://127.0.0.1:8000/elders?page=2&page_size=10&search=%E5%BC%A0");
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
});
