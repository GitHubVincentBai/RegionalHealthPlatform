import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createElderArchiveService } from "./archiveService.js";

function createClient() {
  const store = [
    {
      elder_id: "E-8001",
      elder_code: "EC-8001",
      full_name: "联调样例",
      age: 78,
      risk_level: "medium",
      current_stay_status: "pre_admission",
      stay_info: {
        check_in_status: "pre_admission",
        room_id: "A-102",
        bed_id: "A-102-01",
        check_in_date: "2026-04-05",
        notes: "",
      },
      family_contacts: [],
    },
  ];

  return {
    async listElders(params = {}) {
      const search = String(params.search || "").trim();
      const items = search
        ? store.filter(
            (item) => item.full_name.includes(search) || item.elder_id.includes(search) || item.elder_code.includes(search),
          )
        : store;

      return {
        items,
        total: items.length,
        page: 1,
        page_size: 20,
      };
    },
    async getElder(elderId) {
      return store.find((item) => item.elder_id === elderId) || null;
    },
    async createElder(payload) {
      const created = {
        elder_id: payload.elder_id,
        elder_code: payload.elder_code,
        full_name: payload.full_name,
        age: payload.age,
        risk_level: payload.risk_level,
        current_stay_status: payload.stay_info.check_in_status,
        stay_info: payload.stay_info,
        family_contacts: payload.family_contacts,
      };

      store.unshift(created);
      return created;
    },
  };
}

describe("elder archive flow", () => {
  it("connects create, list, and get through one service instance", async () => {
    const service = createElderArchiveService({
      fallbackToMock: false,
      client: createClient(),
    });

    const beforeCreate = await service.loadArchive();
    const created = await service.createElder({
      elderCode: "EC-8002",
      fullName: "联调新增长者",
      age: 82,
      riskLevel: "高风险",
      checkInStatus: "已入住",
      room: "A-103",
      bed: "A-103-02",
      familyName: "联调家属",
      familyRelation: "女儿",
      familyPhone: "13800001111",
      checkInDate: "2026-04-06",
      note: "最小联调链路",
    });
    const afterCreate = await service.loadArchive();
    const detail = await service.getElder(created.elder.elderId);

    assert.equal(beforeCreate.summary.total, 1);
    assert.equal(created.source, "api");
    assert.equal(afterCreate.summary.total, 2);
    assert.equal(afterCreate.elders[0].fullName, "联调新增长者");
    assert.equal(detail.elder.family, "联调家属");
    assert.equal(detail.elder.status, "已入住");
  });

  it("keeps the create then list/detail smoke path stable for elder intake", async () => {
    const service = createElderArchiveService({
      fallbackToMock: false,
      client: createClient(),
    });

    const created = await service.createElder({
      elderCode: "EC-8003",
      fullName: "冒烟链路长者",
      age: 79,
      riskLevel: "中风险",
      checkInStatus: "待入住",
      room: "B-201",
      bed: "B-201-01",
      familyName: "冒烟联系人",
      familyRelation: "儿子",
      familyPhone: "13700002222",
      checkInDate: "2026-04-07",
      note: "创建后继续查询",
    });

    const archive = await service.loadArchive({ search: "冒烟链路" });
    const detail = await service.getElder(created.elder.elderId);

    assert.equal(created.source, "api");
    assert.equal(created.elder.fullName, "冒烟链路长者");
    assert.equal(archive.summary.total, 1);
    assert.equal(archive.elders[0].elderId, created.elder.elderId);
    assert.equal(archive.elders[0].status, "待入住");
    assert.equal(detail.elder.elderId, created.elder.elderId);
    assert.equal(detail.elder.room, "B-201");
    assert.equal(detail.elder.familyPhone, "13700002222");
    assert.equal(detail.elder.note, "创建后继续查询");
  });
});
