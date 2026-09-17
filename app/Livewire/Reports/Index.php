<?php
namespace App\Livewire\Reports;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use Illuminate\Support\Facades\DB;
use Livewire\Component;

class Index extends Component
{
    public string $range = 'week';

    public function setRange(string $range): void { $this->range = $range; }

    protected function getPeriods(): array
    {
        $now = now();
        return match($this->range) {
            'today'  => [
                'current' => [$now->copy()->startOfDay(), $now->copy()->endOfDay()],
                'prev'    => [$now->copy()->subDay()->startOfDay(), $now->copy()->subDay()->endOfDay()],
            ],
            'week'   => [
                'current' => [$now->copy()->subDays(6)->startOfDay(), $now->copy()->endOfDay()],
                'prev'    => [$now->copy()->subDays(13)->startOfDay(), $now->copy()->subDays(7)->endOfDay()],
            ],
            'month'  => [
                'current' => [$now->copy()->subDays(29)->startOfDay(), $now->copy()->endOfDay()],
                'prev'    => [$now->copy()->subDays(59)->startOfDay(), $now->copy()->subDays(30)->endOfDay()],
            ],
            'year'   => [
                'current' => [$now->copy()->startOfYear(), $now->copy()->endOfDay()],
                'prev'    => [$now->copy()->subYear()->startOfYear(), $now->copy()->subYear()->endOfYear()],
            ],
            default  => [
                'current' => [$now->copy()->subDays(6)->startOfDay(), $now->copy()->endOfDay()],
                'prev'    => [$now->copy()->subDays(13)->startOfDay(), $now->copy()->subDays(7)->endOfDay()],
            ],
        };
    }

    protected function calcTrend($cur, $prev): array
    {
        if ($prev == 0) {
            if ($cur == 0) return ['dir' => 'flat', 'pct' => 0];
            return ['dir' => 'up', 'pct' => 100];
        }
        $pct = (($cur - $prev) / $prev) * 100;
        if ($pct > 1) return ['dir' => 'up', 'pct' => round($pct, 1)];
        if ($pct < -1) return ['dir' => 'down', 'pct' => round(abs($pct), 1)];
        return ['dir' => 'flat', 'pct' => 0];
    }

    public function render()
    {
        $periods = $this->getPeriods();
        [$cFrom, $cTo] = $periods['current'];
        [$pFrom, $pTo] = $periods['prev'];

        $curOrders = Order::whereBetween('created_at', [$cFrom, $cTo])->count();
        $prevOrders = Order::whereBetween('created_at', [$pFrom, $pTo])->count();
        $curAmount = (float) Order::whereBetween('created_at', [$cFrom, $cTo])->sum('amount');
        $prevAmount = (float) Order::whereBetween('created_at', [$pFrom, $pTo])->sum('amount');
        $curCustomers = Customer::whereBetween('created_at', [$cFrom, $cTo])->count();
        $prevCustomers = Customer::whereBetween('created_at', [$pFrom, $pTo])->count();
        $curCerts = Certificate::whereBetween('created_at', [$cFrom, $cTo])->count();
        $prevCerts = Certificate::whereBetween('created_at', [$pFrom, $pTo])->count();
        $curAvg = $curOrders > 0 ? $curAmount / $curOrders : 0;
        $prevAvg = $prevOrders > 0 ? $prevAmount / $prevOrders : 0;
        $curPending = Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'pending')->count();
        $prevPending = Order::whereBetween('created_at', [$pFrom, $pTo])->where('status', 'pending')->count();

