/* ═══════════════════════════════════════════════════════════════
   AFZO Clothing — main.js
   Dark Mode · Loading Spinner · Cart Badge · Popup · Toast
   Wishlist · Quick Add · Mobile Drawer · Animations
   ═══════════════════════════════════════════════════════════════ */

'use strict';

// ── Loading Spinner ─────────────────────────────────────────
const loader = document.getElementById('pageLoader');
if (loader) {
  window.addEventListener('load', () => {
    setTimeout(() => loader.classList.add('hidden'), 300);
  });
}

// ── Dark Mode ───────────────────────────────────────────────
const DARK_KEY = 'afzo-dark';
const htmlEl   = document.documentElement;

function applyTheme(dark) {
  htmlEl.setAttribute('data-theme', dark ? 'dark' : 'light');
  const btn = document.getElementById('darkToggleBtn');
  if (btn) {
    btn.innerHTML = dark
      ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`
      : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
  }
}

let isDark = localStorage.getItem(DARK_KEY) === 'true';
applyTheme(isDark);

function toggleDark() {
  isDark = !isDark;
  localStorage.setItem(DARK_KEY, isDark);
  applyTheme(isDark);
}

// ── Toast ───────────────────────────────────────────────────
let toastTimer;
function showToast(msg, cls = '') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.className   = 'toast show ' + cls;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3000);
}

// ── Auth Popup ──────────────────────────────────────────────
function openLogin(tab = 'login') {
  const overlay = document.getElementById('loginPopup');
  if (!overlay) return;
  overlay.classList.add('open');
  switchTab(tab);
  document.body.style.overflow = 'hidden';
}
function closeLogin() {
  const overlay = document.getElementById('loginPopup');
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}
function switchTab(tab) {
  const tabs  = document.querySelectorAll('.ptab');
  const panels = document.querySelectorAll('.ptab-panel');
  tabs.forEach(t   => t.classList.remove('active'));
  panels.forEach(p => p.classList.remove('active'));
  if (tab === 'login') {
    document.getElementById('tabLogin')?.classList.add('active');
    document.getElementById('panelLogin')?.classList.add('active');
  } else {
    document.getElementById('tabSignup')?.classList.add('active');
    document.getElementById('panelSignup')?.classList.add('active');
  }
}

// Close popup on overlay click
document.getElementById('loginPopup')?.addEventListener('click', e => {
  if (e.target === document.getElementById('loginPopup')) closeLogin();
});

// Tab switching buttons
document.getElementById('tabLogin')?.addEventListener('click',  () => switchTab('login'));
document.getElementById('tabSignup')?.addEventListener('click', () => switchTab('signup'));

// ── Search Popup ───────────────────────────────────────────
function openSearch() {
  const overlay = document.getElementById('searchPopup');
  if (!overlay) return;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
  document.querySelector('#searchForm input[name="q"]').focus();
}
function closeSearch() {
  const overlay = document.getElementById('searchPopup');
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// Close search popup on overlay click
document.getElementById('searchPopup')?.addEventListener('click', e => {
  if (e.target === document.getElementById('searchPopup')) closeSearch();
});

// ── Login Form ──────────────────────────────────────────────
document.getElementById('loginForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  btn.textContent = 'Signing in…';
  btn.disabled = true;
  const data = Object.fromEntries(new FormData(e.target));
  const res  = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const d = await res.json();
  if (res.ok) {
    showToast(`Welcome back, ${d.name}! 👋`, 't-terra');
    closeLogin();
    setTimeout(() => location.reload(), 700);
  } else {
    showToast(d.error || 'Login failed', '');
    btn.textContent = 'Sign In';
    btn.disabled = false;
  }
});

// ── Signup Form ─────────────────────────────────────────────
document.getElementById('signupForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  const data = Object.fromEntries(new FormData(e.target));
  if (data.password !== data.confirm_password) {
    showToast('Passwords do not match', '');
    return;
  }
  btn.textContent = 'Creating account…';
  btn.disabled = true;
  const res = await fetch('/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: data.full_name, email: data.email, password: data.password })
  });
  const d = await res.json();
  if (res.ok) {
    showToast(`Welcome to AFZO, ${d.name}! 🤍`, 't-terra');
    closeLogin();
    setTimeout(() => location.reload(), 700);
  } else {
    showToast(d.error || 'Sign up failed', '');
    btn.textContent = 'Create Account';
    btn.disabled = false;
  }
});

// ── Cart Badge ──────────────────────────────────────────────
async function updateCartBadge() {
  const badge = document.getElementById('cartBadge');
  if (!badge) return;
  try {
    const res  = await fetch('/cart-count');
    const data = await res.json();
    const n    = data.count || 0;
    badge.textContent = n;
    badge.classList.toggle('show', n > 0);
  } catch (_) {}
}
updateCartBadge();

// ── Quick Add ───────────────────────────────────────────────
document.querySelectorAll('[data-quick-add]').forEach(btn => {
  btn.addEventListener('click', async e => {
    e.stopPropagation();
    const pid = parseInt(btn.dataset.quickAdd);
    const loggedIn = document.body.dataset.loggedIn === 'true';
    if (!loggedIn) { openLogin('login'); return; }
    const res = await fetch('/add-to-cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: pid, size: 'M', color: '#C4A882' })
    });
    if (res.status === 401) { openLogin('login'); return; }
    if (res.ok) {
      showToast('Added to cart 🛒', 't-terra');
      updateCartBadge();
    }
  });
});

// ── Product Card → Item Page ────────────────────────────────
document.querySelectorAll('[data-item-link]').forEach(card => {
  card.addEventListener('click', e => {
    if (e.target.closest('[data-quick-add]') || e.target.closest('.card-heart')) return;
    const pid = card.dataset.itemLink;
    if (pid) location.href = `/item/${pid}`;
  });
  card.style.cursor = 'pointer';
});

// ── Wishlist Toggle ─────────────────────────────────────────
async function toggleWishlist(pid) {
  const loggedIn = document.body.dataset.loggedIn === 'true';
  if (!loggedIn) { openLogin('login'); return; }
  const res = await fetch('/toggle-wishlist', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: pid })
  });
  if (res.status === 401) { openLogin('login'); return; }
  const d = await res.json();
  showToast(d.msg || 'Updated', 't-terra');
  const wishBtn = document.getElementById('wishBtn');
  if (wishBtn) {
    wishBtn.classList.toggle('active', d.status === 'added');
    wishBtn.innerHTML = d.status === 'added'
      ? '♥ &nbsp; Saved to Wishlist'
      : '♡ &nbsp; Save to Wishlist';
  }
}

// ── Add to Cart (item page) ─────────────────────────────────
const mainAddBtn = document.getElementById('mainAddToCart');
if (mainAddBtn) {
  let selectedSize  = document.querySelector('.size-btn.active')?.textContent || 'M';
  let selectedColor = document.querySelector('.swatch.active')?.dataset.color || '#C4A882';

  document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedSize = btn.textContent;
    });
  });
  document.querySelectorAll('.swatch').forEach(sw => {
    sw.addEventListener('click', () => {
      document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
      sw.classList.add('active');
      selectedColor = sw.dataset.color;
    });
  });

  mainAddBtn.addEventListener('click', async () => {
    const loggedIn = document.body.dataset.loggedIn === 'true';
    if (!loggedIn) { openLogin('login'); return; }
    const pid = parseInt(mainAddBtn.dataset.pid);
    mainAddBtn.textContent = 'Adding…';
    const res = await fetch('/add-to-cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: pid, size: selectedSize, color: selectedColor })
    });
    if (res.status === 401) { openLogin('login'); return; }
    if (res.ok) {
      showToast('Added to cart 🛒', 't-terra');
      updateCartBadge();
      mainAddBtn.textContent = '✓ Added to Cart';
      setTimeout(() => {
        const price = mainAddBtn.closest('[data-price]')?.dataset.price || '';
        mainAddBtn.textContent = `Add to Cart${price ? ' — ₹' + price : ''}`;
      }, 2000);
    }
  });
}

// ── Accordion ───────────────────────────────────────────────
document.querySelectorAll('.acc-head').forEach(head => {
  head.addEventListener('click', () => {
    const item = head.closest('.acc-item');
    item.classList.toggle('open');
  });
});

// ── Newsletter ──────────────────────────────────────────────
document.getElementById('nlForm')?.addEventListener('submit', async e => {
  e.preventDefault();
  const email = e.target.querySelector('input').value;
  await fetch('/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  document.getElementById('nlThanks').style.display = 'block';
  e.target.querySelector('button').textContent = 'Subscribed ✓';
  e.target.querySelector('button').disabled = true;
  e.target.querySelector('input').disabled  = true;
});

// ── Products Sidebar Filter ─────────────────────────────────
document.querySelectorAll('.sidebar-btn[data-cat]').forEach(btn => {
  btn.addEventListener('click', () => {
    const cat = btn.dataset.cat;
    location.href = `/products?cat=${cat}`;
  });
});

// ── Mobile Drawer ───────────────────────────────────────────
function openDrawer() {
  const drawer = document.getElementById('mobileDrawer');
  if (drawer) {
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    // Animate panel in
    setTimeout(() => drawer.querySelector('.drawer-panel').style.transform = 'translateX(0)', 10);
  }
}
function closeDrawer() {
  const drawer = document.getElementById('mobileDrawer');
  if (drawer) {
    drawer.querySelector('.drawer-panel').style.transform = 'translateX(100%)';
    setTimeout(() => {
      drawer.classList.remove('open');
      document.body.style.overflow = '';
    }, 350);
  }
}
document.getElementById('navBurger')?.addEventListener('click', openDrawer);
document.querySelector('.drawer-overlay')?.addEventListener('click', closeDrawer);
document.querySelector('.drawer-close')?.addEventListener('click', closeDrawer);

// ── Intersection Observer for fade-up ──────────────────────
const fuObs = new IntersectionObserver((entries) => {
  entries.forEach(el => {
    if (el.isIntersecting) {
      el.target.style.animationPlayState = 'running';
      fuObs.unobserve(el.target);
    }
  });
}, { threshold: 0.05 });

document.querySelectorAll('.fu').forEach(el => {
  el.style.animationPlayState = 'paused';
  fuObs.observe(el);
});

// ── Escape key closes popups ────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeLogin(); closeSearch(); closeDrawer(); }
});
