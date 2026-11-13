import rss from "@astrojs/rss";
import type { APIContext } from "astro";
import { getPosts } from "../../lib/blog";

export async function GET(context: APIContext) {
  const posts = await getPosts();
  return rss({
    title: "ReceiptWhere blog",
    description: "Notes on receipts, record keeping and how ReceiptWhere reads and checks what a receipt proves.",
    site: context.site!,
    trailingSlash: true,
    items: posts.map((p) => ({
      title: p.data.title,
      description: p.data.description,
      pubDate: p.data.date,
      link: `/blog/${p.id}/`,
      categories: p.data.tags,
      author: `receipt@receiptwhere.com (${p.data.author})`,
    })),
    customData: "<language>en-us</language>",
  });
}
