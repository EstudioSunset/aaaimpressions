(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Year
  const y = $("#year");
  if (y) y.textContent = new Date().getFullYear();

  // Mobile nav
  const navToggle = $("[data-nav-toggle]");
  const navMenu = $("[data-nav-menu]");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      const open = navMenu.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
    });

    // Close on click
    $$(".nav-link", navMenu).forEach(a => {
      a.addEventListener("click", () => {
        navMenu.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        navToggle.setAttribute("aria-label", "Abrir menú");
      });
    });

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        navMenu.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        navToggle.setAttribute("aria-label", "Abrir menú");
      }
    });
  }

  // Modal quote
  const modal = $("[data-modal]");
  const openButtons = $$("[data-open-quote]");
  const closeButtons = $$("[data-close-quote]");
  let lastFocus = null;

  function openModal(productPrefill) {
    if (!modal) return;
    lastFocus = document.activeElement;

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    // Reset result state
    const form = $("#quoteForm");
    const res = $("#quoteResult");
    if (res) res.hidden = true;
    const qt = $("#quoteText");
    if (qt) qt.value = "";

    // Prefill product if available
    const productSel = $("#qProduct");
    if (productSel && productPrefill) {
      const options = Array.from(productSel.options).map(o => o.textContent);
      const match = options.find(o => o.toLowerCase().includes(String(productPrefill).toLowerCase()));
      if (match) productSel.value = match;
      else {
        // If exact not found, try to set "Otro" and add into notes
        productSel.value = "Otro";
        const notes = $("#qNotes");
        if (notes) notes.value = `Producto de interés: ${productPrefill}\n` + (notes.value || "");
      }
    }

    // Focus first input
    setTimeout(() => {
      const first = $("#qName");
      if (first) first.focus();
    }, 10);
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";

    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  openButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const product = btn.getAttribute("data-product") || btn.dataset.product || btn.getAttribute("data-title") || "";
      openModal(product);
    });
  });

  closeButtons.forEach(btn => btn.addEventListener("click", closeModal));

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal && modal.classList.contains("is-open")) closeModal();
  });

  // Click outside dialog closes
  if (modal) {
    modal.addEventListener("click", (e) => {
      const overlay = e.target.closest(".modal-overlay");
      if (overlay) closeModal();
    });
  }

  // Form validation helpers
  function setError(input, msg) {
    input.classList.add("error");
    const field = input.closest(".field") || input.parentElement;
    if (!field) return;

    let el = $(".error-msg", field);
    if (!el) {
      el = document.createElement("div");
      el.className = "error-msg";
      field.appendChild(el);
    }
    el.textContent = msg;
  }

  function clearError(input) {
    input.classList.remove("error");
    const field = input.closest(".field") || input.parentElement;
    if (!field) return;
    const el = $(".error-msg", field);
    if (el) el.remove();
  }

  // Quote form (generate WhatsApp-ready message)
  const quoteForm = $("#quoteForm");
  if (quoteForm) {
    const requiredIds = ["qName", "qContact", "qProduct", "qQty"];

    requiredIds.forEach(id => {
      const input = $("#" + id);
      if (!input) return;
      input.addEventListener("input", () => clearError(input));
      input.addEventListener("change", () => clearError(input));
    });

    quoteForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const name = $("#qName");
      const contact = $("#qContact");
      const product = $("#qProduct");
      const qty = $("#qQty");

      let ok = true;
      [name, contact, product, qty].forEach(i => {
        if (!i) return;
        if (!i.value || !String(i.value).trim()) {
          ok = false;
          setError(i, "Este campo es obligatorio.");
        } else {
          clearError(i);
        }
      });

      if (!ok) return;

      const size = $("#qSize")?.value?.trim() || "No aplica";
      const date = $("#qDate")?.value ? $("#qDate").value : "Flexible / por confirmar";

      const finishes = $$("input[name='finishes']:checked", quoteForm).map(c => c.value);
      const finishesTxt = finishes.length ? finishes.join(", ") : "Sin preferencia";

      const notes = $("#qNotes")?.value?.trim() || "—";
      const file = $("#qFile")?.files?.[0]?.name || "No adjunto";

      const msg =
`Hola Impresiones AAA 👋
Quiero una cotización:

• Nombre: ${name.value.trim()}
• Contacto: ${contact.value.trim()}
• Producto: ${product.value}
• Cantidad: ${qty.value}
• Medidas: ${size}
• Acabados: ${finishesTxt}
• Fecha requerida: ${date}
• Archivo: ${file}
• Comentarios: ${notes}

Gracias.`;

      const resultBox = $("#quoteResult");
      const out = $("#quoteText");
      if (out) out.value = msg;
      if (resultBox) resultBox.hidden = false;

      const waLink = $("#waSend");
      if (waLink) {
        const wa = "https://wa.me/17729401928?text=" + encodeURIComponent(msg);
        waLink.href = wa;
      }

      // Scroll to result inside modal
      resultBox?.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    // Copy
    const copyBtn = $("[data-copy-quote]");
    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        const t = $("#quoteText");
        if (!t) return;
        try {
          await navigator.clipboard.writeText(t.value);
          copyBtn.textContent = "Copiado ✅";
          setTimeout(() => (copyBtn.textContent = "Copiar"), 1200);
        } catch {
          // fallback
          t.select();
          document.execCommand("copy");
          copyBtn.textContent = "Copiado ✅";
          setTimeout(() => (copyBtn.textContent = "Copiar"), 1200);
        }
      });
    }
  }

  // Products filter
  const productsWrap = $("[data-products]");
  const filterButtons = $$("[data-filter]");
  const searchInput = $("[data-search]");
  if (productsWrap && filterButtons.length) {
    let activeFilter = "all";
    let searchTerm = "";

    function applyFilters() {
      const cards = $$(".product", productsWrap);
      cards.forEach(card => {
        const cat = card.getAttribute("data-category");
        const title = (card.getAttribute("data-title") || card.querySelector("h3")?.textContent || "").toLowerCase();

        const matchFilter = activeFilter === "all" || cat === activeFilter;
        const matchSearch = !searchTerm || title.includes(searchTerm);

        card.style.display = (matchFilter && matchSearch) ? "" : "none";
      });
    }

    filterButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        filterButtons.forEach(b => b.classList.remove("chip-active"));
        btn.classList.add("chip-active");
        activeFilter = btn.getAttribute("data-filter");
        applyFilters();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", () => {
        searchTerm = searchInput.value.trim().toLowerCase();
        applyFilters();
      });
      searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          searchInput.value = "";
          searchTerm = "";
          applyFilters();
        }
      });
    }
  }

  // Blog data (local)
  const POSTS = [
    {
      id: "invitaciones-que-datos",
      title: "Invitaciones: qué datos pedir para que salga perfecto",
      excerpt: "Checklist rápido: nombres, fecha, lugar, dress code, RSVP y tips para evitar errores.",
      category: "Eventos",
      date: "2026-02-01",
      readTime: "3 min",
      content: `
        <h1>Invitaciones: qué datos pedir para que salga perfecto</h1>
        <div class="meta">
          <span class="badge badge-soft">Eventos</span>
          <span class="muted tiny">2026-02-01 • 3 min</span>
        </div>
        <p>Para cotizar y diseñar rápido (sin ida y vuelta), manda estos datos:</p>
        <ol>
          <li><strong>Nombres</strong> (tal cual van a imprimirse).</li>
          <li><strong>Fecha y hora</strong> del evento.</li>
          <li><strong>Dirección</strong> (y si quieres, link de Google Maps).</li>
          <li><strong>Dress code</strong> (opcional).</li>
          <li><strong>RSVP</strong> (teléfono o “confirmar por WhatsApp”).</li>
          <li><strong>Cantidad</strong> (para impreso) o “solo digital”.</li>
        </ol>
        <p><strong>Tip pro:</strong> si el evento es formal, menos texto y más aire se ve más elegante.</p>
        <p>¿Quieres que te mandemos modelos? Usa el botón <strong>Cotizar ahora</strong> y lo resolvemos.</p>
      `
    },
    {
      id: "lona-medidas",
      title: "Lonas: medidas más usadas y cómo elegir",
      excerpt: "Cómo escoger tamaño para que se lea desde lejos. Tips de diseño legible.",
      category: "Publicidad",
      date: "2026-02-03",
      readTime: "4 min",
      content: `
        <h1>Lonas: medidas más usadas y cómo elegir</h1>
        <div class="meta">
          <span class="badge badge-soft">Publicidad</span>
          <span class="muted tiny">2026-02-03 • 4 min</span>
        </div>
        <p>La regla de oro: <strong>menos texto, más lectura</strong>. Si tu lona se ve “llena”, nadie la entiende.</p>
        <ul>
          <li><strong>2x4 ft</strong>: promos simples y eventos.</li>
          <li><strong>3x6 ft</strong>: negocios en calle / mejor visibilidad.</li>
          <li><strong>4x8 ft</strong>: máximo impacto (si el espacio lo permite).</li>
        </ul>
        <p><strong>Tip pro:</strong> pon el teléfono grande y el servicio en 3–5 palabras.</p>
      `
    },
    {
      id: "archivos-para-imprimir",
      title: "Formatos de archivo: qué mandar para imprimir sin problemas",
      excerpt: "PDF, PNG, AI… qué conviene y cómo evitar que se vea borroso.",
      category: "Diseño",
      date: "2026-02-05",
      readTime: "5 min",
      content: `
        <h1>Formatos de archivo: qué mandar para imprimir sin problemas</h1>
        <div class="meta">
          <span class="badge badge-soft">Diseño</span>
          <span class="muted tiny">2026-02-05 • 5 min</span>
        </div>
        <p>Si quieres que se vea nítido, lo ideal es:</p>
        <ul>
          <li><strong>PDF</strong> (preferido para impresión).</li>
          <li><strong>AI/SVG</strong> (vector: perfecto para logos).</li>
          <li><strong>PNG</strong> (alta resolución, fondo transparente si aplica).</li>
        </ul>
        <p><strong>Evita:</strong> screenshots de baja calidad si el diseño lleva texto pequeño.</p>
      `
    },
    {
      id: "sticker-branding",
      title: "Stickers y etiquetas: el truco más barato para verte pro",
      excerpt: "Cómo usar stickers para empaque y hacer que tu marca se vea premium.",
      category: "Branding",
      date: "2026-02-06",
      readTime: "4 min",
      content: `
        <h1>Stickers y etiquetas: el truco más barato para verte pro</h1>
        <div class="meta">
          <span class="badge badge-soft">Branding</span>
          <span class="muted tiny">2026-02-06 • 4 min</span>
        </div>
        <p>Un sticker bien hecho sube la percepción de calidad, aunque el producto sea simple.</p>
        <p><strong>Recomendación:</strong> logo + @redes + teléfono (si aplica). Nada más.</p>
      `
    }
  ];

  // Blog list render
  function renderBlogList() {
    const list = $("#blogList");
    if (!list) return;
    list.innerHTML = POSTS.map(p => `
      <article class="card">
        <div class="product-top">
          <span class="badge badge-soft">${p.category}</span>
          <span class="muted tiny">${p.readTime}</span>
        </div>
        <h3>${p.title}</h3>
        <p class="muted">${p.excerpt}</p>
        <a class="btn btn-ghost w-100" href="post.html?id=${encodeURIComponent(p.id)}">Leer más</a>
      </article>
    `).join("");
  }

  // Blog preview on home
  function renderBlogPreview() {
    const el = $("#blogPreview");
    if (!el) return;
    const top3 = POSTS.slice(0, 3);
    el.innerHTML = top3.map(p => `
      <article class="card">
        <div class="product-top">
          <span class="badge badge-soft">${p.category}</span>
          <span class="muted tiny">${p.readTime}</span>
        </div>
        <h3>${p.title}</h3>
        <p class="muted">${p.excerpt}</p>
        <a class="btn btn-ghost w-100" href="post.html?id=${encodeURIComponent(p.id)}">Leer más</a>
      </article>
    `).join("");
  }

  // Post detail render
  function renderPost() {
    const wrap = $("#post");
    if (!wrap) return;

    const params = new URLSearchParams(window.location.search);
    const id = params.get("id") || "";
    const post = POSTS.find(p => p.id === id);

    if (!post) {
      wrap.innerHTML = `
        <h1>Artículo no encontrado</h1>
        <p class="muted">Revisa el enlace o vuelve al blog.</p>
        <a class="btn btn-ghost" href="blog.html">Volver</a>
      `;
      return;
    }

    wrap.innerHTML = post.content + `
      <hr style="border:0;border-top:1px solid rgba(255,255,255,.08); margin:16px 0;">
      <div class="card" style="padding:14px;">
        <h3>¿Quieres imprimir esto?</h3>
        <p class="muted">Cotiza en menos de un minuto y te guiamos.</p>
        <button class="btn btn-primary" type="button" data-open-quote>🚀 Cotizar ahora</button>
      </div>
    `;

    // More posts
    const more = $("#postMore");
    if (more) {
      const others = POSTS.filter(p => p.id !== id).slice(0, 3);
      more.innerHTML = others.map(p => `
        <a href="post.html?id=${encodeURIComponent(p.id)}">
          <strong>${p.title}</strong>
          <div class="muted tiny">${p.category} • ${p.readTime}</div>
        </a>
      `).join("");
    }
  }

  renderBlogList();
  renderBlogPreview();
  renderPost();

  // Contact form -> WhatsApp
  const contactForm = $("#contactForm");
  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const name = $("#cName");
      const contact = $("#cContact");
      const topic = $("#cTopic");
      const msg = $("#cMsg");
      const when = $("#cWhen")?.value || "Flexible / por confirmar";

      const required = [name, contact, topic, msg];
      let ok = true;
      required.forEach(i => {
        if (!i.value || !String(i.value).trim()) {
          ok = false;
          i.classList.add("error");
        } else i.classList.remove("error");
      });
      if (!ok) return;

      const text =
`Hola Impresiones AAA 👋
Quiero información / cotización:

• Nombre: ${name.value.trim()}
• Contacto: ${contact.value.trim()}
• Tema: ${topic.value}
• Para cuándo: ${when}
• Mensaje: ${msg.value.trim()}

Gracias.`;

      const out = $("#contactText");
      const box = $("#contactResult");
      if (out) out.value = text;
      if (box) box.hidden = false;

      const wa = $("#waSendContact");
      if (wa) wa.href = "https://wa.me/17729401928?text=" + encodeURIComponent(text);

      box?.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    const copy = $("[data-copy-contact]");
    if (copy) {
      copy.addEventListener("click", async () => {
        const t = $("#contactText");
        if (!t) return;
        try {
          await navigator.clipboard.writeText(t.value);
          copy.textContent = "Copiado ✅";
          setTimeout(() => (copy.textContent = "Copiar"), 1200);
        } catch {
          t.select();
          document.execCommand("copy");
          copy.textContent = "Copiado ✅";
          setTimeout(() => (copy.textContent = "Copiar"), 1200);
        }
      });
    }
  }

})();