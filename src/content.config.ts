import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

// Blog posts: src/content/blog/<slug>.md or .mdx. The file name is the URL slug.
// Cover images live in src/content/blog/images/, named after the post's slug
// (e.g. images/<slug>.jpg); see docs/blog-authoring.md.

const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: ({ image }) =>
    z
      .object({
        title: z.string().min(1).max(110),
        description: z.string().min(1).max(200),
        date: z.coerce.date(),
        updated: z.coerce.date().optional(),
        author: z.string().default("Matthijs van Leeuwen"),
        tags: z.array(z.string().min(1)).default([]),
        // Cover image: shown on the post and in blog lists, and used for the social
        // card and the structured data. Required for every published post.
        // Minimum width (1200 px) is enforced in coverCrops() (src/lib/blog.ts), where
        // the image's size is known; the schema only sees the path.
        cover: image().optional(),
        // What the cover shows, for screen readers and search engines.
        coverAlt: z.string().min(1).max(200).optional(),
        // The post's body already opens with the same picture (its Markdown image line):
        // the post page then shows it once, from the body. Lists, the social card and
        // the structured data still use the cover.
        coverInBody: z.boolean().default(false),
        // Drafts are built only for previews (SITE_DRAFTS=1), never for production.
        draft: z.boolean().default(false),
      })
      .refine((d) => d.draft || d.cover !== undefined, {
        message: "a published post needs a cover image (cover: ./images/<slug>.jpg)",
        path: ["cover"],
      })
      .refine((d) => d.cover === undefined || d.coverAlt !== undefined, {
        message: "a post with a cover needs coverAlt: a short description of the image",
        path: ["coverAlt"],
      }),
});

export const collections = { blog };
