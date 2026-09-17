#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""توسعه کامل ShopGun v2.2"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path("/data/data/com.termux/files/home/shopgun-v2.2")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip())

def write(rel, content):
    full = PROJECT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✓ {rel}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# ۱) CSS — Reports + Timeline + Mobile
# ═══════════════════════════════════════════════════════════════
REPORTS_CSS = r'''/* ═══════ Reports & Timeline Styles ═══════ */

/* KPI Cards Horizontal Scroll */
.sg-stats-row {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding: 4px 18px 14px;
    scrollbar-width: none;
    -ms-overflow-style: none;
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
}
.sg-stats-row::-webkit-scrollbar { display: none; }

.sg-stat-card {
    flex: 0 0 auto;
    min-width: 155px;
    max-width: 180px;
    padding: 12px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
    transition: all .2s;
    position: relative;
    overflow: hidden;
}
.sg-stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,.08);
}
.sg-stat-card .top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.sg-stat-card .icon {
    width: 34px;height: 34px;
    border-radius: 10px;
    display: flex;align-items: center;justify-content: center;
    font-size: 17px;
}
.sg-stat-card .trend {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 10.5px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.sg-stat-card .trend.up { background: rgba(39,174,96,.15); color: var(--success); }
.sg-stat-card .trend.down { background: rgba(231,76,60,.15); color: var(--danger); }
.sg-stat-card .trend.flat { background: rgba(127,140,141,.15); color: var(--text-light); }
.sg-stat-card .num {
    font-size: 22px;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    letter-spacing: -.5px;
}
.sg-stat-card .lbl {
    font-size: 10.5px;
    color: var(--text-light);
    font-weight: 600;
    margin-top: 4px;
}

/* Filters Bar */
.sg-filters-bar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding: 0 18px 14px;
    align-items: center;
}
.sg-chip {
    padding: 7px 14px;
    border: 1.5px solid var(--border);
    border-radius: 20px;
    background: var(--bg-card);
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    color: var(--text-light);
    transition: all .15s;
}
.sg-chip:hover { border-color: var(--gold); color: var(--text); }
.sg-chip.active {
    background: linear-gradient(135deg, var(--primary), #0d3b5e);
    color: #fff;
    border-color: var(--primary);
}

/* Mini Charts */
.sg-chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px;
    padding: 0 18px 14px;
}
.sg-chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
}
.sg-chart-card h3 {
    font-size: 12.5px;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border);
}

.sg-bar-chart {
    display: flex;
    align-items: flex-end;
    gap: 6px;
    height: 140px;
    padding-top: 20px;
}
.sg-bar-chart .bar-wrap {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    height: 100%;
    justify-content: flex-end;
}
.sg-bar-chart .bar-val {
    font-size: 10px;
    font-weight: 700;
    color: var(--primary);
    min-height: 14px;
}
.sg-bar-chart .bar {
    width: 100%;
    background: linear-gradient(180deg, #14b8a6, #0891b2);
    border-radius: 6px 6px 0 0;
    transition: all .3s;
    min-height: 3px;
}
.sg-bar-chart .bar-lbl {
    font-size: 9px;
    font-family: monospace;
    color: var(--text-light);
    white-space: nowrap;
}

/* Donut / Pie Alternative - CSS */
.sg-donut {
    position: relative;
    width: 130px;
    height: 130px;
    margin: 0 auto 12px;
    border-radius: 50%;
    background: conic-gradient(
        var(--seg1, #14b8a6) 0deg var(--a1, 90deg),
        var(--seg2, #f59e0b) var(--a1, 90deg) var(--a2, 180deg),
        var(--seg3, #3b82f6) var(--a2, 180deg) var(--a3, 270deg),
        var(--seg4, #a855f7) var(--a3, 270deg) 360deg
    );
    display: flex;
    align-items: center;
    justify-content: center;
}
.sg-donut::after {
    content: '';
    position: absolute;
    inset: 30px;
    background: var(--bg-card);
    border-radius: 50%;
}
.sg-donut .center-text {
    position: relative;
    z-index: 2;
    text-align: center;
}
.sg-donut .center-text .num {
    font-size: 18px;
    font-weight: 800;
    color: var(--primary);
    line-height: 1;
}
.sg-donut .center-text .lbl {
    font-size: 9px;
    color: var(--text-light);
    margin-top: 2px;
}

.sg-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    font-size: 11px;
}
.sg-legend .item {
    display: flex;
    align-items: center;
    gap: 4px;
}
.sg-legend .dot {
    width: 10px;
    height: 10px;
    border-radius: 3px;
}

/* Minimal Table */
.sg-mini-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11.5px;
}
.sg-mini-table th {
    padding: 8px 10px;
    text-align: right;
    font-size: 10.5px;
    font-weight: 700;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: .3px;
    border-bottom: 1px solid var(--border);
}
.sg-mini-table td {
    padding: 10px;
    border-bottom: 1px solid rgba(0,0,0,.04);
}
.sg-mini-table tr:last-child td { border-bottom: none; }
.sg-mini-table tr:hover td { background: rgba(201,168,76,.04); }

/* ═══════ Timeline (horizontal) ═══════ */
.sg-timeline {
    display: flex;
    align-items: flex-start;
    gap: 0;
    padding: 16px 4px 6px;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    position: relative;
}
.sg-timeline::-webkit-scrollbar { display: none; }

.sg-tl-step {
    flex: 1;
    min-width: 85px;
    text-align: center;
    position: relative;
    padding-top: 26px;
}
.sg-tl-step .tl-dot {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--bg);
    border: 2.5px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    color: var(--text-light);
    z-index: 2;
    transition: all .2s;
}
.sg-tl-step.done .tl-dot {
    background: var(--success);
    border-color: var(--success);
    color: #fff;
}
.sg-tl-step.current .tl-dot {
    background: var(--gold);
    border-color: var(--gold);
    color: #fff;
    box-shadow: 0 0 0 5px rgba(201,168,76,.25);
    animation: sgPulse 1.5s infinite;
}
@keyframes sgPulse {
    0%,100% { box-shadow: 0 0 0 5px rgba(201,168,76,.25); }
    50% { box-shadow: 0 0 0 10px rgba(201,168,76,.05); }
}
.sg-tl-step::before {
    content: '';
    position: absolute;
    top: 10px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: var(--border);
    z-index: 1;
}
.sg-tl-step:last-child::before { display: none; }
.sg-tl-step.done::before { background: var(--success); }
.sg-tl-step .tl-lbl {
    font-size: 10px;
    font-weight: 700;
    color: var(--text-light);
    margin-top: 2px;
    line-height: 1.3;
}
.sg-tl-step.done .tl-lbl { color: var(--success); }
.sg-tl-step.current .tl-lbl { color: var(--gold-dark); }
.sg-tl-step .tl-date {
    font-size: 8.5px;
    font-family: monospace;
    color: var(--text-light);
    margin-top: 2px;
}

/* ═══════ Compact Customer Box ═══════ */
.sg-compact-box {
    background: linear-gradient(135deg, rgba(13,148,136,.06), rgba(8,145,178,.03));
    border: 1.5px solid rgba(13,148,136,.2);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.sg-compact-box .header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.sg-compact-box .avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #14b8a6, #0891b2);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 15px;
    flex-shrink: 0;
}
.sg-compact-box .name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
}
.sg-compact-box .phone {
    font-family: monospace;
    font-size: 11.5px;
    color: var(--text-light);
    direction: ltr;
}
.sg-compact-box .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding-top: 8px;
    border-top: 1px dashed rgba(13,148,136,.25);
}
.sg-compact-box .grid .item {
    text-align: center;
}
.sg-compact-box .grid .item .val {
    font-size: 14px;
    font-weight: 800;
    color: var(--primary);
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.sg-compact-box .grid .item .lbl {
    font-size: 9.5px;
    color: var(--text-light);
    margin-top: 3px;
    font-weight: 600;
}

/* ═══════ Info Line (multi-value) ═══════ */
.sg-inline-info {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    padding: 8px 10px;
    background: rgba(0,0,0,.03);
    border-radius: 8px;
    font-size: 11.5px;
    margin-bottom: 8px;
}
.sg-inline-info .item {
    display: flex;
    align-items: center;
    gap: 4px;
}
.sg-inline-info .item strong {
    color: var(--primary);
    font-family: monospace;
}

/* ═══════ Mobile Bar with Scroll ═══════ */
.sg-mobile-bar-inner {
    display: flex !important;
    overflow-x: auto !important;
    gap: 2px;
    scrollbar-width: none;
    justify-content: flex-start !important;
    padding: 0 2px;
}
.sg-mobile-bar-inner::-webkit-scrollbar { display: none; }
.sg-mobile-bar-btn {
    flex: 0 0 auto !important;
    min-width: 62px !important;
    padding: 5px 6px !important;
}

/* ═══════ Modal improvements ═══════ */
@media (max-width: 768px) {
    .sg-stat-card { min-width: 140px; }
    .sg-compact-box .grid { grid-template-columns: repeat(3, 1fr); gap: 4px; }
    .sg-compact-box .grid .item .val { font-size: 12.5px; }
    .sg-compact-box .grid .item .lbl { font-size: 9px; }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۲) REPORTS — Livewire کامل
# ═══════════════════════════════════════════════════════════════
REPORTS_PHP = r'''<?php
namespace App\Livewire\Reports;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Product;
use Illuminate\Support\Facades\DB;
use Livewire\Component;

