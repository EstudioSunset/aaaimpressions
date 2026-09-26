# Plan — Página hub "Advertising Agency Treasure Coast"

Rama: `content/advertising-hub` (ya creada)
Estado: **ningún archivo creado ni editado todavía.** Este documento es para revisión.
No se agrega a git.

---

## 1. Cómo está construido el sitio (verificado)

| Tema | Hallazgo |
|---|---|
| Motor | Eleventy (11ty), Nunjucks `.njk`, un archivo plano por página → `/en/services/<archivo>/` |
| Layout / idioma | Los inyecta `src/en/en.json` + `src/es/es.json`. Las páginas solo llevan front matter + cuerpo. |
| Campos de front matter | `title`, `metaDescription`, `hreflangEs`, `hreflangEn`, `schema: "service"`, `schemaServiceName` |
| Canonical | Autorreferencial automático en `base.njk` (`site.baseUrl + page.url`). **No hay que agregar nada.** |
| hreflang | `base.njk` emite `es`, `en` y `x-default` (= EN) a partir de los dos campos de front matter. Recíproco automáticamente cuando existan los dos archivos. |
| Sitemap | **Manual** — `src/sitemap.njk`. Las dos URLs nuevas se agregan a mano (patrón: un `<url>` por idioma, cada uno lista los dos `xhtml:link` alternates). |
| Componente de FAQ | No existe. Las páginas de servicio usan acordeones `<details>` en línea. Se copia ese markup exacto. |
| Bloque CTA | Patrón en línea: panel oscuro `rounded-3xl`, botones WhatsApp + `tel:`, lista "Related services" al lado. |
| Página de materiales impresos en EN | **Existe**: `/en/services/print-materials-treasure-coast/` — el bloque de sub-servicio 3 enlaza ahí, sin problema de "solo ES". |
| CSS | No se toca — todas las clases utilitarias y variables CSS ya existen. |

No se detectaron conflictos. Las únicas ediciones de arquitectura son: 2 archivos nuevos + 2 entradas de sitemap + enlaces internos de una línea.

---

## 2. Los dos archivos nuevos

### 2.1 `src/en/services/advertising-agency-treasure-coast.njk`

Front matter:

```yaml
---
title: "Advertising Agency Treasure Coast, FL | AAA Impressions"
metaDescription: "Local advertising agency serving Vero Beach, Fort Pierce, Port St. Lucie & Stuart. Google Ads, Meta Ads and print advertising for small businesses."
hreflangEs: "/es/servicios/agencia-de-publicidad-treasure-coast/"
hreflangEn: "/en/services/advertising-agency-treasure-coast/"
schema: "service"
schemaServiceName: "Advertising Agency for Local Businesses"
---
```

- Title = 54 caracteres ✓ (< 60)
- Meta = 148 caracteres ✓ (< 155)

### 2.2 `src/es/servicios/agencia-de-publicidad-treasure-coast.njk`

Se construye **solo después de aprobar la redacción EN**. Front matter previsto:

```yaml
---
title: "Agencia de Publicidad Treasure Coast | AAA Impressions"
metaDescription: "Agencia de publicidad local para Vero Beach, Fort Pierce, Port St. Lucie y Stuart. Google Ads, Meta Ads y publicidad impresa para negocios pequeños."
hreflangEs: "/es/servicios/agencia-de-publicidad-treasure-coast/"
hreflangEn: "/en/services/advertising-agency-treasure-coast/"
schema: "service"
schemaServiceName: "Agencia de Publicidad para Negocios Locales"
---
```

- Title ES = 53 caracteres ✓
- Meta ES = traducción idiomática (pendiente de ajuste fino al redactar el ES)

Estructura del cuerpo para ambos (idéntica a las páginas de servicio existentes):
breadcrumb → hero (H1 + intro + botón WhatsApp) → sección principal (intro / sub-servicios / por ciudad / por qué local / cita / CTA oscuro + lista relacionada) → sección FAQ con acordeones.

---

## 3. Borrador EN completo (~1.140 palabras)

### 3.1 Versión de lectura (para revisar redacción)

#### Hero

**H1:** Advertising agency for local businesses on the Treasure Coast

**Intro del hero:** We're an advertising agency for small businesses on the Treasure Coast — Vero Beach, Fort Pierce, Port St. Lucie, and Stuart. We plan and run the advertising that actually brings you customers: Google, Facebook and Instagram, and printed materials people can hold in their hand.

