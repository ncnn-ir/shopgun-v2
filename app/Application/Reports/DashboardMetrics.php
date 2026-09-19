<?php

namespace App\Application\Reports;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

/**
 * ★ DashboardMetrics — آمار کامل داشبورد
 * شامل: کانال فروش، روند، پرفروش‌ها، نسبت لغو، در انتظار تامین
 */
class DashboardMetrics
{
    public function __construct(
        public Carbon $from,
        public Carbon $to,
    ) {}

    // ═══════════════════════════════════════════════════════════
    // KPI
    // ═══════════════════════════════════════════════════════════
    public function kpi(): array
    {
        return [
            [
                'icon' => '📦', 'label' => 'کل سفارشات',
                'value' => Order::whereBetween('created_at', [$this->from, $this->to])->count(),
                'color' => '#3b82f6',
                'route' => route('orders.index'),
            ],
            [
                'icon' => '✅', 'label' => 'سفارشات موفق',
                'value' => Order::whereBetween('created_at', [$this->from, $this->to])
                    ->whereIn('status', ['final-check', 'courier'])->count(),
                'color' => '#10b981',
                'route' => route('orders.index', ['status' => 'final-check']),
            ],
            [
                'icon' => '⏳', 'label' => 'در انتظار تامین',
                'value' => Order::where('supply_status', 'awaiting_supply')->count(),
                'color' => '#f59e0b',
                'route' => route('orders.index', ['supply' => 'awaiting']),
            ],
            [
                'icon' => '👥', 'label' => 'مشتریان',
                'value' => Customer::count(),
                'color' => '#8b5cf6',
                'route' => route('customers.index'),
            ],
            [
                'icon' => '💎', 'label' => 'شناسنامه‌ها',
                'value' => Certificate::whereBetween('created_at', [$this->from, $this->to])->count(),
                'color' => '#c9a84c',
                'route' => route('certificates.index'),
            ],
            [
                'icon' => '💰', 'label' => 'درآمد (م تومان)',
                'value' => round(Order::whereBetween('created_at', [$this->from, $this->to])
                    ->whereIn('status', ['final-check', 'courier'])
                    ->sum('amount') / 1000000, 1),
                'color' => '#16a34a',
                'route' => route('reports.index'),
            ],
        ];
    }

    // ═══════════════════════════════════════════════════════════
    // Sales by Channel
    // ═══════════════════════════════════════════════════════════
    public function salesByChannel(): array
    {
        $rows = Order::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->select('sales_channel', DB::raw('COUNT(*) as cnt'), DB::raw('SUM(amount) as total'))
            ->groupBy('sales_channel')
            ->orderByDesc('total')
            ->get();

        $total = $rows->sum('total') ?: 1;

        return $rows->map(function ($r) use ($total) {
            $channel = $r->sales_channel ?? 'website';
            return [
                'channel' => $channel,
                'label' => $this->channelLabel($channel),
                'color' => $this->channelColor($channel),
                'count' => (int) $r->cnt,
                'total' => (float) $r->total,
                'percent' => round(($r->total / $total) * 100, 1),
            ];
        })->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Recent Orders per channel (10 per channel)
    // ═══════════════════════════════════════════════════════════
    public function recentByChannel(int $limit = 10): array
    {
        $channels = ['website', 'basalam', 'terb', 'zibal', 'instagram', 'telegram', 'phone'];
        $result = [];

        foreach ($channels as $ch) {
            $orders = Order::query()
                ->where('sales_channel', $ch)
                ->with('items')
                ->latest('id')
                ->limit($limit)
                ->get();

            if ($orders->isEmpty()) continue;

            $result[] = [
                'channel' => $ch,
                'label' => $this->channelLabel($ch),
                'color' => $this->channelColor($ch),
                'count' => $orders->count(),
                'orders' => $orders->map(fn($o) => [
                    'id' => $o->id,
                    'num' => $o->order_number,
                    'customer' => $o->customer_name,
                    'amount' => (float) $o->amount,
                    'status' => $o->status,
                    'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d H:i'),
                    'items_count' => $o->items->count(),
                ])->toArray(),
            ];
        }

        return $result;
    }

    // ═══════════════════════════════════════════════════════════
    // Sales Trend
    // ═══════════════════════════════════════════════════════════
    public function salesTrend(int $days = 30): array
    {
        $trend = [];
        $diff = $this->from->diffInDays($this->to);

        if ($diff <= 1) {
            // امروز — به تفکیک ساعت
            for ($h = 0; $h < 24; $h += 2) {
                $f = $this->from->copy()->addHours($h);
                $t = $f->copy()->addHours(2);
                $trend[] = [
                    'label' => $h . 'h',
                    'total' => (float) Order::whereBetween('created_at', [$f, $t])->sum('amount') / 1000000,
                    'count' => Order::whereBetween('created_at', [$f, $t])->count(),
                ];
            }
        } elseif ($diff <= 31) {
            // روزانه
            for ($i = $diff; $i >= 0; $i--) {
                $d = $this->to->copy()->subDays($i);
                $trend[] = [
                    'label' => \App\Support\PersianDate::format($d, 'm/d'),
                    'total' => (float) Order::whereDate('created_at', $d)->sum('amount') / 1000000,
                    'count' => Order::whereDate('created_at', $d)->count(),
                ];
            }
        } else {
            // ماهانه
            $start = $this->from->copy()->startOfMonth();
            while ($start <= $this->to) {
                $end = $start->copy()->endOfMonth();
                $trend[] = [
                    'label' => \App\Support\PersianDate::format($start, 'n'),
                    'total' => (float) Order::whereBetween('created_at', [$start, $end])->sum('amount') / 1000000,
                    'count' => Order::whereBetween('created_at', [$start, $end])->count(),
                ];
                $start->addMonth();
            }
        }

        return $trend;
    }

