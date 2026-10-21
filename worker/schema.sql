-- AAA Impressions chat log (Cloudflare D1). Run once:
--   npx wrangler d1 execute aaa-chat --remote --file=schema.sql
CREATE TABLE IF NOT EXISTS chat_log (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  ts         TEXT    NOT NULL DEFAULT (datetime('now')),
  sid        TEXT    NOT NULL DEFAULT '',   -- random id per browser tab, no personal data
  lang       TEXT    NOT NULL DEFAULT 'en',
  page       TEXT    NOT NULL DEFAULT '',
  country    TEXT    NOT NULL DEFAULT '',
  question   TEXT    NOT NULL,
  answer     TEXT    NOT NULL,
  failed     INTEGER NOT NULL DEFAULT 0,    -- 1 = AI error, visitor got the fallback message
  price_flag TEXT    NOT NULL DEFAULT ''    -- dollar amounts in the answer that are not in offer.json
);
CREATE INDEX IF NOT EXISTS chat_log_ts ON chat_log (ts);