*[Botón WhatsApp — "Free WhatsApp consult →", igual que las demás páginas de servicio]*

#### Intro (etiqueta de sección: "Advertising · Treasure Coast")

Most people looking for an **ad agency near me** don't want a national firm with account managers who rotate every quarter. They want someone local who picks up the phone, knows the Treasure Coast, and treats a $600 monthly budget with the same care as a $6,000 one. That's what we do — you talk directly to the person building and managing your campaigns. No layers, no middlemen.

Advertising for a local business is not only digital. A well-run Google Ads campaign brings people who are searching right now; a Facebook ad reaches people before they search; and a stack of well-designed business cards or a banner at a community event keeps your name in front of people in the real world. A real **advertising company** treats all of it as one plan, not separate silos.

We work with restaurants, contractors, clinics, salons, retailers, and independent professionals across Vero Beach, Fort Pierce, Port St. Lucie, and Stuart. Whether you need paid ads, print, or a mix, we start by figuring out where your next ten customers are most likely to come from — then we spend your budget there.

#### Sección: What advertising for a local business includes

*(4 tarjetas, cada una H3 + 2–3 oraciones + enlace)*

- **Advertising on Google** — For people who are already searching for what you sell. High intent, ready to act. We build and manage the campaign, the keywords, and the tracking. → enlaza a `/en/services/google-ads-treasure-coast/`
- **Advertising on Facebook & Instagram** — For people who fit your ideal customer but haven't searched yet. Meta ads build awareness and demand in your specific cities and ZIP codes. → enlaza a `/en/services/facebook-instagram-ads-treasure-coast/`
- **Local advertising & printed materials** — Business cards, flyers, banners, door hangers, and promotional items — designed to match your digital ads so everything looks like one brand. → enlaza a `/en/services/print-materials-treasure-coast/`
- **Showing up on the map** — Your Google Business Profile is the free listing that appears in Maps and the local pack. We optimize it and keep it active. → enlaza a `/en/services/google-business-profile-treasure-coast/`

#### Sección: Advertising by city

**Vero Beach** *(más largo)* — Advertising in Vero Beach means reaching a market with money to spend and high expectations for how a business presents itself. Indian River County shoppers compare carefully before they call, so an **advertising company** here has to make you look as established as the national brands you're up against — clean creative, consistent messaging across Google and social, and print that matches. We help Vero Beach boutiques, restaurants, medical practices, and home-service businesses run advertising that looks the part and brings in the right customer.

**Fort Pierce** *(más largo)* — As an **advertising agency in Fort Pierce**, we focus on **local advertising** and **digital advertising** that works for St. Lucie County's mix of waterfront businesses, trades, food, and community services. Fort Pierce customers respond to businesses that feel part of the neighborhood, so we combine Google and Meta campaigns targeted tightly to the area with printed materials for markets, festivals, and route work. This is the city where our organic search visibility is already strongest, and paid advertising builds on top of that.

**Port St. Lucie** — Port St. Lucie is the largest and fastest-growing city on the Treasure Coast, and an **advertising agency** here has to keep up with new neighborhoods and new competitors every year. We run **local advertising** — Google Ads, Meta Ads, and print — for Port St. Lucie service businesses that want to grow as fast as the city does.

**Stuart** — We also cover Stuart and Martin County. If your business is in Stuart, the same services apply — reach out and we'll put together an advertising plan for your area.

#### Sección: Why a local advertising agency instead of a national one

A national agency treats you as one line in a spreadsheet. Your campaign gets a template, your questions go to a queue, and nobody on the team has driven down US-1. A local advertising agency knows which events are worth a booth, which neighborhoods to target by ZIP code, and how a Vero Beach customer reads an ad differently from a Fort Pierce one.

It also means you can actually reach us. When **advertising services online** are sold as a self-serve dashboard, the **small business internet advertising** customer is usually left to figure out targeting, budgets, and reporting alone. We handle all of it and explain the numbers in plain language — how many people saw the ad, how many contacted you, and what each one cost.

We're a small team, so we take on a limited number of clients and stay with them. You get senior attention on a small-business budget, in English or Spanish.

#### Bloque de cita

"Advertising works when every piece points the same direction — the Google ad, the Facebook post, and the flyer all say the same thing to the same person. That consistency is what a local agency can hold together and a national one usually can't." — AAA Impressions

#### CTA oscuro