    // ═══════════════════════════════════════════════════════════
    // Top Products
    // ═══════════════════════════════════════════════════════════
    public function topProducts(int $limit = 10): array
    {
        return OrderItem::query()
            ->whereBetween('order_items.created_at', [$this->from, $this->to])
            ->whereHas('order')
            ->select(
                'title',
                DB::raw('COUNT(*) as cnt'),
                DB::raw('SUM(price * quantity) as total')
            )
            ->groupBy('title')
            ->orderByDesc('cnt')
            ->limit($limit)
            ->get()
            ->map(fn($r) => [
                'title' => $r->title,
                'count' => (int) $r->cnt,
                'total' => (float) $r->total,
            ])
            ->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Top Customers
    // ═══════════════════════════════════════════════════════════
    public function topCustomers(int $limit = 10): array
    {
        return Customer::query()
            ->has('orders')
            ->withCount('orders')
            ->withSum('orders', 'amount')
            ->orderByDesc('orders_sum_amount')
            ->limit($limit)
            ->get()
            ->map(fn($c) => [
                'id' => $c->id,
                'name' => $c->name,
                'phone' => $c->phone,
                'orders_count' => (int) $c->orders_count,
                'total' => (float) $c->orders_sum_amount,
            ])
            ->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Cancelled vs Successful
    // ═══════════════════════════════════════════════════════════
    public function cancelledRatio(): array
    {
        $base = Order::whereBetween('created_at', [$this->from, $this->to]);

        $success = (clone $base)->whereIn('status', ['final-check', 'courier'])->count();
        $cancelled = (clone $base)->whereIn('woo_status', ['cancelled', 'refunded', 'failed'])->count();
        $pending = (clone $base)->where('status', 'pending')->count();
        $total = $success + $cancelled + $pending;

        return [
            'success' => $success,
            'cancelled' => $cancelled,
            'pending' => $pending,
            'total' => $total,
            'success_pct' => $total > 0 ? round(($success / $total) * 100, 1) : 0,
            'cancelled_pct' => $total > 0 ? round(($cancelled / $total) * 100, 1) : 0,
            'pending_pct' => $total > 0 ? round(($pending / $total) * 100, 1) : 0,
        ];
    }

    // ═══════════════════════════════════════════════════════════
    // Pending Supply Orders (در انتظار تامین)
    // ═══════════════════════════════════════════════════════════
    public function pendingSupplyOrders(int $limit = 30): array
    {
        return Order::query()
            ->where('supply_status', 'awaiting_supply')
            ->with(['items', 'customer'])
            ->latest('id')
            ->limit($limit)
            ->get()
            ->map(fn($o) => [
                'id' => $o->id,
                'num' => $o->order_number,
                'customer' => $o->customer_name,
                'phone' => $o->phone,
                'amount' => (float) $o->amount,
                'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d'),
                'items' => $o->items->map(fn($i) => [
                    'title' => $i->title,
                    'sku' => $i->sku,
                    'qty' => (int) $i->quantity,
                ])->toArray(),
            ])
            ->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Helpers
    // ═══════════════════════════════════════════════════════════
    public static function channelLabel(string $ch): string
    {
        return match ($ch) {
            'basalam' => '🛍️ باسلام',
            'terb' => '🏬 ترب',
            'zibal' => '💳 زیبال',
            'zarinpal' => '💳 زرین‌پال',
            'bank' => '🏦 کارت‌به‌کارت',
            'cod' => '💵 در محل',
            'website' => '🌐 سایت',
            'instagram' => '📷 اینستاگرام',
            'telegram' => '✈️ تلگرام',
            'phone' => '📞 تلفنی',
            'direct' => '🤝 حضوری',
            default => '🌐 ' . $ch,
        };
    }

    public static function channelColor(string $ch): string
    {
        return match ($ch) {
            'basalam' => '#00b894',
            'terb' => '#f59e0b',
            'zibal' => '#3b82f6',
            'zarinpal' => '#8b5cf6',
            'bank' => '#64748b',
            'cod' => '#10b981',
            'website' => '#6b0f1a',
            'instagram' => '#e91e63',
            'telegram' => '#29b6f6',
            'phone' => '#66bb6a',
            'direct' => '#ffb74d',
            default => '#94a3b8',
        };
    }
}
