# Respuesta automática con IA — cómo activarla

El código está en `worker/`. Es un Cloudflare Worker que hace esto:

1. Recibe el formulario de contacto.
2. Revisa que no sea spam.
3. Manda al visitante a la página de gracias de inmediato.
4. En segundo plano, Claude redacta una respuesta en el idioma del visitante y se la envía por correo.
5. Te llega a ti un correo con el resumen y la prioridad: `[ALTA] Nuevo lead: …`.

Si Claude falla, se envía una respuesta estándar y a ti igual te llega el aviso.

## Costo

| Pieza | Opción gratis | Si crece la demanda |
|---|---|---|
| Servidor (Cloudflare Workers) | Gratis: 100,000 solicitudes al día | Plan de $5/mes |
| IA que redacta | **Workers AI de Cloudflare**: cuota diaria gratis, sin cuenta extra | **Claude (API)**: cuesta menos de 1 centavo por respuesta y escribe mejor en español |
| Envío de correos (Resend) | Gratis: 3,000 al mes | Desde $20/mes |
| Anti-spam (Turnstile) | Gratis | — |

**Total para empezar: $0.** Si algún día quieres mejor redacción, solo agregas la clave de Claude (paso 1) y el Worker la usa automáticamente.

## 1. (Opcional) Clave de la API de Claude

Sáltate este paso para la versión gratis.

1. Entra a **console.anthropic.com**. Es una cuenta aparte de tu suscripción de Claude.
2. En **Billing** carga $5 de crédito, que alcanzan para cientos de respuestas.
3. En **API Keys** crea una clave y guárdala con `npx wrangler secret put ANTHROPIC_API_KEY`.

## 2. Servicio de correo: Resend (≈ 15 min)

1. Crea una cuenta gratis en **resend.com** (3,000 correos al mes sin costo).
2. Ve a **Domains → Add domain → `aaaimpressions.com`**. Si te ofrece conectarse con Cloudflare, acepta: agrega los registros DNS solo. Si no, copia los registros (SPF, DKIM) en Cloudflare → DNS.
3. Espera a que el dominio aparezca como **Verified** y crea una **API key**.

Los correos salen desde `hola@aaaimpressions.com`. Cuando el cliente responde, la respuesta llega a tu Gmail.

## 3. Anti-spam: Turnstile de Cloudflare (≈ 5 min, gratis)

1. En Cloudflare entra a **Turnstile → Add site**, usa el dominio `aaaimpressions.com` y elige el modo **Managed**.
2. Copia la **Site Key** (pública) y la **Secret Key**.

## 4. Publicar el Worker

En una terminal, dentro de `D:\aaaimpressions\worker`:

```
npx wrangler login
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put TURNSTILE_SECRET
npx wrangler deploy
```

`wrangler deploy` crea `api.aaaimpressions.com` automáticamente, porque tu DNS ya está en Cloudflare. Para comprobar que funciona, abre `https://api.aaaimpressions.com/health`: debe decir `ok`.

## 5. Conectar el formulario

Pásame la **Site Key** de Turnstile y yo pongo esto en `src/_data/site.json`:

```
"contactEndpoint": "https://api.aaaimpressions.com/contact",
"turnstileSiteKey": "TU_SITE_KEY"
```

Mientras esos campos estén vacíos, el formulario sigue usando Web3Forms como hasta hoy.

## Reglas que sigue la IA (en `worker/src/index.js`)

- Responde en el idioma del cliente, en 90 a 160 palabras, y firma como "equipo de AAA Impressions". Al pie avisa que la respuesta se redactó con ayuda de IA.
- Solo menciona los precios "desde" publicados en el sitio. Nunca inventa precios, fechas, clientes ni garantías.
- No da consejos legales ni de cumplimiento normativo, y nunca dice "certificado".
- Trata el mensaje del cliente como datos, no como instrucciones, para evitar manipulaciones.
- Si detecta spam, no responde y te avisa con `[SPAM?]` en el asunto.
