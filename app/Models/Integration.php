<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Crypt;

class Integration extends Model
{
    protected $fillable = [
        'key', 'name', 'base_url', 'consumer_key', 'consumer_secret',
        'is_active', 'last_sync_at', 'sync_stats', 'settings',
    ];

    protected $casts = [
        'is_active'    => 'boolean',
        'last_sync_at' => 'datetime',
        'sync_stats'   => 'array',
        'settings'     => 'array',
    ];
}
