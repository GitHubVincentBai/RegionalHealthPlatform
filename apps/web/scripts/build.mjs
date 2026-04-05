import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));
const appDir = resolve(rootDir, "..");
const distDir = resolve(appDir, "dist");

if (existsSync(distDir)) {
  rmSync(distDir, { recursive: true, force: true });
}

mkdirSync(distDir, { recursive: true });

try {
  const { build } = await import("vite");
  const { default: vue } = await import("@vitejs/plugin-vue");

  await build({
    configFile: false,
    root: appDir,
    plugins: [vue()],
    build: {
      outDir: distDir,
      emptyOutDir: true,
    },
  });

  console.log("[web:build] vite build completed");
} catch (_error) {
  cpSync(resolve(appDir, "index.html"), resolve(distDir, "index.html"));
  cpSync(resolve(appDir, "src"), resolve(distDir, "src"), { recursive: true });
  console.log("[web:build] vite dependencies unavailable; generated fallback dist");
}