**Want an advertising plan for your business?** Tell us about your business and what you're trying to grow. We'll put together a plan — no cost, no commitment.
*[Botón WhatsApp + Botón Call]* · Lista Related services: Google Ads · Meta Ads · Print Materials · Google Business Profile

#### FAQ (4 acordeones)

1. **How much does it cost to hire an advertising agency for a small business?** — For most Treasure Coast small businesses, management fees plus a working ad budget start in the range of a few hundred dollars a month and scale with what you put behind the ads. Print projects are quoted separately. We give you a clear breakdown of what goes to management and what goes to the platforms before you commit — and we work month to month, no long-term contract.
2. **What's the difference between advertising on Google and on Facebook?** — Google advertising reaches people who are already searching for what you sell — high intent, ready to act. Facebook and Instagram advertising reaches people who fit your ideal customer but aren't searching yet — it builds awareness. Most local businesses do best with a mix; our Google Ads and Meta Ads pages go into detail.
3. **Do you do print advertising as well as digital?** — Yes. Business cards, flyers, banners, door hangers, and promotional materials are part of what we offer, designed to match your digital advertising so everything looks like one brand.
4. **Do you work with businesses in my city?** — We work with businesses in Vero Beach, Fort Pierce, Port St. Lucie, Stuart, and the surrounding Treasure Coast. If you're just outside that area, ask — we can usually help.

### 3.2 Archivo `.njk` completo (listo para colocar tras aprobación)

