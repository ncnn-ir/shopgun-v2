# -*- coding: utf-8 -*-
"""ShopGun V2 - ROOT FIX: CertConfig reads from AppSetting"""
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
# 1. CERTCONFIG.PHP — بازنویسی کامل با AppSetting
# ═══════════════════════════════════════════════════════════════

CERTCONFIG = r'''<?php

namespace App\Support;

use App\Models\AppSetting;
use App\Models\CertSetting;

class CertConfig
{
    public const DEFAULT_WIDTH  = 6.5;
    public const DEFAULT_HEIGHT = 6.5;

    /** override موقت برای پیش‌نمایش */
    public static ?array $overrideSizes = null;
    public static ?array $overrideCols = null;
    public static ?bool  $overrideHideDesc = null;
    public static ?array $overrideLogos = null;
    public static ?string $overrideDescImage = null;

    /**
     * خواندن تنظیمات ابعاد
     */
    public static function sizes($source = null): array
    {
        // ۱. پیش‌فرض‌ها
        $d = [
            'width'  => self::DEFAULT_WIDTH,
            'height' => self::DEFAULT_HEIGHT,

            // snake_case
            'img_w' => 120, 'img_h' => 120,
            'qr_size' => 40, 'logo_w' => 28, 'logo_h' => 22,
            'code_font' => 11, 'url_font' => 6, 'table_font' => 8,
            'title_font' => 20, 'desc_font' => 7,
            'table_label_font' => 8, 'table_value_font' => 8,

            // camelCase
            'imgW' => 120, 'imgH' => 120,
            'qrSize' => 40, 'logoW' => 28, 'logoH' => 22,
            'codeFont' => 11, 'urlFont' => 6, 'tableFont' => 8,
            'titleFont' => 20, 'descFont' => 7,
            'tableLabelFont' => 8, 'tableValueFont' => 8,
        ];

        // ۲. ★ خواندن از AppSetting — این قلب ماجراست
        try {
            if (\Illuminate\Support\Facades\Schema::hasTable('app_settings')) {
                $d['width']  = (float) AppSetting::get('cert_width',  $d['width']);
                $d['height'] = (float) AppSetting::get('cert_height', $d['height']);
                $d['img_w']  = (int)   AppSetting::get('cert_img_w',  $d['img_w']);
                $d['img_h']  = (int)   AppSetting::get('cert_img_h',  $d['img_h']);
                $d['qr_size']= (int)   AppSetting::get('cert_qr_size',$d['qr_size']);
                $d['logo_w'] = (int)   AppSetting::get('cert_logo_w', $d['logo_w']);
                $d['logo_h'] = (int)   AppSetting::get('cert_logo_h', $d['logo_h']);
                $d['code_font']  = (int) AppSetting::get('cert_code_font',  $d['code_font']);
                $d['title_font'] = (int) AppSetting::get('cert_title_font', $d['title_font']);
                $d['desc_font']  = (int) AppSetting::get('cert_desc_font',  $d['desc_font']);

                // camelCase همگام
                $d['imgW']  = $d['img_w'];
                $d['imgH']  = $d['img_h'];
                $d['qrSize']= $d['qr_size'];
                $d['logoW'] = $d['logo_w'];
                $d['logoH'] = $d['logo_h'];
                $d['codeFont']  = $d['code_font'];
                $d['titleFont'] = $d['title_font'];
                $d['descFont']  = $d['desc_font'];
            }
        } catch (\Throwable $e) {}

        // ۳. اگر source داده شده
        $saved = null;
        if (is_array($source)) $saved = $source;
        elseif (is_object($source) && isset($source->sizes) && is_array($source->sizes)) $saved = $source->sizes;

        if ($saved !== null) {
            $d = array_merge($d, $saved);
        }

        // ۴. override (پیش‌نمایش زنده) — بالاترین اولویت
        if (self::$overrideSizes !== null) {
            $d = array_merge($d, self::$overrideSizes);
        }

        return $d;
    }

    /**
     * خواندن assets (bg, logos, desc)
     */
    public static function assets(): array
    {
        $bg = null; $logo = null; $desc = null;

        try {
            if (\Illuminate\Support\Facades\Schema::hasTable('app_settings')) {
                $bg   = AppSetting::get('bg_image',   null);
                $logo = AppSetting::get('logo_image', null);
                $desc = AppSetting::get('desc_image', null);
            }
        } catch (\Throwable $e) {}

        // fallback به CertSetting
        if (!$bg && !$logo && !$desc) {
            try {
                if (class_exists(CertSetting::class)) {
                    $bg   = CertSetting::get('bg_image',   null);
                    $logo = CertSetting::get('logo_image', null);
                    $desc = CertSetting::get('desc_image', null);
                }
            } catch (\Throwable $e) {}
        }

        // ★ override desc image
        if (self::$overrideDescImage !== null) {
            $desc = self::$overrideDescImage;
        }

        return [
            'bg_image'   => self::resolveUrl($bg),
            'logo_image' => self::resolveUrl($logo),
            'desc_image' => self::resolveUrl($desc),
        ];
    }

    /**
     * ★ لوگوها (چندتایی) — لیست URL
     */
    public static function logos(): array
    {
        // override
        if (self::$overrideLogos !== null) {
            return array_map(fn($l) => self::resolveUrl($l), self::$overrideLogos);
        }

        try {
            if (\Illuminate\Support\Facades\Schema::hasTable('app_settings')) {
                $logos = AppSetting::get('logo_images', []);
                if (is_array($logos) && !empty($logos)) {
                    return array_map(fn($l) => self::resolveUrl($l), $logos);
                }
            }
        } catch (\Throwable $e) {}

        return [];
    }

    /**
     * ★ اندازه لوگو
     */
    public static function logoSize(): int
    {
        if (self::$overrideSizes !== null && isset(self::$overrideSizes['logo_size'])) {
            return (int) self::$overrideSizes['logo_size'];
        }
        try {
            return (int) AppSetting::get('logo_size', 60);
        } catch (\Throwable $e) {}
        return 60;
    }

    /**
     * ★ ابعاد تصویر توضیحات
     */
    public static function descImageSize(): array
    {
        try {
            return [
                'w' => (int) AppSetting::get('desc_image_w', 120),
                'h' => (int) AppSetting::get('desc_image_h', 80),
            ];
        } catch (\Throwable $e) {}
        return ['w' => 120, 'h' => 80];
    }

    /**
     * ★ ستون‌های جدول
     */
    public static function cols(): array
    {
        if (self::$overrideCols !== null) return self::$overrideCols;
        try {
            return [
                (int) AppSetting::get('cert_col1', 25),
                (int) AppSetting::get('cert_col2', 25),
                (int) AppSetting::get('cert_col3', 25),
                (int) AppSetting::get('cert_col4', 25),
            ];
        } catch (\Throwable $e) {}
        return [25, 25, 25, 25];
    }

    public static function resolveUrl($v): ?string
    {
        if (!$v || !is_string($v)) return null;
        if (str_starts_with($v, 'http') || str_starts_with($v, 'data:')) return $v;
        $c = ltrim($v, '/');
        if (str_starts_with($c, 'storage/')) return asset($c);
        if (file_exists(public_path($c))) return asset($c);
        return asset('storage/' . $c);
    }

    public static function hideDesc(): bool
    {
        if (self::$overrideHideDesc !== null) return self::$overrideHideDesc;
        try {
            return (bool) AppSetting::get('cert_hide_desc', false);
        } catch (\Throwable $e) {}
        return false;
    }
}
'''