class Index extends Component
{
    public string $range = 'week';
    public string $reportType = 'orders';

    public function setRange(string $range): void { $this->range = $range; }
    public function setType(string $type): void { $this->reportType = $type; }

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

        // ═══ KPI Cards ═══
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
            [
                'icon' => '📦', 'color' => 'rgba(41,128,185,.15)', 'num' => $curOrders,
                'lbl' => 'سفارشات', 'trend' => $this->calcTrend($curOrders, $prevOrders), 'raw' => true
            ],
            [
                'icon' => '💰', 'color' => 'rgba(39,174,96,.15)', 'num' => $curAmount / 1000000,
                'lbl' => 'فروش (میلیون)', 'trend' => $this->calcTrend($curAmount, $prevAmount), 'dec' => 1
            ],
            [
                'icon' => '👥', 'color' => 'rgba(155,89,182,.15)', 'num' => $curCustomers,
                'lbl' => 'مشتریان', 'trend' => $this->calcTrend($curCustomers, $prevCustomers), 'raw' => true
            ],
            [
                'icon' => '💎', 'color' => 'rgba(201,168,76,.2)', 'num' => $curCerts,
                'lbl' => 'شناسنامه', 'trend' => $this->calcTrend($curCerts, $prevCerts), 'raw' => true
            ],
            [
                'icon' => '📊', 'color' => 'rgba(230,126,34,.15)', 'num' => $curAvg / 1000,
                'lbl' => 'میانگین (هزار)', 'trend' => $this->calcTrend($curAvg, $prevAvg), 'dec' => 0
            ],
            [
                'icon' => '⏳', 'color' => 'rgba(243,156,18,.15)', 'num' => $curPending,
                'lbl' => 'در انتظار', 'trend' => $this->calcTrend($curPending, $prevPending), 'raw' => true
            ],
        ];

        // ═══ Daily Chart ═══
        $daily = [];
        $days = $this->range === 'today' ? 1 : ($this->range === 'week' ? 7 : ($this->range === 'month' ? 30 : 12));
        if ($days === 1) {
            for ($h = 0; $h < 24; $h += 3) {
                $from = now()->startOfDay()->addHours($h);
                $to = $from->copy()->addHours(3);
                $daily[] = [
                    'date' => $h . ':00',
                    'count' => Order::whereBetween('created_at', [$from, $to])->count(),
                ];
            }
        } else {
            for ($i = $days - 1; $i >= 0; $i--) {
                $d = now()->subDays($i);
                $daily[] = [
                    'date' => \App\Support\PersianDate::format($d, 'm/d'),
                    'count' => Order::whereDate('created_at', $d)->count(),
                ];
            }
        }

        // ═══ By Status ═══
        $byStatus = [
            'pending' => Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'pending')->count(),
            'final-check' => Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'final-check')->count(),
            'courier' => Order::whereBetween('created_at', [$cFrom, $cTo])->where('status', 'courier')->count(),
        ];

        // ═══ By Channel ═══
        $byChannel = Order::whereBetween('created_at', [$cFrom, $cTo])
            ->with('channel')->get()
            ->groupBy('channel_id')
            ->map(fn($g) => [
                'name' => $g->first()->channel?->name ?? 'نامشخص',
                'count' => $g->count(),
                'color' => match($g->first()->channel?->slug) {
                    'website' => '#6b0f1a',
                    'instagram' => '#e91e63',
                    'telegram' => '#29b6f6',
                    'basalam' => '#00b894',
                    'phone' => '#66bb6a',
                    default => '#7f8c8d',
                },
            ])->values()->toArray();

        // ═══ Top Products ═══
        $topProducts = OrderItem::whereBetween('created_at', [$cFrom, $cTo])
            ->select('title', DB::raw('COUNT(*) as cnt'), DB::raw('SUM(price * quantity) as total'))
            ->groupBy('title')
            ->orderByDesc('cnt')
            ->limit(5)->get()->toArray();

        // ═══ Top Customers ═══
        $topCustomers = Customer::has('orders')
            ->withCount('orders')
            ->withSum('orders', 'amount')
            ->orderByDesc('orders_sum_amount')
            ->limit(5)->get();

        return view('livewire.reports.index', [
            'stats' => $stats,
            'daily' => $daily,
            'byStatus' => $byStatus,
            'byChannel' => $byChannel,
            'topProducts' => $topProducts,
            'topCustomers' => $topCustomers,
            'reportType' => $this->reportType,
            'rangeLabel' => match($this->range) {
                'today' => 'امروز', 'week' => '۷ روز اخیر',
                'month' => '۳۰ روز اخیر', 'year' => 'سال جاری', default => '',
            },
        ])->layout('components.layouts.app');
    }
}
'''

REPORTS_BLADE = r'''<div>
    {{-- Header --}}
    <div style="padding:0 18px 14px">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
            <h1 style="font-size:20px;font-weight:700">📊 گزارش‌ها</h1>
            <a href="{{ route('reports.export.excel', ['range' => $range]) }}" class="btn btn-outline btn-sm">📥 CSV</a>
        </div>
    </div>

    {{-- Range Filters --}}
    <div class="sg-filters-bar">
        @foreach([
            'today' => 'امروز',
            'week' => '۷ روز',
            'month' => '۳۰ روز',
            'year' => 'سال',
        ] as $key => $label)
            <button wire:click="setRange('{{ $key }}')" class="sg-chip {{ $range === $key ? 'active' : '' }}">{{ $label }}</button>
        @endforeach
    </div>

    {{-- KPI Stats Row (Horizontal Scroll) --}}
    <div class="sg-stats-row">
        @foreach($stats as $s)
            <div class="sg-stat-card">
                <div class="top-row">
                    <div class="icon" style="background:{{ $s['color'] }}">{{ $s['icon'] }}</div>
                    @if(($s['trend']['dir'] ?? 'flat') === 'up')
                        <span class="trend up">▲ {{ \App\Support\PersianNumber::toFa($s['trend']['pct']) }}%</span>
                    @elseif(($s['trend']['dir'] ?? 'flat') === 'down')
                        <span class="trend down">▼ {{ \App\Support\PersianNumber::toFa($s['trend']['pct']) }}%</span>
                    @else
                        <span class="trend flat">—</span>
                    @endif
                </div>
                <div class="num">
                    @if(!empty($s['raw']))
                        {{ \App\Support\PersianNumber::toFa(number_format($s['num'])) }}
                    @else
                        {{ \App\Support\PersianNumber::toFa(number_format($s['num'], $s['dec'] ?? 1)) }}
                    @endif
                </div>
                <div class="lbl">{{ $s['lbl'] }}</div>
            </div>
        @endforeach
    </div>

    {{-- Charts Grid --}}
    <div class="sg-chart-grid">
        {{-- Daily Chart --}}
        <div class="sg-chart-card">
            <h3>📈 روند {{ $rangeLabel }}</h3>
            @php $max = collect($daily)->max('count') ?: 1; @endphp
            <div class="sg-bar-chart">
                @foreach($daily as $d)
                    <div class="bar-wrap">
                        <div class="bar-val">{{ $d['count'] > 0 ? \App\Support\PersianNumber::toFa($d['count']) : '' }}</div>
                        <div class="bar" style="height:{{ max(4, $d['count'] / $max * 100) }}%"></div>
                        <div class="bar-lbl">{{ $d['date'] }}</div>
                    </div>
                @endforeach
            </div>
        </div>

        {{-- By Status --}}
        <div class="sg-chart-card">
            <h3>🚦 وضعیت سفارشات</h3>
            @php
                $total = array_sum($byStatus) ?: 1;
                $a1 = ($byStatus['pending'] / $total) * 360;
                $a2 = $a1 + (($byStatus['final-check'] / $total) * 360);
                $a3 = $a2 + (($byStatus['courier'] / $total) * 360);
            @endphp
            <div class="sg-donut" style="--a1:{{ $a1 }}deg;--a2:{{ $a2 }}deg;--a3:{{ $a3 }}deg">
                <div class="center-text">
                    <div class="num">{{ \App\Support\PersianNumber::toFa(array_sum($byStatus)) }}</div>
                    <div class="lbl">کل</div>
                </div>
            </div>
            <div class="sg-legend">
                <div class="item"><span class="dot" style="background:#f59e0b"></span> ثبت ({{ \App\Support\PersianNumber::toFa($byStatus['pending']) }})</div>
                <div class="item"><span class="dot" style="background:#3b82f6"></span> چک ({{ \App\Support\PersianNumber::toFa($byStatus['final-check']) }})</div>
                <div class="item"><span class="dot" style="background:#14b8a6"></span> مامور ({{ \App\Support\PersianNumber::toFa($byStatus['courier']) }})</div>
            </div>
        </div>

        {{-- By Channel --}}
        @if(count($byChannel))
            <div class="sg-chart-card">
                <h3>🌐 کانال‌های فروش</h3>
                @php $chTotal = collect($byChannel)->sum('count') ?: 1; @endphp
                @foreach($byChannel as $ch)
                    <div style="margin-bottom:8px">
                        <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:3px">
                            <span style="font-weight:700">{{ $ch['name'] }}</span>
                            <span style="color:{{ $ch['color'] }};font-weight:700">{{ \App\Support\PersianNumber::toFa($ch['count']) }} ({{ round($ch['count'] / $chTotal * 100) }}%)</span>
                        </div>
                        <div style="height:6px;background:rgba(0,0,0,.05);border-radius:3px;overflow:hidden">
                            <div style="height:100%;width:{{ $ch['count'] / $chTotal * 100 }}%;background:{{ $ch['color'] }};border-radius:3px"></div>
                        </div>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- Tables Grid --}}
    <div class="sg-chart-grid">
        {{-- Top Products --}}
        <div class="sg-chart-card">
            <h3>🏆 پرفروش‌ترین محصولات</h3>
            @if(count($topProducts))
                <table class="sg-mini-table">
                    <thead><tr><th>محصول</th><th style="text-align:left">تعداد</th><th style="text-align:left">مبلغ</th></tr></thead>
                    <tbody>
                        @foreach($topProducts as $p)
                            <tr>
                                <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $p['title'] }}</td>
                                <td style="text-align:left;font-weight:700;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($p['cnt']) }}</td>
                                <td style="text-align:left;font-family:monospace;font-size:11px">{{ number_format($p['total']) }}</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            @else
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">داده‌ای نیست</p>
            @endif
        </div>

        {{-- Top Customers --}}
        <div class="sg-chart-card">
            <h3>⭐ بهترین مشتریان</h3>
            @if($topCustomers->count())
                <table class="sg-mini-table">
                    <thead><tr><th>مشتری</th><th style="text-align:left">سفارش</th><th style="text-align:left">مجموع</th></tr></thead>
                    <tbody>
                        @foreach($topCustomers as $c)
                            <tr>
                                <td>
                                    <div style="font-weight:700">{{ $c->name }}</div>
                                    <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $c->phone }}</div>
                                </td>
                                <td style="text-align:left;font-weight:700;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
                                <td style="text-align:left;font-family:monospace;font-size:11px">{{ number_format($c->orders_sum_amount ?? 0) }}</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            @else
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">داده‌ای نیست</p>
            @endif
        </div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) ORDER VIEW MODAL — Minimal + Timeline
