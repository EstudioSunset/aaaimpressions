// Builds the business-facts text the AI uses, from offer.json (single source of truth).
import offer from "./offer.json";

// Brand voice shared by the chat and the contact-form auto-reply.
export const TONE = `Voice and tone:
- Professional, direct and warm, like a knowledgeable person at a small specialist firm. No slang, no emojis,
  no exclamation marks, no sales filler ("Great question!", "¡Excelente pregunta!", "We'd be delighted").
- Lead with the concrete answer, then the next step. Speak as "we" (the AAA Impressions team). Never name an individual person;
  when a quote or personal follow-up is needed, say our team will reply personally.
- Spanish: address the visitor as "tú" (tú, tu, te, escríbenos, mándanos), matching the website. Switch to
  "usted" ONLY if the visitor's own messages clearly use usted (usted, su empresa, puede, le agradezco);
  then keep usted consistently. Never mix tú and usted in the same reply.
- English: plain, direct "you".`;

export function businessFacts() {
  const c = offer.contact;
  const lines = [
    ...offer.about,
    `Contact: form at ${c.form_en} (English) or ${c.form_es} (Spanish) · WhatsApp ${c.whatsapp} · ${c.email}`,
    "",
    'Solutions and published starting prices (use ONLY these, always as "starting at" / "desde"):',
  ];
  for (const it of offer.items) {
    const p = it.prices.map((x) => x.text).join("; ");
    lines.push(`- ${it.name}${p ? ": " + p : ""}.${it.note ? " " + it.note : ""} Page: ${it.page_en} · ${it.page_es}`);
  }
  lines.push("", "Other pages:");
  for (const it of offer.more_pages) lines.push(`- ${it.name}: ${it.page_en} · ${it.page_es}`);
  lines.push("", "Rules of the business:", ...offer.rules.map((r) => "- " + r));
  return lines.join("\n");
}

// Titles for the page the visitor is on (used to give the chat context).
export function pageTopic(path) {
  if (typeof path !== "string") return "";
  const all = [...offer.items, ...offer.more_pages];
  const hit = all.find((it) => path.startsWith(it.page_en) || path.startsWith(it.page_es));
  return hit ? hit.name : "";
}

// True when a Spanish-speaking visitor writes formally (usted). "ustedes" alone does not count:
// in Latin American Spanish it is the normal plural for tú too.
const FORMAL = /\busted\b|\ble (agradezco|agradecer[íi]a|escribo|consulto|saludo)\b|\bsu (atenci[óo]n|empresa|ayuda|tiempo|respuesta|equipo)\b|\bpodr[íi]a usted\b|\bdisculpe\b/i;
export function usesUsted(text) {
  return typeof text === "string" && FORMAL.test(text);
}
