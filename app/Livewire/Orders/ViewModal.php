<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use App\Models\OrderStatusHistory;
use App\Support\OrderStatus;
use Livewire\Component;

class ViewModal extends Component
{
    public ?int $orderId = null;
    public ?Order $order = null;
    public string $tab = 'details';   // details | history

    public array $statusFlow = [];
    public array $history    = [];

    public bool  $showProductPopup = false;
    public array $productDetail    = [];

    protected $listeners = [
        'open-order-view' => 'open',
    ];

    public function open(int $orderId): void
    {
        $this->orderId = $orderId;
        $this->tab     = 'details';
        $this->load();
    }

    public function setTab(string $tab): void
    {
        if (in_array($tab, ['details', 'history'], true)) {
            $this->tab = $tab;
        }
    }

    public function load(): void
    {
        if (! $this->orderId) return;

        $this->order = Order::with(['items', 'customer', 'channel'])->find($this->orderId);
        if (! $this->order) return;

        $currentStatus = $this->order->status ?? 'pending';
        $currentIdx    = OrderStatus::order($currentStatus);

        $this->statusFlow = collect(OrderStatus::FLOW)
            ->map(function ($s, $key) use ($currentIdx) {
                $idx = OrderStatus::order($key);
                return [
                    'key'   => $key,
                    'label' => $s['label'],
                    'icon'  => $s['icon'],
                    'color' => $s['color'],
                    'state' => $idx < $currentIdx ? 'done'
                             : ($idx === $currentIdx ? 'current' : 'future'),
                ];
            })
            ->values()
            ->toArray();

        $this->history = OrderStatusHistory::where('order_id', $this->orderId)
            ->orderBy('changed_at', 'desc')
            ->limit(50)
            ->get()
            ->map(fn ($h) => [
                'from'    => $h->from_status ? OrderStatus::label($h->from_status) : null,
                'to'      => OrderStatus::label($h->to_status),
                'color'   => OrderStatus::color($h->to_status),
                'note'    => $h->note,
                'user'    => optional($h->changer ?? null)->name,
                'date'    => $h->changed_at?->format('Y/m/d'),
                'time'    => $h->changed_at?->format('H:i'),
            ])
            ->toArray();
    }

    public function close(): void
    {
        $this->orderId          = null;
        $this->order            = null;
        $this->statusFlow       = [];
        $this->history          = [];
        $this->tab              = 'details';
        $this->showProductPopup = false;
        $this->productDetail    = [];
    }

    public function changeStatus(string $status): void
    {
        if (! $this->order || ! OrderStatus::valid($status)) return;
        $from = $this->order->status;
        if ($from === $status) return;

        $this->order->update(['status' => $status]);

        OrderStatusHistory::create([
            'order_id'    => $this->order->id,
            'from_status' => $from,
            'to_status'   => $status,
            'changed_by'  => auth()->id(),
            'changed_at'  => now(),
        ]);

        $this->load();
        $this->dispatch('notify', type: 'success', message: 'وضعیت به‌روزرسانی شد');
    }

    public function showProduct(int $itemId): void
    {
        if (! $this->order) return;
        $item = $this->order->items->firstWhere('id', $itemId);
        if (! $item) return;

        $this->productDetail = [
            'title'    => $item->title,
            'sku'      => $item->sku,
            'price'    => $item->price,
            'quantity' => $item->quantity,
            'total'    => $item->price * $item->quantity,
            'image'    => $item->image_url ?? $item->image_path ?? null,
            'weight'   => $item->weight ?? null,
            'length'   => $item->length ?? null,
            'width'    => $item->width ?? null,
            'metal'    => $item->metal ?? null,
            'carat'    => $item->metal_carat ?? null,
            'stone'    => $item->stone_name ?? $item->stone_en ?? null,
            'updated'  => $item->updated_at?->format('Y/m/d') ?? null,
            'site_url' => $item->meta['permalink'] ?? null,
        ];

        $this->showProductPopup = true;
    }

    public function closeProduct(): void
    {
        $this->showProductPopup = false;
        $this->productDetail    = [];
    }

    public function render()
    {
        return view('livewire.orders.view-modal');
    }
}