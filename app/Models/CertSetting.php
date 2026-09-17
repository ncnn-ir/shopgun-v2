<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CertSetting extends Model
{
    protected $fillable = ['key', 'value', 'group'];

    public static function get(string $key, $default = null)
    {
        $s = self::where('key', $key)->first();
        if (! $s) return $default;

        $v = $s->value;
        if (is_string($v)) {
            if (str_starts_with($v, '{') || str_starts_with($v, '[')) {
                return json_decode($v, true) ?: $default;
            }
            if (is_numeric($v)) return $v + 0;
            if ($v === 'true')  return true;
            if ($v === 'false') return false;
        }

        return $v ?? $default;
    }

    public static function set(string $key, $value, string $group = 'general'): void
    {
        if (is_array($value) || is_object($value)) {
            $value = json_encode($value, JSON_UNESCAPED_UNICODE);
        } elseif (is_bool($value)) {
            $value = $value ? 'true' : 'false';
        }

        self::updateOrCreate(
            ['key' => $key],
            ['value' => (string) $value, 'group' => $group]
        );
    }
}
