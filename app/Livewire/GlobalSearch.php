<?php

namespace App\Livewire;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class GlobalSearch extends Component
{
    public string $query = '';
    public bool $open = false;

    public function updatedQuery(): void
    {
        $this->open = strlen(trim($this->query)) >= 2;
    }

    public function openSearch(): void { $this->open = true; }
    public function close(): void { $this->open = false; $this->query = ''; }

    public function render()
    {
        $orders = [];
        $customers = [];

        if (strlen(trim($this->query)) >= 2) {
            $q = trim($this->query);
            $orders = Order::query()
                ->where(function ($qq) use ($q) {
                    $qq->where('order_number', 'like', "%{$q}%")
                       ->orWhere('phone', 'like', "%{$q}%")
                       ->orWhereHas('customer', fn ($cq) => $cq->where('name', 'like', "%{$q}%"));
                })
                ->latest('id')->limit(5)->get();

            $customers = Customer::query()
                ->where(function ($qq) use ($q) {
                    $qq->where('phone', 'like', "%{$q}%")
                       ->orWhere('name', 'like', "%{$q}%");
                })
                ->latest('id')->limit(5)->get();
        }

        return view('livewire.global-search', compact('orders', 'customers'));
    }
}
