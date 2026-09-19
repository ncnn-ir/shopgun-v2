<?php

namespace App\Models\Concerns;

/**
 * افزودن قابلیت‌های لیست تامین به مدل Order
 */
trait HasSupplyTracking
{
    public function supplyFoundBy()
    {
        return $this->belongsTo(\App\Models\User::class, 'supply_found_by');
    }

    public function deliveredToShippingBy()
    {
        return $this->belongsTo(\App\Models\User::class, 'delivered_to_shipping_by');
    }

    public function isAwaitingSupply(): bool
    {
        return in_array($this->supply_status, [null, '', 'default', 'awaiting_supply', 'pending'], true);
    }

    public function isSupplyFound(): bool
    {
        return $this->supply_status === 'found';
    }

    public function isDeliveredToShipping(): bool
    {
        return $this->supply_status === 'delivered_to_shipping';
    }

    public function markSupplyFound(?int $userId = null): void
    {
        $this->update([
            'supply_status'   => 'found',
            'supply_found_at' => now(),
            'supply_found_by' => $userId ?? auth()->id(),
        ]);
    }

    public function markDeliveredToShipping(?int $userId = null): void
    {
        $this->update([
            'supply_status'            => 'delivered_to_shipping',
            'delivered_to_shipping_at' => now(),
            'delivered_to_shipping_by' => $userId ?? auth()->id(),
        ]);
    }

    /**
     * ساخت آرایه تایم‌لاین برای نمایش در پاپ‌آپ
     */
    public function timeline(): array
    {
        $t = [];

        $t[] = [
            'key'   => 'created',
            'title' => 'سفارش ثبت شد',
            'at'    => $this->created_at,
            'icon'  => '📝',
            'done'  => (bool) $this->created_at,
        ];

        if (!empty($this->paid_at) || in_array($this->status, ['processing','completed'])) {
            $t[] = [
                'key'   => 'paid',
                'title' => 'پرداخت تأیید شد',
                'at'    => $this->paid_at ?? $this->updated_at,
                'icon'  => '💳',
                'done'  => true,
            ];
        }

        $t[] = [
            'key'   => 'supply_found',
            'title' => 'محصول پیدا شد',
            'at'    => $this->supply_found_at,
            'icon'  => '📦',
            'done'  => (bool) $this->supply_found_at,
        ];

        $t[] = [
            'key'   => 'delivered_to_shipping',
            'title' => 'تحویل به واحد ارسال',
            'at'    => $this->delivered_to_shipping_at,
            'icon'  => '🚚',
            'done'  => (bool) $this->delivered_to_shipping_at,
        ];

        $t[] = [
            'key'   => 'shipped',
            'title' => 'ارسال شد',
            'at'    => $this->shipped_at,
            'icon'  => '✈️',
            'done'  => (bool) $this->shipped_at,
        ];

        $t[] = [
            'key'   => 'delivered',
            'title' => 'تحویل به مشتری',
            'at'    => $this->delivered_at,
            'icon'  => '🏠',
            'done'  => (bool) $this->delivered_at,
        ];

        return $t;
    }

    /**
     * مختصات مبدا (نیشابور)
     */
    public static function originCoordinates(): array
    {
        return ['lat' => 36.2133, 'lng' => 58.7958, 'name' => 'نیشابور'];
    }
}