write('app/Support/CertConfig.php', CERTCONFIG)


# ═══════════════════════════════════════════════════════════════
# 2. CERTRENDERER.PHP — استفاده از CertConfig::logos + descImage
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # پاک کردن override های قبلی و نوشتن clean
    import re
    
    # در buildCardInner — جایگزینی logo
    old_logo = re.search(
        r"\$logoHtml\s*=\s*!empty\(\$assets\['logo_image'\]\).*?;",
        txt,
        flags=re.DOTALL
    )
    
    new_logo = '''$logoHtml = '';
        $_logos = \\App\\Support\\CertConfig::logos();
        $_logoSize = \\App\\Support\\CertConfig::logoSize();

        if (!empty($_logos)) {
            foreach ($_logos as $_l) {
                $logoHtml .= '<div class="ico" style="width:' . $_logoSize . 'px;height:' . $_logoSize . 'px;margin:0 3px"><img src="' . e($_l) . '" alt="" crossorigin="anonymous" style="width:100%;height:100%;object-fit:contain"></div>';
            }
        } elseif (!empty($assets['logo_image'])) {
            $logoHtml = '<div class="ico"><img src="' . e($assets['logo_image']) . '" alt="" crossorigin="anonymous"></div>';
        } else {
            $logoHtml = '<div class="ico"><span>💎</span></div>';
        }'''
    
    if old_logo:
        txt = txt[:old_logo.start()] + new_logo + txt[old_logo.end():]
        print("[OK] CertRenderer - logo جدید")

    # در buildCardInner — جایگزینی desc
    old_desc = re.search(
        r"\$descHtml\s*=\s*'';\s*\n\s*if\s*\(!\$hide\).*?;",
        txt,
        flags=re.DOTALL
    )
    
    new_desc = '''$descHtml = '';
        if (!$hide) {
            $_descSize = \\App\\Support\\CertConfig::descImageSize();
            if (!empty($assets['desc_image'])) {
                $descHtml = '<img src="' . e($assets['desc_image']) . '" alt="" crossorigin="anonymous" style="max-width:' . $_descSize['w'] . 'px;max-height:' . $_descSize['h'] . 'px;object-fit:contain;display:block;margin:auto">';
            } else {
                $descHtml = '<div class="cert-auth-text">This certificate is only for authenticity of purchased product.</div>';
            }
        }'''
    
    if old_desc:
        txt = txt[:old_desc.start()] + new_desc + txt[old_desc.end():]
        print("[OK] CertRenderer - desc جدید")

    # تصویر محصول — کراپ
    old_img = re.search(
        r"\$imgInner\s*=\s*\$imgSrc\s*\n\s*\?\s*'.*?'\s*\n\s*:\s*'.*?';",
        txt,
        flags=re.DOTALL
    )
    
    new_img = '''$imgInner = $imgSrc
            ? '<img src="' . e($imgSrc) . '" alt="" crossorigin="anonymous" style="width:100%;height:100%;object-fit:cover;display:block;border-radius:4px">'
            : '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;color:#ccc">💎</div>';'''
    
    if old_img:
        txt = txt[:old_img.start()] + new_img + txt[old_img.end():]
        print("[OK] CertRenderer - img cover")

    # ستون‌ها — از CertConfig::cols()
    old_cols = re.search(
        r'\$_c\s*=\s*\\App\\Support\\CertConfig::\$overrideCols.*?\$__c4\s*=\s*\$_c\[3\]\s*\?\?\s*25;',
        txt,
        flags=re.DOTALL
    )
    
    new_cols = '''$_c = \\App\\Support\\CertConfig::cols();
        $__c1 = $_c[0] ?? 25;
        $__c2 = $_c[1] ?? 25;
        $__c3 = $_c[2] ?? 25;
        $__c4 = $_c[3] ?? 25;'''
    
    if old_cols:
        txt = txt[:old_cols.start()] + new_cols + txt[old_cols.end():]
        print("[OK] CertRenderer - cols جدید")

    # CSS کراپ
    txt = txt.replace('object-fit:contain', 'object-fit:cover')
    txt = txt.replace('object-fit: contain', 'object-fit: cover')

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer - ذخیره شد")


