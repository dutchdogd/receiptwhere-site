// Site facts used in meta and structured data. The co-founder is not named publicly
// (Chat, 2026-11-12); tools/check_names.py enforces it.
export const SITE = "https://receiptwhere.com";
export const ORG_ID = `${SITE}/#organization`;

export const organization = {
  "@type": "Organization",
  "@id": ORG_ID,
  name: "DuoNex AI LLC",
  url: `${SITE}/`,
  logo: { "@type": "ImageObject", url: `${SITE}/icons/icon-512.png`, width: 512, height: 512 },
  email: "receipt@receiptwhere.com",
  address: { "@type": "PostalAddress", addressLocality: "Burien", addressRegion: "WA", addressCountry: "US" },
  founder: { "@type": "Person", name: "Matthijs van Leeuwen" },
  brand: { "@type": "Brand", name: "ReceiptWhere" },
};

/** JSON for a <script type="application/ld+json"> data block, safe inside HTML. */
export function ldJson(data: unknown): string {
  return JSON.stringify(data).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");
}

// The full mark (same geometry as src/components/Mark.astro), for raster icons.
export const MARK_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
<rect width="100" height="100" rx="22" fill="#12233D"/>
<path d="M50 86C41 73 24 60 24 42a26 26 0 0 1 52 0c0 18-17 31-26 44z" fill="#F2A93B"/>
<path d="M39 27h22v26l-3.7-2.6-3.6 2.6-3.7-2.6-3.7 2.6-3.6-2.6L39 53z" fill="#FFFFFF"/>
<rect x="43" y="32" width="14" height="2.6" rx="1.3" fill="#12233D"/>
<rect x="43" y="37.5" width="14" height="2.6" rx="1.3" fill="#12233D"/>
<rect x="43" y="43" width="9" height="2.6" rx="1.3" fill="#12233D"/>
</svg>`;
