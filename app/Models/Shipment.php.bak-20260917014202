<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Shipment extends Model
{
    protected $fillable = [
        'order_id', 'tracking_code', 'carrier', 'status',
        'receiver_name', 'receiver_phone', 'address', 'postal_code',
        'weight', 'cost', 'events', 'shipped_at', 'delivered_at',
    ];

    protected $casts = [
        'events'       => 'array',
        'weight'       => 'decimal:3',
        'cost'         => 'decimal:2',
        'shipped_at'   => 'datetime',
        'delivered_at' => 'datetime',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'pending'    => '📦 ثبت شده',
            'in_transit' => '🚚 در مسیر',
            'delivered'  => '✅ تحویل شد',
            'returned'   => '↩️ مرجوع',
            'failed'     => '❌ ناموفق',
            default      => $this->status,
        };
    }
}
