import { defineConfig } from "astro/config";

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
  // No dev toolbar, no telemetry-style extras in the built site.
  devToolbar: { enabled: false },
});
