const DEFAULT_BASE_URL = "/api";
const DEFAULT_TIMEOUT_MS = 1500;

function normalizeBaseUrl(baseUrl) {
  return (baseUrl || DEFAULT_BASE_URL).replace(/\/+$/, "");
}

function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }

    searchParams.set(key, String(value));
  }

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

async function parseResponse(response) {
  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers?.get?.("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

export function createElderServiceHttpClient(options = {}) {
  const baseUrl = normalizeBaseUrl(options.baseUrl ?? import.meta.env?.VITE_ELDER_SERVICE_BASE_URL);
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;
  const timeoutMs = Number(options.timeoutMs ?? import.meta.env?.VITE_ELDER_SERVICE_TIMEOUT_MS ?? DEFAULT_TIMEOUT_MS);

  if (typeof fetchImpl !== "function") {
    throw new Error("global fetch is unavailable; cannot call elder-service");
  }

  async function request(path, init = {}) {
    const controller = typeof AbortController === "function" ? new AbortController() : null;
    const timeoutId =
      controller && timeoutMs > 0
        ? setTimeout(() => controller.abort(new Error(`elder-service request timeout after ${timeoutMs}ms`)), timeoutMs)
        : null;

    let response;

    try {
      response = await fetchImpl(`${baseUrl}${path}`, {
        method: init.method || "GET",
        headers: {
          Accept: "application/json",
          ...(init.body ? { "Content-Type": "application/json" } : {}),
          ...(init.headers || {}),
        },
        signal: init.signal ?? controller?.signal,
        ...init,
      });
    } catch (error) {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      if (error?.name === "AbortError") {
        throw new Error(`elder-service request timeout after ${timeoutMs}ms`);
      }

      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`elder-service network error: ${message}`);
    }

    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`.trim();

      try {
        const body = await parseResponse(response);
        if (body && typeof body === "object" && "detail" in body) {
          detail = String(body.detail);
        }
      } catch (_error) {
        detail = detail || "request failed";
      }

      throw new Error(`elder-service request failed: ${detail}`);
    }

    return parseResponse(response);
  }

  return {
    listElders(params = {}) {
      return request(`/elders${buildQueryString(params)}`);
    },
    getElder(elderId) {
      return request(`/elders/${encodeURIComponent(elderId)}`);
    },
    createElder(payload) {
      return request("/elders", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };
}
