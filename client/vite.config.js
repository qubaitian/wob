import { defineConfig } from "vite";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const dependencies = Object.keys(require("@voxelize/core/package.json").dependencies);
export default defineConfig({
  build: { target: "esnext" },
  optimizeDeps: {
    // Keep worker URLs relative to the engine and prebundle its CommonJS dependencies.
    exclude: ["@voxelize/core"],
    include: dependencies.filter(name => name !== "vite-plugin-copy").map(name => "@voxelize/core > " + name),
  },
});
