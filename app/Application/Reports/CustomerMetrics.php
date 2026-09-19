<?php

namespace App\Application\Reports;

use App\Models\Customer;

class CustomerMetrics
{
    public function __construct(
        public \Carbon\Carbon $from,
        public \Carbon\Carbon $to,
    ) {}

    public function newCustomersCount(): int
    {
        return Customer::whereBetween('created_at', [$this->from, $this->to])->count();
    }

    public function totalCustomers(): int
    {
        return Customer::count();
    }

    public function customersWithOrdersCount(): int
    {
        return Customer::has('orders')->count();
    }

    public function topCustomers(int $limit = 5): \Illuminate\Database\Eloquent\Collection
    {
        return Customer::query()
            ->has('orders')
            ->withCount('orders')
            ->withSum('orders', 'amount')
            ->orderByDesc('orders_sum_amount')
            ->limit($limit)
            ->get();
    }

    public function repeatRate(): float
    {
        $withOrders = $this->customersWithOrdersCount();
        if ($withOrders === 0) return 0;

        $repeaters = Customer::has('orders', '>=', 2)->count();
        return round(($repeaters / $withOrders) * 100, 1);
    }
}
