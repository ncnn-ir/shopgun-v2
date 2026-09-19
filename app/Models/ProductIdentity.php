<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ProductIdentity extends Model
{
    protected $fillable = [
        'sku', 'local_product_id', 'woo_product_id',
        'canonical_name', 'canonical_slug',
        'last_known_price', 'last_known_weight',
        'last_known_woo_data', 'sync_count', 'last_synced_at',
    ];

    protected $casts = [
        'last_known_woo_data' => 'array',
        'last_known_price' => 'decimal:2',
        'last_known_weight' => 'decimal:3',
        'last_synced_at' => 'datetime',
    ];

    public function getWooEditUrlAttribute(): ?string
    {
        if (!$this->woo_product_id) return null;
        $site = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/wp-admin/post.php?post={$this->woo_product_id}&action=edit" : null;
    }
}
