<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Attributes\On;
use Livewire\Component;

class ProfileModal extends Component
{
    public bool $show = false;
    public ?Customer $customer = null;
    public array $stats = [];
    public array $orders = [];

    #[On('open-customer-profile')]
    public function open($customerId = null, $phone = null): void
    {
        $customer = null;

        if (is_numeric($customerId)) {
            $customer = Customer::find((int) $customerId);
        } elseif ($phone) {
            $np = preg_replace('/\D/', '', (string) $phone);
            $customer = Customer::where('phone', 'like', "%{$np}%")->first();
        }

        if (!$customer) {
            $this->dispatch('notify', type: 'error', message: 'مشتری پیدا نشد');
            return;
        }

        $this->customer = $customer;
        $orders = $customer->orders()->with('items')->latest()->get();

        $this->stats = [
            'total' => $orders->count(),
            'sum' => (float) $orders->sum('amount'),
            'insurance' => (float) $orders->sum('insurance'),
            'first' => $orders->last()?->created_at,
            'last' => $orders->first()?->created_at,
        ];

        $this->orders = $orders->take(15)->map(fn($o) => [
            'id' => $o->id,
            'num' => $o->order_number,
            'amount' => (float) $o->amount,
            'status' => $o->status,
            'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d'),
            'products' => $o->items->pluck('title')->take(3)->implode('، '),
            'items_count' => $o->items->count(),
        ])->toArray();

        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->customer = null;
    }

    public function viewOrder(int $orderId): void
    {
        $this->close();
        $this->dispatch('open-order-view', orderId: $orderId);
    }

    public function newOrder(): void
    {
        if (!$this->customer) return;
        $phone = $this->customer->phone;
        $this->close();
        $this->dispatch('open-order-form');
        // اطلاعات مشتری auto fill by phone
    }

    public function callCustomer(): void
    {
        if (!$this->customer) return;
        $this->dispatch('open-call', phone: $this->customer->phone);
    }

    public function render()
    {
        return view('livewire.customers.profile-modal');
    }
}
