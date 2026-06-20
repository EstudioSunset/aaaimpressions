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

window.addEventListener('message', e => {
  const data = e.data || {};
  const submitted = data.type === 'hsFormCallback' && data.eventName === 'onFormSubmitted';
  if (!submitted) return;

  trackMarketingEvent('generate_lead', {
    form_name: 'hubspot_contact',
    lead_destination: 'hubspot',
    hubspot_form_id: data.id || data.formGuid || ''
  });
});
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
