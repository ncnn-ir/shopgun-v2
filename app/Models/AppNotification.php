<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AppNotification extends Model
{
    protected $table = 'app_notifications';

    protected $fillable = ['user_id', 'type', 'title', 'message', 'icon', 'url', 'is_read', 'data'];
    protected $casts = ['is_read' => 'boolean', 'data' => 'array'];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }

    public static function broadcast(string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): void
    {
        foreach (User::all() as $user) {
            self::create([
                'user_id' => $user->id,
                'type'    => $type,
                'title'   => $title,
                'message' => $message,
                'icon'    => $icon,
                'url'     => $url,
                'data'    => $data,
            ]);
        }
    }
}
