// Chat logging (D1) and the daily digest email. Everything here is optional:
// without a DB binding the chat works exactly as before and nothing is stored.
import offer from "./offer.json";

const KEEP_DAYS = 180;

// Dollar amounts the business actually publishes; anything else in an answer is flagged.
const KNOWN = new Set(offer.items.flatMap((it) => it.prices.map((p) => norm(p.match))));
function norm(x) { return x.replace(/[^\d]/g, ""); }
export function unknownPrices(text) {
  const found = (text.match(/\$\s?\d[\d,]*(\.\d+)?/g) || []).map(norm);
  return [...new Set(found.filter((n) => !KNOWN.has(n)))].map((n) => "$" + n);
}

export async function logChat(db, r) {
  const flag = unknownPrices(r.answer).join(" ");
  await db.prepare(
    "INSERT INTO chat_log (sid, lang, page, country, question, answer, failed, price_flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
  ).bind(r.sid, r.lang, r.page, r.country, r.question, r.answer, r.failed ? 1 : 0, flag).run();
}

export async function sendChatDigest(env, sendEmail) {
  if (!env.DB) return;
  await env.DB.prepare(`DELETE FROM chat_log WHERE ts < datetime('now', '-${KEEP_DAYS} days')`).run();
  const { results = [] } = await env.DB.prepare(
    "SELECT * FROM chat_log WHERE ts >= datetime('now', '-1 day') ORDER BY sid, id"
  ).all();
  if (!results.length || !env.RESEND_API_KEY) return; // quiet day: no email

  const convs = new Map();
  for (const row of results) {
    const k = row.sid || "row" + row.id;
    if (!convs.has(k)) convs.set(k, []);
    convs.get(k).push(row);
  }
  const flagged = results.filter((r) => r.price_flag).length;
  const failed = results.filter((r) => r.failed).length;

  const parts = [
    `Resumen del chat del sitio, últimas 24 horas.`,
    `${convs.size} conversaciones, ${results.length} preguntas.` +
      (flagged ? ` ${flagged} respuesta(s) mencionan un precio que no está publicado: revísalas.` : "") +
      (failed ? ` ${failed} vez/veces la IA no respondió y salió el mensaje de respaldo.` : ""),
    "",
  ];
  let n = 0;
  for (const rows of convs.values()) {
    const f = rows[0];
    parts.push(`=== Conversación ${++n} · ${f.lang.toUpperCase()} · ${f.country || "?"} · ${f.page || "?"} · ${f.ts} UTC`);
    for (const r of rows) {
      parts.push(`Visitante: ${r.question}`);
      parts.push(`IA: ${r.answer}`);
      if (r.price_flag) parts.push(`  >> PRECIO NO PUBLICADO: ${r.price_flag}`);
      if (r.failed) parts.push(`  >> la IA falló, se envió el mensaje de respaldo`);
      parts.push("");
    }
  }
  const subject = `[Chat IA] ${convs.size} conversación(es) en 24 h` + (flagged ? ` · ${flagged} con precio dudoso` : "");
  await sendEmail(env, { to: env.OWNER_EMAIL, subject, text: parts.join("\n").slice(0, 90000) });
}
