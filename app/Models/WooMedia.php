<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class WooMedia extends Model
{
    protected $table = 'woo_media';

    protected $fillable = [
        'woo_id', 'filename', 'slug', 'mime_type', 'source_url',
        'file_size', 'width', 'height', 'title', 'alt_text',
        'sizes', 'meta', 'synced_at',
    ];

    protected $casts = [
        'sizes' => 'array',
        'meta' => 'array',
        'synced_at' => 'datetime',
    ];

    public static function findByFilename(string $filename): ?self
    {
        return self::where('filename', $filename)->first();
    }

    /**
     * پیدا کردن تصویر با الگوی {index}-{sku}.{ext}
     */
    public static function findByPattern(int $index, string $sku, string $ext = 'jpg'): ?self
    {
        return self::where('filename', "{$index}-{$sku}.{$ext}")->first()
            ?? self::where('filename', 'like', "{$index}-{$sku}.%")->first();
    }
}
