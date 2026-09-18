<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class WooAttributeTerm extends Model
{
    protected $table = 'woo_attribute_terms';

    protected $fillable = [
        'woo_id', 'attribute_woo_id', 'name', 'slug', 'description',
        'count', 'menu_order', 'synced_at',
    ];

    protected $casts = [
        'synced_at' => 'datetime',
    ];
}
