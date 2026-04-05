import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { dashboardModel } from "../../modules/dashboard/model.js";

describe("dashboardModel", () => {
  it("returns dashboard sections for the Vue shell", () => {
    const model = dashboardModel();

    assert.equal(model.stats.length > 0, true);
    assert.equal(model.tasks.length > 0, true);
    assert.equal(model.alerts.length > 0, true);
    assert.equal(model.services.length > 0, true);
    assert.equal(model.releases.length > 0, true);
  });
});
