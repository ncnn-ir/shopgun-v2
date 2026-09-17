<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Product extends Model
{
    protected $fillable = [
        'sku', 'wc_id', 'barcode', 'name', 'slug',
        'description', 'short_description',
        'price', 'regular_price', 'sale_price',
        'stock_quantity', 'stock_status',
        'weight', 'length', 'width', 'height',
        'stone_id', 'metal_id',
        'image_path', 'image_url',
        'gallery', 'categories', 'attributes', 'tags', 'wc_data',
        'is_active', 'synced_at',
    ];

    protected $casts = [
        'price'          => 'decimal:2',
        'regular_price'  => 'decimal:2',
        'sale_price'     => 'decimal:2',
        'weight'         => 'decimal:3',
        'length'         => 'decimal:2',
        'width'          => 'decimal:2',
        'height'         => 'decimal:2',
        'stock_quantity' => 'integer',
        'gallery'        => 'array',
        'categories'     => 'array',
        'attributes'     => 'array',
        'tags'           => 'array',
        'wc_data'        => 'array',
        'is_active'      => 'boolean',
        'synced_at'      => 'datetime',
    ];

    public function stone(): BelongsTo   { return $this->belongsTo(Stone::class); }
    public function metal(): BelongsTo   { return $this->belongsTo(Metal::class); }

    public function scopeActive($q)      { return $q->where('is_active', true); }
    public function scopeInStock($q)     { return $q->where('stock_status', 'instock'); }

    /**
     * جستجوی هوشمند: SKU → name → barcode → wc_id
     */
    public function scopeSearch($q, string $term)
    {
        $term = trim($term);
        if ($term === '') return $q;

        $q->where(function ($qq) use ($term) {
            $qq->where('sku', 'like', "%{$term}%")
               ->orWhere('name', 'like', "%{$term}%")
               ->orWhere('barcode', 'like', "%{$term}%")
               ->orWhere('wc_id', 'like', "%{$term}%");
        });

        return $q;
    }

    /**
     * تصویر نهایی
     */
    public function getImageSrcAttribute(): ?string
    {
        if (!empty($this->image_path)) {
            return asset('storage/' . $this->image_path);
        }
        return $this->image_url ?: null;
    }

    public function getPriceFormattedAttribute(): string
    {
        return number_format((float) $this->price);
    }

    /**
     * ساخت از WooCommerce product
     */
    public static function upsertFromWoo(array $wc): self
    {
        $sku = $wc['sku'] ?? null;
        if (!$sku) {
            $sku = 'PROD-' . ($wc['id'] ?? uniqid());
        }

        $data = [
            'sku'               => $sku,
            'wc_id'             => $wc['id'] ?? null,
            'name'              => $wc['name'] ?? '',
            'slug'              => $wc['slug'] ?? null,
            'description'       => $wc['description'] ?? null,
            'short_description' => $wc['short_description'] ?? null,
            'price'             => (float) ($wc['price'] ?? 0),
            'regular_price'     => (float) ($wc['regular_price'] ?? 0),
            'sale_price'        => isset($wc['sale_price']) && $wc['sale_price'] !== '' ? (float) $wc['sale_price'] : null,
            'stock_quantity'    => isset($wc['stock_quantity']) ? (int) $wc['stock_quantity'] : null,
            'stock_status'      => $wc['stock_status'] ?? 'instock',
            'weight'            => !empty($wc['weight']) ? (float) $wc['weight'] : null,
            'length'            => isset($wc['dimensions']['length']) && $wc['dimensions']['length'] !== '' ? (float) $wc['dimensions']['length'] : null,
            'width'             => isset($wc['dimensions']['width']) && $wc['dimensions']['width'] !== '' ? (float) $wc['dimensions']['width'] : null,
            'height'            => isset($wc['dimensions']['height']) && $wc['dimensions']['height'] !== '' ? (float) $wc['dimensions']['height'] : null,
            'image_url'         => $wc['images'][0]['src'] ?? null,
            'gallery'           => array_map(fn($i) => $i['src'] ?? null, $wc['images'] ?? []),
            'categories'        => array_map(fn($c) => ['id' => $c['id'] ?? null, 'name' => $c['name'] ?? ''], $wc['categories'] ?? []),
            'attributes'        => array_map(fn($a) => ['name' => $a['name'] ?? '', 'options' => $a['options'] ?? []], $wc['attributes'] ?? []),
            'tags'              => array_map(fn($t) => ['id' => $t['id'] ?? null, 'name' => $t['name'] ?? ''], $wc['tags'] ?? []),
            'wc_data'           => $wc,
            'is_active'         => ($wc['status'] ?? 'publish') === 'publish',
            'synced_at'         => now(),
        ];

        return static::updateOrCreate(['sku' => $sku], $data);
    }
}
