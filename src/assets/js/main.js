// ============================================================
// HEADER - scroll glass effect
// ============================================================
const header = document.querySelector('header[data-header]');
if (header) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 24) {
      header.style.cssText = 'background:rgba(255,255,255,.97);box-shadow:0 1px 0 rgba(0,0,0,.07);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)';
    } else {
      header.style.cssText = 'background:transparent;box-shadow:none';
    }
  }, { passive: true });
}

// ============================================================
// MOBILE MENU
// ============================================================
const menuBtn = document.getElementById('menuBtn');
const mobileMenu = document.getElementById('mobileMenu');
const iconOpen = document.getElementById('iconOpen');
const iconClose = document.getElementById('iconClose');

if (menuBtn && mobileMenu) {
  menuBtn.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('hidden') === false;
    menuBtn.setAttribute('aria-expanded', String(open));
    if (iconOpen) iconOpen.classList.toggle('hidden', open);
    if (iconClose) iconClose.classList.toggle('hidden', !open);
  });

  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    mobileMenu.classList.add('hidden');
    menuBtn.setAttribute('aria-expanded', 'false');
    if (iconOpen) iconOpen.classList.remove('hidden');
    if (iconClose) iconClose.classList.add('hidden');
  }));
}

// ============================================================
// SCROLL REVEAL
// ============================================================
const ro = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.08 });
document.querySelectorAll('.reveal').forEach(el => ro.observe(el));

// ============================================================
// ACTIVE NAV
// ============================================================
const navLinks = document.querySelectorAll('.nav-link');
if (navLinks.length) {
  const no = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        navLinks.forEach(l =>
          l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id)
        );
      }
    });
  }, { rootMargin: '-35% 0px -60% 0px' });
  document.querySelectorAll('section[id]').forEach(s => no.observe(s));
}

// ============================================================
// MARKETING EVENT TRACKING
// ============================================================
function trackMarketingEvent(eventName, payload = {}) {
  const data = {
    ...payload,
    source_page: window.location.pathname,
    page_language: document.documentElement.lang || 'es'
  };

  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event: eventName, ...data });

  if (typeof gtag === 'function') {
    gtag('event', eventName, data);
  }
}

// ============================================================
// GA4/GTM -> WhatsApp, phone, and email click events
// ============================================================
document.addEventListener('click', e => {
  const link = e.target.closest('a[href]');
  if (!link) return;
  const href = link.getAttribute('href') || '';
  const linkText = (link.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 120);

  if (href.includes('wa.me') || href.includes('api.whatsapp.com')) {
    trackMarketingEvent('whatsapp_click', {
      contact_method: 'whatsapp',
      link_url: href,
      link_text: linkText
    });
  } else if (href.startsWith('tel:')) {
    trackMarketingEvent('click_to_call', {
      contact_method: 'phone',
      link_url: href,
      link_text: linkText
    });
  } else if (href.startsWith('mailto:')) {
    trackMarketingEvent('email_click', {
      contact_method: 'email',
      link_url: href,
      link_text: linkText
    });
  }
});

// ============================================================
// MISC
// ============================================================
const yr = document.getElementById('yr');
if (yr) yr.textContent = new Date().getFullYear();

// ============================================================
// ANIMATED BACKGROUND — hexagonal network canvas
// ============================================================
(function () {
  const canvas = document.getElementById('sb-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const R        = 36;           // hex radius (center to vertex)
  const INTERACT = 175;          // mouse influence radius in px
  const CW       = Math.sqrt(3) * R;   // pointy-top col width
  const RH       = 1.5 * R;            // row height
  const PAD_Y    = 2000;         // extra canvas rows above viewport for parallax

  let W = 0, H = 0, hexes = [];
  let mouse = { x: -9999, y: -9999 };
  let scY = 0, rafP = false;

  function buildGrid() {
    hexes = [];
    const cols = Math.ceil(W / CW) + 3;
    const rows = Math.ceil((H + PAD_Y) / RH) + 4;
    for (let r = -1; r <= rows; r++) {
      for (let c = -1; c <= cols; c++) {
        hexes.push({
          cx: c * CW + (r % 2 !== 0 ? CW / 2 : 0),
          cy: r * RH - PAD_Y
        });
      }
    }
  }

  function verts(cx, cy) {
    const v = [];
    for (let i = 0; i < 6; i++) {
      const a = (Math.PI / 3) * i - Math.PI / 6;
      v.push([cx + R * Math.cos(a), cy + R * Math.sin(a)]);
    }
    return v;
  }

  function draw() {
    rafP = false;
    ctx.clearRect(0, 0, W, H);
    const oy = scY * 0.07;      // parallax shift (hexes drift down at 7% of scroll)
    const mx = mouse.x, my = mouse.y;

    for (const { cx, cy } of hexes) {
      const dy = cy + oy;                          // hex draw position Y on canvas
      if (dy + R < -10 || dy - R > H + 10) continue;  // off-screen cull

      const ddx = mx - cx, ddy = my - dy;
      const d   = Math.sqrt(ddx * ddx + ddy * ddy);
      const t   = d < INTERACT ? 1 - d / INTERACT : 0;
      const v   = verts(cx, dy);

      ctx.beginPath();
      ctx.moveTo(v[0][0], v[0][1]);
      for (let i = 1; i < 6; i++) ctx.lineTo(v[i][0], v[i][1]);
      ctx.closePath();

      if (t > 0) {
        if (t > 0.5) { ctx.fillStyle = `rgba(0,87,231,${(t - 0.5) * 0.09})`; ctx.fill(); }
        ctx.strokeStyle = `rgba(0,87,231,${0.07 + t * 0.28})`;
        ctx.lineWidth   = 0.5 + t * 1.6;
      } else {
        ctx.strokeStyle = 'rgba(0,87,231,0.07)';
        ctx.lineWidth   = 0.5;
      }
      ctx.stroke();

      if (t > 0.35) {
        ctx.beginPath();
        ctx.arc(cx, dy, t * 3.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,87,231,${t * 0.55})`;
        ctx.fill();
      }
    }

    // Spider-web lines from nearby hex centers toward mouse
    if (mx > -100) {
      for (const { cx, cy } of hexes) {
        const dy  = cy + oy;
        if (dy + R < -10 || dy - R > H + 10) continue;
        const ddx = mx - cx, ddy = my - dy;
        const d   = Math.sqrt(ddx * ddx + ddy * ddy);
        const th  = INTERACT * 0.62;
        if (d < th && d > 5) {
          const t = 1 - d / th;
          ctx.beginPath();
          ctx.moveTo(cx, dy);
          ctx.lineTo(mx, my);
          ctx.strokeStyle = `rgba(0,87,231,${t * 0.19})`;
          ctx.lineWidth   = t * 1.5;
          ctx.stroke();
        }
      }
    }
  }

  function schedule() { if (!rafP) { rafP = true; requestAnimationFrame(draw); } }

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
    buildGrid();
    schedule();
  }

  window.addEventListener('resize',    resize, { passive: true });
  window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; schedule(); }, { passive: true });
  window.addEventListener('touchmove', e => {
    if (e.touches.length) { mouse.x = e.touches[0].clientX; mouse.y = e.touches[0].clientY; schedule(); }
  }, { passive: true });
  window.addEventListener('touchend',  () => { mouse.x = -9999; mouse.y = -9999; schedule(); }, { passive: true });
  window.addEventListener('scroll',    () => { scY = window.scrollY; schedule(); }, { passive: true });

  resize();
}());
