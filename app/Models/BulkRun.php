<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class BulkRun extends Model
{
    protected $fillable = [
        'user_id', 'source', 'mode', 'status',
        'total_items', 'validated_items', 'queued_items',
        'processing_items', 'success_items', 'failed_items',
        'settings_snapshot', 'last_error', 'started_at', 'finished_at',
    ];

    protected $casts = [
        'settings_snapshot' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function batches(): HasMany
    {
        return $this->hasMany(BulkBatch::class, 'run_id')->orderBy('sequence');
    }

    public function items(): HasMany
    {
        return $this->hasMany(BulkItem::class, 'run_id');
    }

    public function getProgressPercentAttribute(): int
    {
        if ($this->total_items <= 0) return 0;
        $done = $this->success_items + $this->failed_items;
        return (int) round(($done / $this->total_items) * 100);
    }

    public function recalcCounters(): void
    {
        $this->update([
            'queued_items' => $this->items()->where('status', 'queued')->count(),
            'processing_items' => $this->items()->where('status', 'processing')->count(),
            'success_items' => $this->items()->whereIn('status', ['success', 'draft_created'])->count(),
            'failed_items' => $this->items()->where('status', 'failed')->count(),
        ]);
    }
}
