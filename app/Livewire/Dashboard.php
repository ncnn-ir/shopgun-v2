<?php

namespace App\Livewire;

use App\Models\Order;
use App\Models\Certificate;
use App\Models\Customer;
use Livewire\Component;

class Dashboard extends Component
{
    public string $range = 'week';

    public function setRange(string $range): void
    {
        $this->range = $range;
    }

    /**
     * محاسبه‌ی روند رشد/کاهش
     */
    protected function trend(int|float $current, int|float $previous): array
    {
        if ($previous == 0) {
            return [
                'dir'   => $current > 0 ? 'up' : 'flat',
                'pct'   => $current > 0 ? 100 : 0,
                'diff'  => $current - $previous,
            ];
        }
        $pct = (($current - $previous) / $previous) * 100;
        return [
            'dir'  => $pct > 1 ? 'up' : ($pct < -1 ? 'down' : 'flat'),
            'pct'  => round(abs($pct), 1),
            'diff' => $current - $previous,
        ];
    }

    public function render()
    {
        $now          = now();
        $today        = $now->copy()->startOfDay();
        $yesterday    = $now->copy()->subDay()->startOfDay();
        $yesterdayEnd = $now->copy()->subDay()->endOfDay();

        // ─── KPI امروز vs دیروز ───
        $ordersToday     = Order::whereDate('created_at', $today)->count();
        $ordersYesterday = Order::whereBetween('created_at', [$yesterday, $yesterdayEnd])->count();

        $revenueToday     = (float) Order::whereDate('created_at', $today)->sum('amount');
        $revenueYesterday = (float) Order::whereBetween('created_at', [$yesterday, $yesterdayEnd])->sum('amount');

        $customersToday     = Customer::whereDate('created_at', $today)->count();
        $customersYesterday = Customer::whereBetween('created_at', [$yesterday, $yesterdayEnd])->count();

        $certsToday     = Certificate::whereDate('created_at', $today)->count();
        $certsYesterday = Certificate::whereBetween('created_at', [$yesterday, $yesterdayEnd])->count();

        $pending = Order::whereNotIn('status', ['delivered', 'cancelled'])->count();
        $courier = Order::where('status', 'courier')->count();

        $kpi = [
            [
                'icon'      => '📦',
                'label'     => 'سفارش امروز',
                'value'     => $ordersToday,
                'yesterday' => $ordersYesterday,
                'trend'     => $this->trend($ordersToday, $ordersYesterday),
                'color'     => '#3b82f6',
                'format'    => 'int',
                'route'     => route('orders.index'),
            ],
            [
                'icon'      => '💰',
                'label'     => 'فروش امروز',
                'value'     => $revenueToday,
                'yesterday' => $revenueYesterday,
                'trend'     => $this->trend($revenueToday, $revenueYesterday),
                'color'     => '#10b981',
                'format'    => 'money',
                'route'     => route('orders.index'),
            ],
            [
                'icon'      => '👥',
                'label'     => 'مشتری جدید',
                'value'     => $customersToday,
                'yesterday' => $customersYesterday,
                'trend'     => $this->trend($customersToday, $customersYesterday),
                'color'     => '#a855f7',
                'format'    => 'int',
                'route'     => route('customers.index'),
            ],
            [
                'icon'      => '💎',
                'label'     => 'شناسنامه',
                'value'     => $certsToday,
                'yesterday' => $certsYesterday,
                'trend'     => $this->trend($certsToday, $certsYesterday),
                'color'     => '#c9a84c',
                'format'    => 'int',
                'route'     => route('certificates.index'),
            ],
            [
                'icon'      => '⏳',
                'label'     => 'در جریان',
                'value'     => $pending,
                'yesterday' => null,
                'trend'     => ['dir' => 'flat', 'pct' => 0, 'diff' => 0],
                'color'     => '#f59e0b',
                'format'    => 'int',
                'route'     => route('orders.index') . '?filterStatus=pending',
            ],
            [
                'icon'      => '🚚',
                'label'     => 'تحویل پیک',
                'value'     => $courier,
                'yesterday' => null,
                'trend'     => ['dir' => 'flat', 'pct' => 0, 'diff' => 0],
                'color'     => '#0ea5e9',
                'format'    => 'int',
                'route'     => route('orders.index') . '?filterStatus=courier',
            ],
        ];

        // ─── سری روزانه برای نمودار ───
        $series = [];
        if ($this->range === 'today') {
            for ($h = 0; $h < 24; $h += 3) {
                $from = $now->copy()->startOfDay()->addHours($h);
                $to   = $from->copy()->addHours(3);
                $series[] = [
                    'date'  => $h . 'h',
                    'count' => Order::whereBetween('created_at', [$from, $to])->count(),
                ];
            }
        } else {
            $days = match ($this->range) {
                'week'  => 7,
                'month' => 30,
                'year'  => 12,
                default => 7,
            };

            if ($this->range === 'year') {
                for ($i = $days - 1; $i >= 0; $i--) {
                    $m = $now->copy()->subMonths($i);
                    $series[] = [
                        'date'  => \App\Support\PersianDate::format($m, 'Y/m'),
                        'count' => Order::whereYear('created_at', $m->year)
                                        ->whereMonth('created_at', $m->month)
                                        ->count(),
                    ];
                }
            } else {
                for ($i = $days - 1; $i >= 0; $i--) {
                    $d = $now->copy()->subDays($i);
                    $series[] = [
                        'date'  => \App\Support\PersianDate::format($d, 'm/d'),
                        'count' => Order::whereDate('created_at', $d)->count(),
                    ];
                }
            }
        }

        // ─── کانال‌ها ───
        $byChannel = Order::with('channel')
            ->whereDate('created_at', '>=', $now->copy()->subDays(30))
            ->get()
            ->groupBy('channel_id')
            ->map(fn ($g) => [
                'name'  => $g->first()->channel?->name ?? 'نامشخص',
                'color' => $g->first()->channel?->color ?? '#64748b',
                'count' => $g->count(),
            ])
            ->values()
            ->toArray();

        $recent = Order::with('channel', 'customer', 'items')
            ->latest('id')
            ->limit(6)
            ->get();

        return view('livewire.dashboard-v3', [
            'kpi'       => $kpi,
            'series'    => $series,
            'byChannel' => $byChannel,
            'recent'    => $recent,
        ])->layout('components.layouts.app');
    }
}