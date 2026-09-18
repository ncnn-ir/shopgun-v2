<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SyncItem extends Model
{
    protected $fillable = [
        'sync_run_id', 'entity_type', 'entity_id', 'local_id',
        'status', 'action', 'error_message', 'diff_data',
        'started_at', 'finished_at',
    ];

    protected $casts = [
        'diff_data' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function run(): BelongsTo
    {
        return $this->belongsTo(SyncRun::class, 'sync_run_id');
    }
}
