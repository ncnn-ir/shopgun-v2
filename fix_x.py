# -*- coding: utf-8 -*-
"""ShopGun V2 - Fix: WithFileUploads + oklch download + image cover + modal"""
from pathlib import Path
import time

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. SETTINGS/INDEX.PHP — اضافه کردن WithFileUploads
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # اضافه کردن use
    if 'WithFileUploads' not in txt:
        txt = txt.replace(
            'use Livewire\\Component;',
            'use Livewire\\Component;\nuse Livewire\\WithFileUploads;'
        )
        txt = txt.replace(
            'class Index extends Component\n{',
            'class Index extends Component\n{\n    use WithFileUploads;\n'
        )
        sphp.write_text(txt, encoding='utf-8')
        print("[OK] Settings/Index.php - WithFileUploads اضافه شد")
    else:
        print("[SKIP] WithFileUploads از قبل هست")


# ═══════════════════════════════════════════════════════════════
# 2. VIEW MODAL — فیکس دانلود PNG (oklch → hex)
# ═══════════════════════════════════════════════════════════════

vm_path = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm_path.exists():
    txt = vm_path.read_text(encoding='utf-8')

    # جایگزینی کامل اسکریپت
    import re
    txt = re.sub(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/html2canvas[^>]*></script>\s*<script>.*?</script>',
        '',
        txt,
        flags=re.DOTALL
    )

    script = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
// ★ تبدیل oklch به rgb (DaisyUI 5 problem)
function _oklchToRgb(str) {
    if (!str || str.indexOf('oklch') === -1) return str;
    try {
        var m = str.match(/oklch\\(\\s*([\\d.]+%?)\\s+([\\d.]+)\\s+([\\d.]+)(?:\\s*\\/\\s*([\\d.]+%?))?\\s*\\)/);
        if (!m) return '#cccccc';
        var L = parseFloat(m[1]); if (m[1].endsWith('%')) L /= 100;
        var C = parseFloat(m[2]);
        var H = parseFloat(m[3]);
        var A = m[4] ? (m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])) : 1;

        var hRad = H * Math.PI / 180;
        var a_ = C * Math.cos(hRad);
        var b_ = C * Math.sin(hRad);

        var l_ = L + 0.3963377774 * a_ + 0.2158037573 * b_;
        var m_ = L - 0.1055613458 * a_ - 0.0638541728 * b_;
        var s_ = L - 0.0894841775 * a_ - 1.2914855480 * b_;

        var l = l_ * l_ * l_, mm = m_ * m_ * m_, s = s_ * s_ * s_;

        var r  = +4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s;
        var g  = -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s;
        var bb = -0.0041960863 * l - 0.7034186147 * mm + 1.7076147010 * s;

        function toSrgb(x) {
            x = Math.max(0, Math.min(1, x));
            return x <= 0.0031308 ? x * 12.92 : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
        }
        var R = Math.round(toSrgb(r) * 255);
        var G = Math.round(toSrgb(g) * 255);
        var B = Math.round(toSrgb(bb) * 255);
        return 'rgba(' + R + ',' + G + ',' + B + ',' + A + ')';
    } catch (e) { return '#cccccc'; }
}

