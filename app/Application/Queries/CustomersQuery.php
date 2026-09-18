<?php

namespace App\Application\Queries;

use App\Models\Customer;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

class CustomersQuery
{
    public function __construct(
        public string $search = '',
        public string $filter = '',
        public string $sortField = 'id',
        public string $sortDir = 'desc',
        public int $perPage = 20,
    ) {}

    public function paginate(): LengthAwarePaginator
    {
        return Customer::query()
            ->withCount('orders')
            ->withSum('orders', 'amount')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filter === 'has_orders', fn($q) => $q->has('orders'))
            ->when($this->filter === 'no_orders', fn($q) => $q->doesntHave('orders'))
            ->orderBy($this->sortField, $this->sortDir)
            ->paginate($this->perPage);
    }

    public function summary(): array
    {
        return [
            'total' => Customer::count(),
            'with_orders' => Customer::has('orders')->count(),
            'today' => Customer::whereDate('created_at', today())->count(),
        ];
    }
}
