# -*- coding: utf-8 -*-
"""ShopGun V2 - Fix sliders live + desc hides text + logo x + download"""
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. SETTINGS/INDEX.PHP — اضافه کردن logo_offset_x
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    if 'logo_offset_x' not in txt:
        txt = txt.replace(
            "public int $logo_size = 60;",
            "public int $logo_size = 60;\n    public int $logo_offset_x = 50;"
        )
        txt = txt.replace(
            "$this->logo_size = (int) AppSetting::get('logo_size', 60);",
            "$this->logo_size = (int) AppSetting::get('logo_size', 60);\n        $this->logo_offset_x = (int) AppSetting::get('logo_offset_x', 50);"
        )
        txt = txt.replace(
            "'logo_size' => $this->logo_size,",
            "'logo_size' => $this->logo_size,\n            'logo_offset_x' => $this->logo_offset_x,"
        )
        txt = txt.replace(
            "'logo_images' => $this->logo_images,\n            'logo_size' => $this->logo_size,",
            "'logo_images' => $this->logo_images,\n            'logo_size' => $this->logo_size,\n            'logo_offset_x' => $this->logo_offset_x,"
        )

    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - logo_offset_x")


# ═══════════════════════════════════════════════════════════════
# 2. CERTCONFIG.PHP — logoOffsetX
# ═══════════════════════════════════════════════════════════════

cc = ROOT / 'app' / 'Support' / 'CertConfig.php'
if cc.exists():
    txt = cc.read_text(encoding='utf-8')

    if 'logoOffsetX' not in txt:
        method = '''
    /**
     * ★ موقعیت افقی لوگو (0-100 درصد)
     */
    public static function logoOffsetX(): int
    {
        try {
            return (int) AppSetting::get('logo_offset_x', 50);
        } catch (\\Throwable $e) {}
        return 50;
    }
'''
        txt = txt.replace('    public static function resolveUrl', method + '\n    public static function resolveUrl', 1)

    cc.write_text(txt, encoding='utf-8')
    print("[OK] CertConfig - logoOffsetX")


# ═══════════════════════════════════════════════════════════════
# 3. CERTRENDERER.PHP — موقعیت لوگو + hide sig block
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # جابجایی لوگو با offset
    old = '$logoHtml = \'\';'
    new = '$logoOffset = CertConfig::logoOffsetX();\n        $logoHtml = \'\';'
    if 'logoOffset' not in txt:
        txt = txt.replace(old, new, 1)

    # اضافه کردن position:absolute برای لوگو
    old_logo_div = "foreach ($logos as $l) {\n                $logoHtml .= '<div class=\"ico\" style=\"width:' . $logoSize . 'px;height:' . $logoSize . 'px;margin:0 3px\">"
    new_logo_div = "foreach ($logos as $l) {\n                $logoHtml .= '<div class=\"ico\" style=\"width:' . $logoSize . 'px;height:' . $logoSize . 'px;margin:0 3px\">"
    # همونجا بذار — کاری نمی‌کنیم
    
    # ★ hide sig block اگه desc_image
    old_sig = '''<div class="cert-sig-block">
          <div class="cert-sig-line">Quality Guarantee</div>
          <div class="cert-sig-label">تضمین کیفیت</div>
        </div>'''
    
    new_sig = '$sigBlock'
    
    if old_sig in txt:
        txt = txt.replace(old_sig, new_sig, 1)
        # اضافه کردن محاسبه sigBlock
        marker = "$flagHtml = $flagUrl ?"
        if marker in txt:
            before = '''$hasDescImage = !empty($assets['desc_image']);
        $sigBlock = '';
        if (!$hasDescImage) {
            $sigBlock = '<div class="cert-sig-block"><div class="cert-sig-line">Quality Guarantee</div><div class="cert-sig-label">تضمین کیفیت</div></div>';
        }

        '''
            txt = txt.replace(marker, before + marker, 1)
            print("[OK] CertRenderer - sig hide when desc image")

    # ★ موقعیت افقی لوگو — با flex justify
    old_panel = '<div class="cert-logo-mini">{$logoHtml}</div>'
    new_panel = '<div class="cert-logo-mini" style="position:relative;width:100%;height:' . ($logoSize + 10) . 'px;display:block"><div style="position:absolute;top:0;right:{$logoOffset}%;transform:translateX(50%);display:flex;align-items:center">{$logoHtml}</div></div>'
    if old_panel in txt:
        txt = txt.replace(old_panel, new_panel, 1)
        print("[OK] CertRenderer - logo offset")

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer.php")


