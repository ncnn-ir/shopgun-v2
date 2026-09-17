# -*- coding: utf-8 -*-
"""ShopGun V2 - DEEP FIX"""
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
# 1. CERTRENDERER.PHP — بازنویسی کامل با CSS Variables
# ═══════════════════════════════════════════════════════════════

CERTRENDERER = r'''<?php

namespace App\Services;

use App\Models\Certificate;
use App\Support\CertConfig;
use App\Support\PersianNumber;

class CertRenderer
{
    /**
     * HTML فقط کارت (بدون DOCTYPE) — برای نمایش
     */
    public static function renderCard(Certificate $cert): string
    {
        // ★ اول design_data اگه موجود باشه
        if (!empty($cert->design_data) && is_array($cert->design_data)) {
            return self::renderFromDesign($cert, $cert->design_data);
        }

        // ★ پیش‌فرض — با CSS inline
        return self::buildCard($cert);
    }

    /**
     * HTML کامل با DOCTYPE — برای iframe/چاپ
     */
    public static function renderHtml(Certificate $cert): string
    {
        $card = self::renderCard($cert);
        return self::wrapHtml($card);
    }

    /**
     * چند کارت برای چاپ A4
     */
    public static function renderBatchHtml(array $certs, int $cols = 3): string
    {
        $sizes = CertConfig::sizes();
        $cw = (float) ($sizes['width'] ?? 6.5);
        $ch = (float) ($sizes['height'] ?? 6.5);
        $gap = $cols === 1 ? 0 : round((210 - ($cols * $cw) - 6) / max(1, $cols - 1), 2);

        $cards = '';
        foreach ($certs as $cert) {
            $cards .= '<div class="batch-card">' . self::renderCard($cert) . '</div>';
        }

        $css = self::inlineCss(CertConfig::sizes(), CertConfig::assets(), CertConfig::hideDesc());

        return '<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">'
            . '<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">'
            . '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
            . '<style>' . $css . '</style>'
            . '<style>'
            . '@page{size:A4 portrait;margin:3mm}'
            . '*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}'
            . 'html,body{background:#fff;margin:0!important;padding:0!important;width:210mm}'
            . '.cert-print-grid{display:grid;grid-template-columns:repeat(' . $cols . ',' . $cw . 'cm);'
            . 'column-gap:' . $gap . 'cm;row-gap:2mm;justify-content:start;align-content:start;padding:0;width:100%;direction:rtl}'
            . '.batch-card .certificate{width:' . $cw . 'cm!important;height:' . $ch . 'cm!important;'
            . 'page-break-inside:avoid;break-inside:avoid;box-shadow:none!important;'
            . 'transform:none!important;margin:0!important}'
            . '</style>'
            . '</head><body><div class="cert-print-grid">' . $cards . '</div></body></html>';
    }

    /**
     * ★ ساخت کارت با همه اندازه‌ها از CertConfig
     */
    protected static function buildCard(Certificate $cert): string
    {
        $sizes   = CertConfig::sizes();
        $assets  = CertConfig::assets();
        $hide    = CertConfig::hideDesc();
        $logos   = CertConfig::logos();
        $logoSize = CertConfig::logoSize();
        $descSize = CertConfig::descImageSize();

        // ابعاد فیزیکی
        $cw = (float) ($sizes['width']  ?? 6.5);
        $ch = (float) ($sizes['height'] ?? 6.5);
        $pxW = (int) round($cw * 96 / 2.54);
        $pxH = (int) round($ch * 96 / 2.54);

        // ★ همه اندازه‌ها
        $imgW = (int) ($sizes['img_w'] ?? 120);
        $imgH = (int) ($sizes['img_h'] ?? 120);
        $qrS  = (int) ($sizes['qr_size'] ?? 40);
        $titleFont = (int) ($sizes['title_font'] ?? 20);
        $codeFont  = (int) ($sizes['code_font'] ?? 11);
        $descFont  = (int) ($sizes['desc_font'] ?? 7);

        // محتوا
        $code   = e($cert->code);
        $serial = e($cert->serial ?? '');
        $stoneEn = e($cert->stone_en ?? '');
        $metalEn = e($cert->metal_en ?? $cert->metal ?? '');
        $carat   = e($cert->metal_carat ?? '');
        $origin  = e($cert->stone_origin ?? '');
        $flag    = $cert->stone_flag ?? '';
        $flagUrl = $flag ? 'https://flagcdn.com/w40/' . strtolower($flag) . '.png' : '';
        $length  = e($cert->length_clean ?? '0');
        $widthS  = e($cert->width_clean  ?? '0');
        $weight  = e($cert->weight_clean ?? '0');
        $brill   = PersianNumber::toFa($cert->brilliant_clean ?? '0');
        $qrUrl   = $cert->qr_url;

        // تصویر
        $imgSrc = '';
        if (!empty($cert->image_url)) $imgSrc = $cert->image_url;
        elseif (!empty($cert->image_path)) $imgSrc = asset('storage/' . $cert->image_path);

        $imgInner = $imgSrc
            ? '<img src="' . e($imgSrc) . '" alt="" crossorigin="anonymous" style="width:100%;height:100%;object-fit:cover;display:block">'
            : '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;color:#ccc">💎</div>';

        // لوگوها
        $logoHtml = '';
        if (!empty($logos)) {
            foreach ($logos as $l) {
                $logoHtml .= '<div class="ico" style="width:' . $logoSize . 'px;height:' . $logoSize . 'px;margin:0 3px"><img src="' . e($l) . '" alt="" crossorigin="anonymous" style="width:100%;height:100%;object-fit:contain"></div>';
            }
        } elseif (!empty($assets['logo_image'])) {
            $logoHtml = '<div class="ico"><img src="' . e($assets['logo_image']) . '" alt="" crossorigin="anonymous"></div>';
        } else {
            $logoHtml = '<div class="ico"><span>💎</span></div>';
        }

        // توضیحات (تصویر یا متن)
        $descHtml = '';
        if (!$hide) {
            if (!empty($assets['desc_image'])) {
                $descHtml = '<img src="' . e($assets['desc_image']) . '" alt="" crossorigin="anonymous" style="max-width:' . $descSize['w'] . 'px;max-height:' . $descSize['h'] . 'px;object-fit:contain;display:block;margin:auto">';
            } else {
                $descHtml = '<div class="cert-auth-text" style="font-size:' . $descFont . 'px">This certificate is only for authenticity of purchased product.</div>';
            }
        }

        $flagHtml = $flagUrl ? '<img src="' . e($flagUrl) . '" style="width:14px;vertical-align:middle;border-radius:2px" alt="">' : '';

        $bgStyle = !empty($assets['bg_image']) ? 'background-image:url(\'' . e($assets['bg_image']) . '\');' : '';

        // ★ ساخت کارت با inline styles
        $card = <<<HTML
<div class="certificate" data-cert-code="{$code}" style="width:{$pxW}px;height:{$pxH}px">
  <div class="cert-bg-layer" style="{$bgStyle}"></div>
  <div class="cert-main">
    <div class="cert-top-section">
      <div class="cert-right-text">
        <div class="cert-title-script" style="font-size:{$titleFont}px">Certificate</div>
        <div class="cert-subtitle-script" style="font-size:{$descFont}px">Quality Guarantee</div>
        <div class="cert-desc-area">{$descHtml}</div>
        <div class="cert-sig-block">
          <div class="cert-sig-line">Quality Guarantee</div>
          <div class="cert-sig-label">تضمین کیفیت</div>
        </div>
      </div>
      <div class="cert-img-frame-wrap" style="width:{$imgW}px;height:{$imgH}px">
        <div class="cert-img-frame">{$imgInner}</div>
        <div class="cert-serial-balloon">{$serial}</div>
      </div>
    </div>
    <div class="cert-qr-panel">
      <div class="cert-logo-mini">{$logoHtml}</div>
      <div class="cert-qr-wrap">
        <div class="cert-qr-url">mashahirid.ir/{$code}</div>
        <div class="cert-qr-inner">
          <div class="cert-qr-box" style="width:{$qrS}px;height:{$qrS}px">
            <img src="{$qrUrl}" alt="QR">
          </div>
          <div class="cert-code-inline">
            <span class="lbl">CODE</span>
            <span class="val" style="font-size:{$codeFont}px">{$code}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="cert-table-wrap">
      <table class="cert-bottom-table">
        <colgroup>
          <col style="width:{$__c1 = (CertConfig::cols()[0] ?? 25)}%">
          <col style="width:{$__c2 = (CertConfig::cols()[1] ?? 25)}%">
          <col style="width:{$__c3 = (CertConfig::cols()[2] ?? 25)}%">
          <col style="width:{$__c4 = (CertConfig::cols()[3] ?? 25)}%">
        </colgroup>
        <tr>
          <td class="tbl-label">Stone</td><td class="tbl-value">{$stoneEn}</td>
          <td class="tbl-label">Metal</td><td class="tbl-value">{$metalEn} <span class="unit">{$carat}</span></td>
        </tr>
        <tr>
          <td class="tbl-label">Originality</td><td class="tbl-value">{$origin} {$flagHtml}</td>
          <td class="tbl-label">Stone S</td><td class="tbl-value">{$length}*{$widthS} <span class="unit">mm</span></td>
        </tr>
        <tr>
          <td class="tbl-label">Brillant</td><td class="tbl-value">{$brill}</td>
          <td class="tbl-label">Total W</td><td class="tbl-value">{$weight} <span class="unit">gr</span></td>
        </tr>
      </table>
    </div>
  </div>
</div>
HTML;

        return '<style>' . self::inlineCss($sizes, $assets, $hide) . '</style>' . $card;
    }

    protected static function wrapHtml(string $card): string
    {
        return '<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">'
            . '<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">'
            . '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
            . '</head><body style="margin:0;padding:0;background:transparent;display:flex;justify-content:center;align-items:center">'
            . $card . '</body></html>';
    }

    protected static function renderFromDesign(Certificate $cert, array $design): string
    {
        // فعلا ساده — بدون design data
        return self::buildCard($cert);
    }

    protected static function inlineCss(array $sizes, array $assets, bool $hide): string
    {
        return <<<CSS
.certificate{background:#fffef9;color:#2c3e50;position:relative;overflow:hidden;font-family:'Inter','Vazirmatn',Tahoma,sans-serif;font-size:11px;border:1px solid #999;border-radius:10px;box-sizing:border-box;line-height:1.2}
.certificate *{box-sizing:border-box}
.certificate .cert-bg-layer{position:absolute;inset:0;background-size:cover;background-position:center;z-index:0;opacity:.12;pointer-events:none;border-radius:10px}
.certificate .cert-main{position:relative;z-index:3;width:100%;height:100%;padding:8px;display:flex;flex-direction:column}
.certificate .cert-top-section{display:flex;gap:8px;margin-bottom:4px;flex:0 0 auto;overflow:hidden}
.certificate .cert-right-text{flex:1;display:flex;flex-direction:column;padding:2px 0 2px 4px;text-align:right;min-width:60px}
.certificate .cert-title-script{font-family:'Great Vibes',cursive;color:#6b4423;line-height:1}
.certificate .cert-subtitle-script{font-family:'Playfair Display',serif;color:#6b4423;font-style:italic;margin-bottom:6px}
.certificate .cert-desc-area{flex:1;text-align:right;display:flex;align-items:center;justify-content:flex-end}
.certificate .cert-desc-area img{max-width:100%;max-height:100%;object-fit:contain}
.certificate .cert-auth-text{font-family:'Playfair Display',serif;color:#6b4423;line-height:1.5;text-align:right}
.certificate .cert-sig-block{text-align:right;margin-top:4px}
.certificate .cert-sig-line{font-family:'Great Vibes',cursive;font-size:12px;color:#6b4423;border-bottom:1px solid #6b4423;display:inline-block;padding:0 6px 2px;min-width:70px}
.certificate .cert-sig-label{font-family:'Playfair Display',serif;font-size:6px;color:#999;margin-top:2px}
.certificate .cert-img-frame-wrap{flex:0 0 auto;position:relative;padding:4px;border:1px solid #b8860b;border-radius:8px;background:#fff;overflow:hidden;align-self:flex-start}
.certificate .cert-img-frame{width:100%;height:100%;border:1.5px solid #b8860b;border-radius:6px;overflow:hidden;background:#f8f5ef}
.certificate .cert-img-frame img{width:100%;height:100%;object-fit:cover;display:block}
.certificate .cert-serial-balloon{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.55);color:#fff;font-family:monospace;font-size:5px;font-weight:700;padding:2px 6px;border-radius:8px;white-space:nowrap}
.certificate .cert-qr-panel{display:flex;gap:6px;align-items:center;padding:4px 2px;margin-bottom:4px;justify-content:flex-end;flex:0 0 auto}
.certificate .cert-qr-wrap{display:flex;flex-direction:column;align-items:center;background:#fff;border:1px solid #0d5c63;border-radius:6px;padding:3px 4px}
.certificate .cert-qr-url{color:#1a5276;font-weight:600;font-size:6px;direction:ltr;margin-bottom:2px}
.certificate .cert-qr-inner{display:flex;gap:6px;align-items:center}
.certificate .cert-qr-box{background:#fff;border-radius:3px;overflow:hidden;flex-shrink:0}
.certificate .cert-qr-box img{width:100%;height:100%;object-fit:contain;display:block}
.certificate .cert-code-inline{display:flex;flex-direction:column;align-items:flex-start;gap:2px}
.certificate .cert-code-inline .lbl{font-size:6px;color:#7f8c8d;text-transform:uppercase}
.certificate .cert-code-inline .val{font-family:monospace;font-weight:700;color:#1a5276;letter-spacing:.8px}
.certificate .cert-logo-mini{display:flex;align-items:center;gap:4px;margin-right:auto;flex-wrap:nowrap;max-width:50%;overflow:hidden}
.certificate .cert-logo-mini .ico{display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0}
.certificate .cert-logo-mini .ico img{width:100%;height:100%;object-fit:contain;display:block}
.certificate .cert-table-wrap{width:100%;flex:0 0 auto;border-radius:8px;overflow:hidden;border:1.5px solid #0d5c63;background:#fff}
.certificate .cert-bottom-table{width:100%;border-collapse:collapse;table-layout:fixed}
.certificate .cert-bottom-table td{border:1px solid #7fbfc4;vertical-align:middle;padding:2px 3px;overflow:hidden;text-overflow:ellipsis;word-break:break-word}
.certificate .cert-bottom-table .tbl-label{background:#0d5c63;color:#e0f7f8;font-weight:700;text-align:right;font-size:8px}
.certificate .cert-bottom-table .tbl-value{background:#fff;color:#2c3e50;font-weight:600;text-align:right;font-size:8px}
.certificate .cert-bottom-table .unit{float:left;font-size:6px;color:#888;font-weight:400}
CSS;
    }
}
'''

