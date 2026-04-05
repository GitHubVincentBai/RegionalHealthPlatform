import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { buildCreatePayload, mapElderProfileToViewModel } from "./mapper.js";

describe("elder service mapper", () => {
  it("maps elder-service detail payloads to the view model used by list and detail pages", () => {
    const elder = mapElderProfileToViewModel({
      elder_id: "E-5001",
      elder_code: "EC-5001",
      full_name: "吴奶奶",
      gender: "女",
      age: 83,
      birth_date: "1941-02-10",
      phone: "13600000001",
      id_card: "210102194102100022",
      status: "active",
      station_id: "station-heping",
      risk_level: "medium",
      current_stay_status: "checked_in",
      stay_info: {
        check_in_status: "checked_in",
        room_id: "A-502",
        bed_id: "A-502-02",
        check_in_date: "2026-04-05",
        notes: "需要靠窗床位",
      },
      family_contacts: [
        {
          family_name: "吴女士",
          relation_type: "女儿",
          phone: "13600000000",
          is_primary_contact: true,
        },
      ],
    });

    assert.equal(elder.elderId, "E-5001");
    assert.equal(elder.status, "已入住");
    assert.equal(elder.gender, "女");
    assert.equal(elder.station, "station-heping");
    assert.equal(elder.phone, "13600000001");
    assert.equal(elder.room, "A-502");
    assert.equal(elder.family, "吴女士");
    assert.equal(elder.note, "需要靠窗床位");
    assert.equal(elder.source, "api");
  });

  it("builds a create payload compatible with elder-service minimal schema", () => {
    const payload = buildCreatePayload({
      elderCode: "EC-6001",
      fullName: "刘爷爷",
      gender: "男",
      age: 86,
      birthDate: "1940-06-12",
      phone: "13612345678",
      idCard: "210102194006120031",
      riskLevel: "高风险",
      stationId: "station-longhu",
      checkInStatus: "待入住",
      room: "B-201",
      bed: "B-201-01",
      familyName: "刘先生",
      familyRelation: "儿子",
      familyPhone: "13500000000",
      checkInDate: "2026-04-06",
      note: "首批入住联调",
    });

    assert.equal(payload.elder_code, "EC-6001");
    assert.equal(payload.risk_level, "high");
    assert.equal(payload.gender, "男");
    assert.equal(payload.station_id, "station-longhu");
    assert.equal(payload.stay_info.check_in_status, "pre_admission");
    assert.equal(payload.stay_info.bed_id, "B-201-01");
    assert.equal(payload.family_contacts[0].relation_type, "儿子");
  });
});
