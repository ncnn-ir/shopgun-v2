<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ApiLog extends Model
{
    public $timestamps = false;
    protected $fillable = [
        'service', 'method', 'url', 'status_code', 'duration_ms',
        'request_body', 'response_body', 'error', 'items_count',
        'user_id', 'created_at',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'status_code' => 'integer',
        'duration_ms' => 'integer',
        'items_count' => 'integer',
    ];

    public static function record(array $data): self
    {
        $data['created_at'] = now();
        $data['user_id'] = $data['user_id'] ?? (auth()->id() ?? null);

        // پاکسازی لاگ‌های قدیمی
        if (random_int(1, 20) === 1) {
            static::where('created_at', '<', now()->subDays(7))->delete();
        }

        return static::create($data);
    }

    public static function cleanup(int $days = 7): int
    {
        return static::where('created_at', '<', now()->subDays($days))->delete();
    }
}
