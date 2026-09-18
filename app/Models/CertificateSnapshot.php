<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CertificateSnapshot extends Model
{
    protected $fillable = [
        'certificate_id', 'event', 'sku',
        'stone_name', 'stone_en', 'metal', 'metal_carat',
        'length', 'width', 'weight', 'brilliant',
        'image_path', 'image_url',
        'product_data', 'meta', 'changed_by', 'captured_at',
    ];

    protected $casts = [
        'product_data' => 'array',
        'meta' => 'array',
        'captured_at' => 'datetime',
        'length' => 'decimal:2',
        'width' => 'decimal:2',
        'weight' => 'decimal:3',
    ];

    public function certificate(): BelongsTo
    {
        return $this->belongsTo(Certificate::class);
    }

    public function getChangedByNameAttribute(): string
    {
        if (!$this->changed_by) return 'سیستم';
        return User::find($this->changed_by)?->name ?? 'سیستم';
    }
}
