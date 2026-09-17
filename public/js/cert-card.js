/* ═══════════════════════════════════════════════════════════════
   Certificate Card Logic — ShopGun V2
   بر اساس «جواهری مشاهیر v6.14»
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ──────────────────────────────────────────────
     oklch → rgb  (فیکس html2canvas + DaisyUI 5)
     ────────────────────────────────────────────── */
  function oklchToRgb(str) {
    if (!str || !str.includes('oklch')) return str;
    const m = str.match(/oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([\d.]+%?)(?:\s*\/\s*([\d.]+%?))?\s*\)/);
    if (!m) return str;

    let L = parseFloat(m[1]); if (m[1].endsWith('%')) L /= 100;
    let C = parseFloat(m[2]);
    let H = parseFloat(m[3]);
    let A = m[4] ? (m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])) : 1;

    const hRad = H * Math.PI / 180;
    const a_ = C * Math.cos(hRad);
    const b_ = C * Math.sin(hRad);

    const l_ = L + 0.3963377774 * a_ + 0.2158037573 * b_;
    const m_ = L - 0.1055613458 * a_ - 0.0638541728 * b_;
    const s_ = L - 0.0894841775 * a_ - 1.2914855480 * b_;

    const l = l_ ** 3, mm = m_ ** 3, s = s_ ** 3;

    const r  = +4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s;
    const g  = -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s;
    const bb = -0.0041960863 * l - 0.7034186147 * mm + 1.7076147010 * s;

    const toSrgb = (x) => {
      x = Math.max(0, Math.min(1, x));
      return x <= 0.0031308 ? x * 12.92 : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
    };

    const R = Math.round(toSrgb(r)  * 255);
    const G = Math.round(toSrgb(g)  * 255);
    const B = Math.round(toSrgb(bb) * 255);

    return `rgba(${R}, ${G}, ${B}, ${A})`;
  }

  function sanitizeOklchIn(rootEl) {
    if (!rootEl) return;
    const els = [rootEl, ...rootEl.querySelectorAll('*')];
    const props = [
      'color', 'backgroundColor',
      'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor',
      'outlineColor', 'fill', 'stroke',
      'backgroundImage', 'borderTopColor', 'caretColor'
    ];
    for (const el of els) {
      const cs = window.getComputedStyle(el);
      for (const p of props) {
        let v = cs[p];
        if (typeof v === 'string' && v.includes('oklch')) {
          // برای background-image که ممکنه گرادیانت باشه، همه رو جایگزین کن
          v = v.replace(/oklch\([^)]*\)/g, (match) => oklchToRgb(match));
          try { el.style[p] = v; } catch (e) { /* ignore */ }
        }
      }
    }
  }

  /* ──────────────────────────────────────────────
     خواندن CSS سراسری صفحه (برای iframe چاپ)
     ────────────────────────────────────────────── */
  function collectAppCSS() {
    let css = '';
    document.querySelectorAll('style, link[rel="stylesheet"]').forEach((s) => {
      if (s.tagName === 'STYLE') {
        if (s.media && s.media.includes('print')) return;
        css += s.textContent + '\n';
      }
    });
    return css;
  }

  /* ──────────────────────────────────────────────
     چاپ A4 — چند کارت در یک صفحه
     ────────────────────────────────────────────── */
  function printCertsA4(codes, options) {
    options = options || {};
    const certW = parseFloat(options.width || 6.5);   // cm
    const certH = parseFloat(options.height || 6.5);  // cm
    const certs = Array.isArray(codes) ? codes : [codes];
    if (!certs.length) { alert('شناسنامه‌ای انتخاب نشده'); return; }

    // محاسبه تعداد ستون‌ها
    let cols = 3;
    if (certW > 6.6) cols = 2;
    if (certW > 10)  cols = 1;

    // ساخت HTML کارت‌ها
    let htmls = '';
    certs.forEach((code) => {
      const src = document.querySelector(`[data-cert-code="${code}"] .certificate`);
      if (!src) return;
      const clone = src.cloneNode(true);
      clone.style.width  = Math.round(certW * 96 / 2.54) + 'px';
      clone.style.height = Math.round(certH * 96 / 2.54) + 'px';
      clone.style.transform = 'none';
      clone.style.boxShadow = 'none';
      clone.style.margin = '0';
      clone.style.overflow = 'hidden';
      htmls += clone.outerHTML;
    });

    if (!htmls) { alert('کارت پیدا نشد'); return; }

    // ساخت iframe مخفی
    const iframe = document.createElement('iframe');
    iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:0;height:0;border:0;';
    document.body.appendChild(iframe);

    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write('<!DOCTYPE html><html dir="rtl" lang="fa"><head><meta charset="UTF-8">');
    doc.write('<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">');
    doc.write('<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">');
    doc.write('<style>' + collectAppCSS() + '</style>');

    const gap = cols === 1 ? 0 : ((210 - cols * certW - 6) / (cols - 1)).toFixed(2);

    doc.write('<style>');
    doc.write('@page{size:A4 portrait;margin:3mm}');
    doc.write('*{print-color-adjust:exact!important;-webkit-print-color-adjust:exact!important;box-sizing:border-box}');
    doc.write('html,body{margin:0!important;padding:0!important;background:#fff;width:210mm}');
    doc.write('.cert-print-grid{display:grid;grid-template-columns:repeat(' + cols + ',' + certW + 'cm);');
    doc.write('column-gap:' + gap + 'cm;row-gap:2mm;justify-content:center;align-content:start;padding:0;width:100%}');
    doc.write('.cert-print-grid .certificate{width:' + certW + 'cm!important;height:' + certH + 'cm!important;');
    doc.write('min-width:' + certW + 'cm!important;min-height:' + certH + 'cm!important;');
    doc.write('max-width:' + certW + 'cm!important;max-height:' + certH + 'cm!important;');
    doc.write('aspect-ratio:auto!important;box-shadow:none!important;transform:none!important;');
    doc.write('margin:0!important;padding:0!important;page-break-inside:avoid;break-inside:avoid;');
    doc.write('overflow:hidden!important;flex:0 0 auto!important}');
    doc.write('.certificate .cert-main{overflow:hidden!important;height:100%!important;width:100%!important}');
    doc.write('.certificate .cert-bottom-table{table-layout:fixed!important;width:100%!important}');
    doc.write('</style>');

    doc.write('</head><body><div class="cert-print-grid">' + htmls + '</div></body></html>');
    doc.close();

    setTimeout(() => {
      try {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      } catch (e) { console.error(e); }
      setTimeout(() => { if (iframe.parentNode) document.body.removeChild(iframe); }, 3000);
    }, 900);
  }

  /* ──────────────────────────────────────────────
     PNG — با فیکس oklch
     ────────────────────────────────────────────── */
  function exportCertPNG(code, options) {
    options = options || {};
    if (typeof html2canvas !== 'function') {
      alert('html2canvas بارگذاری نشده');
      return;
    }
    const src = document.querySelector(`[data-cert-code="${code}"] .certificate`);
    if (!src) { alert('کارت پیدا نشد'); return; }

    const certW = parseFloat(options.width || 6.5);
    const certH = parseFloat(options.height || 6.5);
    const pxW = Math.round(certW * 96 / 2.54);
    const pxH = Math.round(certH * 96 / 2.54);

    // Clone در یک ظرف مخفی
    const clone = src.cloneNode(true);
    clone.style.width  = pxW + 'px';
    clone.style.height = pxH + 'px';
    clone.style.transform = 'none';
    clone.style.position = 'static';
    clone.style.boxShadow = 'none';
    clone.style.overflow = 'hidden';

    const hidden = document.createElement('div');
    hidden.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;width:' + pxW + 'px;height:' + pxH + 'px;';
    hidden.appendChild(clone);
    document.body.appendChild(hidden);

    // ★ فیکس oklch قبل از html2canvas
    sanitizeOklchIn(clone);

    setTimeout(() => {
      html2canvas(clone, {
        scale: 3,
        backgroundColor: '#fffef9',
        useCORS: true,
        allowTaint: false,
        logging: false,
        width: pxW,
        height: pxH,
        windowWidth: pxW,
        windowHeight: pxH,
      }).then((canvas) => {
        if (hidden.parentNode) document.body.removeChild(hidden);
        const a = document.createElement('a');
        a.download = 'cert-' + code + '.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
      }).catch((err) => {
        if (hidden.parentNode) document.body.removeChild(hidden);
        console.error(err);
        alert('خطا در ساخت PNG: ' + err.message);
      });
    }, 300);
  }

  /* ──────────────────────────────────────────────
     پیش‌نمایش تمام‌صفحه
     ────────────────────────────────────────────── */
  function openCertPreview(code, options) {
    options = options || {};
    const src = document.querySelector(`[data-cert-code="${code}"] .certificate`);
    if (!src) { alert('کارت پیدا نشد'); return; }

    const certW = parseFloat(options.width || 6.5);
    const certH = parseFloat(options.height || 6.5);
    const pxW = Math.round(certW * 96 / 2.54);
    const pxH = Math.round(certH * 96 / 2.54);

    // محاسبه scale
    const availW = Math.min(window.innerWidth - 60, 900);
    const availH = Math.max(window.innerHeight - 260, 300);
    let scale = Math.min(availW / pxW, availH / pxH);
    if (scale > 3) scale = 3;
    if (scale < 0.8) scale = 0.8;

    // ساخت overlay
    const overlay = document.createElement('div');
    overlay.className = 'cert-preview-overlay active';
    overlay.innerHTML = `
      <div class="cert-preview-container">
        <div class="cert-preview-actions">
          <button class="btn btn-primary" data-action="print">🖨️ چاپ A4</button>
          <button class="btn btn-secondary" data-action="png">📸 PNG</button>
          <button class="btn btn-outline" data-action="close" style="background:#fff;color:#333;">✕</button>
        </div>
        <div class="cert-preview-stage">
          <div style="position:relative;width:${pxW * scale}px;height:${pxH * scale}px;flex-shrink:0;">
            <div style="position:absolute;top:0;right:0;transform-origin:top right;transform:scale(${scale});"></div>
          </div>
          <div style="font-size:11px;color:rgba(255,255,255,.55);text-align:center;padding:4px;font-family:monospace;">
            ${certW}×${certH} cm · ${Math.round(scale * 100)}%
          </div>
        </div>
      </div>
    `;

    // کپی کارت داخل stage
    const inner = overlay.querySelector('[style*="transform-origin"]');
    const clone = src.cloneNode(true);
    clone.style.width  = pxW + 'px';
    clone.style.height = pxH + 'px';
    clone.style.boxShadow = '0 10px 40px rgba(0,0,0,.4)';
    inner.appendChild(clone);

    // رویدادها
    overlay.querySelector('[data-action="print"]').onclick = () => printCertsA4([code], options);
    overlay.querySelector('[data-action="png"]').onclick   = () => exportCertPNG(code, options);
    overlay.querySelector('[data-action="close"]').onclick = () => overlay.remove();
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    document.body.appendChild(overlay);
  }

  /* ──────────────────────────────────────────────
     Expose عمومی
     ────────────────────────────────────────────── */
  window.ShopGunCert = {
    printCertsA4,
    exportCertPNG,
    openCertPreview,
    sanitizeOklchIn,
    oklchToRgb,
  };
})();
