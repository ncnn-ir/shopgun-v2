<?php

namespace App\Support;

use App\Models\Product;

/**
 * استخراج URL تصویر محصول از منابع مختلف
 * WooCommerce ممکنه تصویر رو در meta, images, gallery, thumbnail و... ذخیره کنه
 */
class ProductImage
{
    public static function resolve($product): ?string
    {
        if (!$product) return null;

        // 1) ستون‌های مستقیم
        foreach (['image', 'thumbnail', 'main_image', 'featured_image', 'image_url', 'photo', 'cover'] as $col) {
            if (isset($product->$col) && is_string($product->$col) && trim($product->$col) !== '') {
                return self::normalize($product->$col);
            }
        }

        // 2) images / gallery (JSON array)
        foreach (['images', 'gallery', 'photos'] as $col) {
            if (isset($product->$col)) {
                $v = $product->$col;
                if (is_string($v) && trim($v) !== '') {
                    $decoded = json_decode($v, true);
                    if (is_array($decoded) && count($decoded)) {
                        $first = $decoded[0];
                        if (is_string($first)) return self::normalize($first);
                        if (is_array($first)) {
                            foreach (['src', 'url', 'image', 'thumbnail'] as $k) {
                                if (!empty($first[$k])) return self::normalize($first[$k]);
                            }
                        }
                    } elseif (is_string($decoded)) {
                        return self::normalize($decoded);
                    }
                    // اگه URL خالص بود
                    if (filter_var($v, FILTER_VALIDATE_URL)) return self::normalize($v);
                } elseif (is_array($v) && count($v)) {
                    $first = $v[0] ?? null;
                    if (is_string($first)) return self::normalize($first);
                    if (is_array($first)) {
                        foreach (['src', 'url', 'image', 'thumbnail'] as $k) {
                            if (!empty($first[$k])) return self::normalize($first[$k]);
                        }
                    }
                }
            }
        }

        // 3) meta JSON
        if (isset($product->meta)) {
            $meta = is_array($product->meta) ? $product->meta : json_decode((string)$product->meta, true);
            if (is_array($meta)) {
                $candidates = [
                    $meta['image'] ?? null,
                    $meta['thumbnail'] ?? null,
                    $meta['featured_image'] ?? null,
                    $meta['main_image'] ?? null,
                    $meta['_thumbnail_id'] ?? null,
                ];
                // اگر meta['image'] آرایه بود
                if (is_array($meta['image'] ?? null)) {
                    foreach (['src','url','thumbnail'] as $k) {
                        if (!empty($meta['image'][$k])) $candidates[] = $meta['image'][$k];
                    }
                }
                // گالری
                if (!empty($meta['gallery']) && is_array($meta['gallery'])) {
                    $candidates = array_merge($candidates, $meta['gallery']);
                }
                foreach ($candidates as $c) {
                    if (is_string($c) && trim($c) !== '') return self::normalize($c);
                }
            }
        }

        // 4) ارتباط Media (اگه medialibrary استفاده شده)
        if (method_exists($product, 'getFirstMediaUrl')) {
            try {
                $url = $product->getFirstMediaUrl('images') ?: $product->getFirstMediaUrl();
                if ($url) return $url;
            } catch (\Throwable $e) {}
        }

        return null;
    }

    public static function normalize(string $url): string
    {
        $url = trim($url);
        if (str_starts_with($url, '//')) return 'https:' . $url;
        if (str_starts_with($url, 'http://') || str_starts_with($url, 'https://')) return $url;
        if (str_starts_with($url, '/')) return $url;
        return $url;
    }

    /**
     * لینک محصول در سایت
     */
    public static function permalink($product): ?string
    {
        if (!$product) return null;
        foreach (['permalink', 'url', 'product_url', 'link', 'slug'] as $col) {
            if (isset($product->$col) && is_string($product->$col) && trim($product->$col) !== '') {
                $v = $product->$col;
                if (filter_var($v, FILTER_VALIDATE_URL)) return $v;
                if ($col === 'slug') {
                    // اگر اسلاگ بود، با site_url ترکیب کن
                    $base = \App\Models\AppSetting::get('commerce_url', '');
                    if ($base) return rtrim($base, '/') . '/product/' . $v;
                }
                return $v;
            }
        }
        if (isset($product->meta)) {
            $meta = is_array($product->meta) ? $product->meta : json_decode((string)$product->meta, true);
            if (is_array($meta)) {
                foreach (['permalink', 'url', 'link'] as $k) {
                    if (!empty($meta[$k]) && is_string($meta[$k])) return $meta[$k];
                }
            }
        }
        return null;
    }
}
