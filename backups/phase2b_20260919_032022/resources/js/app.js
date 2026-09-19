import './bootstrap';

// ---------- همگام‌سازی تم و سبک از localStorage ----------
const savedTheme = localStorage.getItem('sg-theme');
const savedStyle = localStorage.getItem('sg-style');

if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);
if (savedStyle) document.documentElement.setAttribute('data-style', savedStyle);

// ---------- گوش دادن به تغییرات از Livewire ----------
window.addEventListener('theme-changed', (e) => {
  const d = e.detail || {};
  if (d.theme) { document.documentElement.setAttribute('data-theme', d.theme); localStorage.setItem('sg-theme', d.theme); }
  if (d.style) { document.documentElement.setAttribute('data-style', d.style); localStorage.setItem('sg-style', d.style); }
  if (d.primary) document.documentElement.style.setProperty('--sg-primary', d.primary);
  if (d.accent)  document.documentElement.style.setProperty('--sg-accent', d.accent);
  if (d.font)    document.documentElement.style.setProperty('--sg-font', `'${d.font}', sans-serif`);
});

// ---------- شناسایی تم سیستم ----------
if (!savedTheme) {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
}
