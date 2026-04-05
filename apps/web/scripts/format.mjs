import { existsSync } from "node:fs";

const requiredFiles = [
  "index.html",
  "vite.config.js",
  "src/App.vue",
  "src/main.js",
  "src/styles.css",
  "src/views/dashboard/DashboardPage.vue",
  "src/views/elder/ElderArchivePage.vue",
  "src/views/elder/ElderDetailPage.vue",
  "src/views/elder/ElderIntakePage.vue",
  "src/views/dashboard/DashboardPage.spec.mjs",
  "src/modules/dashboard/model.js",
  "src/modules/elder/mock.js",
  "src/modules/elder/mock.spec.mjs",
  "src/components/StatCard.vue",
  "src/components/SectionCard.vue",
  "src/components/AppHeader.vue",
  "src/components/AppNav.vue",
  "src/composables/useHashView.js",
];

for (const file of requiredFiles) {
  if (!existsSync(new URL(`../${file}`, import.meta.url))) {
    console.error(`[web:format] missing required file: ${file}`);
    process.exit(1);
  }
}

console.log("[web:format] no-op formatter completed");
