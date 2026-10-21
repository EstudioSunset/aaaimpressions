// Checks that the AI's business facts (worker/src/offer.json) match the built site (_site).
// Run after `npm run build`:  npm run check:offer
// Fails if a page is missing or a listed price is not on its page; warns if a page shows a price not listed.
import { readFileSync, existsSync } from "node:fs";

const offer = JSON.parse(readFileSync("worker/src/offer.json", "utf8"));
const norm = (x) => x.replace(/[^\d]/g, "");
let errors = 0, warnings = 0;

function pageText(path) {
  const f = `_site${path}index.html`;
  if (!existsSync(f)) return null;
  return readFileSync(f, "utf8")
    .replace(/<script[\s\S]*?<\/script>/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ");
}

for (const it of [...offer.items, ...offer.more_pages]) {
  for (const path of [it.page_en, it.page_es]) {
    const text = pageText(path);
    if (text === null) { console.log(`ERROR  page not found: ${path}`); errors++; continue; }
    const listed = new Set([...(it.prices || []).map((p) => norm(p.match)), ...(it.not_prices || []).map(norm)]);
    const onPage = new Set((text.match(/\$\s?\d[\d,]*/g) || []).map(norm));
    for (const p of it.prices || []) {
      if (!onPage.has(norm(p.match))) { console.log(`ERROR  ${path}: "${p.text}" not found on the page`); errors++; }
    }
    if (it.prices) {
      for (const n of onPage) {
        if (!listed.has(n)) { console.log(`WARN   ${path}: page shows $${n}, which offer.json does not list for this item`); warnings++; }
      }
    }
  }
}
console.log(`\n${errors} error(s), ${warnings} warning(s).`);
process.exit(errors ? 1 : 0);
