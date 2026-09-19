<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class OrderStatusHistory extends Model
{
    protected $table = 'order_status_history';

    protected $fillable = [
        'order_id', 'from_status', 'to_status',
        'note', 'changed_by', 'changed_at',
    ];

    protected $casts = [
        'changed_at' => 'datetime',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function getToStatusLabelAttribute(): string
    {
        return \App\Support\OrderStatus::label($this->to_status);
    }

    public function getFromStatusLabelAttribute(): string
    {
        return $this->from_status ? \App\Support\OrderStatus::label($this->from_status) : '—';
    }
}
