<?php

namespace App\Support;

use App\Models\CertSetting;

class CertConfig
{
    public const DEFAULT_WIDTH  = 6.5;
    public const DEFAULT_HEIGHT = 6.5;

    public static function sizes($source = null): array
    {
        $d = [
            'width'  => self::DEFAULT_WIDTH,
            'height' => self::DEFAULT_HEIGHT,

            // snake_case (CertRenderer استفاده می‌کند)
            'img_w' => 120, 'img_h' => 120,
            'qr_size' => 40, 'logo_w' => 28, 'logo_h' => 22,
            'code_font' => 11, 'url_font' => 6, 'table_font' => 8,
            'title_font' => 20, 'desc_font' => 7,
            'table_label_font' => 8, 'table_value_font' => 8,

            // camelCase (Blade Component استفاده می‌کند)
            'imgW' => 120, 'imgH' => 120,
            'qrSize' => 40, 'logoW' => 28, 'logoH' => 22,
            'codeFont' => 11, 'urlFont' => 6, 'tableFont' => 8,
            'titleFont' => 20, 'descFont' => 7,
            'tableLabelFont' => 8, 'tableValueFont' => 8,
        ];

        $saved = null;
        if (is_array($source)) $saved = $source;
        elseif (is_object($source) && isset($source->sizes) && is_array($source->sizes)) $saved = $source->sizes;

        if ($saved === null) {
            try {
                $path = storage_path('app/cert-config.json');
                if (file_exists($path)) {
                    $data = json_decode(file_get_contents($path), true);
                    if (is_array($data)) $saved = $data['sizes'] ?? $data;
                }
            } catch (\Throwable $e) {}
        }

        return is_array($saved) ? array_merge($d, $saved) : $d;
    }

    public static function assets(): array
    {
        $bg = null; $logo = null; $desc = null;
        try {
            if (class_exists(CertSetting::class)) {
                $bg   = CertSetting::get('bg_image',   null);
                $logo = CertSetting::get('logo_image', null);
                $desc = CertSetting::get('desc_image', null);
            }
        } catch (\Throwable $e) {}

        return [
            'bg_image'   => self::resolveUrl($bg),
            'logo_image' => self::resolveUrl($logo),
            'desc_image' => self::resolveUrl($desc),
        ];
    }

    protected static function resolveUrl($v): ?string
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
        try {
            if (class_exists(CertSetting::class)) {
                return (bool) CertSetting::get('hide_desc', false);
            }
        } catch (\Throwable $e) {}
        return false;
    }

    public static function __callStatic($name, $args)
    {
        if (stripos($name, 'asset') !== false) return self::assets();
        if (stripos($name, 'hide')  !== false) return self::hideDesc();
        if (stripos($name, 'size')  !== false) return self::sizes();
        if (stripos($name, 'font')  !== false) return self::sizes();
        return self::sizes();
    }
}