```njk
---
title: "Advertising Agency Treasure Coast, FL | AAA Impressions"
metaDescription: "Local advertising agency serving Vero Beach, Fort Pierce, Port St. Lucie & Stuart. Google Ads, Meta Ads and print advertising for small businesses."
hreflangEs: "/es/servicios/agencia-de-publicidad-treasure-coast/"
hreflangEn: "/en/services/advertising-agency-treasure-coast/"
schema: "service"
schemaServiceName: "Advertising Agency for Local Businesses"
---

<nav class="breadcrumb pt-24 pb-4 bg-white border-b border-gray-100">
  <div class="mx-auto max-w-6xl px-5">
    <ol class="flex items-center gap-2 text-xs text-gray-400">
      <li><a href="/en/" class="hover:underline">Home</a></li>
      <li>/</li>
      <li><a href="/en/services/" class="hover:underline">Services</a></li>
      <li>/</li>
      <li class="text-gray-600 font-medium">Advertising Agency</li>
    </ol>
  </div>
</nav>

<section class="py-16 lg:py-24" style="background:var(--surf)">
  <div class="mx-auto max-w-6xl px-5">
    <div class="max-w-3xl">
      <span class="accent-line"></span>
      <p class="text-xs font-semibold tracking-[0.18em] uppercase text-gray-400 mb-4">Advertising · Treasure Coast</p>
      <h1 class="text-4xl sm:text-5xl mb-6 leading-tight">Advertising agency for <span style="color:var(--primary)">local businesses</span> on the Treasure Coast</h1>
      <p class="text-xl text-gray-500 leading-relaxed mb-8">We're an advertising agency for small businesses on the Treasure Coast — Vero Beach, Fort Pierce, Port St. Lucie, and Stuart. We plan and run the advertising that actually brings you customers: Google, Facebook and Instagram, and printed materials people can hold in their hand.</p>
      <a href="{{ site.whatsapp }}?text=Hello%2C%20I%27m%20interested%20in%20advertising%20for%20my%20business%20on%20the%20Treasure%20Coast."
         target="_blank" rel="noopener noreferrer"
         class="inline-flex items-center gap-2 rounded-xl px-7 py-3.5 text-sm font-semibold text-white hover:opacity-90 transition-opacity"
         style="background:var(--whatsapp)">
        Free WhatsApp consult →
      </a>
    </div>
  </div>
</section>

<section class="py-20 lg:py-28 bg-white">
  <div class="mx-auto max-w-6xl px-5">

    <div class="max-w-3xl mb-20">
      <p class="text-gray-500 leading-relaxed mb-5">Most people looking for an <strong>ad agency near me</strong> don't want a national firm with account managers who rotate every quarter. They want someone local who picks up the phone, knows the Treasure Coast, and treats a $600 monthly budget with the same care as a $6,000 one. That's what we do — you talk directly to the person building and managing your campaigns. No layers, no middlemen.</p>
      <p class="text-gray-500 leading-relaxed mb-5">Advertising for a local business is not only digital. A well-run Google Ads campaign brings people who are searching right now; a Facebook ad reaches people before they search; and a stack of well-designed business cards or a banner at a community event keeps your name in front of people in the real world. A real <strong>advertising company</strong> treats all of it as one plan, not separate silos.</p>
      <p class="text-gray-500 leading-relaxed">We work with restaurants, contractors, clinics, salons, retailers, and independent professionals across Vero Beach, Fort Pierce, Port St. Lucie, and Stuart. Whether you need paid ads, print, or a mix, we start by figuring out where your next ten customers are most likely to come from — then we spend your budget there.</p>
    </div>

    <p class="text-xs font-semibold tracking-widest uppercase text-gray-400 mb-10 text-center">What advertising for a local business includes</p>
    <div class="grid sm:grid-cols-2 gap-6 mb-20">
      <div class="service-card reveal rounded-2xl border border-gray-100 p-6 bg-white shadow-sm">
        <h3 class="font-semibold mb-2">Advertising on Google</h3>
        <p class="text-sm text-gray-400 leading-relaxed mb-3">For people who are already searching for what you sell — high intent, ready to act. We build and manage the campaign, the keywords, and the conversion tracking so you know what each lead costs.</p>
        <a href="/en/services/google-ads-treasure-coast/" class="text-xs font-semibold hover:underline" style="color:var(--primary)">Google Ads service →</a>
      </div>
      <div class="service-card reveal rounded-2xl border border-gray-100 p-6 bg-white shadow-sm" style="transition-delay:.05s">
        <h3 class="font-semibold mb-2">Advertising on Facebook &amp; Instagram</h3>
        <p class="text-sm text-gray-400 leading-relaxed mb-3">For people who fit your ideal customer but haven't searched yet. Meta ads build awareness and demand in your specific cities and ZIP codes, starting with a small budget.</p>
        <a href="/en/services/facebook-instagram-ads-treasure-coast/" class="text-xs font-semibold hover:underline" style="color:var(--primary)">Meta Ads service →</a>
      </div>
      <div class="service-card reveal rounded-2xl border border-gray-100 p-6 bg-white shadow-sm" style="transition-delay:.10s">
        <h3 class="font-semibold mb-2">Local advertising &amp; printed materials</h3>
        <p class="text-sm text-gray-400 leading-relaxed mb-3">Business cards, flyers, banners, door hangers, and promotional items — designed to match your digital ads so everything looks like one brand in a customer's hands and on their screen.</p>
        <a href="/en/services/print-materials-treasure-coast/" class="text-xs font-semibold hover:underline" style="color:var(--primary)">Print materials service →</a>
      </div>
      <div class="service-card reveal rounded-2xl border border-gray-100 p-6 bg-white shadow-sm" style="transition-delay:.15s">
        <h3 class="font-semibold mb-2">Showing up on the map</h3>
        <p class="text-sm text-gray-400 leading-relaxed mb-3">Your Google Business Profile is the free listing that appears in Maps and the local pack when someone searches nearby. We optimize it, manage reviews, and keep it active.</p>
        <a href="/en/services/google-business-profile-treasure-coast/" class="text-xs font-semibold hover:underline" style="color:var(--primary)">Google Business Profile service →</a>
      </div>
    </div>

    <p class="text-xs font-semibold tracking-widest uppercase text-gray-400 mb-10 text-center">Advertising by city</p>
    <div class="grid lg:grid-cols-2 gap-6 mb-20">
      <div class="rounded-2xl border border-gray-100 p-6 bg-white">
        <h3 class="font-semibold text-gray-900 mb-2">Vero Beach</h3>
        <p class="text-sm text-gray-500 leading-relaxed">Advertising in Vero Beach means reaching a market with money to spend and high expectations for how a business presents itself. Indian River County shoppers compare carefully before they call, so an advertising company here has to make you look as established as the national brands you're up against — clean creative, consistent messaging across Google and social, and print that matches. We help Vero Beach boutiques, restaurants, medical practices, and home-service businesses run advertising that looks the part and brings in the right customer.</p>
      </div>
      <div class="rounded-2xl border border-gray-100 p-6 bg-white">
        <h3 class="font-semibold text-gray-900 mb-2">Fort Pierce</h3>
        <p class="text-sm text-gray-500 leading-relaxed">As an advertising agency in Fort Pierce, we focus on local advertising and digital advertising that works for St. Lucie County's mix of waterfront businesses, trades, food, and community services. Fort Pierce customers respond to businesses that feel part of the neighborhood, so we combine Google and Meta campaigns targeted tightly to the area with printed materials for markets, festivals, and route work. This is the city where our organic search visibility is already strongest, and paid advertising builds on top of that.</p>
      </div>
      <div class="rounded-2xl border border-gray-100 p-6 bg-white">
        <h3 class="font-semibold text-gray-900 mb-2">Port St. Lucie</h3>
        <p class="text-sm text-gray-500 leading-relaxed">Port St. Lucie is the largest and fastest-growing city on the Treasure Coast, and an advertising agency here has to keep up with new neighborhoods and new competitors every year. We run local advertising — Google Ads, Meta Ads, and print — for Port St. Lucie service businesses that want to grow as fast as the city does.</p>
      </div>
      <div class="rounded-2xl border border-gray-100 p-6 bg-white">
        <h3 class="font-semibold text-gray-900 mb-2">Stuart</h3>
        <p class="text-sm text-gray-500 leading-relaxed">We also cover Stuart and Martin County. If your business is in Stuart, the same services apply — reach out and we'll put together an advertising plan for your area.</p>
      </div>
    </div>

    <div class="grid lg:grid-cols-3 gap-10 mb-20">
      <div class="lg:col-span-2">
        <p class="text-xs font-semibold tracking-widest uppercase text-gray-400 mb-6">Why a local advertising agency instead of a national one</p>
        <p class="text-gray-500 leading-relaxed mb-5">A national agency treats you as one line in a spreadsheet. Your campaign gets a template, your questions go to a queue, and nobody on the team has driven down US-1. A local advertising agency knows which events are worth a booth, which neighborhoods to target by ZIP code, and how a Vero Beach customer reads an ad differently from a Fort Pierce one.</p>
        <p class="text-gray-500 leading-relaxed mb-5">It also means you can actually reach us. When advertising services online are sold as a self-serve dashboard, the small business internet advertising customer is usually left to figure out targeting, budgets, and reporting alone. We handle all of it and explain the numbers in plain language — how many people saw the ad, how many contacted you, and what each one cost.</p>
        <p class="text-gray-500 leading-relaxed">We're a small team, so we take on a limited number of clients and stay with them. You get senior attention on a small-business budget, in English or Spanish.</p>
      </div>
      <div>
        <p class="text-xs font-semibold tracking-widest uppercase text-gray-400 mb-5">Related services</p>
        <ul class="space-y-3">
          <li><a href="/en/services/google-ads-treasure-coast/" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition"><span style="color:var(--primary)">→</span> Google Ads</a></li>
          <li><a href="/en/services/facebook-instagram-ads-treasure-coast/" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition"><span style="color:var(--primary)">→</span> Meta Ads</a></li>
          <li><a href="/en/services/print-materials-treasure-coast/" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition"><span style="color:var(--primary)">→</span> Print Materials</a></li>
          <li><a href="/en/services/google-business-profile-treasure-coast/" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition"><span style="color:var(--primary)">→</span> Google Business Profile</a></li>
        </ul>
      </div>
    </div>

    <div class="rounded-3xl p-8 sm:p-12 mb-20 border-l-4" style="background:var(--primary-lt);border-color:var(--primary)">
      <p class="text-lg italic text-gray-600 mb-4">"Advertising works when every piece points the same direction — the Google ad, the Facebook post, and the flyer all say the same thing to the same person. That consistency is what a local agency can hold together and a national one usually can't."</p>
      <p class="text-xs font-semibold" style="color:var(--primary)">— AAA Impressions</p>
    </div>

    <div class="rounded-3xl p-8 sm:p-10" style="background:var(--dark)">
      <h2 class="text-2xl text-white mb-3">Want an advertising plan for your business?</h2>
      <p class="text-gray-400 text-sm mb-6 max-w-xl">Tell us about your business and what you're trying to grow. We'll put together a plan — no cost, no commitment.</p>
      <div class="flex flex-col sm:flex-row gap-3">
        <a href="{{ site.whatsapp }}?text=Hello%2C%20I%27d%20like%20an%20advertising%20plan%20for%20my%20Treasure%20Coast%20business."
           target="_blank" rel="noopener noreferrer"
           class="inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white hover:opacity-90 transition-opacity"
           style="background:var(--whatsapp)">
          Free WhatsApp consult →
        </a>
        <a href="tel:{{ site.phoneRaw }}" class="inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold border border-gray-600 text-gray-300 hover:border-gray-400 transition">
          Call: {{ site.phone }}
        </a>
      </div>
    </div>

  </div>
</section>

<!-- FAQ -->
<section class="py-20 lg:py-24" style="background:var(--surf)">
  <div class="mx-auto max-w-3xl px-5">
    <div class="text-center mb-12 reveal">
      <span class="accent-line mx-auto"></span>
      <h2 class="text-3xl">Frequently asked questions about advertising</h2>
    </div>
    <div class="space-y-4 reveal">

      <details class="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        <summary class="flex items-center justify-between cursor-pointer px-7 py-5 font-semibold text-gray-800 hover:text-blue-600 transition list-none">
          How much does it cost to hire an advertising agency for a small business?
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"/></svg>
        </summary>
        <div class="px-7 pb-6 text-sm text-gray-500 leading-relaxed">
          For most Treasure Coast small businesses, management fees plus a working ad budget start in the range of a few hundred dollars a month and scale with what you put behind the ads. Print projects are quoted separately. We give you a clear breakdown of what goes to management and what goes to the platforms before you commit — and we work month to month, with no long-term contract.
        </div>
      </details>

      <details class="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        <summary class="flex items-center justify-between cursor-pointer px-7 py-5 font-semibold text-gray-800 hover:text-blue-600 transition list-none">
          What is the difference between advertising on Google and on Facebook?
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"/></svg>
        </summary>
        <div class="px-7 pb-6 text-sm text-gray-500 leading-relaxed">
          Google advertising reaches people who are already searching for what you sell — high intent, ready to act. <a href="/en/services/facebook-instagram-ads-treasure-coast/" class="font-medium hover:underline" style="color:var(--primary)">Facebook and Instagram advertising</a> reaches people who fit your ideal customer but aren't searching yet — it builds awareness and demand. Most local businesses do best with a mix. Our <a href="/en/services/google-ads-treasure-coast/" class="font-medium hover:underline" style="color:var(--primary)">Google Ads</a> and Meta Ads pages go into detail on each.
        </div>
      </details>

      <details class="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        <summary class="flex items-center justify-between cursor-pointer px-7 py-5 font-semibold text-gray-800 hover:text-blue-600 transition list-none">
          Do you do print advertising as well as digital?
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"/></svg>
        </summary>
        <div class="px-7 pb-6 text-sm text-gray-500 leading-relaxed">
          Yes. Business cards, flyers, banners, door hangers, and promotional materials are part of what we offer, designed to match your digital advertising so everything looks like one brand. See our <a href="/en/services/print-materials-treasure-coast/" class="font-medium hover:underline" style="color:var(--primary)">print materials</a> page.
        </div>
      </details>

      <details class="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        <summary class="flex items-center justify-between cursor-pointer px-7 py-5 font-semibold text-gray-800 hover:text-blue-600 transition list-none">
          Do you work with businesses in my city?
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"/></svg>
        </summary>
        <div class="px-7 pb-6 text-sm text-gray-500 leading-relaxed">
          We work with businesses in Vero Beach, Fort Pierce, Port St. Lucie, Stuart, and the surrounding Treasure Coast. If you're just outside that area, ask — we can usually help.
        </div>
      </details>

    </div>

    <div class="mt-10 p-6 rounded-2xl border-l-4 reveal" style="background:var(--primary-lt);border-color:var(--primary)">
      <p class="text-sm text-gray-600 leading-relaxed">See all our <a href="/en/services/" class="font-semibold hover:underline" style="color:var(--primary)">digital marketing services</a> or review our <a href="/en/packages/" class="font-semibold hover:underline" style="color:var(--primary)">packages</a>.</p>
    </div>
  </div>
</section>
```

