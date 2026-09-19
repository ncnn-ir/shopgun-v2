<?php

namespace App\Observers;

use App\Models\AppNotification;
use App\Models\Order;
use Illuminate\Support\Facades\Route;

class OrderObserver
{
    public function created(Order $order): void
    {
        // ★ سفارشات pending → awaiting_supply به صورت خودکار
        if ($order->status === 'pending' && $order->supply_status === 'default') {
            try {
                $order->updateQuietly(['supply_status' => 'awaiting_supply']);
            } catch (\Throwable $e) {}
        }

        if (! Route::has('orders.show')) {
            return;
        }

        AppNotification::broadcast(
            type: 'order_created',
            title: "سفارش جدید #{$order->order_number}",
            message: ($order->customer?->name ?? 'مشتری') . ' — ' . number_format((float) $order->amount),
            icon: '📦',
            url: route('orders.show', $order),
            data: ['order_id' => $order->id],
        );
    }

    public function updated(Order $order): void
    {
        if (! $order->wasChanged('status')) {
            return;
        }

        if (! Route::has('orders.show')) {
            return;
        }

        AppNotification::broadcast(
            type: 'order_status',
            title: "تغییر وضعیت سفارش #{$order->order_number}",
            message: 'وضعیت جدید: ' . $order->status_label,
            icon: '🔄',
            url: route('orders.show', $order),
            data: ['order_id' => $order->id],
        );
    }
}
