import { elderArchiveModel } from "../../../modules/elder/mock.js";
import { createElderServiceHttpClient } from "./httpClient.js";
import {
  buildCreatePayload,
  calculateArchiveSummary,
  createMockElderFromDraft,
  mapElderProfileToViewModel,
  mapListResponseToArchive,
} from "./mapper.js";

const MOCK_WARNING = "elder-service 当前不可达，页面已切换到显式 mock 兜底数据。";

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function createMockStore() {
  return clone(elderArchiveModel());
}

export function createElderArchiveService(options = {}) {
  const client = options.client || createElderServiceHttpClient(options);
  const fallbackToMock = options.fallbackToMock !== false;
  let mockStore = createMockStore();

  function getMockArchive() {
    return {
      elders: clone(mockStore.elders),
      summary: calculateArchiveSummary(mockStore.elders, Number(mockStore.summary?.total || mockStore.elders.length)),
      pagination: {
        total: Number(mockStore.summary?.total || mockStore.elders.length),
        page: 1,
        pageSize: mockStore.elders.length,
      },
    };
  }

  return {
    async loadArchive(params = {}) {
      try {
        const response = await client.listElders(params);
        return {
          ...mapListResponseToArchive(response),
          source: "api",
          warning: "",
        };
      } catch (error) {
        if (!fallbackToMock) {
          throw error;
        }

        return {
          ...getMockArchive(),
          source: "mock",
          warning: MOCK_WARNING,
          error,
        };
      }
    },

    async getElder(elderId) {
      try {
        const response = await client.getElder(elderId);
        return {
          elder: mapElderProfileToViewModel(response),
          source: "api",
          warning: "",
        };
      } catch (error) {
        if (!fallbackToMock) {
          throw error;
        }

        const elder = mockStore.elders.find((item) => item.elderId === elderId) || null;
        return {
          elder: elder ? clone(elder) : null,
          source: "mock",
          warning: MOCK_WARNING,
          error,
        };
      }
    },

    async createElder(draft) {
      const payload = buildCreatePayload(draft);

      try {
        const response = await client.createElder(payload);
        return {
          elder: mapElderProfileToViewModel(response),
          payload,
          source: "api",
          warning: "",
        };
      } catch (error) {
        if (!fallbackToMock) {
          throw error;
        }

        const elder = createMockElderFromDraft(draft, payload.elder_id);
        mockStore = {
          summary: calculateArchiveSummary(
            [elder, ...mockStore.elders],
            Number(mockStore.summary?.total || mockStore.elders.length) + 1,
          ),
          elders: [elder, ...mockStore.elders],
        };

        return {
          elder,
          payload,
          source: "mock",
          warning: MOCK_WARNING,
          error,
        };
      }
    },
  };
}

export { MOCK_WARNING as ELDER_SERVICE_MOCK_WARNING };