# ═══════════════════════════════════════════════════════════════
ORDER_VIEW_PHP = r'''<?php
namespace App\Livewire\Orders;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?Order $order = null;
    public array $customerStats = [];
    public array $timeline = [];

    #[On('open-order-view')]
    public function open(int $orderId): void
    {
        $this->order = Order::with(['customer', 'items', 'channel'])->find($orderId);
        if (!$this->order) return;

        // آمار مشتری
        if ($this->order->customer_id) {
            $customer = Customer::find($this->order->customer_id);
            if ($customer) {
                $orders = $customer->orders()->orderBy('created_at')->get();
                $this->customerStats = [
                    'total' => $orders->count(),
                    'sum' => (float) $orders->sum('amount'),
                    'first' => $orders->first()?->created_at,
                    'last' => $orders->last()?->created_at,
                ];
            }
        }

        // Timeline
        $stages = [
            ['id' => 'pending', 'label' => 'ثبت سفارش', 'icon' => '📝'],
            ['id' => 'final-check', 'label' => 'چک نهایی', 'icon' => '🔍'],
            ['id' => 'courier', 'label' => 'تحویل مامور', 'icon' => '🚚'],
        ];
        $current = array_search($this->order->status, array_column($stages, 'id'));
        if ($current === false) $current = 0;

        $this->timeline = [];
        foreach ($stages as $i => $s) {
            $this->timeline[] = [
                'label' => $s['label'],
                'icon' => $s['icon'],
                'state' => $i < $current ? 'done' : ($i === $current ? 'current' : ''),
            ];
        }

        $this->show = true;
    }

    public function close(): void { $this->show = false; $this->order = null; }

    public function cycleStatus(): void
    {
        if (!$this->order) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($this->order->status, $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $this->order->update(['status' => $next]);
        $this->order->refresh();
        $this->open($this->order->id);
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'وضعیت تغییر کرد');
    }

    public function editOrder(): void
    {
        $id = $this->order->id;
        $this->close();
        $this->dispatch('open-order-form', orderId: $id);
    }

    public function deleteOrder(): void
    {
        $this->order?->delete();
        $this->close();
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() { return view('livewire.orders.view-modal'); }
}
'''

