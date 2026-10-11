import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const files = ["src/styles/base.css", "src/styles/responsive.css"];
const css = files.map(file => readFileSync(resolve(root, file), "utf8")).join("\n");
writeFileSync(resolve(root, "src/styles.ts"), `export const pttCSS: string = ${JSON.stringify(css)};\n`);
console.log(`CSS embedded: ${Buffer.byteLength(css)} bytes`);
