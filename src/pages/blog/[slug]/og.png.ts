// /blog/<slug>/og.png: the post's Open Graph image, rendered at build time.
import type { APIRoute, GetStaticPaths } from "astro";
import { formatDate, getPosts, type Post } from "../../../lib/blog";
import { ogPng } from "../../../lib/og";

export const getStaticPaths = (async () =>
  (await getPosts()).map((post) => ({ params: { slug: post.id }, props: { post } }))) satisfies GetStaticPaths;

export const GET: APIRoute = async ({ props }) => {
  const { data } = (props as { post: Post }).post;
  const png = await ogPng({
    eyebrow: "ReceiptWhere blog",
    title: data.title,
    footer: `${data.author} · ${formatDate(data.date)}`,
  });
  return new Response(png, { headers: { "Content-Type": "image/png" } });
};
