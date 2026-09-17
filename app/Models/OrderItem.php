<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class OrderItem extends Model
{
    protected $fillable = [
        'order_id',
        'title',
        'sku',
        'price',
        'quantity',
        'cert_needed',
        'sort_order',
    ];

    protected $casts = [
        'price'       => 'decimal:2',
        'quantity'    => 'integer',
        'cert_needed' => 'boolean',
        'sort_order'  => 'integer',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }
}