# ═══════════════════════════════════════════════════════════════
# 3. SETTINGS/INDEX.PHP — حذف override ها (دیگه لزومی نداره)
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')
    
    # در preview_card — از override استفاده کن (چون AppSetting قطعاً ذخیره نشده)
    import re
    
    if 'CertConfig::$overrideLogos' not in txt:
        txt = txt.replace(
            "CertConfig::\$overrideHideDesc = \$this->cert_hide_desc;",
            """CertConfig::\$overrideHideDesc = \$this->cert_hide_desc;
            CertConfig::\$overrideLogos = \$this->logo_images;
            CertConfig::\$overrideDescImage = \$this->desc_image ?: null;
            CertConfig::\$overrideSizes = array_merge(CertConfig::\$overrideSizes ?? [], ['logo_size' => \$this->logo_size]);"""
        )
    
    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - override logos")


# ═══════════════════════════════════════════════════════════════
# 4. DOWNLOAD PNG — روش iframe (بدون oklch)
# ═══════════════════════════════════════════════════════════════

vm_path = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm_path.exists():
    txt = vm_path.read_text(encoding='utf-8')
    
    # حذف اسکریپت قدیمی
    import re
    txt = re.sub(
        r'<script[^>]*html2canvas[^>]*></script>\s*<script>.*?</script>',
        '',
        txt,
        flags=re.DOTALL
    )
    
    # اسکریپت جدید با iframe
    NEW_SCRIPT = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCertModal() {
    var source = document.querySelector('#cert-card-area .certificate');
    if (!source) { alert('کارت پیدا نشد'); return; }

    // ۱. ساخت iframe مخفی
    var iframe = document.createElement('iframe');
    iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:1000px;height:1000px;border:0';
    document.body.appendChild(iframe);

    var doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write('<!DOCTYPE html><html><head><meta charset="UTF-8">');
    doc.write('<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">');
    doc.write('<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">');
    doc.write('<style>body{margin:0;padding:20px;background:#fffef9;font-family:Vazirmatn,Tahoma,sans-serif}');
    doc.write('*{box-sizing:border-box}');
    doc.write('</style></head><body></body></html>');
    doc.close();

    // ۲. کپی استایل‌های inline کارت
    var clone = source.cloneNode(true);
    clone.style.transform = 'none';
    clone.style.boxShadow = '0 0 0 1px #ddd';

    iframe.contentDocument.body.appendChild(clone);

    // ۳. صبر کن تصاویر لود بشن
    var imgs = clone.querySelectorAll('img');
    var loaded = 0;
    var total = imgs.length;

    function tryCapture() {
        if (loaded < total) return;
        setTimeout(function() {
            html2canvas(clone, {
                scale: 3,
                backgroundColor: '#fffef9',
                useCORS: true,
                logging: false,
                windowWidth: 1000,
                windowHeight: 1000
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
        }, 300);
    }

    if (total === 0) {
        tryCapture();
    } else {
        imgs.forEach(function(img) {
            if (img.complete) {
                loaded++;
                tryCapture();
            } else {
                img.onload = function() { loaded++; tryCapture(); };
                img.onerror = function() { loaded++; tryCapture(); };
            }
        });
    }
}
</script>
'''
    
    # اضافه در انتها
    last_div = txt.rfind('</div>')
    if last_div > 0:
        txt = txt[:last_div] + '</div>\n' + NEW_SCRIPT
    else:
        txt += NEW_SCRIPT
    
    vm_path.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - iframe download")


# ═══════════════════════════════════════════════════════════════
# 5. DEBUG — چک Create.php
# ═══════════════════════════════════════════════════════════════

cp = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if cp.exists():
    txt = cp.read_text(encoding='utf-8')
    has_listener = '#[On(\'open-cert-form\')]' in txt
    has_show = 'public bool $show = false;' in txt
    print("[DEBUG] Create.php - listener: " + ("YES" if has_listener else "NO") + ", show prop: " + ("YES" if has_show else "NO"))


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")