// /sitemap.xml: every public page, canonical URLs (apex, trailing slash). Draft posts
// are never listed, not even on previews. /signin/ is a redirector and is left out.
import type { APIRoute } from "astro";
import { getPosts, PAGE_SIZE, pageUrl, tagIndex } from "../lib/blog";
import { SITE } from "../lib/site";

const STATIC = ["/", "/features/", "/pricing/", "/about/", "/blog/", "/terms/", "/privacy/", "/delete-account/"];

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const day = (d: Date) => d.toISOString().slice(0, 10);

export const GET: APIRoute = async () => {
  const posts = (await getPosts()).filter((p) => !p.data.draft);
  const urls: { loc: string; lastmod?: string }[] = STATIC.map((p) => ({ loc: p }));
  const blogPages = Math.max(1, Math.ceil(posts.length / PAGE_SIZE));
  for (let n = 2; n <= blogPages; n++) urls.push({ loc: pageUrl(n) });
  for (const p of posts) urls.push({ loc: `/blog/${p.id}/`, lastmod: day(p.data.updated ?? p.data.date) });
  for (const [slug] of tagIndex(posts)) urls.push({ loc: `/blog/tags/${slug}/` });

  const body = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`,
    ...urls.map((u) => `  <url><loc>${esc(SITE + u.loc)}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ""}</url>`),
    `</urlset>`,
    "",
  ].join("\n");
  return new Response(body, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
};
