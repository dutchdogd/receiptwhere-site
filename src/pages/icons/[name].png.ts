// /icons/icon-192.png and /icons/icon-512.png: web manifest icons, rendered at build
// time from the full mark. (favicon.ico / apple-touch-icon.png stay as they are.)
import type { APIRoute, GetStaticPaths } from "astro";
import { MARK_SVG } from "../../lib/site";
import { svgPng } from "../../lib/og";

export const getStaticPaths = (() =>
  [192, 512].map((size) => ({ params: { name: `icon-${size}` }, props: { size } }))) satisfies GetStaticPaths;

export const GET: APIRoute = async ({ props }) => {
  const png = await svgPng(MARK_SVG, (props as { size: number }).size);
  return new Response(png, { headers: { "Content-Type": "image/png" } });
};
