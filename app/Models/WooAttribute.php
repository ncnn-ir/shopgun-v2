<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class WooAttribute extends Model
{
    protected $table = 'woo_attributes';

    protected $fillable = [
        'woo_id', 'name', 'slug', 'type', 'order_by', 'has_archives', 'synced_at',
    ];

    protected $casts = [
        'has_archives' => 'boolean',
        'synced_at' => 'datetime',
    ];

    public function terms(): HasMany
    {
        return $this->hasMany(WooAttributeTerm::class, 'attribute_woo_id', 'woo_id')
            ->orderBy('menu_order')
            ->orderBy('name');
    }
}
