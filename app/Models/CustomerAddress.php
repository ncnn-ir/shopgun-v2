<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CustomerAddress extends Model
{
    protected $fillable = [
        'customer_id', 'label', 'province', 'city', 'address',
        'postal_code', 'is_primary', 'lat', 'lng',
    ];

    protected $casts = [
        'is_primary' => 'boolean',
        'lat'        => 'float',
        'lng'        => 'float',
    ];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function scopePrimary($q)
    {
        return $q->where('is_primary', true);
    }

    /**
     * آدرس کامل یک خطی
     */
    public function getFullAddressAttribute(): string
    {
        $parts = array_filter([
            $this->province,
            $this->city,
            $this->address,
        ]);
        return implode(' - ', $parts);
    }

    public function getShortAttribute(): string
    {
        $loc = array_filter([$this->city, $this->province]);
        $loc = implode('، ', $loc);
        $addr = mb_substr((string) $this->address, 0, 40);
        return trim($loc . ($addr ? ' - ' . $addr : ''));
    }
}
