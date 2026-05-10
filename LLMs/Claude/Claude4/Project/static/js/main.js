/* FC Ironclad — main.js */

// ── Mobile nav toggle ────────────────────────────────────────────────────
const toggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
if (toggle && navLinks) {
  toggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
    }
  });
}

// ── Auto-dismiss flash messages ──────────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4500);
});

// ── Scroll reveal animations ─────────────────────────────────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.08 });

document.querySelectorAll('.card, .fixture-row, .stat-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity .45s ease, transform .45s ease';
  observer.observe(el);
});

// ── Hero stat counter animation ───────────────────────────────────────────
function animateCounter(el, target, duration = 1200) {
  let start = 0;
  const step = target / (duration / 16);
  const run = () => {
    start += step;
    if (start >= target) { el.textContent = target + (el.dataset.suffix || ''); return; }
    el.textContent = Math.floor(start) + (el.dataset.suffix || '');
    requestAnimationFrame(run);
  };
  requestAnimationFrame(run);
}

const statNums = document.querySelectorAll('.stat-num');
if (statNums.length) {
  const heroObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const val = parseInt(e.target.textContent, 10);
        animateCounter(e.target, val);
        heroObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  statNums.forEach(el => heroObserver.observe(el));
}

// ── Textarea auto-resize ─────────────────────────────────────────────────
document.querySelectorAll('textarea').forEach(ta => {
  ta.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
  });
});
