// /og/default.png: the site-wide Open Graph image for pages without their own.
import type { APIRoute } from "astro";
import { ogPng } from "../../lib/og";

export const GET: APIRoute = async () => {
  const png = await ogPng({
    eyebrow: "The shoebox that reads itself",
    title: "Every receipt. Read, checked, and ready when you need it.",
  });
  return new Response(png, { headers: { "Content-Type": "image/png" } });
};