ORDER_VIEW_BLADE = r'''<div>
@if($show && $order)
<div class="sg-modal-overlay active" wire:key="ov-{{ $order->id }}" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:620px">
        <div class="sg-modal-header">
            <h2>📋 سفارش #{{ $order->order_number }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body" style="padding:14px">

            {{-- ═══ Timeline افقی ═══ --}}
            <div class="sg-timeline">
                @foreach($timeline as $i => $step)
                    <div class="sg-tl-step {{ $step['state'] }}">
                        <div class="tl-dot">{{ $step['state'] === 'done' ? '✓' : $step['icon'] }}</div>
                        <div class="tl-lbl">{{ $step['label'] }}</div>
                    </div>
                @endforeach
            </div>

            {{-- ═══ باکس مشتری مینیمال ═══ --}}
            @if($order->customer)
                <div class="sg-compact-box">
                    <div class="header">
                        <div class="avatar">{{ mb_substr($order->customer_name ?? $order->customer->name ?? '?', 0, 1) }}</div>
                        <div style="flex:1;min-width:0">
                            <div class="name">{{ $order->customer_name ?? $order->customer->name }}</div>
                            <div class="phone">{{ $order->phone }}</div>
                        </div>
                        @if(!empty($customerStats))
                            <div style="text-align:left">
                                <div style="background:var(--gold);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">
                                    {{ \App\Support\PersianNumber::toFa($customerStats['total']) }} سفارش
                                </div>
                            </div>
                        @endif
                    </div>

                    @if(!empty($customerStats))
                        <div class="grid">
                            <div class="item">
                                <div class="val">{{ number_format($customerStats['sum'] / 1000000, 1) }}M</div>
                                <div class="lbl">مجموع خرید</div>
                            </div>
                            <div class="item">
                                <div class="val" style="font-size:11px;font-family:monospace">{{ \App\Support\PersianDate::format($customerStats['first'], 'Y/m/d') }}</div>
                                <div class="lbl">اولین سفارش</div>
                            </div>
                            <div class="item">
                                <div class="val" style="font-size:11px;font-family:monospace">{{ \App\Support\PersianDate::format($customerStats['last'], 'Y/m/d') }}</div>
                                <div class="lbl">آخرین سفارش</div>
                            </div>
                        </div>
                    @endif
                </div>
            @endif

            {{-- ═══ اطلاعات در یک خط ═══ --}}
            <div class="sg-inline-info">
                <div class="item">📅 <strong>{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</strong></div>
                @if($order->channel)
                    <div class="item">🌐 <span class="sg-channel-cell {{ $order->channel->slug ?? 'default' }}" style="font-size:10px">{{ $order->channel->name }}</span></div>
                @endif
                <div class="item">💰 <strong>{{ \App\Support\PersianNumber::toFa(number_format($order->insurance ?? 0)) }}</strong></div>
                @if($order->postal_code)
                    <div class="item">📮 <strong style="font-family:monospace">{{ $order->postal_code }}</strong></div>
                @endif
            </div>

            {{-- ═══ محصولات ═══ --}}
            @if($order->items->count())
                <div style="margin-bottom:10px">
                    <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:6px">🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})</div>
                    <div style="border:1px solid var(--border);border-radius:10px;overflow:hidden">
                        @foreach($order->items as $item)
                            <div style="padding:8px 10px;border-bottom:1px solid var(--border);display:flex;gap:8px;align-items:center;font-size:12px">
                                <div style="flex:1;min-width:0">
                                    <div style="font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $item->title }}</div>
                                    @if($item->sku) <div style="font-family:monospace;font-size:9.5px;opacity:.5" dir="ltr">{{ $item->sku }}</div> @endif
                                </div>
                                <div style="opacity:.6;font-size:11px">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                                <div style="font-weight:700;font-family:monospace;font-size:11.5px">{{ number_format($item->price) }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- ═══ آدرس ═══ --}}
            @if($order->address)
                <div style="background:rgba(0,0,0,.03);padding:10px;border-radius:10px;margin-bottom:10px;font-size:11.5px;line-height:1.6">
                    📍 {{ $order->address }}
                </div>
            @endif

            {{-- ═══ Totals ═══ --}}
            <div style="background:linear-gradient(135deg,rgba(13,148,136,.08),rgba(8,145,178,.03));padding:10px 14px;border-radius:10px">
                <div class="sg-inline-info" style="background:transparent;padding:0;margin:0;justify-content:space-between">
                    @if(($order->shipping ?? 0) > 0)
                        <div class="item">📦 ارسال: <strong>{{ number_format($order->shipping) }}</strong></div>
                    @endif
                    @if(($order->discount ?? 0) > 0)
                        <div class="item" style="color:var(--warn)">🏷️ تخفیف: <strong>-{{ number_format($order->discount) }}</strong></div>
                    @endif
                    <div class="item" style="font-size:14px">💵 <strong style="color:var(--primary);font-size:15px">{{ number_format($order->amount ?? 0) }} ت</strong></div>
                </div>
            </div>

            @if($order->notes)
                <div style="background:rgba(201,168,76,.08);padding:8px 12px;border-radius:10px;margin-top:10px;font-size:11.5px">
                    📝 {{ $order->notes }}
                </div>
            @endif
        </div>

        <div class="sg-modal-footer" style="padding:10px 14px">
            <button wire:click="deleteOrder" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">🗑️</button>
            <div style="display:flex;gap:6px">
                <button wire:click="cycleStatus" class="btn btn-outline btn-sm">🔄 وضعیت بعدی</button>
                <button wire:click="editOrder" class="btn btn-primary btn-sm">✏️ ویرایش</button>
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۴) LAYOUT — Mobile Bar با همه بخش‌ها
# ═══════════════════════════════════════════════════════════════
def patch_layout():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists():
        print("  ⚠️ Layout پیدا نشد")
        return

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    # جایگزینی mobile bar
    new_bar = '''<nav class="sg-mobile-bar">
    <div class="sg-mobile-bar-inner">
        @php
            $items = [
                ['dashboard','🏠','خانه'],
                ['orders.index','📦','سفارش'],
                ['orders.create','➕','جدید'],
                ['customers.index','👥','مشتری'],
                ['certificates.index','💎','کارت'],
                ['certificates.create','✨','کارت جدید'],
                ['reports.index','📊','گزارش'],
                ['settings.index','⚙️','تنظیم'],
                ['activity-log','📜','لاگ'],
            ];
        @endphp
        @foreach($items as $it)
            @php
                $isActive = request()->routeIs($it[0]) || request()->routeIs(explode('.', $it[0])[0] . '.*');
                $cls = 'sg-mobile-bar-btn';
                if ($it[0] === 'orders.create') $cls .= ' add';
                elseif ($isActive) $cls .= ' active';
            @endphp
            <a href="{{ route($it[0]) }}" wire:navigate class="{{ $cls }}">
                <span class="ico">{{ $it[1] }}</span>
                <span>{{ $it[2] }}</span>
            </a>
        @endforeach
    </div>
