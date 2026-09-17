#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix ShopGun CertConfig — رفع خطای sizes() و سایر متدهای گم‌شده
"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌ مسیر پیدا نشد"); exit(1)

# ═══════════════════════════════════════════════════════════════
# CertConfig کامل با همه متدها
# ═══════════════════════════════════════════════════════════════
CERT_CONFIG = r'''<?php

namespace App\Support;

/**
 * ╔══════════════════════════════════════════════════════════════╗
 * ║  CertConfig — تنظیمات کارت شناسنامه                          ║
 * ║  ShopGun V2                                                  ║
 * ╚══════════════════════════════════════════════════════════════╝
 */
class CertConfig
{
    /* ─── سایز پیش‌فرض کارت (cm) ─── */
    public const DEFAULT_WIDTH  = 6.5;
    public const DEFAULT_HEIGHT = 6.5;
    public const DEFAULT_QR_SIZE = 40;

    /* ─── سایز لیبل (mm) ─── */
    public const LABEL_DEFAULT_WIDTH  = 100;
    public const LABEL_DEFAULT_HEIGHT = 50;

    /* ═══════════════════════════════════════════════════════════
       ★★★ متد اصلی گم‌شده — sizes()  ★★★
       ═══════════════════════════════════════════════════════════ */

    /**
     * برگرداندن آرایه‌ی سایزها (برای CertRenderer)
     * این متد با هر دو حالت استفاده می‌شود:
     *   CertConfig::sizes()                → تنظیمات پیش‌فرض
     *   CertConfig::sizes($certificate)    → از تنظیمات ذخیره‌شده
     */
    public static function sizes($source = null): array
    {
        $defaults = [
            'imgW'           => 120,
            'imgH'           => 120,
            'qrSize'         => 40,
            'logoW'          => 28,
            'logoH'          => 22,
            'codeFont'       => 11,
            'urlFont'        => 6,
            'tableFont'      => 8,
            'titleFont'      => 20,
            'descFont'       => 7,
            'tableLabelFont' => 8,
            'tableValueFont' => 8,
        ];

        // اگر از سرور / settings آمده
        if (is_array($source)) {
            return array_merge($defaults, $source);
        }

        // اگر مدل Certificate / CertSetting آمده و فیلد sizes دارد
        if (is_object($source)) {
            if (isset($source->sizes) && is_array($source->sizes)) {
                return array_merge($defaults, $source->sizes);
            }
            if (isset($source->cert_sizes) && is_array($source->cert_sizes)) {
                return array_merge($defaults, $source->cert_sizes);
            }
            if (method_exists($source, 'getCertSizes')) {
                $s = $source->getCertSizes();
                if (is_array($s)) return array_merge($defaults, $s);
            }
        }

        // ★ تلاش برای خواندن از فایل settings یا cache
        $saved = self::loadFromStorage();
        if (is_array($saved) && !empty($saved)) {
            return array_merge($defaults, $saved);
        }

        return $defaults;
    }

    /**
     * خواندن تنظیمات از فایل storage/app/cert-config.json
     */
    protected static function loadFromStorage(): ?array
    {
        try {
            $path = storage_path('app/cert-config.json');
            if (file_exists($path)) {
                $data = json_decode(file_get_contents($path), true);
                if (isset($data['sizes']) && is_array($data['sizes'])) {
                    return $data['sizes'];
                }
                if (is_array($data)) return $data;
            }
        } catch (\Throwable $e) {
            // silent
        }
        return null;
    }

    /* ═══════════════════════════════════════════════════════════
       متدهای کمکی مشابه — برای هر کد قدیمی که این‌ها را صدا می‌زند
       ═══════════════════════════════════════════════════════════ */

    public static function defaults(): array
    {
        return [
            'width'  => self::DEFAULT_WIDTH,
            'height' => self::DEFAULT_HEIGHT,
            'sizes'  => self::sizes(),
        ];
    }

    /** فقط ابعاد کارت */
    public static function dimensions(): array
    {
        return [
            'width'  => self::DEFAULT_WIDTH,
            'height' => self::DEFAULT_HEIGHT,
        ];
    }

    public static function width(): float   { return self::DEFAULT_WIDTH; }
    public static function height(): float  { return self::DEFAULT_HEIGHT; }
    public static function qrSize(): int    { return self::DEFAULT_QR_SIZE; }

    /** ابعاد تصویر */
    public static function imageSizes(): array
    {
        $s = self::sizes();
        return ['width' => $s['imgW'], 'height' => $s['imgH']];
    }

    /** ابعاد لوگو */
    public static function logoSizes(): array
    {
        $s = self::sizes();
        return ['width' => $s['logoW'], 'height' => $s['logoH']];
    }

    /** فونت‌ها */
    public static function fontSizes(): array
    {
        $s = self::sizes();
        return [
            'title' => $s['titleFont'],
            'code'  => $s['codeFont'],
            'desc'  => $s['descFont'],
            'table' => $s['tableLabelFont'],
        ];
    }

    /** لیبل */
    public static function labelDefaults(): array
    {
        return [
            'width'  => self::LABEL_DEFAULT_WIDTH,
            'height' => self::LABEL_DEFAULT_HEIGHT,
            'fonts'  => [
                'customer'   => 16,
                'insurance'  => 12,
                'address'    => 14,
                'contactLbl' => 11,
                'contactVal' => 16,
                'meta'       => 11,
                'footer'     => 10,
            ],
        ];
    }

    public static function labelSizes(): array
    {
        return [
            'width'  => self::LABEL_DEFAULT_WIDTH,
            'height' => self::LABEL_DEFAULT_HEIGHT,
        ];
    }

    /** تبدیل‌ها */
    public static function cmToPx(float $cm): int  { return (int) round($cm * 96 / 2.54); }
    public static function pxToCm(int $px): float  { return round($px * 2.54 / 96, 2); }
    public static function mmToPx(float $mm): int  { return (int) round($mm * 96 / 25.4); }

    /** scale نسبت به سایز پیش‌فرض */
    public static function scaleFrom(float $certW): float
    {
        return $certW / self::DEFAULT_WIDTH;
    }

    /* ═══════════════════════════════════════════════════════════
       متد عمومی get — برای دسترسی با نقطه
       CertConfig::get('sizes.imgW', 120)
       ═══════════════════════════════════════════════════════════ */
    public static function get(string $key, $default = null)
    {
        $all = array_merge(self::defaults(), self::labelDefaults());
        $parts = explode('.', $key);
        $cur = $all;
        foreach ($parts as $p) {
            if (!is_array($cur) || !array_key_exists($p, $cur)) return $default;
            $cur = $cur[$p];
        }
        return $cur;
    }

    /* ═══════════════════════════════════════════════════════════
       __callStatic — پشتیبانی از هر متد ناشناخته
       ═══════════════════════════════════════════════════════════ */
    public static function __callStatic($name, $args)
    {
        // اگر متدی با نام sizes* یا imageSizes* صدا شد
        if (str_contains($name, 'size') || str_contains($name, 'Size')) {
            return self::sizes();
        }
        if (str_contains($name, 'width') || str_contains($name, 'Width')) {
            return self::DEFAULT_WIDTH;
        }
        if (str_contains($name, 'height') || str_contains($name, 'Height')) {
            return self::DEFAULT_HEIGHT;
        }
        if (str_contains($name, 'font') || str_contains($name, 'Font')) {
            return self::fontSizes();
        }
        if (str_contains($name, 'label') || str_contains($name, 'Label')) {
            return self::labelDefaults();
        }

        // پیش‌فرض
        return self::sizes();
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix CertConfig — رفع خطای sizes()                            ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    target = PROJECT / "app/Support/CertConfig.php"

    # backup
    if target.exists():
        bak_dir = PROJECT / "storage/backups"
        bak_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = bak_dir / f"CertConfig_{ts}.php.bak"
        shutil.copy2(target, bak)
        print(f"  📦 backup: {bak}")
        # حذف backup های قدیمی‌تر از ۱۰ تا
        all_baks = sorted(bak_dir.glob("CertConfig_*.php.bak"), reverse=True)
        for old in all_baks[10:]:
            old.unlink()

    # write
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, 'w', encoding='utf-8', newline='\n') as f:
        f.write(CERT_CONFIG)
    print(f"  ✓ نوشته شد: {target}")
    print(f"  📏 حجم: {len(CERT_CONFIG.encode('utf-8')):,} bytes\n")

    # نمایش CertRenderer.php برای اینکه ببینیم چه متدهای دیگری لازم است
    renderer = PROJECT / "app/Services/CertRenderer.php"
    if renderer.exists():
        print("═" * 64)
        print("📄 محتوای CertRenderer.php (برای بررسی متدهای استفاده‌شده):")
        print("═" * 64)
        with open(renderer, 'r', encoding='utf-8') as f:
            content = f.read()
        # نمایش فقط ۶۰ خط اول
        lines = content.split('\n')
        for i, line in enumerate(lines[:80], 1):
            print(f"{i:>3} │ {line}")
        if len(lines) > 80:
            print(f"    │ ... ({len(lines) - 80} خط دیگر)")
        print("═" * 64)

        # پیدا کردن همه CertConfig:: calls
        import re
        calls = set(re.findall(r'CertConfig::(\w+)\s*\(', content))
        print(f"\n🔍 متدهای CertConfig که در CertRenderer صدا زده می‌شود:")
        for c in sorted(calls):
            print(f"   • {c}()")
        print()
    else:
        print("⚠️ فایل CertRenderer.php پیدا نشد\n")

    print("✅ حالا اجرا کنید:")
    print(f"   cd {PROJECT}")
    print("   php artisan optimize:clear")
    print("   php artisan serve\n")
    print("سپس صفحه را refresh کنید.")


if __name__ == "__main__":
    main()