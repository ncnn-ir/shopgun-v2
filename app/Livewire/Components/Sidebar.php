<?php

namespace App\Livewire\Components;

use App\Models\ApiLog;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use App\Support\PersianDate;
use App\Support\PersianNumber;
use Livewire\Component;

class Sidebar extends Component
{
    public array $stats = [];
    public int $notifCount = 0;
    public string $today = '';
    public string $dayOfWeek = '';

    public function mount(): void
    {
        $this->refresh();
    }

    public function refresh(): void
    {
        $this->stats = [
            'orders_total'    => Order::count(),
            'orders_today'    => Order::whereDate('created_at', today())->count(),
            'orders_pending'  => Order::where('status', 'pending')->count(),
            'orders_check'    => Order::where('status', 'final-check')->count(),
            'orders_courier'  => Order::where('status', 'courier')->count(),
            'customers'       => Customer::count(),
            'products'        => Product::count(),
            'certificates'    => Certificate::count(),
            'api_today'       => ApiLog::whereDate('created_at', today())->count(),
            'api_errors'      => ApiLog::whereNotNull('error')
                                    ->whereDate('created_at', today())->count(),
        ];

        $this->notifCount = $this->stats['orders_pending'] + $this->stats['api_errors'];

        $now = now();
        $this->today = PersianDate::format($now, 'Y/m/d');
        $this->dayOfWeek = PersianDate::dayOfWeek($now);
    }

    public function render()
    {
        return view('livewire.components.sidebar');
    }
}
