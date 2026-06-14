// ============================================================
// HEADER — scroll glass effect
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
const menuBtn  = document.getElementById('menuBtn');
const mobileMenu = document.getElementById('mobileMenu');
const iconOpen = document.getElementById('iconOpen');
const iconClose = document.getElementById('iconClose');

if (menuBtn && mobileMenu) {
  menuBtn.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('hidden') === false;
    menuBtn.setAttribute('aria-expanded', String(open));
    if (iconOpen)  iconOpen.classList.toggle('hidden', open);
    if (iconClose) iconClose.classList.toggle('hidden', !open);
  });

  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    mobileMenu.classList.add('hidden');
    menuBtn.setAttribute('aria-expanded', 'false');
    if (iconOpen)  iconOpen.classList.remove('hidden');
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
// FAQ ACCORDION (if native <details> not preferred)
// ============================================================
// Using native <details> elements — no JS needed.

// ============================================================
// CONTACT FORM
// ============================================================
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', e => {
    e.preventDefault();
    const name  = document.getElementById('f-name');
    const email = document.getElementById('f-email');
    const msg   = document.getElementById('f-msg');
    if (name  && !name.checkValidity())  { name.reportValidity();  return; }
    if (email && !email.checkValidity()) { email.reportValidity(); return; }
    if (msg   && !msg.checkValidity())   { msg.reportValidity();   return; }

    const out    = document.getElementById('formMsg');
    const okText = contactForm.dataset.formOk || 'Thank you! We\'ll get back to you shortly.';
    if (out) {
      out.textContent = okText;
      out.style.cssText = 'background:var(--primary-lt);color:var(--primary-dk);border-radius:12px;padding:1rem;text-align:center;font-size:.875rem;display:block';
    }
    e.target.reset();

    // TODO: connect to Formspree / EmailJS
    // fetch('https://formspree.io/f/YOUR_ID', { method:'POST', body: new FormData(e.target) })
    // gtag('event', 'form_submit', { event_category: 'contact' });
  });
}

// ============================================================
// MISC
// ============================================================
const yr = document.getElementById('yr');
if (yr) yr.textContent = new Date().getFullYear();