function _sanitizeOklch(root) {
    if (!root) return;
    var all = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
    var props = ['color', 'backgroundColor', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor', 'outlineColor', 'fill', 'stroke'];
    for (var i = 0; i < all.length; i++) {
        var el = all[i];
        var cs;
        try { cs = window.getComputedStyle(el); } catch (e) { continue; }
        for (var j = 0; j < props.length; j++) {
            var v = cs[props[j]];
            if (v && v.indexOf('oklch') !== -1) {
                try { el.style[props[j]] = _oklchToRgb(v); } catch (e) {}
            }
        }
    }
}

function downloadCertModal() {
    var el = document.querySelector('#cert-card-area .certificate');
    if (!el) { alert('کارت پیدا نشد'); return; }

    var clone = el.cloneNode(true);
    var w = el.offsetWidth || 600;
    var h = el.offsetHeight || 600;

    clone.style.transform = 'none';
    clone.style.boxShadow = 'none';
    clone.style.width = w + 'px';
    clone.style.height = h + 'px';

    var wrap = document.createElement('div');
    wrap.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;width:' + w + 'px;height:' + h + 'px';
    wrap.appendChild(clone);
    document.body.appendChild(wrap);

    // ★ پاک کردن oklch
    _sanitizeOklch(clone);

    setTimeout(function() {
        html2canvas(clone, {
            scale: 3,
            backgroundColor: '#fffef9',
            useCORS: true,
            allowTaint: false,
            logging: false,
            width: w,
            height: h,
            windowWidth: w,
            windowHeight: h
        }).then(function(canvas) {
            wrap.remove();
            var a = document.createElement('a');
            a.download = 'certificate-{{ $certificate->code ?? "card" }}.png';
            a.href = canvas.toDataURL('image/png');
            a.click();
        }).catch(function(e) {
            wrap.remove();
            alert('خطا در ساخت PNG: ' + e.message);
        });
    }, 250);
}
</script>
'''

    # جایگزین کردن
    if '</div>\n@endif\n</div>' in txt:
        txt = txt.replace('</div>\n@endif\n</div>', '</div>\n@endif\n</div>\n' + script, 1)
    elif '</div>' in txt:
        # آخرین </div> رو پیدا کن
        last = txt.rfind('</div>')
        txt = txt[:last] + '</div>\n' + script
    
    vm_path.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - download با oklch fix")


# ═══════════════════════════════════════════════════════════════
# 3. CERT INDEX — دکمه دانلود PNG
# ═══════════════════════════════════════════════════════════════

ci = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if ci.exists():
    txt = ci.read_text(encoding='utf-8')

    # اضافه کردن دکمه دانلود
    old = '<button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>'
    new = '''<button type="button" onclick="downloadCertRow({{ $c->id }}, '{{ $c->code }}')" class="sg-action-btn" title="دانلود PNG" style="background:rgba(8,145,178,.15);color:#0891b2">📥</button>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>'''
    if old in txt and 'downloadCertRow' not in txt:
        txt = txt.replace(old, new)

    # اسکریپت
    import re
    txt = re.sub(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/html2canvas[^>]*></script>\s*<script>\s*function downloadCertPng.*?</script>',
        '',
        txt,
        flags=re.DOTALL
    )

    script = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCertRow(id, code) {
    fetch('/certificates/' + id, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function(r) { return r.text(); })
        .then(function(html) {
            var div = document.createElement('div');
            div.innerHTML = html;
            var card = div.querySelector('.certificate');
            if (!card) { alert('کارت پیدا نشد'); return; }

            div.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9';
            document.body.appendChild(div);

            // sanitize oklch
            if (typeof _sanitizeOklch === 'function') _sanitizeOklch(card);

            setTimeout(function() {
                html2canvas(card, {
                    scale: 3,
                    backgroundColor: '#fffef9',
                    useCORS: true,
                    logging: false
                }).then(function(canvas) {
                    div.remove();
                    var a = document.createElement('a');
                    a.download = 'cert-' + code + '.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                }).catch(function(e) {
                    div.remove();
                    alert('خطا: ' + e.message);
                });
            }, 250);
        });
}
</script>
'''
    txt = txt + script
    ci.write_text(txt, encoding='utf-8')
    print("[OK] certificates/index - download button")


# ═══════════════════════════════════════════════════════════════
# 4. CERT RENDERER — فیکس کراپ تصویر با style مستقیم
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # داخل buildCardInner، img رو با style مستقیم
    # تصویر محصول
    old_img = '''$imgInner = $imgSrc
            ? '<img src="' . e($imgSrc) . '" alt="" crossorigin="anonymous">'
            : '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;">💎</div>';'''
    
    new_img = '''$imgInner = $imgSrc
            ? '<img src="' . e($imgSrc) . '" alt="" crossorigin="anonymous" style="width:100%;height:100%;object-fit:cover;display:block">'
            : '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;">💎</div>';'''
    
    if old_img in txt:
        txt = txt.replace(old_img, new_img)
        print("[OK] CertRenderer - img cover direct")

    # CSS
    txt = txt.replace(
        '.certificate .cert-img-frame img{width:100%;height:100%;object-fit:contain;display:block}',
        '.certificate .cert-img-frame img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important}'
    )
    txt = txt.replace(
        '.certificate .cert-img-frame{width:100%;height:100%;border:1.5px solid #b8860b;border-radius:6px;overflow:hidden;background:#fff;position:relative}',
        '.certificate .cert-img-frame{width:100%;height:100%;border:1.5px solid #b8860b;border-radius:6px;overflow:hidden;background:#f8f5ef;position:relative}'
    )

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer - CSS cover")


# ═══════════════════════════════════════════════════════════════
# 5. CREATE MODAL — فیکس ایجاد/ویرایش
# ═══════════════════════════════════════════════════════════════

# چک کن layout
layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    if '<livewire:certificates.create' not in txt:
        # اضافه کن بعد از view-modal
        marker = '<livewire:certificates.view-modal'
        if marker in txt:
            txt = txt.replace(marker, '<livewire:certificates.create :key="\'cfm\'" />\n    ' + marker, 1)
            layout.write_text(txt, encoding='utf-8')
            print("[OK] layout - cert create modal اضافه شد")

    if '<livewire:certificates.view-modal' not in txt:
        marker = '@auth'
        if marker in txt:
            txt = txt.replace(marker, marker + "\n    <livewire:certificates.view-modal :key=\"'cvm'\" />", 1)
            layout.write_text(txt, encoding='utf-8')
            print("[OK] layout - cert view modal اضافه شد")


# چک کن Create.php listener داره
cp = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if cp.exists():
    txt = cp.read_text(encoding='utf-8')
    if 'open-cert-form' not in txt:
        print("[WARN] Create.php listener نداره!")
    else:
        print("[OK] Create.php listener OK")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")