import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

// Blog posts: src/content/blog/<slug>.md or .mdx. The file name is the URL slug.
const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string().min(1).max(110),
    description: z.string().min(1).max(200),
    date: z.coerce.date(),
    updated: z.coerce.date().optional(),
    author: z.string().default("Matthijs van Leeuwen"),
    tags: z.array(z.string().min(1)).default([]),
    // Drafts are built only for previews (SITE_DRAFTS=1), never for production.
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
