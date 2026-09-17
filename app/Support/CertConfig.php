<?php

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


    /**
     * ★ لیست سنگ‌ها از AppSetting
     */
    public static function stones(): array
    {
        try {
            if (\Illuminate\Support\Facades\Schema::hasTable('app_settings')) {
                $s = AppSetting::get('cert_stones', null);
                if (is_array($s) && !empty($s)) return $s;
            }
        } catch (\Throwable $e) {}
        return [];
    }

    /**
     * ★ لیست فلزات از AppSetting
     */
    public static function metals(): array
    {
        try {
            if (\Illuminate\Support\Facades\Schema::hasTable('app_settings')) {
                $m = AppSetting::get('cert_metals', null);
                if (is_array($m) && !empty($m)) return $m;
            }
        } catch (\Throwable $e) {}
        return [];
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
