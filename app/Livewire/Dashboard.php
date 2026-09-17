<?php
namespace App\Livewire;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Component;

class Dashboard extends Component
{
    public function render() {
        $stats = [
            'orders' => Order::count(),
            'orders_today' => Order::whereDate('created_at', today())->count(),
            'orders_pending' => Order::where('status', 'pending')->count(),
            'orders_final' => Order::where('status', 'final-check')->count(),
            'orders_courier' => Order::where('status', 'courier')->count(),
            'customers' => Customer::count(),
            'products' => Product::count(),
            'certificates' => Certificate::count(),
        ];

        // Recent orders
        $recent = Order::latest('id')->limit(10)->get();

        // Daily chart (7 days)
        $daily = [];
        for ($i = 6; $i >= 0; $i--) {
            $d = now()->subDays($i);
            $daily[] = [
                'date' => \App\Support\PersianDate::format($d, 'm/d'),
                'count' => Order::whereDate('created_at', $d)->count(),
            ];
        }

        return view('livewire.dashboard', compact('stats', 'recent', 'daily'))
            ->layout('components.layouts.app');
    }
}
