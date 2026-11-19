// Remove build assets nothing refers to.
//
// Astro copies every image named in a content entry's frontmatter into dist/_astro/,
// including the cover of a draft post that a production build does not render. Such a
// file would be online at an unlinked URL. After the build, every file in
// dist/_astro/ that no HTML, CSS, XML or JSON file in dist/ mentions is deleted.
// tools/check_drafts.py checks that no draft cover is left in a production build.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TEXT = new Set([".html", ".css", ".xml", ".json", ".txt", ".webmanifest", ".js"]);

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

export default function pruneAssets() {
  return {
    name: "prune-unreferenced-assets",
    hooks: {
      "astro:build:done": ({ dir, logger }) => {
        const out = fileURLToPath(dir);
        const assets = path.join(out, "_astro");
        if (!fs.existsSync(assets)) return;
        const text = walk(out)
          .filter((f) => TEXT.has(path.extname(f)))
          .map((f) => fs.readFileSync(f, "utf8"))
          .join("\n");
        const removed = [];
        for (const file of fs.readdirSync(assets)) {
          if (!text.includes(`/_astro/${file}`)) {
            fs.rmSync(path.join(assets, file));
            removed.push(file);
          }
        }
        logger.info(`removed ${removed.length} unreferenced file(s)${removed.length ? ": " + removed.join(", ") : ""}`);
      },
    },
  };
}
