<?php

namespace App\Livewire;

use App\Models\Order;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Product;
use Livewire\Component;

class Dashboard extends Component
{
    public string $range = 'week';

    public function setRange(string $range): void
    {
        $this->range = $range;
    }

    protected function trend(int $current, int $previous): array
    {
        if ($previous == 0) {
            return ['dir' => $current > 0 ? 'up' : 'flat', 'pct' => $current > 0 ? 100 : 0];
        }
        $pct = (($current - $previous) / $previous) * 100;
        if ($pct > 1) return ['dir' => 'up', 'pct' => round($pct, 1)];
        if ($pct < -1) return ['dir' => 'down', 'pct' => round(abs($pct), 1)];
        return ['dir' => 'flat', 'pct' => 0];
    }

    public function render()
    {
        $now = now();
        $today = $now->copy()->startOfDay();
        $yesterday = $now->copy()->subDay()->startOfDay();
        $yesterdayEnd = $now->copy()->subDay()->endOfDay();

        // آمار امروز
        $ordersToday = Order::whereDate('created_at', $today)->count();
        $ordersYesterday = Order::whereBetween('created_at', [$yesterday, $yesterdayEnd])->count();

        $revenueToday = (float) Order::whereDate('created_at', $today)->sum('amount');
        $revenueYesterday = (float) Order::whereBetween('created_at', [$yesterday, $yesterdayEnd])->sum('amount');

        $customersToday = Customer::whereDate('created_at', $today)->count();
        $customersYesterday = Customer::whereBetween('created_at', [$yesterday, $yesterdayEnd])->count();

        $certsToday = Certificate::whereDate('created_at', $today)->count();
        $certsYesterday = Certificate::whereBetween('created_at', [$yesterday, $yesterdayEnd])->count();

        $pending = Order::where('status', 'pending')->count();
        $courier = Order::where('status', 'courier')->count();

        $kpi = [
            [
                'icon' => '📦', 'label' => 'سفارش امروز', 'value' => $ordersToday,
                'yesterday' => $ordersYesterday, 'trend' => $this->trend($ordersToday, $ordersYesterday),
                'color' => 'rgba(41,128,185,.15)', 'raw' => true,
            ],
            [
                'icon' => '💰', 'label' => 'فروش امروز', 'value' => round($revenueToday / 1000000, 1), 'unit' => 'م',
                'yesterday' => round($revenueYesterday / 1000000, 1), 'trend' => $this->trend((int) $revenueToday, (int) $revenueYesterday),
                'color' => 'rgba(39,174,96,.15)', 'dec' => 1,
            ],
            [
                'icon' => '👥', 'label' => 'مشتری جدید', 'value' => $customersToday,
                'yesterday' => $customersYesterday, 'trend' => $this->trend($customersToday, $customersYesterday),
                'color' => 'rgba(155,89,182,.15)', 'raw' => true,
            ],
            [
                'icon' => '💎', 'label' => 'شناسنامه', 'value' => $certsToday,
                'yesterday' => $certsYesterday, 'trend' => $this->trend($certsToday, $certsYesterday),
                'color' => 'rgba(201,168,76,.2)', 'raw' => true,
            ],
            [
                'icon' => '⏳', 'label' => 'در انتظار', 'value' => $pending,
                'color' => 'rgba(243,156,18,.15)', 'raw' => true,
            ],
            [
                'icon' => '🚚', 'label' => 'تحویل مامور', 'value' => $courier,
                'color' => 'rgba(16,185,129,.15)', 'raw' => true,
            ],
        ];

        // سری روزانه
        $series = [];
        $days = $this->range === 'today' ? 8 : 7;
        if ($this->range === 'today') {
            for ($h = 0; $h < 24; $h += 3) {
                $from = $now->copy()->startOfDay()->addHours($h);
                $to = $from->copy()->addHours(3);
                $series[] = [
                    'date' => $h . 'h',
                    'count' => Order::whereBetween('created_at', [$from, $to])->count(),
                ];
            }
        } else {
            for ($i = $days - 1; $i >= 0; $i--) {
                $d = $now->copy()->subDays($i);
                $series[] = [
                    'date' => \App\Support\PersianDate::format($d, 'm/d'),
                    'count' => Order::whereDate('created_at', $d)->count(),
                ];
            }
        }

        // کانال‌ها
        $byChannel = Order::with('channel')
            ->whereDate('created_at', '>=', $now->copy()->subDays(30))
            ->get()
            ->groupBy('channel_id')
            ->map(fn($g) => [
                'name' => $g->first()->channel?->name ?? 'نامشخص',
                'color' => $g->first()->channel?->color ?? '#64748b',
                'count' => $g->count(),
            ])
            ->values()
            ->toArray();

        $recent = Order::with('channel', 'customer', 'items')->latest('id')->limit(6)->get();

        return view('livewire.dashboard-v3', [
            'kpi' => $kpi,
            'series' => $series,
            'byChannel' => $byChannel,
            'recent' => $recent,
        ])->layout('components.layouts.app');
    }
}
