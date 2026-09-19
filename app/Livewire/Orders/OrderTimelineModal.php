<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class OrderTimelineModal extends Component
{
    public ?int $orderId = null;
    public bool $open = false;

    protected $listeners = ['showOrderTimeline' => 'show'];

    public function show(int $orderId): void
    {
        $this->orderId = $orderId;
        $this->open = true;
    }

    public function close(): void
    {
        $this->open = false;
        $this->orderId = null;
    }

    public function render()
    {
        $order = $this->orderId
            ? Order::with(['customer', 'items', 'supplyFoundBy', 'deliveredToShippingBy'])
                ->find($this->orderId)
            : null;

        $timeline = $order ? $order->timeline() : [];
        $origin = Order::originCoordinates();

        $dest = null;
        if ($order) {
            $dest = [
                'lat'   => (float) ($order->shipping_lat ?? 35.6892),
                'lng'   => (float) ($order->shipping_lng ?? 51.3890),
                'name'  => $order->shipping_city
                        ?? optional($order->customer)->city
                        ?? 'مقصد',
                'address' => $order->shipping_address
                        ?? optional($order->customer)->address
                        ?? '',
            ];
        }

        return view('livewire.orders.order-timeline-modal', compact(
            'order', 'timeline', 'origin', 'dest'
        ));
    }
}
