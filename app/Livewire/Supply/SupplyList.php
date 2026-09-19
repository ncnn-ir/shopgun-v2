<?php

namespace App\Livewire\Supply;

use App\Models\Order;
use Illuminate\Support\Facades\Auth;
use Livewire\Component;
use Livewire\WithPagination;

class SupplyList extends Component
{
    use WithPagination;

    public string $filter = 'pending';
    public string $search = '';
    public int $perPage = 20;
    public array $selected = [];

    protected $queryString = ['filter' => ['except' => 'pending'], 'search' => ['except' => '']];

    public function updatingSearch()  { $this->resetPage(); }
    public function updatingFilter()  { $this->resetPage(); }

    public function markFound(int $orderId): void
    {
        $order = Order::find($orderId);
        if (!$order) return;
        $order->markSupplyFound(Auth::id());
        session()->flash('message', "سفارش #{$order->id} — محصول پیدا شد ✓");
    }

    public function unmarkFound(int $orderId): void
    {
        $order = Order::find($orderId);
        if (!$order) return;
        $order->update([
            'supply_status'   => 'awaiting_supply',
            'supply_found_at' => null,
            'supply_found_by' => null,
        ]);
        session()->flash('message', "تیک برداشته شد.");
    }

    public function deliverToShipping(int $orderId): void
    {
        $order = Order::find($orderId);
        if (!$order) return;
        if (!$order->isSupplyFound()) {
            session()->flash('error', 'ابتدا باید محصول پیدا شود.');
            return;
        }
        $order->markDeliveredToShipping(Auth::id());
        session()->flash('message', "سفارش #{$order->id} به واحد ارسال تحویل شد ✓");
    }

    public function bulkMarkFound(): void
    {
        if (empty($this->selected)) {
            session()->flash('error', 'چیزی انتخاب نشده.');
            return;
        }
        $n = 0;
        foreach ($this->selected as $id) {
            $o = Order::find($id);
            if ($o && $o->isAwaitingSupply()) {
                $o->markSupplyFound(Auth::id());
                $n++;
            }
        }
        $this->selected = [];
        session()->flash('message', "{$n} سفارش علامت‌گذاری شد.");
    }

    public function bulkDeliver(): void
    {
        if (empty($this->selected)) {
            session()->flash('error', 'چیزی انتخاب نشده.');
            return;
        }
        $n = 0;
        foreach ($this->selected as $id) {
            $o = Order::find($id);
            if ($o && $o->isSupplyFound()) {
                $o->markDeliveredToShipping(Auth::id());
                $n++;
            }
        }
        $this->selected = [];
        session()->flash('message', "{$n} سفارش تحویل ارسال شد.");
    }

    protected function baseQuery()
    {
        $q = Order::query()->with(['customer', 'items']);

        match ($this->filter) {
            'pending' => $q->where(function ($x) {
                $x->whereIn('supply_status', ['awaiting_supply', 'pending'])
                  ->orWhereNull('supply_status');
            }),
            'found'     => $q->where('supply_status', 'found'),
            'delivered' => $q->where('supply_status', 'delivered_to_shipping'),
            default     => null,
        };

        if ($this->search) {
            $s = '%' . $this->search . '%';
            $q->where(function ($x) use ($s) {
                $x->where('id', 'like', $s)
                  ->orWhereHas('customer', function ($c) use ($s) {
                      $c->where('first_name', 'like', $s)
                        ->orWhere('last_name',  'like', $s)
                        ->orWhere('phone',      'like', $s);
                  });
            });
        }

        return $q->orderByDesc('created_at');
    }

    public function render()
    {
        $orders = $this->baseQuery()->paginate($this->perPage);

        $stats = [
            'pending'   => Order::where(function ($q) {
                $q->whereIn('supply_status', ['awaiting_supply', 'pending'])
                  ->orWhereNull('supply_status');
            })->count(),
            'found'     => Order::where('supply_status', 'found')->count(),
            'delivered' => Order::where('supply_status', 'delivered_to_shipping')->count(),
        ];

        return view('livewire.supply.supply-list', compact('orders', 'stats'))
            ->layout('components.layouts.app');
    }
}
