import { getCollection, type CollectionEntry } from "astro:content";

export type Post = CollectionEntry<"blog">;

// Drafts are included only when the build is for a preview. CI sets SITE_DRAFTS=1 on
// pushes to branches other than main; production builds never see them
// (tools/check_drafts.py fails the build if one slips through).
export const SHOW_DRAFTS = process.env.SITE_DRAFTS === "1";

export const PAGE_SIZE = 10;

/** Published posts (plus drafts on previews), newest first. */
export async function getPosts(): Promise<Post[]> {
  const posts = await getCollection("blog", ({ data }) => SHOW_DRAFTS || !data.draft);
  return posts.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

export function tagSlug(tag: string): string {
  return tag.toLowerCase().normalize("NFKD").replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-+|-+$/g, "");
}

/** Every tag in use, with its posts (newest first) and display name. */
export function tagIndex(posts: Post[]): Map<string, { name: string; posts: Post[] }> {
  const map = new Map<string, { name: string; posts: Post[] }>();
  for (const post of posts) {
    for (const name of post.data.tags) {
      const slug = tagSlug(name);
      if (!map.has(slug)) map.set(slug, { name, posts: [] });
      map.get(slug)!.posts.push(post);
    }
  }
  return map;
}

/** Minutes to read, at 230 words a minute, from the raw Markdown body. */
export function readingMinutes(body: string | undefined): number {
  const text = (body ?? "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/[#>*_`|[\]()-]/g, " ");
  const words = text.split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 230));
}

const dateFmt = new Intl.DateTimeFormat("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
export function formatDate(d: Date): string {
  return dateFmt.format(d);
}

/** Split posts into pages of PAGE_SIZE. Page 1 is /blog/, page n is /blog/page/n/. */
export function pages(posts: Post[]): Post[][] {
  const out: Post[][] = [];
  for (let i = 0; i < posts.length; i += PAGE_SIZE) out.push(posts.slice(i, i + PAGE_SIZE));
  return out.length ? out : [[]];
}

export function pageUrl(n: number): string {
  return n <= 1 ? "/blog/" : `/blog/page/${n}/`;
}