Conteo aproximado de palabras del cuerpo visible: ~1.140 (dentro del rango 800–1.200).

---

## 4. Archivos existentes que se tocan para enlaces internos (una línea cada uno)

| # | Archivo | Edición |
|---|---|---|
| 1 | `src/en/services/index.njk` | Nueva tarjeta `<a>` de servicio en la grilla de servicios (misma estructura que la tarjeta "Print Materials"), etiqueta de categoría "Paid advertising" + `Advertising Agency`. Además una chip en "Related local pages". |
| 2 | `src/es/servicios/index.njk` | Misma tarjeta + chip, en español (`Agencia de Publicidad`). |
| 3 | `src/_includes/footer.njk` | Un `<li>` en la columna Services — rama EN (`Advertising Agency`) y rama ES (`Agencia de Publicidad`). |
| 4 | `src/en/locations/digital-marketing-vero-beach.njk` | Una chip en "More services in Vero Beach": `Advertising agency for Vero Beach businesses →` |
| 5 | `src/en/locations/digital-marketing-fort-pierce.njk` | Una chip en "More services in Fort Pierce". |
| 6 | `src/en/locations/digital-marketing-port-st-lucie.njk` | Una chip (prioridad secundaria). |
| 7 | `src/en/locations/digital-marketing-stuart.njk` | Una chip (prioridad secundaria). |
| 8 | `src/es/ubicaciones/marketing-digital-vero-beach.njk` | Chip equivalente en "Más servicios en Vero Beach". |
| 9 | `src/es/ubicaciones/marketing-digital-fort-pierce.njk` | Chip equivalente en "Más servicios en Fort Pierce". |
| 10 | `src/es/ubicaciones/marketing-digital-port-st-lucie.njk` | Chip equivalente (prioridad secundaria). |
| 11 | `src/es/ubicaciones/marketing-digital-stuart.njk` | Chip equivalente (prioridad secundaria). |
| 12 | `src/en/services/google-ads-treasure-coast.njk` | Un `<li>` en "Related services": `→ Advertising Agency`. |
| 13 | `src/en/services/facebook-instagram-ads-treasure-coast.njk` | Un `<li>` en "Related services": `→ Advertising Agency`. |
| 14 | `src/es/servicios/google-ads-treasure-coast.njk` | Un `<li>` en "Servicios relacionados": `→ Agencia de Publicidad`. |
| 15 | `src/es/servicios/publicidad-facebook-instagram-treasure-coast.njk` | Un `<li>` en "Servicios relacionados": `→ Agencia de Publicidad`. |
| 16 | `src/sitemap.njk` | Agregar los dos bloques `<url>` (EN + ES) en la sección SERVICIOS / SERVICES, `priority` 0.85, cada uno con los dos `xhtml:link` alternates — igual que el patrón existente. |

