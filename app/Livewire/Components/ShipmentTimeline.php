<?php

namespace App\Livewire\Components;

use App\Models\Order;
use Livewire\Component;

class ShipmentTimeline extends Component
{
    public ?int $orderId = null;
    public bool $show = false;

    protected $listeners = ['show-timeline' => 'showTimeline'];

    public function showTimeline(int $orderId): void
    {
        $this->orderId = $orderId;
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->orderId = null;
    }

    public function render()
    {
        $order = $this->orderId ? Order::with(['customer', 'items'])->find($this->orderId) : null;
        $events = $order ? ($order->shipping_events ?? []) : [];
        usort($events, fn ($a, $b) => ($b['ts'] ?? 0) <=> ($a['ts'] ?? 0));
        $events = array_reverse($events);

        return view('livewire.components.shipment-timeline', [
            'order'  => $order,
            'events' => $events,
        ]);
    }
}
