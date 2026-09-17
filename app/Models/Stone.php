<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Stone extends Model
{
    protected $fillable = [
        'name', 'en', 'origin', 'origin_en', 'flag', 'balloon',
        'icon', 'png_path', 'is_active', 'sort_order',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'sort_order' => 'integer',
    ];

    public function getPngUrlAttribute(): ?string
    {
        return $this->png_path ? asset('storage/' . $this->png_path) : null;
    }
}
