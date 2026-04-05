import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const css = readFileSync(new URL("../src/styles.css", import.meta.url), "utf8");
const appVue = readFileSync(new URL("../src/App.vue", import.meta.url), "utf8");
const elderArchiveVue = readFileSync(new URL("../src/views/elder/ElderArchivePage.vue", import.meta.url), "utf8");
const elderDetailVue = readFileSync(new URL("../src/views/elder/ElderDetailPage.vue", import.meta.url), "utf8");
const elderIntakeVue = readFileSync(new URL("../src/views/elder/ElderIntakePage.vue", import.meta.url), "utf8");
const appViews = readFileSync(new URL("../src/navigation/appViews.js", import.meta.url), "utf8");
const elderApiIndex = readFileSync(new URL("../src/api/adapters/elder-service/index.js", import.meta.url), "utf8");
const elderService = readFileSync(new URL("../src/api/adapters/elder-service/archiveService.js", import.meta.url), "utf8");

assert.match(html, /id="app"/);
assert.match(css, /\.app-nav|\.archive-list|\.intake-form|\.info-banner/);
assert.match(appVue, /createElderArchiveService/);
assert.match(elderArchiveVue, /新建长者档案/);
assert.match(elderDetailVue, /elder-service|Mock Fallback/);
assert.match(elderIntakeVue, /保存入住草稿/);
assert.match(appViews, /APP_NAV_ITEMS/);
assert.match(elderApiIndex, /createElderArchiveService|createElderServiceHttpClient/);
assert.match(elderService, /loadArchive|getElder|createElder/);

execFileSync(
  "node",
  [
    "--test",
    "./src/modules/elder/mock.spec.mjs",
    "./src/api/adapters/elder-service/httpClient.spec.mjs",
    "./src/api/adapters/elder-service/mapper.spec.mjs",
    "./src/api/adapters/elder-service/archiveService.spec.mjs",
    "./src/api/adapters/elder-service/flow.spec.mjs",
    "./src/views/dashboard/DashboardPage.spec.mjs",
  ],
  {
  cwd: new URL("..", import.meta.url).pathname,
  stdio: "inherit",
  },
);

console.log("[web:test] smoke tests passed");
