<?php

namespace App\Application\Actions;

use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use App\Application\Notifications\NotificationService;

/**
 * ★ CreateOrderAction
 * نقطه واحد ساخت سفارش — با منطق دامنه
 */
class CreateOrderAction
{
    /**
     * @param array $data {
     *   phone, name, address, postal_code, channel_id,
     *   insurance, discount, shipping, notes, invoice_needed,
     *   items: [{title, sku, price, quantity, cert_needed}]
     * }
     */
    public function execute(array $data): Order
    {
        // ۱. Resolve یا ایجاد مشتری
        $customer = $this->resolveCustomer($data);

        // ۲. محاسبه مبلغ کل
        $amount = 0;
        foreach ($data['items'] ?? [] as $it) {
            $amount += ((float) ($it['price'] ?? 0)) * ((int) ($it['quantity'] ?? 1));
        }

        // ۳. ایجاد سفارش
        $order = Order::create([
            'order_number' => Order::generateNumber(),
            'customer_id' => $customer->id,
            'customer_name' => $data['name'] ?? $customer->name,
            'phone' => $customer->phone,
            'address' => $data['address'] ?? $customer->address,
            'postal_code' => $data['postal_code'] ?? $customer->postal_code,
            'channel_id' => $data['channel_id'] ?? null,
            'status' => $data['status'] ?? 'pending',
            'amount' => $amount,
            'insurance' => (float) ($data['insurance'] ?? 0),
            'discount' => (float) ($data['discount'] ?? 0),
            'shipping' => (float) ($data['shipping'] ?? 0),
            'notes' => $data['notes'] ?? null,
            'invoice_needed' => (bool) ($data['invoice_needed'] ?? false),
        ]);

        // ۴. اقلام سفارش
        foreach (($data['items'] ?? []) as $idx => $it) {
            if (empty($it['title']) && empty($it['sku'])) continue;

            OrderItem::create([
                'order_id' => $order->id,
                'sku' => $it['sku'] ?? null,
                'title' => $it['title'] ?? 'محصول',
                'price' => (float) ($it['price'] ?? 0),
                'quantity' => (int) ($it['quantity'] ?? 1),
                'cert_needed' => (bool) ($it['cert_needed'] ?? true),
                'sort_order' => $idx,
            ]);
        }

        // ۵. اعلان
        try {
            NotificationService::toAll(
                type: 'order_created',
                title: "سفارش جدید #{$order->order_number}",
                message: ($customer->name ?? 'مشتری') . ' — ' . number_format($amount),
                icon: '📦',
                url: route('orders.show', $order),
                data: ['order_id' => $order->id],
            );
        } catch (\Throwable $e) {}

        return $order;
    }

    protected function resolveCustomer(array $data): Customer
    {
        $phone = Customer::normalizePhone($data['phone'] ?? '');
        if ($phone === '') {
            throw new \InvalidArgumentException('شماره تلفن معتبر نیست');
        }

        $customer = Customer::where('phone', $phone)->first();

        if (!$customer) {
            $customer = Customer::create([
                'name' => $data['name'] ?? 'بدون نام',
                'phone' => $phone,
                'address' => $data['address'] ?? null,
                'postal_code' => $data['postal_code'] ?? null,
            ]);
        } else {
            // بروزرسانی اطلاعات اگر داده جدید داشتیم
            $update = [];
            if (!empty($data['name']) && $data['name'] !== $customer->name) {
                $update['name'] = $data['name'];
            }
            if (!empty($data['address']) && $data['address'] !== $customer->address) {
                $update['address'] = $data['address'];
            }
            if (!empty($data['postal_code']) && $data['postal_code'] !== $customer->postal_code) {
                $update['postal_code'] = $data['postal_code'];
            }
            if (!empty($update)) $customer->update($update);
        }

        return $customer;
    }
}
