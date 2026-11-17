// Stage flag. site.stage (repo root) holds "prelaunch" or "launch".
//
// prelaunch: after the build, dist/ is cut down to exactly the files live today on
// GitHub Pages: the protected files (protected.sha256), the self-hosted fonts, the
// holding page (prelaunch/index.html, byte-identical to main's index.html), plus
// _headers and a plain 404 page (prelaunch/404.html; without a 404.html, Cloudflare
// Pages would answer unknown paths with the home page and status 200). Everything
// else the build produced (S2 pages, blog, sitemap, robots, OG images, icons) is
// removed. It is an allowlist: a new page cannot slip into a pre-launch build.
//
// launch: the full site, unchanged.
//
// tools/check_stage.py checks the result in CI; the launch flip is one commit that
// changes site.stage, together with the launch Terms and Privacy.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const STAGES = ["prelaunch", "launch"];

export function readStage() {
  const stage = fs.readFileSync(path.join(ROOT, "site.stage"), "utf8").trim();
  if (!STAGES.includes(stage)) {
    throw new Error(`site.stage must be one of ${STAGES.join(", ")}; found "${stage}"`);
  }
  return stage;
}

// Paths relative to dist/, with forward slashes.
export function prelaunchFiles() {
  const manifest = fs
    .readFileSync(path.join(ROOT, "protected.sha256"), "utf8")
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => line.trim().split(/\s+/)[1]);
  const fonts = fs.readdirSync(path.join(ROOT, "public", "fonts")).map((f) => `fonts/${f}`);
  return new Set([...manifest, ...fonts, "_headers", "index.html", "404.html"]);
}

function walk(dir, base = dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full, base));
    else out.push(path.relative(base, full).split(path.sep).join("/"));
  }
  return out;
}

function removeEmptyDirs(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) removeEmptyDirs(path.join(dir, entry.name));
  }
  if (fs.readdirSync(dir).length === 0) fs.rmdirSync(dir);
}

export default function stage() {
  return {
    name: "site-stage",
    hooks: {
      "astro:build:done": ({ dir, logger }) => {
        const current = readStage();
        logger.info(`site.stage: ${current}`);
        if (current !== "prelaunch") return;
        const out = fileURLToPath(dir);
        for (const name of ["index.html", "404.html"]) {
          fs.copyFileSync(path.join(ROOT, "prelaunch", name), path.join(out, name));
        }
        const keep = prelaunchFiles();
        let removed = 0;
        for (const rel of walk(out)) {
          if (!keep.has(rel)) {
            fs.rmSync(path.join(out, rel));
            removed += 1;
          }
        }
        for (const entry of fs.readdirSync(out, { withFileTypes: true })) {
          if (entry.isDirectory()) removeEmptyDirs(path.join(out, entry.name));
        }
        logger.info(`prelaunch: kept ${keep.size} files, removed ${removed}`);
      },
    },
  };
}
