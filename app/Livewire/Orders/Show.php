<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class Show extends Component
{
    public Order $order;

    public function mount(Order $order): void
    {
        $this->order = $order->load(['customer', 'channel', 'items']);
    }

    public function changeStatus(string $status): void
    {
        if (! in_array($status, ['pending', 'final-check', 'courier'])) return;
        $this->order->update(['status' => $status]);
        $this->order->refresh();
        session()->flash('success', 'وضعیت به‌روز شد.');
    }

    public function delete()
    {
        $number = $this->order->order_number;
        $this->order->delete();
        session()->flash('success', "سفارش #{$number} حذف شد.");
        return redirect()->route('orders.index');
    }

    public function render()
    {
        $activities = $this->order->activities()->with('causer')->limit(20)->get();
        return view('livewire.orders.show', compact('activities'))
            ->layout('components.layouts.app');
    }
}
