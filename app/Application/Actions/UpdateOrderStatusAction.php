<?php

namespace App\Application\Actions;

use App\Models\Order;
use App\Application\Notifications\NotificationService;

/**
 * ★ UpdateOrderStatusAction — با اعتبارسنجی وضعیت
 */
class UpdateOrderStatusAction
{
    public const VALID_STATUSES = ['pending', 'final-check', 'courier'];

    /**
     * تغییر وضعیت سفارش با اعتبارسنجی و اعلان
     */
    public function execute(int $orderId, string $newStatus, ?int $userId = null): ?Order
    {
        if (!in_array($newStatus, self::VALID_STATUSES, true)) {
            throw new \InvalidArgumentException("وضعیت نامعتبر: {$newStatus}");
        }

        $order = Order::find($orderId);
        if (!$order) return null;

        $oldStatus = $order->status;
        if ($oldStatus === $newStatus) return $order;

        $order->update(['status' => $newStatus]);

        // اعلان
        try {
            NotificationService::toAll(
                type: 'order_status',
                title: "تغییر وضعیت سفارش #{$order->order_number}",
                message: "از «{$oldStatus}» به «{$order->status_label}»",
                icon: '🔄',
                url: route('orders.show', $order),
                data: ['order_id' => $order->id, 'old' => $oldStatus, 'new' => $newStatus],
            );
        } catch (\Throwable $e) {}

        return $order;
    }

    /**
     * چرخه وضعیت (برای کلیک)
     */
    public function cycle(int $orderId): ?Order
    {
        $order = Order::find($orderId);
        if (!$order) return null;

        $list = self::VALID_STATUSES;
        $cur = array_search($order->status, $list, true);
        $next = $list[($cur === false ? 0 : ($cur + 1)) % count($list)];

        return $this->execute($orderId, $next);
    }
}