write('app/Services/CertRenderer.php', CERTRENDERER)


# ═══════════════════════════════════════════════════════════════
# 2. SETTINGS — fix logo upload with wire:model
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    # تغییر input لوگو
    old = '<input type="file" wire:model="logoUpload" accept="image/*"\n                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">'
    new = '<input type="file" wire:model="logoUpload" accept="image/*"\n                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">\n                    <div wire:loading wire:target="logoUpload" style="font-size:11px;color:#0891b2;margin-top:4px">⏳ در حال آپلود...</div>'
    if old in txt:
        txt = txt.replace(old, new)

    # desc upload
    old2 = '<input type="file" wire:model="descUpload" accept="image/*"\n                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">'
    new2 = '<input type="file" wire:model="descUpload" accept="image/*"\n                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">\n                    <div wire:loading wire:target="descUpload" style="font-size:11px;color:#0891b2;margin-top:4px">⏳ در حال آپلود...</div>'

    if old2 in txt:
        txt = txt.replace(old2, new2)

    sv.write_text(txt, encoding='utf-8')
    print("[OK] settings blade - wire:model")


# ═══════════════════════════════════════════════════════════════
# 3. SETTINGS PHP — updated hooks برای upload
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # اضافه کردن updated hooks
    if 'public function updatedLogoUpload' not in txt:
        hooks = '''
    public function updatedLogoUpload(): void
    {
        if (!$this->logoUpload) return;
        try {
            $path = $this->logoUpload->store('logos', 'public');
            if ($path) {
                $arr = $this->logo_images;
                $arr[] = $path;
                $this->logo_images = array_values($arr);
                AppSetting::put('logo_images', $this->logo_images, 'certificate');
                Cache::forget('app_settings_all');
                $this->logoUpload = null;
                $this->dispatch('notify', type: 'success', message: 'لوگو اضافه شد');
            }
        } catch (\\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function updatedDescUpload(): void
    {
        if (!$this->descUpload) return;
        try {
            $path = $this->descUpload->store('desc', 'public');
            if ($path) {
                $this->desc_image = $path;
                AppSetting::put('desc_image', $path, 'certificate');
                Cache::forget('app_settings_all');
                $this->descUpload = null;
                $this->dispatch('notify', type: 'success', message: 'تصویر ذخیره شد');
            }
        } catch (\\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }
'''
        txt = txt.replace('    public function render()', hooks + '\n    public function render()', 1)

    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - upload hooks")


