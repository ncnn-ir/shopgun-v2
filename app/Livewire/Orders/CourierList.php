<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class CourierList extends Component
{
    public function render()
    {
        $orders = Order::with('customer')->where('status', 'courier')->orderBy('created_at')->get();
        return view('livewire.orders.courier-list', compact('orders'))->layout('components.layouts.app');
    }
}