Resultado: **enlaces entrantes desde 8+ páginas existentes** (índice de servicios ×2, footer, 4 páginas de ubicación EN, Google Ads, Meta Ads) — por encima del mínimo de seis.

### Snippets propuestos

**Índice de servicios EN — nueva tarjeta** (después de la tarjeta de Google Ads):

```njk
      <a href="/en/services/advertising-agency-treasure-coast/" class="service-card reveal rounded-2xl bg-white border border-gray-100 p-7 shadow-sm hover:no-underline sm:flex gap-6 items-start" style="transition-delay:.10s">
        <div class="service-thumb flex-shrink-0 mb-5 sm:mb-0">
          <img src="/assets/img/services-google-ads.webp" alt="Advertising campaigns across Google, Meta and print for a local business" width="800" height="600" loading="lazy" decoding="async">
        </div>
        <div class="flex-1">
          <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color:var(--accent)">Paid advertising</p>
          <h3 class="text-lg font-semibold mb-2 text-gray-900">Advertising Agency</h3>
          <p class="text-sm text-gray-400 leading-relaxed">The umbrella over paid digital ads, local advertising, and printed materials. If you want one team planning your Google Ads, your Facebook and Instagram ads, and your print — all pointing the same direction — this is where to start.</p>
          <p class="mt-3 text-xs font-semibold" style="color:var(--primary)">View advertising agency service →</p>
        </div>
      </a>
```

