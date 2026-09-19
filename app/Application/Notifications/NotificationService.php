<?php

namespace App\Application\Notifications;

use App\Models\AppNotification;
use App\Models\User;

/**
 * ★ NotificationService
 * نقطه واحد برای ارسال اعلان
 */
class NotificationService
{
    public static function toUser(int $userId, string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): AppNotification
    {
        return AppNotification::create([
            'user_id' => $userId,
            'type' => $type,
            'title' => $title,
            'message' => $message,
            'icon' => $icon,
            'url' => $url,
            'data' => $data,
        ]);
    }

    public static function toAll(string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): int
    {
        $count = 0;
        foreach (User::all() as $user) {
            self::toUser($user->id, $type, $title, $message, $icon, $url, $data);
            $count++;
        }
        return $count;
    }

    public static function toRole(string $roleName, string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): int
    {
        $count = 0;
        $users = User::role($roleName)->get();
        foreach ($users as $user) {
            self::toUser($user->id, $type, $title, $message, $icon, $url, $data);
            $count++;
        }
        return $count;
    }

    /**
     * اعلان سیستمی
     */
    public static function system(string $title, string $message, string $icon = '⚙️', array $data = []): int
    {
        return self::toAll('system', $title, $message, $icon, null, $data);
    }
}
