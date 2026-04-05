import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createElderDraft, elderArchiveModel } from "./mock.js";

describe("elderArchiveModel", () => {
  it("returns elder archive data for the intake workflow", () => {
    const model = elderArchiveModel();

    assert.equal(model.summary.total > 0, true);
    assert.equal(model.elders.length > 0, true);
    assert.equal(model.elders[0].fullName.length > 0, true);
    assert.equal(model.elders.some((elder) => elder.status === "已入住"), true);
  });
});

describe("createElderDraft", () => {
  it("returns an empty intake draft with defaults", () => {
    const draft = createElderDraft();

    assert.equal(draft.fullName, "");
    assert.equal(draft.gender, "女");
    assert.equal(draft.riskLevel, "中风险");
  });
});
