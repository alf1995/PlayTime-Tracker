import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const absolute = file => resolve(root, file);
const require = createRequire(import.meta.url);

let ts;
try {
  ts = require("typescript");
} catch {
  const globalPath = execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim();
  ts = require(resolve(globalPath, "typescript"));
}

const files = [
  "src/i18n/en.ts",
  "src/i18n/es.ts",
  "src/i18n/translations.ts",
  "src/styles.ts",
  "src/utils/format.ts",
  "src/components/Glyph.tsx",
  "src/components/Ui.tsx",
  "src/components/Bars.tsx",
  "src/components/NavTabs.tsx",
  "src/api/decky.ts",
  "src/views/Overview.tsx",
  "src/views/Games.tsx",
  "src/views/Settings.tsx",
  "src/components/PluginContent.tsx",
  "src/index.tsx",
];

function transpile(file) {
  const result = ts.transpileModule(readFileSync(absolute(file), "utf8"), {
    fileName: file,
    reportDiagnostics: true,
    compilerOptions: {
      target: ts.ScriptTarget.ES2020,
      module: ts.ModuleKind.ESNext,
      jsx: ts.JsxEmit.ReactJSX,
    },
  });
  const errors = (result.diagnostics || []).filter(error => error.category === ts.DiagnosticCategory.Error);
  if (errors.length) {
    throw new Error(`${file}: ${errors.map(error => ts.flattenDiagnosticMessageText(error.messageText, "\n")).join("\n")}`);
  }
  return result.outputText
    .replace(/^import\s+[\s\S]*?\s+from\s+["'][^"']+["'];\s*/gm, "")
    .replace(/^import\s+["'][^"']+["'];\s*/gm, "")
    .replace(/^export\s+(?=(const|function|class)\b)/gm, "");
}

const source = files.map(transpile).join("\n");
if (/^import\s/m.test(source)) throw new Error("Unresolved import in offline bundle");
const entry = "var index = definePlugin(";
if (!source.includes("export default definePlugin(")) throw new Error("Missing Decky entrypoint");
const normalized = source.replace("export default definePlugin(", entry)
  .replace("function PluginContent()", "const SettingsView = Settings;\nfunction PluginContent()");
const adapters = `
const { PanelSection, PanelSectionRow, ButtonItem, ToggleField, staticClasses } = DFL;
const { useCallback, useEffect, useMemo, useState } = SP_REACT;
const { jsx: _jsx, jsxs: _jsxs, Fragment: _Fragment } = SP_JSX;
`;
const prelude = readFileSync(absolute("scripts/decky_bundle_prelude.js"), "utf8");
const output = `${prelude}\n${adapters}\n${normalized}\nexport { index as default };\n`;
writeFileSync(absolute("dist/index.js"), output);
console.log(`Offline fallback bundle: ${Buffer.byteLength(output)} bytes`);
console.log("Uses the previous working Decky bootstrap; prefer npm run build for release builds.");
