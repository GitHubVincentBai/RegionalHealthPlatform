import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const css = readFileSync(new URL("../src/styles.css", import.meta.url), "utf8");
const appVue = readFileSync(new URL("../src/App.vue", import.meta.url), "utf8");
const elderArchiveVue = readFileSync(new URL("../src/views/elder/ElderArchivePage.vue", import.meta.url), "utf8");
const elderIntakeVue = readFileSync(new URL("../src/views/elder/ElderIntakePage.vue", import.meta.url), "utf8");

assert.match(html, /id="app"/);
assert.match(css, /\.app-nav|\.archive-list|\.intake-form/);
assert.match(appVue, /ElderArchivePage/);
assert.match(elderArchiveVue, /新建长者档案/);
assert.match(elderIntakeVue, /保存入住草稿/);

execFileSync("node", ["--test", "./src/modules/elder/mock.spec.mjs", "./src/views/dashboard/DashboardPage.spec.mjs"], {
  cwd: new URL("..", import.meta.url).pathname,
  stdio: "inherit",
});

console.log("[web:test] smoke tests passed");
