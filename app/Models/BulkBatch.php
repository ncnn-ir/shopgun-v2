<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class BulkBatch extends Model
{
    protected $fillable = [
        'run_id', 'sequence', 'status', 'attempts',
        'items_count', 'success_count', 'failed_count',
        'started_at', 'finished_at', 'error',
    ];

    protected $casts = [
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function run(): BelongsTo
    {
        return $this->belongsTo(BulkRun::class, 'run_id');
    }

    public function items(): HasMany
    {
        return $this->hasMany(BulkItem::class, 'batch_id');
    }
}
