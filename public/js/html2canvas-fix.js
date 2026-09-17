// =========================================================
// رفع مشکل oklch برای html2canvas
// =========================================================

// تبدیل oklch به hex ساده
function oklchToHex(oklch) {
    try {
        // روش سریع: از یه canvas استفاده کن
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 1;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = oklch;
        ctx.fillRect(0, 0, 1, 1);
        const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
    } catch (e) {
        return '#808080';
    }
}

// قبل از html2canvas، استایل‌ها رو با hex جایگزین کن
function preprocessForHtml2Canvas(element) {
    const all = [element, ...element.querySelectorAll('*')];
    const backups = [];

    for (const el of all) {
        const computed = window.getComputedStyle(el);
        const props = ['color', 'background-color', 'border-color', 'border-top-color',
                       'border-right-color', 'border-bottom-color', 'border-left-color',
                       'outline-color', 'fill', 'stroke'];

        const backup = { el, styles: {} };

        for (const prop of props) {
            const val = computed.getPropertyValue(prop);
            if (val && val.includes('oklch')) {
                backup.styles[prop] = el.style.getPropertyValue(prop) || '';
                el.style.setProperty(prop, oklchToHex(val), 'important');
            }
        }

        backups.push(backup);
    }

    return () => {
        for (const b of backups) {
            for (const [k, v] of Object.entries(b.styles)) {
                if (v) b.el.style.setProperty(k, v);
                else b.el.style.removeProperty(k);
            }
        }
    };
}

// html2canvas امن
async function safeHtml2Canvas(element, options = {}) {
    // قبل از اجرا، oklch رو hex کن
    const restore = preprocessForHtml2Canvas(element);

    try {
        const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            logging: false,
            backgroundColor: '#ffffff',
            ...options,
        });

        restore();
        return canvas;
    } catch (e) {
        restore();
        throw e;
    }
}

window.safeHtml2Canvas = safeHtml2Canvas;
