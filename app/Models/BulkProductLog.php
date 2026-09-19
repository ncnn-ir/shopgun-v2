<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BulkProductLog extends Model
{
    protected $fillable = [
        'sku', 'woo_id', 'name', 'slug',
        'regular_price', 'sale_price', 'weight', 'stock_quantity',
        'status', 'error_message', 'payload', 'response',
        'batch_id', 'sent_at',
    ];

    protected $casts = [
        'regular_price' => 'decimal:2',
        'sale_price' => 'decimal:2',
        'weight' => 'decimal:3',
        'payload' => 'array',
        'response' => 'array',
        'sent_at' => 'datetime',
    ];

    public function getWooEditUrlAttribute(): ?string
    {
        if (!$this->woo_id) return null;
        $site = rtrim((string) \App\Models\AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/wp-admin/post.php?post={$this->woo_id}&action=edit" : null;
    }

    public function getWooViewUrlAttribute(): ?string
    {
        if (!$this->slug) return null;
        $site = rtrim((string) \App\Models\AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/?p={$this->woo_id}" : null;
    }
}
