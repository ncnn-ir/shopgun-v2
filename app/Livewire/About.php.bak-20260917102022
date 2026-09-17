<?php

namespace App\Livewire;

use Livewire\Component;
use App\Models\Order;
use App\Models\Customer;
use App\Models\Product;
use App\Models\Certificate;

class About extends Component
{
    public function render()
    {
        $stats = [
            'orders'       => Order::count(),
            'customers'    => Customer::count(),
            'products'     => Product::count(),
            'certificates' => Certificate::count(),
        ];

        return view('livewire.about', compact('stats'))
            ->layout('components.layouts.app');
    }
}