        $stats = [
            ['icon'=>'📦','color'=>'rgba(41,128,185,.15)','num'=>$curOrders,'lbl'=>'سفارشات','trend'=>$this->calcTrend($curOrders, $prevOrders),'raw'=>true],
            ['icon'=>'💰','color'=>'rgba(39,174,96,.15)','num'=>$curAmount / 1000000,'lbl'=>'فروش (م)','trend'=>$this->calcTrend($curAmount, $prevAmount),'dec'=>1],
            ['icon'=>'👥','color'=>'rgba(155,89,182,.15)','num'=>$curCustomers,'lbl'=>'مشتریان','trend'=>$this->calcTrend($curCustomers, $prevCustomers),'raw'=>true],
            ['icon'=>'💎','color'=>'rgba(201,168,76,.2)','num'=>$curCerts,'lbl'=>'شناسنامه','trend'=>$this->calcTrend($curCerts, $prevCerts),'raw'=>true],
            ['icon'=>'📊','color'=>'rgba(230,126,34,.15)','num'=>$curAvg / 1000,'lbl'=>'میانگین (ه)','trend'=>$this->calcTrend($curAvg, $prevAvg),'dec'=>0],
            ['icon'=>'⏳','color'=>'rgba(243,156,18,.15)','num'=>$curPending,'lbl'=>'در انتظار','trend'=>$this->calcTrend($curPending, $prevPending),'raw'=>true],
        ];

        // ═══ داده‌های نمودارها ═══
        $daily = [];
        $days = $this->range === 'today' ? 8 : ($this->range === 'week' ? 7 : ($this->range === 'month' ? 30 : 12));

        if ($this->range === 'today') {
            for ($h = 0; $h < 24; $h += 3) {
                $from = now()->startOfDay()->addHours($h);
                $to = $from->copy()->addHours(3);
                $daily[] = [
                    'date' => $h . 'h',
                    'orders' => Order::whereBetween('created_at', [$from, $to])->count(),
                    'certs' => Certificate::whereBetween('created_at', [$from, $to])->count(),
                ];
            }
        } elseif ($this->range === 'year') {
            for ($m = 1; $m <= 12; $m++) {
                $from = now()->startOfYear()->addMonths($m - 1);
                $to = $from->copy()->endOfMonth();
                $daily[] = [
                    'date' => \App\Support\PersianDate::format($from, 'n'),
                    'orders' => Order::whereBetween('created_at', [$from, $to])->count(),
                    'certs' => Certificate::whereBetween('created_at', [$from, $to])->count(),
                ];
            }
        } else {
            for ($i = $days - 1; $i >= 0; $i--) {
                $d = now()->subDays($i);
                $daily[] = [
                    'date' => \App\Support\PersianDate::format($d, 'm/d'),
                    'orders' => Order::whereDate('created_at', $d)->count(),
                    'certs' => Certificate::whereDate('created_at', $d)->count(),
                ];
            }
        }

        $byStatus = [
            'pending' => Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'pending')->count(),
            'final-check' => Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'final-check')->count(),
            'courier' => Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'courier')->count(),
        ];

        $byChannel = Order::whereBetween('created_at', [$cFrom, $cTo])
            ->with('channel')->get()
            ->groupBy('channel_id')
            ->map(fn($g) => [
                'name' => $g->first()->channel?->name ?? 'نامشخص',
                'count' => $g->count(),
                'color' => match($g->first()->channel?->slug) {
                    'website' => '#6b0f1a', 'instagram' => '#e91e63',
                    'telegram' => '#29b6f6', 'basalam' => '#00b894',
                    'phone' => '#66bb6a', default => '#7f8c8d',
                },
            ])->values()->toArray();

        $topProducts = OrderItem::whereBetween('created_at', [$cFrom, $cTo])
            ->select('title', DB::raw('COUNT(*) as cnt'), DB::raw('SUM(price * quantity) as total'))
            ->groupBy('title')->orderByDesc('cnt')->limit(5)->get()->toArray();

        $topCustomers = Customer::has('orders')
            ->withCount('orders')->withSum('orders', 'amount')
            ->orderByDesc('orders_sum_amount')->limit(5)->get();

        return view('livewire.reports.index', [
            'stats' => $stats,
            'daily' => $daily,
            'byStatus' => $byStatus,
            'byChannel' => $byChannel,
            'topProducts' => $topProducts,
            'topCustomers' => $topCustomers,
            'rangeLabel' => match($this->range) {
                'today' => 'امروز', 'week' => '۷ روز اخیر',
                'month' => '۳۰ روز اخیر', 'year' => 'سال جاری', default => '',
            },
        ])->layout('components.layouts.app');
    }
}
