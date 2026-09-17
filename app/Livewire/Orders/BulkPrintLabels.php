<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class BulkPrintLabels extends Component
{
    public array $orders = [];

    public function mount(): void
    {
        $ids = request()->query('ids', '');
        $idArray = array_filter(explode(',', $ids));
        $this->orders = empty($idArray) ? [] : Order::with('customer')->whereIn('id', $idArray)->orderBy('id')->get()->all();
    }

    public function render()
    {
        return view('livewire.orders.bulk-print-labels')->layout('components.layouts.app');
    }
}
