<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class WooCategory extends Model
{
    protected $table = 'woo_categories';

    protected $fillable = [
        'woo_id', 'parent_woo_id', 'name', 'slug', 'description',
        'count', 'image', 'menu_order', 'synced_at',
    ];

    protected $casts = [
        'image' => 'array',
        'synced_at' => 'datetime',
    ];

    public function scopeOrdered($q)
    {
        return $q->orderBy('menu_order')->orderBy('name');
    }
}
