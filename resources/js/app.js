import './bootstrap';

// ═══════════════════════════════════════════════════════════
// Theme & Style Manager
// ═══════════════════════════════════════════════════════════

const THEME_KEY = 'sg-theme';
const STYLE_KEY = 'sg-style';

function applyTheme(theme) {
  if (!theme) return;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
}

function applyStyle(style) {
  if (!style) return;
  document.documentElement.setAttribute('data-style', style);
  localStorage.setItem(STYLE_KEY, style);
}

function applyVar(name, value) {
  if (!value) return;
  document.documentElement.style.setProperty(name, value);
}

// ─── Livewire: theme-changed event ───
window.addEventListener('theme-changed', (e) => {
  // Livewire 3 ممکن است در e.detail آرایه بفرستد
  let d = e.detail;
  if (Array.isArray(d)) d = d[0] || {};
  if (!d || typeof d !== 'object') return;

  if (d.theme)   applyTheme(d.theme);
  if (d.style)   applyStyle(d.style);
  if (d.primary) applyVar('--sg-primary', d.primary);
  if (d.accent)  applyVar('--sg-accent', d.accent);
  if (d.font)    applyVar('--sg-font', `'${d.font}', 'Vazirmatn', sans-serif`);
});

// ─── همان‌سازی localStorage با داده‌های سرور در هر لود ───
document.addEventListener('DOMContentLoaded', () => {
  const html = document.documentElement;
  const serverTheme = html.getAttribute('data-theme');
  const serverStyle = html.getAttribute('data-style');

  if (serverTheme && serverTheme !== localStorage.getItem(THEME_KEY)) {
    localStorage.setItem(THEME_KEY, serverTheme);
  }
  if (serverStyle && serverStyle !== localStorage.getItem(STYLE_KEY)) {
    localStorage.setItem(STYLE_KEY, serverStyle);
  }
});

// ═══════════════════════════════════════════════════════════
// Global popup close
// ═══════════════════════════════════════════════════════════
window.sgGlobalPopupClose = function () {
  document.addEventListener('click', function (e) {
    const backdrop = e.target.closest('.sg-popup-backdrop');
    if (!backdrop) return;
    const panel = e.target.closest('.sg-popup-panel');
    if (panel) return;

    const alpineData = backdrop._x_dataStack && backdrop._x_dataStack[0];
    if (alpineData && typeof alpineData.open !== 'undefined') {
      alpineData.open = false;
      return;
    }
    backdrop.style.display = 'none';
  });
};

document.addEventListener('DOMContentLoaded', window.sgGlobalPopupClose);
document.addEventListener('livewire:navigated', window.sgGlobalPopupClose);