*(Nota: reutiliza la imagen `services-google-ads.webp` existente para no agregar assets ni tocar `/assets`. Si se prefiere una imagen propia, hay que crearla aparte — reportar.)*

**Footer EN — nuevo `<li>`** (en la lista de la columna Services):

```njk
            <li><a class="text-gray-500 hover:text-white transition" href="/en/services/advertising-agency-treasure-coast/">Advertising Agency</a></li>
```

**Footer ES — nuevo `<li>`**:

```njk
            <li><a class="text-gray-500 hover:text-white transition" href="/es/servicios/agencia-de-publicidad-treasure-coast/">Agencia de Publicidad</a></li>
```

**Página de ubicación EN (Vero Beach / Fort Pierce / PSL / Stuart) — nueva chip** en el bloque "More services in …":

```njk
        <a href="/en/services/advertising-agency-treasure-coast/" class="inline-flex items-center gap-2 rounded-full border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-600 hover:border-gray-300 hover:text-gray-900 transition">Advertising agency for CIUDAD businesses →</a>
```

**Página de ubicación ES — nueva chip** en "Más servicios en …":

```njk
        <a href="/es/servicios/agencia-de-publicidad-treasure-coast/" class="inline-flex items-center gap-2 rounded-full border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-600 hover:border-gray-300 hover:text-gray-900 transition">Agencia de publicidad para negocios en CIUDAD →</a>
```

