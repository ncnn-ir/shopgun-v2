<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CustomerPhone extends Model
{
    protected $fillable = [
        'customer_id', 'phone', 'label', 'is_primary', 'verified_at', 'note',
    ];

    protected $casts = [
        'is_primary'  => 'boolean',
        'verified_at' => 'datetime',
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
     * نمایش با فرمت خوانا: 0915 153 1301
     */
    public function getFormattedAttribute(): string
    {
        $p = $this->phone;
        if (strlen($p) === 10) {
            return substr($p, 0, 3) . ' ' . substr($p, 3, 3) . ' ' . substr($p, 6, 4);
        }
        if (strlen($p) === 11 && $p[0] === '0') {
            return substr($p, 0, 4) . ' ' . substr($p, 4, 3) . ' ' . substr($p, 7, 4);
        }
        return $p;
    }

    public function getDisplayAttribute(): string
    {
        return ($this->label ? "({$this->label}) " : '') . $this->formatted;
    }
}
