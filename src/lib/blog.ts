import { getImage } from "astro:assets";
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

/** Google asks for large images at least 1200 px wide; 675 px tall keeps the 16:9
    crop and the 1200x630 social card at full size. */
export const COVER_MIN_WIDTH = 1200;
export const COVER_MIN_HEIGHT = 675;

/** Crops of a post's cover for sharing and structured data, as site-relative URLs.
    og: the 1200x630 social card. schema: 16:9, 4:3 and 1:1, the aspect ratios
    Google asks for in Article structured data. Centre crops, JPEG. */
export async function coverCrops(post: Post) {
  const cover = post.data.cover;
  if (!cover) return undefined;
  if (cover.width < COVER_MIN_WIDTH || cover.height < COVER_MIN_HEIGHT) {
    throw new Error(`blog/${post.id}: cover is ${cover.width}x${cover.height} px; ` +
      `it must be at least ${COVER_MIN_WIDTH}x${COVER_MIN_HEIGHT} px`);
  }
  // Images are never upscaled: each crop is the largest one of that aspect ratio,
  // up to 1200 px wide, that fits inside the cover.
  const crop = async (rw: number, rh: number) => {
    const width = Math.min(1200, cover.width, Math.floor((cover.height * rw) / rh));
    const height = Math.round((width * rh) / rw);
    const img = await getImage({ src: cover, width, height, fit: "cover", position: "center", format: "jpg", quality: 82 });
    return { src: img.src, width, height };
  };
  const [og, w16, w4, w1] = await Promise.all([crop(40, 21), crop(16, 9), crop(4, 3), crop(1, 1)]);
  return { og: og.src, ogWidth: og.width, ogHeight: og.height, schema: [w16, w4, w1] };
}
