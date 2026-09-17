<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class PrintLabel extends Component
{
    public Order $order;
    public function mount(Order $order): void { $this->order = $order->load('customer'); }
    public function render()
    {
        return view('livewire.orders.print-label')->layout('components.layouts.app');
    }
}
