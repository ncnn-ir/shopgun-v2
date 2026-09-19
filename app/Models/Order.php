<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;
use App\Models\Concerns\HasSupplyTracking;

class Order extends Model
{
    use HasSupplyTracking;

    use LogsActivity;

    protected $fillable = [
        'order_number', 'customer_id', 'channel_id', 'status',
        'amount', 'insurance', 'address', 'postal_code', 'phone',
        'notes', 'invoice_needed', 'meta',
        'payment_method', 'payment_title', 'sales_channel',
        'channel_metadata', 'customer_note', 'supply_status', 'woo_status',
        'tracking_code', 'carrier', 'shipping_status', 'shipping_events',
        'shipped_at', 'delivered_at',
        'supply_found_at',
        'supply_found_by',
        'supply_notes',
        'delivered_to_shipping_at',
        'delivered_to_shipping_by',
        'paid_at',
        'shipping_lat',
        'shipping_lng',
        'shipping_city',
        'shipping_province',
        'shipping_address'
    ];

    protected $casts = [
        'amount'          => 'decimal:2',
        'insurance'       => 'decimal:2',
        'invoice_needed'  => 'boolean',
        'meta'            => 'array',
        'shipping_events' => 'array',
        'channel_metadata' => 'array',
        'shipped_at'      => 'datetime',
        'delivered_at'    => 'datetime'
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
    public function getSalesChannelLabelAttribute(): string
    {
        return match ($this->sales_channel) {
            'basalam' => '🛍️ باسلام',
            'terb' => '🏬 ترب',
            'zibal' => '💳 زیبال',
            'zarinpal' => '💳 زرین‌پال',
            'bank' => '🏦 کارت به کارت',
            'cod' => '💵 پرداخت در محل',
            'website' => '🌐 سایت',
            'instagram' => '📷 اینستاگرام',
            'telegram' => '✈️ تلگرام',
            'phone' => '📞 تلفنی',
            default => '🌐 ' . ($this->sales_channel ?? 'نامشخص'),
        };
    }

    public function getSalesChannelColorAttribute(): string
    {
        return match ($this->sales_channel) {
            'basalam' => '#00b894',
            'terb' => '#f59e0b',
            'zibal' => '#3b82f6',
            'zarinpal' => '#8b5cf6',
            'bank' => '#64748b',
            'cod' => '#10b981',
            'website' => '#6b0f1a',
            'instagram' => '#e91e63',
            'telegram' => '#29b6f6',
            'phone' => '#66bb6a',
            default => '#94a3b8',
        };
    }

    public function getSupplyStatusLabelAttribute(): string
    {
        return match ($this->supply_status) {
            'awaiting_supply' => '⏳ در انتظار تامین',
            'supplied' => '✅ تامین شد',
            'delivered_to_shipping' => '📦 تحویل واحد ارسال',
            default => '—',
        };
    }

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


    /**
     * نگاشت کانال فروش → برچسب فارسی (برای استفاده در گزارش‌ها)
     */
    public function channelLabel(): string
    {
        return (new \App\View\Components\ChannelBadge($this->sales_channel))->label;
    }

    public function channelIcon(): string
    {
        return (new \App\View\Components\ChannelBadge($this->sales_channel))->icon;
    }


    public function getCustomerNameAttribute(): ?string
    {
        if (!$this->customer) return null;
        return trim(($this->customer->first_name ?? '') . ' ' . ($this->customer->last_name ?? '')) ?: null;
    }


}