</nav>'''

    content = re.sub(
        r'<nav class="sg-mobile-bar">.*?</nav>',
        new_bar,
        content,
        count=1,
        flags=re.DOTALL
    )

    # اضافه کردن CSS reports
    if 'reports.css' not in content and '</head>' in content:
        content = content.replace('</head>', '    <link rel="stylesheet" href="{{ asset(\'css/reports.css\') }}?v=1">\n</head>', 1)

    with open(layout, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("  ✓ Layout: Mobile Bar + Reports CSS")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  توسعه کامل v2.2                                               ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    for rel in [
        "app/Livewire/Reports/Index.php",
        "resources/views/livewire/reports/index.blade.php",
        "app/Livewire/Orders/ViewModal.php",
        "resources/views/livewire/orders/view-modal.blade.php",
        "resources/views/components/layouts/app.blade.php",
    ]: backup(rel)

    print("\n📄 نوشتن فایل‌ها...")
    write("public/css/reports.css", REPORTS_CSS)
    write("app/Livewire/Reports/Index.php", REPORTS_PHP)
    write("resources/views/livewire/reports/index.blade.php", REPORTS_BLADE)
    write("app/Livewire/Orders/ViewModal.php", ORDER_VIEW_PHP)
    write("resources/views/livewire/orders/view-modal.blade.php", ORDER_VIEW_BLADE)

    print("\n🔧 Patch Layout...")
    patch_layout()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print("""
📋 اجرا کن:

  cd ~/shopgun-v2.2
  php artisan optimize:clear
  php artisan view:clear
  # سرور رو ببند و دوباره
  php artisan serve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی اضافه شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ گزارشات کامل:
     • 6 کارت KPI در یک خط با اسکرول افقی
     • مقایسه با دوره قبل (▲▼ درصد رشد/کاهش)
     • نمودار میله‌ای روند
     • نمودار دایره‌ای وضعیت‌ها
     • نمودار کانال‌ها
     • جدول پرفروش‌ترین‌ها
     • جدول بهترین مشتریان

  ✅ Mobile Bar کامل:
     • 9 دکمه با اسکرول افقی
     • خانه، سفارش، ➕، مشتری، کارت، کارت جدید، گزارش، تنظیم، لاگ

  ✅ سفارش‌ها View:
     • تایم‌لاین افقی گرافیکی
     • باکس مشتری مینیمال با آواتار
     • 3 کارت آماری (سفارش، اولین، آخرین)
     • اطلاعات در یک خط (تاریخ، کانال، بیمه، کدپستی)
     • محصولات فشرده
     • Totals در یک خط

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 برای اتصال به سایت:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  مشکل: "API is not configured"
  راه‌حل: تنظیمات → کامرس → وارد کن URL + Key + Secret → ذخیره → تست

  اگه باز خطا داد، در Console مرورگر این رو بزن:
    fetch('/api/settings').then(r => r.json()).then(console.log)
""")

if __name__ == "__main__":
    main()
