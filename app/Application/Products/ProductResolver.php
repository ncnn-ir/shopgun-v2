<?php

namespace App\Application\Products;

use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\ProductIdentity;
use App\Models\Certificate;
use App\Models\OrderItem;
use App\Models\Product;
use Illuminate\Support\Facades\Log;

/**
 * ★ ProductResolver
 * SKU مرکزی — همه ماژول‌ها برای یافتن محصول از این استفاده می‌کنند
 *
 * - resolve(sku) → ProductIdentity یا null
 * - enrich(sku) → گرفتن اطلاعات از Woo در صورت نیاز
 * - certificates(sku) → شناسنامه‌های مرتبط
 * - orderItems(sku) → سفارشات مرتبط
 */
class ProductResolver
{
    protected WooCommerceClient $woo;

    public function __construct()
    {
        $this->woo = (new WooCommerceClient())->module('resolver');
    }

    /**
     * یافتن یا ساخت ProductIdentity
     */
    public function resolve(string $sku, bool $fetchFromWooIfMissing = false): ?ProductIdentity
    {
        $sku = trim($sku);
        if ($sku === '') return null;

        $identity = ProductIdentity::where('sku', $sku)->first();
        if ($identity) return $identity;

        // اگه در local Product بود
        $local = Product::where('sku', $sku)->first();
        if ($local) {
            return $this->touchFromLocal($local);
        }

        // از Woo بگیر
        if ($fetchFromWooIfMissing) {
            return $this->enrichFromWoo($sku);
        }

        return null;
    }

    /**
     * بروزرسانی از Product local
     */
    public function touchFromLocal(Product $product): ProductIdentity
    {
        return ProductIdentity::updateOrCreate(
            ['sku' => $product->sku],
            [
                'local_product_id' => $product->id,
                'woo_product_id' => $product->wc_id,
                'canonical_name' => $product->name,
                'last_known_price' => $product->price,
                'last_known_weight' => $product->weight,
                'last_synced_at' => now(),
            ]
        );
    }

    /**
     * غنی‌سازی از Woo
     */
    public function enrichFromWoo(string $sku): ?ProductIdentity
    {
        try {
            $r = $this->woo->productBySku($sku);
            if (!$r['ok'] || empty($r['body'])) return null;

            $p = $r['body'][0] ?? null;
            if (!$p) return null;

            return $this->touchFromWoo($p);
        } catch (\Throwable $e) {
            Log::warning("ProductResolver enrich failed for {$sku}: " . $e->getMessage());
            return null;
        }
    }

    /**
     * بروزرسانی از Woo data
     */
    public function touchFromWoo(array $wooData): ProductIdentity
    {
        $sku = $wooData['sku'] ?? null;
        if (!$sku) throw new \InvalidArgumentException('SKU یافت نشد');

        $existing = ProductIdentity::where('sku', $sku)->first();

        return ProductIdentity::updateOrCreate(
            ['sku' => $sku],
            [
                'woo_product_id' => $wooData['id'] ?? null,
                'canonical_name' => $wooData['name'] ?? null,
                'canonical_slug' => $wooData['slug'] ?? null,
                'last_known_price' => $wooData['price'] ?? null,
                'last_known_weight' => $wooData['weight'] ?? null,
                'last_known_woo_data' => $wooData,
                'sync_count' => ($existing?->sync_count ?? 0) + 1,
                'last_synced_at' => now(),
            ]
        );
    }

    /**
     * شناسنامه‌های مرتبط با SKU
     */
    public function certificates(string $sku): \Illuminate\Database\Eloquent\Collection
    {
        return Certificate::where('sku', $sku)->get();
    }

    /**
     * سفارشات مرتبط با SKU
     */
    public function orderItems(string $sku): \Illuminate\Database\Eloquent\Collection
    {
        return OrderItem::where('sku', $sku)->with('order')->get();
    }

    /**
     * Snapshot کامل برای Preview/Diff
     */
    public function snapshot(string $sku): array
    {
        $identity = $this->resolve($sku, true);

        return [
            'sku' => $sku,
            'in_local' => (bool) $identity?->local_product_id,
            'in_woo' => (bool) $identity?->woo_product_id,
            'woo_id' => $identity?->woo_product_id,
            'canonical_name' => $identity?->canonical_name,
            'last_price' => $identity?->last_known_price,
            'last_weight' => $identity?->last_known_weight,
            'woo_data' => $identity?->last_known_woo_data,
            'edit_url' => $identity?->woo_edit_url,
            'certificates_count' => $this->certificates($sku)->count(),
            'order_items_count' => $this->orderItems($sku)->count(),
        ];
    }
}
