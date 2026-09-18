<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class SyncRun extends Model
{
    protected $fillable = [
        'user_id', 'type', 'mode', 'status',
        'total_items', 'processed_items',
        'created_items', 'updated_items', 'failed_items', 'skipped_items',
        'options', 'last_error', 'started_at', 'finished_at',
    ];

    protected $casts = [
        'options' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function items(): HasMany
    {
        return $this->hasMany(SyncItem::class);
    }

    public function getProgressPercentAttribute(): int
    {
        if ($this->total_items <= 0) return 0;
        return (int) round(($this->processed_items / $this->total_items) * 100);
    }

    public function getDurationAttribute(): ?int
    {
        if (!$this->started_at) return null;
        $end = $this->finished_at ?? now();
        return $end->diffInSeconds($this->started_at);
    }

    public function recalcCounters(): void
    {
        $this->update([
            'processed_items' => $this->items()->whereIn('status', ['created', 'updated', 'skipped', 'failed'])->count(),
            'created_items' => $this->items()->where('status', 'created')->count(),
            'updated_items' => $this->items()->where('status', 'updated')->count(),
            'failed_items' => $this->items()->where('status', 'failed')->count(),
            'skipped_items' => $this->items()->where('status', 'skipped')->count(),
        ]);
    }
}