# ═══════════════════════════════════════════════════════════════
# 4. SETTINGS BLADE — live (بدون debounce) + logo x slider + wire:key
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    # ★ تغییر همه debounce.200ms به live (بدون debounce)
    txt = re.sub(r'wire:model\.live\.debounce\.\d+ms=', 'wire:model.live=', txt)
    txt = re.sub(r'wire:model\.live\.debounce\.\d+ms="', 'wire:model.live="', txt)

    # ★ اضافه کردن wire:key به preview برای force re-render
    old_preview = '''<div style="transform-origin:top center">
                            {!! $this->previewCard !!}
                        </div>'''
    
    new_preview = '''<div wire:key="cert-preview-{{ md5(($cert_width ?? 0) . ($cert_height ?? 0) . ($cert_img_w ?? 0) . ($cert_img_h ?? 0) . ($cert_qr_size ?? 0) . ($cert_title_font ?? 0) . ($cert_code_font ?? 0) . ($cert_desc_font ?? 0) . ($cert_col1 ?? 0) . ($cert_col2 ?? 0) . ($cert_col3 ?? 0) . ($cert_col4 ?? 0) . ($cert_hide_desc ? 1 : 0) . ($logo_size ?? 0) . ($logo_offset_x ?? 50) . ($desc_image ?: '')) }}" style="transform-origin:top center">
                            {!! $this->previewCard !!}
                        </div>'''
    
    if old_preview in txt:
        txt = txt.replace(old_preview, new_preview, 1)
        print("[OK] blade - wire:key on preview")

    # ★ اضافه کردن اسلایدر افقی لوگو
    old_logo_size = '''<div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:12px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">اندازه</label>
                        <input type="range" min="20" max="120" step="4" wire:model.live="logo_size" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $logo_size }}px</span>
                    </div>'''
    
    new_logo_size = '''<div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:12px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">اندازه</label>
                        <input type="range" min="20" max="120" step="4" wire:model.live="logo_size" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $logo_size }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:8px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">موقعیت افقی</label>
                        <input type="range" min="5" max="95" step="1" wire:model.live="logo_offset_x" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $logo_offset_x }}%</span>
                    </div>'''

    if old_logo_size in txt:
        txt = txt.replace(old_logo_size, new_logo_size, 1)
        print("[OK] blade - logo offset slider")

    sv.write_text(txt, encoding='utf-8')
    print("[OK] settings blade")


# ═══════════════════════════════════════════════════════════════
# 5. ROUTE — download-html
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')

    # حذف نسخه قدیمی
    if 'download-html' in txt:
        txt = re.sub(
            r'Route::get\(\'/\{certificate\}/download-html\'.*?\}\)->name\(\'download-html\'\);\s*',
            '',
            txt,
            flags=re.DOTALL
        )
        print("[OK] deleted old download-html route")

    # اضافه کردن نسخه جدید
    marker = "Route::get('/{certificate}', CertificatesShow::class)->name('show');"
    new_route = '''Route::get('/{certificate}/render', function (\\App\\Models\\Certificate $certificate) {
            $html = \\App\\Services\\CertRenderer::renderHtml($certificate);
            return response($html)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('render');

        '''
    
    if marker in txt:
        txt = txt.replace(marker, new_route + marker, 1)
        routes.write_text(txt, encoding='utf-8')
        print("[OK] route certificates.render")


# ═══════════════════════════════════════════════════════════════
# 6. VIEW MODAL — download از render route
# ═══════════════════════════════════════════════════════════════

vm = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm.exists():
    txt = vm.read_text(encoding='utf-8')

    # حذف اسکریپت‌های قدیمی
    txt = re.sub(
        r'<script[^>]*html2canvas[^>]*></script>\s*<script>.*?</script>',
        '',
        txt,
        flags=re.DOTALL
    )

    NEW_SCRIPT = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCertModal() {
    var certId = {{ $certificate->id ?? 0 }};
    if (!certId) { alert('شناسنامه پیدا نشد'); return; }

    // ★ راه‌حل: استفاده از render route که HTML کامل با style میده
    fetch('/certificates/' + certId + '/render')
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        })
        .then(function(html) {
            // ساخت iframe مخفی
            var iframe = document.createElement('iframe');
            iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:1400px;height:1400px;border:0';
            document.body.appendChild(iframe);

            var doc = iframe.contentDocument || iframe.contentWindow.document;
            doc.open();
            doc.write(html);
            doc.close();

            // صبر کن همه چیز لود بشه
            setTimeout(function() {
                var card = doc.querySelector('.certificate');
                if (!card) {
                    document.body.removeChild(iframe);
                    alert('کارت در HTML نبود');
                    return;
                }

                // اطمینان از ابعاد درست
                var cw = card.offsetWidth || 600;
                var ch = card.offsetHeight || 600;

                html2canvas(card, {
                    scale: 3,
                    backgroundColor: '#fffef9',
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    width: cw,
                    height: ch,
                    windowWidth: cw,
                    windowHeight: ch,
                    onclone: function(clonedDoc) {
                        // ★ پاک کردن oklch در cloned doc
                        var clonedCard = clonedDoc.querySelector('.certificate');
                        if (clonedCard) {
                            var els = [clonedCard].concat(Array.from(clonedCard.querySelectorAll('*')));
                            els.forEach(function(el) {
                                var cs = window.getComputedStyle(el);
                                ['color', 'backgroundColor', 'borderColor', 'fill', 'stroke'].forEach(function(prop) {
                                    var val = cs[prop];
                                    if (val && val.indexOf('oklch') !== -1) {
                                        el.style[prop] = '#999999';
                                    }
                                });
                            });
                        }
                    }
                }).then(function(canvas) {
                    document.body.removeChild(iframe);
                    var a = document.createElement('a');
                    a.download = 'certificate-{{ $certificate->code ?? "card" }}.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                }).catch(function(e) {
                    document.body.removeChild(iframe);
                    alert('خطا در ساخت PNG: ' + e.message);
                });
            }, 1800);
        })
        .catch(function(e) {
            alert('خطا در دریافت HTML: ' + e.message);
        });
}
</script>
'''

    last = txt.rfind('</div>')
    if last > 0:
        txt = txt[:last] + '</div>\n' + NEW_SCRIPT
    else:
        txt += NEW_SCRIPT

    vm.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - download جدید")


# ═══════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")