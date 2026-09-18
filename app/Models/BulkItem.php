<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class BulkItem extends Model
{
    protected $fillable = [
        'run_id', 'batch_id', 'sku', 'woo_product_id',
        'status', 'attempt', 'idempotency_key', 'payload_hash',
        'input_data', 'request_payload', 'response_payload',
        'error_code', 'error_message', 'validation_warnings', 'diff_data',
        'started_at', 'finished_at',
    ];

    protected $casts = [
        'input_data' => 'array',
        'request_payload' => 'array',
        'response_payload' => 'array',
        'validation_warnings' => 'array',
        'diff_data' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function run(): BelongsTo
    {
        return $this->belongsTo(BulkRun::class, 'run_id');
    }

    public function batch(): BelongsTo
    {
        return $this->belongsTo(BulkBatch::class, 'batch_id');
    }

    public function getWooEditUrlAttribute(): ?string
    {
        if (!$this->woo_product_id) return null;
        $site = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/wp-admin/post.php?post={$this->woo_product_id}&action=edit" : null;
    }

    public function getWooViewUrlAttribute(): ?string
    {
        if (!$this->woo_product_id) return null;
        $site = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/?p={$this->woo_product_id}" : null;
    }
}
