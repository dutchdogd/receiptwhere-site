import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import pruneAssets from "./src/integrations/prune-assets.mjs";
import stage from "./src/integrations/stage.mjs";

// Static output only. public/ is copied into dist/ byte for byte; that is how the
// protected files (see protected.sha256) are carried over unchanged.
export default defineConfig({
  site: "https://receiptwhere.com",
  output: "static",
  trailingSlash: "always",
  build: {
    format: "directory",
    // Never inline CSS: the CSP is style-src 'self' with no 'unsafe-inline'.
    inlineStylesheets: "never",
  },
  markdown: {
    // Shiki writes inline style="" attributes, which the CSP blocks. Code blocks are
    // styled from site.css instead.
    syntaxHighlight: false,
  },
  // pruneAssets() deletes dist/_astro files nothing refers to (e.g. a draft's cover).
  // stage() must stay last: in a pre-launch build it cuts dist/ down to the files
  // live today (see src/integrations/stage.mjs and site.stage).
  integrations: [mdx(), pruneAssets(), stage()],
  // No dev toolbar, no telemetry-style extras in the built site.
  devToolbar: { enabled: false },
});