**Google Ads EN + Meta Ads EN — nuevo `<li>`** en "Related services":

```njk
          <li><a href="/en/services/advertising-agency-treasure-coast/" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition"><span style="color:var(--primary)">→</span> Advertising Agency</a></li>
```

**Google Ads ES + Meta Ads ES — nuevo `<li>`** en "Servicios relacionados":

```njk
          <li><a href="/es/servicios/agencia-de-publicidad-treasure-coast/" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition"><span style="color:var(--primary)">→</span> Agencia de Publicidad</a></li>
```

**`src/sitemap.njk` — dos bloques nuevos** (en la sección SERVICIOS / SERVICES):

```njk
  <url>
    <loc>{{ site.baseUrl }}/es/servicios/agencia-de-publicidad-treasure-coast/</loc>
    <xhtml:link rel="alternate" hreflang="es" href="{{ site.baseUrl }}/es/servicios/agencia-de-publicidad-treasure-coast/"/>
    <xhtml:link rel="alternate" hreflang="en" href="{{ site.baseUrl }}/en/services/advertising-agency-treasure-coast/"/>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>
  <url>
    <loc>{{ site.baseUrl }}/en/services/advertising-agency-treasure-coast/</loc>
    <xhtml:link rel="alternate" hreflang="es" href="{{ site.baseUrl }}/es/servicios/agencia-de-publicidad-treasure-coast/"/>
    <xhtml:link rel="alternate" hreflang="en" href="{{ site.baseUrl }}/en/services/advertising-agency-treasure-coast/"/>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>
```

---

## 5. hreflang / sitemap / canonical — estado final

- **Canonical**: automático, autorreferencial en las dos páginas nuevas. Nada agregado a páginas existentes.
- **hreflang**: cada página nueva obtiene `es` + `en` + `x-default` (→ EN) desde el front matter. Recíproco porque los dos archivos se apuntan mutuamente. No se toca el hreflang de ninguna página existente.
- **Sitemap**: dos entradas `<url>` nuevas, cada una con alternates `hreflang="es"` y `hreflang="en"`, igual que cualquier otro par de servicio.

---

## 6. Preguntas abiertas antes de proceder

1. **Bloque de sub-servicio "Showing up on the map"** — incluí un 4º bloque para Google Business Profile. El brief lo lista como opcional (bloque 4). ¿Se mantiene o se dejan 3 bloques?
2. **Enlaces en páginas de ubicación** — el brief prioriza Vero Beach + Fort Pierce y marca PSL/Stuart como opcionales. Propongo agregar las cuatro EN + las cuatro ES por consistencia (sigue siendo una chip cada una). ¿OK, o solo Vero Beach + Fort Pierce?
3. **Imagen de la tarjeta en el índice de servicios** — propongo reutilizar `services-google-ads.webp` para no agregar assets. ¿OK, o se quiere una imagen propia (`services-advertising.webp`) que habría que crear y colocar en `assets/img/`?
4. **`schemaServiceName`** — usé `"Advertising Agency for Local Businesses"`. ¿Bien?

---

## 7. Flujo restante (tras aprobar la redacción EN)

1. Crear `src/en/services/advertising-agency-treasure-coast.njk` con el contenido de §3.2.
2. Crear `src/es/servicios/agencia-de-publicidad-treasure-coast.njk` (traducción idiomática, misma estructura).
3. Aplicar los 16 enlaces internos de §4.
4. Agregar las dos URLs al `src/sitemap.njk`.
5. `npm run build` (o el script equivalente) — verificar 0 errores.
6. Verificar y reportar: las dos páginas en el output, sitemap con las dos URLs, hreflang recíproco, ningún archivo existente modificado más allá de los enlaces aprobados.
7. Todo queda en la rama `content/advertising-hub` — sin push ni merge.
