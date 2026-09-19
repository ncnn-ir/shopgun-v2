<?php

namespace App\Observers;

use App\Models\Order;
use App\Models\OrderStatusHistory;
use App\Models\AppNotification;
use App\Application\Notifications\NotificationService;
use Illuminate\Support\Facades\Route;

class OrderObserver
{
    public function created(Order $order): void
    {
        // ثبت وضعیت اولیه
        try {
            OrderStatusHistory::create([
                'order_id' => $order->id,
                'from_status' => null,
                'to_status' => $order->status ?? 'pending',
                'note' => 'ایجاد سفارش',
                'changed_by' => auth()->id(),
                'changed_at' => now(),
            ]);
        } catch (\Throwable $e) {}

        // اعلان
        try {
            if (Route::has('orders.show')) {
                NotificationService::toAll(
                    type: 'order_created',
                    title: "🆕 سفارش جدید #{$order->order_number}",
                    message: ($order->customer?->name ?? 'مشتری') . ' — ' . number_format((float) $order->amount),
                    icon: '📦',
                    url: route('orders.show', $order),
                    data: ['order_id' => $order->id],
                );
            }
        } catch (\Throwable $e) {}
    }

    public function updated(Order $order): void
    {
        if (!$order->wasChanged('status')) return;

        $from = $order->getOriginal('status');
        $to = $order->status;

        // ثبت تاریخچه
        try {
            OrderStatusHistory::create([
                'order_id' => $order->id,
                'from_status' => $from,
                'to_status' => $to,
                'changed_by' => auth()->id(),
                'changed_at' => now(),
            ]);
        } catch (\Throwable $e) {}

        // اعلان
        try {
            if (Route::has('orders.show')) {
                NotificationService::toAll(
                    type: 'order_status',
                    title: "🔄 تغییر وضعیت #{$order->order_number}",
                    message: \App\Support\OrderStatus::label($to),
                    icon: '🔄',
                    url: route('orders.show', $order),
                    data: ['order_id' => $order->id, 'from' => $from, 'to' => $to],
                );
            }
        } catch (\Throwable $e) {}
    }
}
