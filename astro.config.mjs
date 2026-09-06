// @ts-check
import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";

import cloudflare from "@astrojs/cloudflare";

// https://astro.build/config
export default defineConfig({
  site: "https://cftrust.org",
  integrations: [
    mdx(),
    // privacy-cardproai excluded: an unrelated hobby-business privacy policy
    // hosted here temporarily for an eBay developer app requirement, not a
    // CFTrust page — kept out of the sitemap and unlinked from nav (Christian,
    // 2026-09-06), reachable only by direct URL.
    sitemap({ filter: (page) => !page.includes("/privacy-cardproai") }),
  ],
  adapter: cloudflare({
    platformProxy: {
      enabled: true,
    },
  }),
});
