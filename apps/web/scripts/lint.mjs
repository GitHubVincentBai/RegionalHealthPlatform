import { readFileSync } from "node:fs";

const mainJs = readFileSync(new URL("../src/main.js", import.meta.url), "utf8");
const indexHtml = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const appVue = readFileSync(new URL("../src/App.vue", import.meta.url), "utf8");
const dashboardVue = readFileSync(new URL("../src/views/dashboard/DashboardPage.vue", import.meta.url), "utf8");
const elderArchiveVue = readFileSync(new URL("../src/views/elder/ElderArchivePage.vue", import.meta.url), "utf8");
const elderDetailVue = readFileSync(new URL("../src/views/elder/ElderDetailPage.vue", import.meta.url), "utf8");
const elderIntakeVue = readFileSync(new URL("../src/views/elder/ElderIntakePage.vue", import.meta.url), "utf8");
const elderMock = readFileSync(new URL("../src/modules/elder/mock.js", import.meta.url), "utf8");

if (!mainJs.includes('createApp')) {
  console.error("[web:lint] Vue createApp bootstrap is missing");
  process.exit(1);
}

if (!appVue.includes("ElderArchivePage") || !appVue.includes("ElderIntakePage")) {
  console.error("[web:lint] App.vue elder workflow mount is missing");
  process.exit(1);
}

if (!dashboardVue.includes("今日待办") || !dashboardVue.includes("告警概览")) {
  console.error("[web:lint] dashboard page sections are missing");
  process.exit(1);
}

if (!elderArchiveVue.includes("长者档案列表") || !elderArchiveVue.includes("新建长者档案")) {
  console.error("[web:lint] elder archive page copy is missing");
  process.exit(1);
}

if (!elderDetailVue.includes("长者详情") || !elderIntakeVue.includes("入住办理")) {
  console.error("[web:lint] elder detail or intake page copy is missing");
  process.exit(1);
}

if (!elderMock.includes("elderArchiveModel") || !elderMock.includes("createElderDraft")) {
  console.error("[web:lint] elder mock data layer is missing");
  process.exit(1);
}

if (!indexHtml.includes('id="app"')) {
  console.error("[web:lint] root mount point placeholder is missing");
  process.exit(1);
}

console.log("[web:lint] basic repository lint passed");
