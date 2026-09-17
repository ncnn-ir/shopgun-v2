<?php

namespace App\Services;

use App\Models\Product;
use Illuminate\Support\Facades\Log;

class ProductSyncService
{
    /**
     * سینک محصولات از WooCommerce به دیتابیس
     *
     * @param  bool  $full  اگر false، فقط تغییرات ۳۰ روز اخیر
     * @return array  گزارش
     */
    public static function syncFromWoo(bool $full = true): array
    {
        $report = [
            'total'   => 0,
            'created' => 0,
            'updated' => 0,
            'failed'  => 0,
            'errors'  => [],
        ];

        try {
            $wc = app(WooCommerceService::class);
        } catch (\Throwable $e) {
            $report['errors'][] = 'WooCommerceService بارگذاری نشد: ' . $e->getMessage();
            return $report;
        }

        $page = 1;
        $perPage = 100;
        $maxPages = 200;

        while ($page <= $maxPages) {
            $raw = null;
            try {
                $raw = $wc->getProducts(['per_page' => $perPage, 'page' => $page]);
            } catch (\Throwable $e) {
                $report['errors'][] = "page {$page}: " . $e->getMessage();
                break;
            }

            if (!is_array($raw) || empty($raw)) break;

            foreach ($raw as $item) {
                $report['total']++;
                try {
                    $sku = $item['sku'] ?? null;
                    $exists = $sku ? Product::where('sku', $sku)->exists() : false;

                    Product::upsertFromWoo($item);

                    if ($exists) $report['updated']++;
                    else         $report['created']++;
                } catch (\Throwable $e) {
                    $report['failed']++;
                    $report['errors'][] = 'item ' . ($item['id'] ?? '?') . ': ' . $e->getMessage();
                }
            }

            if (count($raw) < $perPage) break;
            $page++;
        }

        return $report;
    }

    /**
     * سینک محصولات از آرایه‌ی آماده (مثلاً از localStorage قدیمی)
     */
    public static function syncFromArray(array $products): array
    {
        $report = ['created' => 0, 'updated' => 0, 'failed' => 0];

        foreach ($products as $p) {
            try {
                $sku = $p['sku'] ?? null;
                if (!$sku) continue;

                $exists = Product::where('sku', $sku)->exists();

                Product::updateOrCreate(['sku' => $sku], [
                    'sku'               => $sku,
                    'wc_id'             => $p['id'] ?? null,
                    'name'              => $p['title'] ?? $p['name'] ?? '',
                    'price'             => (float) ($p['price'] ?? 0),
                    'regular_price'     => (float) ($p['regularPrice'] ?? 0),
                    'stock_quantity'    => isset($p['stock']) ? (int) $p['stock'] : null,
                    'stock_status'      => $p['stockStatus'] ?? 'instock',
                    'image_url'         => $p['image'] ?? null,
                    'categories'        => is_string($p['categories'] ?? null)
                        ? array_map('trim', explode('،', $p['categories']))
                        : ($p['categories'] ?? []),
                    'attributes'        => $p['attributes'] ?? [],
                    'weight'            => !empty($p['weight']) ? (float) $p['weight'] : null,
                    'synced_at'         => now(),
                    'is_active'         => true,
                ]);

                if ($exists) $report['updated']++;
                else         $report['created']++;
            } catch (\Throwable $e) {
                $report['failed']++;
            }
        }

        return $report;
    }
}
