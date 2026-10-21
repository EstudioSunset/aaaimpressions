/* AAA Impressions: website AI assistant widget (talks to api.aaaimpressions.com/chat). */
(function () {
  var script = document.currentScript;
  var ENDPOINT = script && script.getAttribute("data-endpoint");
  if (!ENDPOINT) return;
  var LANG = (script.getAttribute("data-lang") || document.documentElement.lang || "en").slice(0, 2) === "es" ? "es" : "en";
  var STORE = "aaa-chat-v1";

  var T = {
    en: {
      launcher: "Ask our AI assistant",
      title: "AAA Impressions assistant",
      sub: "AI · answers instantly, 24/7",
      hello: "Hi! I can answer questions about our spec sheets, bilingual safety materials, B2B marketing and pricing. What are you working on?",
      chips: ["What do spec sheets cost?", "Do you make bilingual safety signs?", "How do I get a quote?"],
      placeholder: "Type your question…",
      send: "Send",
      close: "Close chat",
      note: "AI assistant: it can make mistakes. For a quote, Adinel replies personally.",
      contact: "Request a proposal",
      contactUrl: "/en/contact/",
      error: "I couldn't connect. Please try again, or use the contact form / WhatsApp +1 772-940-1928.",
      limited: "Too many messages in a row. Please wait a minute and try again.",
      thinking: "Typing…",
    },
    es: {
      launcher: "Pregúntale a nuestra IA",
      title: "Asistente de AAA Impressions",
      sub: "IA · responde al instante, 24/7",
      hello: "¡Hola! Puedo responder preguntas sobre fichas técnicas, materiales de seguridad bilingües, marketing B2B y precios. ¿En qué estás trabajando?",
      chips: ["¿Cuánto cuestan las fichas técnicas?", "¿Hacen señalización de seguridad bilingüe?", "¿Cómo pido una cotización?"],
      placeholder: "Escribe tu pregunta…",
      send: "Enviar",
      close: "Cerrar chat",
      note: "Asistente de IA: puede equivocarse. Para cotizar, Adinel te responde personalmente.",
      contact: "Solicitar propuesta",
      contactUrl: "/es/contacto/",
      error: "No pude conectarme. Intenta de nuevo o usa el formulario / WhatsApp +1 772-940-1928.",
      limited: "Demasiados mensajes seguidos. Espera un minuto e intenta de nuevo.",
      thinking: "Escribiendo…",
    },
  }[LANG];

  // Random id per browser tab so the daily digest can group one visitor's questions. No personal data.
  var SID = (function () {
    try {
      var v = sessionStorage.getItem(STORE + "-sid");
      if (!v) { v = Math.random().toString(36).slice(2, 12) + Date.now().toString(36); sessionStorage.setItem(STORE + "-sid", v); }
      return v;
    } catch (e) { return ""; }
  })();

  function load() { try { return JSON.parse(sessionStorage.getItem(STORE)) || []; } catch (e) { return []; } }
  function save(h) { try { sessionStorage.setItem(STORE, JSON.stringify(h.slice(-20))); } catch (e) {} }
  function track(name) { try { if (window.gtag) window.gtag("event", name, { event_category: "ai_chat" }); } catch (e) {} }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  // Render text with clickable links, without innerHTML.
  function richText(node, text) {
    var re = /(https?:\/\/[^\s<>"')]+|\+1 ?772[- ]?940[- ]?1928)/g, last = 0, m;
    while ((m = re.exec(text))) {
      var url = m[0], trail = "";
      while (/[.,;:!?]$/.test(url)) { trail = url.slice(-1) + trail; url = url.slice(0, -1); }
      node.appendChild(document.createTextNode(text.slice(last, m.index)));
      // Internal links show a short label (path only) instead of the full URL.
      var label = url.replace(/^https:\/\/(www\.)?aaaimpressions\.com/, "aaaimpressions.com");
      var a = el("a", null, label);
      if (/^\+1/.test(url)) { a.href = "https://wa.me/17729401928"; a.target = "_blank"; a.rel = "noopener"; }
      else {
        a.href = url;
        if (!/^https:\/\/(www\.)?aaaimpressions\.com/.test(url)) { a.target = "_blank"; a.rel = "noopener nofollow"; }
      }
      node.appendChild(a);
      node.appendChild(document.createTextNode(trail));
      last = m.index + m[0].length;
    }
    node.appendChild(document.createTextNode(text.slice(last)));
  }

  var history = load();
  var busy = false;

  // ---- DOM ----
  var root = el("div", "aaa-chat");
  var launcher = el("button", "aaa-chat-launcher");
  launcher.type = "button";
  launcher.setAttribute("aria-expanded", "false");
  launcher.setAttribute("aria-controls", "aaa-chat-panel");
  launcher.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M4 4h16v11H8.8L4 19.2V4zm2 2v8.4L8 12.6h10V6H6z"/><circle cx="9" cy="9.5" r="1.2" fill="currentColor"/><circle cx="12" cy="9.5" r="1.2" fill="currentColor"/><circle cx="15" cy="9.5" r="1.2" fill="currentColor"/></svg>';
  launcher.appendChild(el("span", "aaa-chat-launcher-label", T.launcher));

  var panel = el("div", "aaa-chat-panel");
  panel.id = "aaa-chat-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", T.title);
  panel.hidden = true;

  var head = el("div", "aaa-chat-head");
  var headText = el("div");
  headText.appendChild(el("p", "aaa-chat-title", T.title));
  headText.appendChild(el("p", "aaa-chat-sub", T.sub));
  var closeBtn = el("button", "aaa-chat-close");
  closeBtn.type = "button";
  closeBtn.setAttribute("aria-label", T.close);
  closeBtn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M6.4 5 5 6.4 10.6 12 5 17.6 6.4 19l5.6-5.6 5.6 5.6 1.4-1.4-5.6-5.6L19 6.4 17.6 5 12 10.6z"/></svg>';
  head.appendChild(headText);
  head.appendChild(closeBtn);

  var log = el("div", "aaa-chat-log");
  log.setAttribute("aria-live", "polite");

  var chips = el("div", "aaa-chat-chips");
  T.chips.forEach(function (c) {
    var b = el("button", "aaa-chat-chip", c);
    b.type = "button";
    b.addEventListener("click", function () { send(c); });
    chips.appendChild(b);
  });

  var form = el("form", "aaa-chat-form");
  var input = el("textarea", "aaa-chat-input");
  input.rows = 1;
  input.maxLength = 800;
  input.placeholder = T.placeholder;
  input.setAttribute("aria-label", T.placeholder);
  var sendBtn = el("button", "aaa-chat-send", T.send);
  sendBtn.type = "submit";
  form.appendChild(input);
  form.appendChild(sendBtn);

  var foot = el("div", "aaa-chat-foot");
  foot.appendChild(el("span", null, T.note));
  var cta = el("a", "aaa-chat-cta", T.contact + " →");
  cta.href = T.contactUrl;
  cta.addEventListener("click", function () { track("chat_cta_click"); });
  foot.appendChild(cta);

  panel.appendChild(head);
  panel.appendChild(log);
  panel.appendChild(chips);
  panel.appendChild(form);
  panel.appendChild(foot);
  root.appendChild(panel);
  root.appendChild(launcher);
  document.body.appendChild(root);

  function bubble(role, text) {
    var b = el("div", "aaa-chat-msg aaa-chat-" + role);
    richText(b, text);
    log.appendChild(b);
    log.scrollTop = log.scrollHeight;
    return b;
  }

  function render() {
    log.textContent = "";
    bubble("assistant", T.hello);
    history.forEach(function (m) { bubble(m.role, m.content); });
    chips.hidden = history.length > 0;
  }

  function open() {
    panel.hidden = false;
    root.classList.add("is-open");
    launcher.setAttribute("aria-expanded", "true");
    render();
    setTimeout(function () { input.focus(); }, 50);
    track("chat_open");
  }
  function close() {
    panel.hidden = true;
    root.classList.remove("is-open");
    launcher.setAttribute("aria-expanded", "false");
    launcher.focus();
  }

  function send(text) {
    text = (text || "").trim();
    if (!text || busy) return;
    busy = true;
    sendBtn.disabled = true;
    chips.hidden = true;
    history.push({ role: "user", content: text });
    save(history);
    bubble("user", text);
    input.value = "";
    autosize();
    var wait = bubble("assistant", T.thinking);
    wait.classList.add("is-typing");
    if (history.length === 1) track("chat_first_message");

    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: LANG, page: location.pathname, sid: SID, messages: history.slice(-12) }),
    })
      .then(function (r) {
        if (r.status === 429) return { reply: T.limited, transient: true };
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (d) {
        wait.remove();
        var reply = (d && d.reply) || T.error;
        bubble("assistant", reply);
        if (!d.transient) { history.push({ role: "assistant", content: reply }); save(history); }
        else { history.pop(); save(history); }
      })
      .catch(function () {
        wait.remove();
        bubble("assistant", T.error);
        history.pop();
        save(history);
      })
      .then(function () {
        busy = false;
        sendBtn.disabled = false;
        input.focus();
      });
  }

  function autosize() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  }

  launcher.addEventListener("click", function () { panel.hidden ? open() : close(); });
  closeBtn.addEventListener("click", close);
  form.addEventListener("submit", function (e) { e.preventDefault(); send(input.value); });
  input.addEventListener("input", autosize);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input.value); }
  });
  panel.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
