<?php

namespace App\Application\Queries;

use App\Models\Order;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

/**
 * ★ OrdersQuery — کوئری یکدست برای سفارشات
 */
class OrdersQuery
{
    public function __construct(
        public string $search = '',
        public string $status = '',
        public ?int $channelId = null,
        public string $dateFrom = '',
        public string $dateTo = '',
        public string $sortField = 'id',
        public string $sortDir = 'desc',
        public int $perPage = 20,
    ) {}

    public function paginate(): LengthAwarePaginator
    {
        return Order::query()
            ->with(['items', 'channel', 'customer'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('customer_name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->status, fn($q) => $q->where('status', $this->status))
            ->when($this->channelId, fn($q) => $q->where('channel_id', $this->channelId))
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo))
            ->orderBy($this->sortField, $this->sortDir)
            ->paginate($this->perPage);
    }

    /**
     * شمارش بر اساس وضعیت
     */
    public function statusCounts(): array
    {
        return Order::query()
            ->selectRaw('status, COUNT(*) as cnt')
            ->groupBy('status')
            ->pluck('cnt', 'status')
            ->toArray();
    }

    /**
     * آمار خلاصه
     */
    public function summary(): array
    {
        $base = Order::query()
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo));

        return [
            'total' => (clone $base)->count(),
            'sum' => (float) (clone $base)->sum('amount'),
            'avg' => (float) (clone $base)->avg('amount'),
            'today' => Order::whereDate('created_at', today())->count(),
        ];
    }
}
