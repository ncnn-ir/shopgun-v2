<?php

namespace App\Support;

/**
 * ★ OrderStatus — مدیریت وضعیت‌های سفارش
 * Enum معنایی + ترجمه + رنگ + ترتیب
 */
class OrderStatus
{
    public const FLOW = [
        'pending'         => ['label' => 'ثبت سفارش',       'icon' => '📝', 'color' => '#f59e0b', 'bg' => '#fef3c7'],
        'email-sent'      => ['label' => 'ارسال ایمیل',      'icon' => '📧', 'color' => '#8b5cf6', 'bg' => '#ede9fe'],
        'size-order'      => ['label' => 'سفارش سایز',       'icon' => '📐', 'color' => '#06b6d4', 'bg' => '#cffafe'],
        'in-production'   => ['label' => 'در حال ساخت',      'icon' => '🔨', 'color' => '#f97316', 'bg' => '#fed7aa'],
        'shipping-dept'   => ['label' => 'تحویل به ارسال',   'icon' => '📦', 'color' => '#0ea5e9', 'bg' => '#e0f2fe'],
        'packaged'        => ['label' => 'بسته‌بندی شده',    'icon' => '🎁', 'color' => '#a855f7', 'bg' => '#f3e8ff'],
        'final-check'     => ['label' => 'چک نهایی',         'icon' => '🔍', 'color' => '#3b82f6', 'bg' => '#dbeafe'],
        'courier'         => ['label' => 'تحویل به پیک',     'icon' => '🚚', 'color' => '#10b981', 'bg' => '#d1fae5'],
        'posted'          => ['label' => 'ارسال پستی',       'icon' => '📮', 'color' => '#0891b2', 'bg' => '#cffafe'],
        'delivered'       => ['label' => 'تحویل داده شد',    'icon' => '✅', 'color' => '#16a34a', 'bg' => '#dcfce7'],
        'cancelled'       => ['label' => 'لغو شده',          'icon' => '❌', 'color' => '#dc2626', 'bg' => '#fee2e2'],
    ];

    public static function all(): array
    {
        return self::FLOW;
    }

    public static function labels(): array
    {
        return array_map(fn($v) => $v['icon'] . ' ' . $v['label'], self::FLOW);
    }

    public static function label(string $status): string
    {
        $s = self::FLOW[$status] ?? null;
        return $s ? ($s['icon'] . ' ' . $s['label']) : $status;
    }

    public static function color(string $status): string
    {
        return self::FLOW[$status]['color'] ?? '#64748b';
    }

    public static function bg(string $status): string
    {
        return self::FLOW[$status]['bg'] ?? '#f1f5f9';
    }

    public static function order(string $status): int
    {
        return array_search($status, array_keys(self::FLOW)) ?: 0;
    }

    public static function next(string $current): string
    {
        $keys = array_keys(self::FLOW);
        $idx = array_search($current, $keys);
        if ($idx === false) return $keys[0];
        return $keys[($idx + 1) % count($keys)];
    }

    /**
     * اعتبارسنجی
     */
    public static function valid(string $status): bool
    {
        return isset(self::FLOW[$status]);
    }

    /**
     * دسته‌بندی برای فیلتر
     */
    public static function activeStatuses(): array
    {
        return ['pending', 'email-sent', 'size-order', 'in-production', 'shipping-dept', 'packaged', 'final-check', 'courier', 'posted'];
    }
}
