<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Order extends Model
{
    use LogsActivity;

    protected $fillable = [
        'order_number', 'customer_id', 'channel_id', 'status',
        'amount', 'insurance', 'address', 'postal_code', 'phone',
        'notes', 'invoice_needed', 'meta',
        'tracking_code', 'carrier', 'shipping_status', 'shipping_events',
        'shipped_at', 'delivered_at',
    ];

    protected $casts = [
        'amount'          => 'decimal:2',
        'insurance'       => 'decimal:2',
        'invoice_needed'  => 'boolean',
        'meta'            => 'array',
        'shipping_events' => 'array',
        'shipped_at'      => 'datetime',
        'delivered_at'    => 'datetime',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['status', 'amount', 'insurance', 'address'])
            ->logOnlyDirty()
            ->useLogName('order');
    }

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function channel(): BelongsTo  { return $this->belongsTo(Channel::class); }
    public function items(): HasMany      { return $this->hasMany(OrderItem::class)->orderBy('sort_order'); }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

    public function getStatusColorAttribute(): string
    {
        return match ($this->status) {
            'pending'     => 'warning',
            'final-check' => 'info',
            'courier'     => 'success',
            default       => 'ghost',
        };
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'pending'     => '📝 ثبت سفارش',
            'final-check' => '🔍 چک نهایی',
            'courier'     => '🚚 تحویل مامور',
            default       => $this->status,
        };
    }

    public function getItemsTotalAttribute(): float
    {
        return (float) $this->items->sum(fn ($i) => $i->price * $i->quantity);
    }

    public function getProductsSummaryAttribute(): string
    {
        if ($this->items->isEmpty()) return '—';
        return $this->items->map(function ($i) {
            $t = $i->title;
            if ($i->sku) $t .= " [{$i->sku}]";
            if ($i->quantity > 1) $t .= " ×{$i->quantity}";
            return $t;
        })->join(' • ');
    }

    // بررسی اینکه آیا مرسوله داره
    public function getHasShipmentAttribute(): bool
    {
        return ! empty($this->tracking_code);
    }

    // رنگ بج وضعیت مرسوله
    public function getShippingColorAttribute(): string
    {
        $s = strtolower((string) $this->shipping_status);
        return match (true) {
            str_contains($s, 'deliver') || str_contains($s, 'تحویل') => 'success',
            str_contains($s, 'transit') || str_contains($s, 'مسیر') || str_contains($s, 'ارسال') => 'info',
            str_contains($s, 'return') || str_contains($s, 'مرجوع') => 'error',
            str_contains($s, 'fail') || str_contains($s, 'ناموفق') => 'error',
            default => 'warning',
        };
    }


    /* ═══════════════════════════════════════════════════════════
       تولید شماره سفارش یکتا
       ═══════════════════════════════════════════════════════════ */
    public static function generateNumber(): string
    {
        $last = static::orderByDesc('id')->value('order_number');
        $num = 10000;
        if ($last && is_numeric($last)) {
            $num = ((int) $last) + 1;
        }
        while (static::where('order_number', (string) $num)->exists()) {
            $num++;
        }
        return (string) $num;
    }

}
