// Build-time Open Graph images (1200x630 PNG): satori lays out, resvg (WebAssembly)
// rasterises. Fonts come from the pinned @fontsource packages (WOFF; satori does not
// read WOFF2). Nothing is fetched from the network.
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import satori from "satori";
import { initWasm, Resvg } from "@resvg/resvg-wasm";

const ROOT = process.cwd();
const NAVY = "#12233D";
const AMBER = "#F2A93B";
const MUTED = "#C5CEDB";
const TEXT_W = 1200 - 2 * 72; // satori wraps text only within an explicit width

let ready: Promise<void> | undefined;
function initOnce(): Promise<void> {
  ready ??= readFile(join(ROOT, "node_modules/@resvg/resvg-wasm/index_bg.wasm")).then((wasm) => initWasm(wasm));
  return ready;
}

let fonts: Promise<{ name: string; data: Buffer; weight: 400 | 700; style: "normal" }[]> | undefined;
function loadFonts() {
  fonts ??= Promise.all(
    ([400, 700] as const).map(async (weight) => ({
      name: "DM Sans",
      weight,
      style: "normal" as const,
      data: await readFile(join(ROOT, `node_modules/@fontsource/dm-sans/files/dm-sans-latin-${weight}-normal.woff`)),
    })),
  );
  return fonts;
}

let mark: Promise<string> | undefined;
function loadMark() {
  mark ??= readFile(join(ROOT, "public/favicon.svg")).then((b) => `data:image/svg+xml;base64,${b.toString("base64")}`);
  return mark;
}

type Node = { type: string; props: Record<string, unknown> };
const h = (type: string, style: Record<string, unknown>, children?: unknown, extra: Record<string, unknown> = {}): Node =>
  ({ type, props: { style, children, ...extra } });

/** Rasterise an SVG string to a square PNG of the given width (app icons). */
export async function svgPng(svg: string, width: number): Promise<Uint8Array> {
  await initOnce();
  return new Resvg(svg, { fitTo: { mode: "width", value: width } }).render().asPng();
}

export interface OgInput { eyebrow: string; title: string; footer?: string }

export async function ogPng({ eyebrow, title, footer }: OgInput): Promise<Uint8Array> {
  const [, fontData, markUri] = await Promise.all([initOnce(), loadFonts(), loadMark()]);
  const size = title.length > 70 ? 56 : title.length > 40 ? 66 : 76;
  const tree = h("div", {
    // satori sizes are content-box: 1200x630 minus the padding below.
    width: TEXT_W, height: 630 - 2 * 64, display: "flex", flexDirection: "column", justifyContent: "space-between",
    background: NAVY, padding: "64px 72px", fontFamily: "DM Sans", color: "#FFFFFF",
  }, [
    h("div", { display: "flex", alignItems: "center", gap: "18px" }, [
      h("img", { width: 56, height: 56 }, undefined, { src: markUri, width: 56, height: 56 }),
      h("div", { display: "flex", fontSize: 34, fontWeight: 700 }, "ReceiptWhere"),
    ]),
    h("div", { display: "flex", flexDirection: "column", gap: "20px", width: TEXT_W }, [
      h("div", { display: "flex", fontSize: 26, fontWeight: 700, letterSpacing: 3, color: AMBER, textTransform: "uppercase" }, eyebrow),
      h("div", { display: "block", width: TEXT_W, fontSize: size, fontWeight: 700, lineHeight: 1.1 }, title),
    ]),
    h("div", { display: "flex", width: TEXT_W, fontSize: 26, color: MUTED }, footer ?? "receiptwhere.com"),
  ]);
  const svg = await satori(tree as never, { width: 1200, height: 630, fonts: fontData });
  return new Resvg(svg, { fitTo: { mode: "width", value: 1200 } }).render().asPng();
}
