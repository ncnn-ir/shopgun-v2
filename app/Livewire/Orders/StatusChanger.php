<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use App\Models\OrderTimelineEvent;
use Livewire\Component;

class StatusChanger extends Component
{
    public int $orderId = 0;
    public string $event_key = '';
    public string $notes = '';
    public bool $open = false;

    protected $listeners = ['openStatusChanger' => 'show'];

    public function show(int $orderId): void
    {
        $this->orderId = $orderId;
        $this->event_key = '';
        $this->notes = '';
        $this->open = true;
    }

    public function close(): void { $this->open = false; }

    public function save(): void
    {
        $this->validate([
            'event_key' => 'required|string|max:64',
            'notes'     => 'nullable|string|max:1000',
        ]);

        $order = Order::find($this->orderId);
        if (!$order) { $this->close(); return; }

        // اگر جدول timeline هست
        if (class_exists(OrderTimelineEvent::class) && method_exists($order, 'logEvent')) {
            $order->logEvent($this->event_key, $this->notes ?: null);
        }

        // سینک با status/supply_status
        $sync = [
            'supply_found'          => ['supply_status' => 'found'],
            'delivered_to_shipping' => ['supply_status' => 'delivered_to_shipping'],
            'final_check'           => ['status' => 'final-check'],
            'handed_to_courier'     => ['status' => 'courier'],
        ];
        if (isset($sync[$this->event_key])) {
            $order->update($sync[$this->event_key]);
        }

        $this->dispatch('timeline-updated');
        session()->flash('message', '✓ رویداد ثبت شد');
        $this->close();
    }

    public function render()
    {
        $catalog = [
            'created'               => ['ثبت سفارش',          '📝', '#f59e0b'],
            'paid'                  => ['پرداخت تأیید شد',     '💳', '#10b981'],
            'sent_for_sizing'       => ['ارسال برای سایز',     '📏', '#8b5cf6'],
            'sent_for_making'       => ['ارسال برای ساخت',     '🔨', '#f97316'],
            'supply_found'          => ['محصول پیدا شد',       '📦', '#3b82f6'],
            'delivered_to_shipping' => ['تحویل واحد ارسال',    '🚚', '#0ea5e9'],
            'packaging'             => ['بسته بندی',           '📦', '#a855f7'],
            'final_check'           => ['چک نهایی',            '🔍', '#6366f1'],
            'handed_to_courier'     => ['تحویل پیک',           '🛵', '#f59e0b'],
            'registered_in_system'  => ['ثبت در سامانه ارسال', '💾', '#14b8a6'],
            'shipped'               => ['ارسال شد',            '✈️', '#06b6d4'],
            'delivered'             => ['تحویل به مشتری',      '🏠', '#22c55e'],
            'cancelled'             => ['لغو شد',              '❌', '#ef4444'],
            'note'                  => ['یادداشت',             '📌', '#6b7280'],
        ];

        if (class_exists(OrderTimelineEvent::class)) {
            $catalog = OrderTimelineEvent::CATALOG;
        }

        return view('livewire.orders.status-changer', [
            'order'   => $this->orderId ? Order::find($this->orderId) : null,
            'catalog' => $catalog,
        ]);
    }
}
