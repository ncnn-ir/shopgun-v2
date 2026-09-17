<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Cache;

class AppSetting extends Model
{
    protected $fillable = ['key', 'value', 'group', 'type'];

    /**
     * خواندن مقدار
     */
    public static function get(string $key, $default = null)
    {
        $all = Cache::remember('app_settings_all', 60, function () {
            return static::all()->mapWithKeys(fn($s) => [$s->key => $s->value])->toArray();
        });

        if (!array_key_exists($key, $all)) return $default;

        return static::castValue($all[$key], static::where('key', $key)->value('type'));
    }

    /**
     * نوشتن مقدار
     */
    public static function put(string $key, $value, string $group = 'general', string $type = 'string'): void
    {
        if (is_array($value) || is_object($value)) {
            $value = json_encode($value, JSON_UNESCAPED_UNICODE);
            $type = 'json';
        } elseif (is_bool($value)) {
            $value = $value ? '1' : '0';
            $type = 'bool';
        }

        static::updateOrCreate(
            ['key' => $key],
            ['value' => (string) $value, 'group' => $group, 'type' => $type]
        );

        Cache::forget('app_settings_all');
    }

    /**
     * چند مقدار با هم
     */
    public static function putMany(array $data, string $group = 'general'): void
    {
        foreach ($data as $key => $value) {
            $type = 'string';
            if (is_bool($value)) $type = 'bool';
            elseif (is_int($value)) $type = 'int';
            elseif (is_array($value)) $type = 'json';
            static::put($key, $value, $group, $type);
        }
    }

    protected static function castValue($value, $type)
    {
        return match ($type) {
            'int'  => (int) $value,
            'bool' => $value === '1' || $value === 'true',
            'json' => json_decode($value, true),
            default => $value,
        };
    }
}
