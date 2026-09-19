<?php

namespace App\Application\Reports;

use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Channel;
use Illuminate\Support\Facades\DB;

/**
 * ★ SalesMetrics — آمار فروش
 * همه کوئری‌های آماری اینجا متمرکز
 */
class SalesMetrics
{
    public function __construct(
        public \Carbon\Carbon $from,
        public \Carbon\Carbon $to,
    ) {}

    public function ordersCount(): int
    {
        return Order::whereBetween('created_at', [$this->from, $this->to])->count();
    }

    public function totalRevenue(): float
    {
        return (float) Order::whereBetween('created_at', [$this->from, $this->to])->sum('amount');
    }

    public function avgOrderValue(): float
    {
        $count = $this->ordersCount();
        return $count > 0 ? $this->totalRevenue() / $count : 0;
    }

    public function pendingOrdersCount(): int
    {
        return Order::whereBetween('created_at', [$this->from, $this->to])
            ->where('status', 'pending')->count();
    }

    public function byStatus(): array
    {
        return Order::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->selectRaw('status, COUNT(*) as cnt, SUM(amount) as total')
            ->groupBy('status')
            ->get()
            ->keyBy('status')
            ->map(fn($r) => ['count' => (int) $r->cnt, 'total' => (float) $r->total])
            ->toArray();
    }

    public function byChannel(): array
    {
        return Order::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->with('channel')
            ->get()
            ->groupBy('channel_id')
            ->map(fn($g) => [
                'name' => $g->first()->channel?->name ?? 'نامشخص',
                'color' => $g->first()->channel?->color ?? '#64748b',
                'count' => $g->count(),
                'total' => (float) $g->sum('amount'),
            ])
            ->values()
            ->toArray();
    }

    public function dailySeries(int $days = 7): array
    {
        $series = [];
        for ($i = $days - 1; $i >= 0; $i--) {
            $d = now()->subDays($i);
            $series[] = [
                'date' => \App\Support\PersianDate::format($d, 'm/d'),
                'date_raw' => $d->format('Y-m-d'),
                'count' => Order::whereDate('created_at', $d)->count(),
                'total' => (float) Order::whereDate('created_at', $d)->sum('amount'),
            ];
        }
        return $series;
    }

    public function topProducts(int $limit = 5): array
    {
        return OrderItem::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->select('title', DB::raw('COUNT(*) as cnt'), DB::raw('SUM(price * quantity) as total'))
            ->groupBy('title')
            ->orderByDesc('cnt')
            ->limit($limit)
            ->get()
            ->toArray();
    }
}