# ═══════════════════════════════════════════════════════════════
# 4. VIEW MODAL — دانلود PNG با iframe
# ═══════════════════════════════════════════════════════════════

vm_path = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm_path.exists():
    txt = vm_path.read_text(encoding='utf-8')

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
    // ★ راه‌حل: لود HTML کامل کارت در iframe با style
    var iframe = document.createElement('iframe');
    iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:1200px;height:1200px;border:0';
    document.body.appendChild(iframe);

    var doc = iframe.contentDocument || iframe.contentWindow.document;
    // ★ دریافت HTML کامل با style از route
    fetch('{{ route('certificates.download-html', ['certificate' => $certificate->id ?? 0]) }}')
        .then(function(r) { return r.text(); })
        .then(function(html) {
            doc.open();
            doc.write(html);
            doc.close();

            // منتظر لود شدن تصاویر و فونت‌ها
            setTimeout(function() {
                var card = doc.querySelector('.certificate');
                if (!card) {
                    document.body.removeChild(iframe);
                    alert('کارت پیدا نشد');
                    return;
                }

                html2canvas(card, {
                    scale: 3,
                    backgroundColor: '#fffef9',
                    useCORS: true,
                    allowTaint: true,
                    logging: false
                }).then(function(canvas) {
                    document.body.removeChild(iframe);
                    var a = document.createElement('a');
                    a.download = 'certificate-{{ $certificate->code ?? "card" }}.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                }).catch(function(e) {
                    document.body.removeChild(iframe);
                    alert('خطا: ' + e.message);
                });
            }, 1500);
        })
        .catch(function(e) {
            document.body.removeChild(iframe);
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

    vm_path.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - iframe download")


# ═══════════════════════════════════════════════════════════════
# 5. ROUTE — download-html
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')

    if 'download-html' not in txt:
        marker = "Route::get('/{certificate}', CertificatesShow::class)->name('show');"
        new_route = """Route::get('/{certificate}/download-html', function (\\App\\Models\\Certificate $certificate) {
            return response(\\App\\Services\\CertRenderer::renderHtml($certificate), 200)
                ->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('download-html');

        """
        if marker in txt:
            txt = txt.replace(marker, new_route + marker, 1)
            routes.write_text(txt, encoding='utf-8')
            print("[OK] route download-html")


# ═══════════════════════════════════════════════════════════════
# 6. CREATE.PHP — بررسی و اصلاح
# ═══════════════════════════════════════════════════════════════

cp = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if cp.exists():
    txt = cp.read_text(encoding='utf-8')
    issues = []
    if '#[On(\'open-cert-form\')]' not in txt:
        issues.append("listener نبود")
    if 'public function openModal' not in txt:
        issues.append("openModal نبود")
    if 'public bool $show' not in txt:
        issues.append("show prop نبود")
    
    if issues:
        print("[WARN] Create.php: " + "، ".join(issues))
    else:
        print("[OK] Create.php OK")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")