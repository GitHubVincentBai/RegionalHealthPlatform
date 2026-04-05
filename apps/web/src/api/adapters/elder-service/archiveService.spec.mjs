import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createElderArchiveService } from "./archiveService.js";

function createApiProfile(overrides = {}) {
  return {
    elder_id: "E-3001",
    elder_code: "EC-3001",
    full_name: "赵六",
    age: 79,
    risk_level: "high",
    is_high_risk: true,
    current_stay_status: "checked_in",
    stay_info: {
      check_in_status: "checked_in",
      room_id: "3B",
      bed_id: "3B-08",
      check_in_date: "2026-04-05",
      notes: "corner bed",
    },
    family_contacts: [
      {
        family_name: "赵家属",
        relation_type: "子女",
        phone: "13900000000",
        is_primary_contact: true,
      },
    ],
    ...overrides,
  };
}

describe("createElderArchiveService", () => {
  it("loads elder list from elder-service and maps summary for the archive page", async () => {
    const service = createElderArchiveService({
      fallbackToMock: false,
      client: {
        async listElders() {
          return {
            items: [
              createApiProfile(),
              createApiProfile({
                elder_id: "E-3002",
                elder_code: "EC-3002",
                full_name: "钱阿姨",
                risk_level: "medium",
                is_high_risk: false,
                current_stay_status: "pre_admission",
                stay_info: {
                  check_in_status: "pre_admission",
                  room_id: "",
                  bed_id: "",
                  check_in_date: "",
                  notes: "",
                },
                family_contacts: [],
              }),
            ],
            total: 9,
            page: 1,
            page_size: 20,
          };
        },
      },
    });

    const archive = await service.loadArchive();

    assert.equal(archive.source, "api");
    assert.equal(archive.summary.total, 9);
    assert.equal(archive.summary.checkedIn, 1);
    assert.equal(archive.summary.waitingCheckIn, 1);
    assert.equal(archive.elders[0].family, "赵家属");
  });

  it("creates elder profiles with a payload compatible with elder-service", async () => {
    let capturedPayload = null;

    const service = createElderArchiveService({
      fallbackToMock: false,
      client: {
        async createElder(payload) {
          capturedPayload = payload;
          return createApiProfile({
            elder_id: payload.elder_id,
            elder_code: payload.elder_code,
            full_name: payload.full_name,
            age: payload.age,
            risk_level: payload.risk_level,
            current_stay_status: payload.stay_info.check_in_status,
            stay_info: payload.stay_info,
            family_contacts: payload.family_contacts,
          });
        },
      },
    });

    const created = await service.createElder({
      elderCode: "EC-4001",
      fullName: "孙奶奶",
      age: 81,
      riskLevel: "高风险",
      checkInStatus: "待入住",
      room: "A-201",
      bed: "A-201-01",
      familyName: "孙先生",
      familyRelation: "子女",
      familyPhone: "13812345678",
      checkInDate: "2026-04-06",
      note: "首批联调",
    });

    assert.equal(created.source, "api");
    assert.equal(capturedPayload.risk_level, "high");
    assert.equal(capturedPayload.stay_info.check_in_status, "pre_admission");
    assert.equal(capturedPayload.family_contacts[0].phone, "13812345678");
    assert.equal(created.elder.status, "待入住");
    assert.equal(created.elder.family, "孙先生");
  });

  it("gets elder detail from elder-service and maps it for the detail page", async () => {
    const service = createElderArchiveService({
      fallbackToMock: false,
      client: {
        async getElder(elderId) {
          return createApiProfile({
            elder_id: elderId,
            full_name: "详情长者",
            stay_info: {
              check_in_status: "checked_in",
              room_id: "C-302",
              bed_id: "C-302-02",
              check_in_date: "2026-04-07",
              notes: "detail note",
            },
          });
        },
      },
    });

    const detail = await service.getElder("E-4100");

    assert.equal(detail.source, "api");
    assert.equal(detail.elder.elderId, "E-4100");
    assert.equal(detail.elder.fullName, "详情长者");
    assert.equal(detail.elder.bed, "C-302-02");
    assert.equal(detail.elder.note, "detail note");
  });

  it("falls back to explicit mock data when elder-service list fails", async () => {
    const service = createElderArchiveService({
      client: {
        async listElders() {
          throw new Error("connect ECONNREFUSED");
        },
      },
    });

    const archive = await service.loadArchive();

    assert.equal(archive.source, "mock");
    assert.match(archive.warning, /mock/);
    assert.equal(archive.elders.length > 0, true);
  });

  it("falls back to mock create so the intake page can still complete a draft flow", async () => {
    const service = createElderArchiveService({
      client: {
        async createElder() {
          throw new Error("service unavailable");
        },
      },
    });

    const created = await service.createElder({
      fullName: "周奶奶",
      age: 84,
      riskLevel: "中风险",
      checkInStatus: "待入住",
      familyName: "周女士",
      familyRelation: "女儿",
      familyPhone: "13700000000",
    });

    const detail = await service.getElder(created.elder.elderId);

    assert.equal(created.source, "mock");
    assert.equal(detail.source, "mock");
    assert.equal(detail.elder.fullName, "周奶奶");
    assert.equal(detail.elder.familyPhone, "13700000000");
  });
});
