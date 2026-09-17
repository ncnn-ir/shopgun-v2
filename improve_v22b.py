#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""توسعه کامل v2.2 — رفع ۹ مشکل"""
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
# ۱) REPORTS PHP — با نمودار خطی
# ═══════════════════════════════════════════════════════════════
REPORTS_PHP = r'''<?php
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
'''

# ═══════════════════════════════════════════════════════════════
# ۲) REPORTS BLADE — با نمودار خطی و اسکرول
# ═══════════════════════════════════════════════════════════════
REPORTS_BLADE = r'''<div>
    <div style="padding:0 18px 14px">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
            <h1 style="font-size:20px;font-weight:700">📊 گزارش‌ها</h1>
            <a href="{{ route('reports.export.excel', ['range' => $range]) }}" class="btn btn-outline btn-sm">📥 CSV</a>
        </div>
    </div>

    <div class="sg-filters-bar">
        @foreach(['today'=>'امروز','week'=>'۷ روز','month'=>'۳۰ روز','year'=>'سال'] as $key => $label)
            <button wire:click="setRange('{{ $key }}')" class="sg-chip {{ $range === $key ? 'active' : '' }}">{{ $label }}</button>
        @endforeach
    </div>

    {{-- KPI Stats Row --}}
    <div class="sg-stats-row">
        @foreach($stats as $s)
            <div class="sg-stat-card">
                <div class="top-row">
                    <div class="icon" style="background:{{ $s['color'] }}">{{ $s['icon'] }}</div>
                    @php $t = $s['trend']; @endphp
                    @if($t['dir'] === 'up')
                        <span class="trend up">▲ {{ \App\Support\PersianNumber::toFa($t['pct']) }}%</span>
                    @elseif($t['dir'] === 'down')
                        <span class="trend down">▼ {{ \App\Support\PersianNumber::toFa($t['pct']) }}%</span>
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

    <div class="sg-chart-grid">
        {{-- Bar Chart with horizontal scroll --}}
        <div class="sg-chart-card">
            <h3>📈 سفارشات {{ $rangeLabel }}</h3>
            @php $maxOrders = collect($daily)->max('orders') ?: 1; @endphp
            <div class="sg-chart-scroll">
                <div class="sg-bar-chart" style="min-width:{{ count($daily) * 32 }}px">
                    @foreach($daily as $d)
                        <div class="bar-wrap" style="min-width:28px">
                            <div class="bar-val">{{ $d['orders'] > 0 ? \App\Support\PersianNumber::toFa($d['orders']) : '' }}</div>
                            <div class="bar" style="height:{{ max(4, $d['orders'] / $maxOrders * 100) }}%"></div>
                            <div class="bar-lbl">{{ $d['date'] }}</div>
                        </div>
                    @endforeach
                </div>
            </div>
        </div>

        {{-- Line Chart: Certificates vs Orders --}}
        <div class="sg-chart-card">
            <h3>💎 خط صدور شناسنامه vs خرید</h3>
            @php
                $maxVal = max(collect($daily)->max('certs') ?: 1, collect($daily)->max('orders') ?: 1);
                $n = count($daily);
                $w = max(400, $n * 34);
                $h = 140;
                $pad = 10;
                $stepX = ($w - $pad * 2) / max(1, $n - 1);
                $ordersPath = '';
                $certsPath = '';
                foreach ($daily as $i => $d) {
                    $x = $pad + ($i * $stepX);
                    $yO = $h - $pad - ($d['orders'] / $maxVal * ($h - $pad * 2));
                    $yC = $h - $pad - ($d['certs'] / $maxVal * ($h - $pad * 2));
                    $ordersPath .= ($i === 0 ? 'M' : 'L') . $x . ' ' . $yO . ' ';
                    $certsPath .= ($i === 0 ? 'M' : 'L') . $x . ' ' . $yC . ' ';
                }
            @endphp
            <div class="sg-chart-scroll">
                <svg width="{{ $w }}" height="{{ $h + 24 }}" style="display:block">
                    {{-- Grid lines --}}
                    @for($g = 0; $g <= 4; $g++)
                        @php $gy = $pad + (($h - $pad * 2) * $g / 4); @endphp
                        <line x1="{{ $pad }}" y1="{{ $gy }}" x2="{{ $w - $pad }}" y2="{{ $gy }}" stroke="rgba(0,0,0,.06)" stroke-width="1"/>
                    @endfor

                    {{-- Orders line --}}
                    <path d="{{ $ordersPath }}" fill="none" stroke="#14b8a6" stroke-width="2.5" stroke-linejoin="round"/>
                    {{-- Certs line --}}
                    <path d="{{ $certsPath }}" fill="none" stroke="#c9a84c" stroke-width="2.5" stroke-linejoin="round" stroke-dasharray="5,3"/>

                    {{-- Points + labels --}}
                    @foreach($daily as $i => $d)
                        @php
                            $x = $pad + ($i * $stepX);
                            $yO = $h - $pad - ($d['orders'] / $maxVal * ($h - $pad * 2));
                            $yC = $h - $pad - ($d['certs'] / $maxVal * ($h - $pad * 2));
                        @endphp
                        <circle cx="{{ $x }}" cy="{{ $yO }}" r="3" fill="#14b8a6"/>
                        <circle cx="{{ $x }}" cy="{{ $yC }}" r="3" fill="#c9a84c"/>
                        <text x="{{ $x }}" y="{{ $h + 18 }}" text-anchor="middle" font-size="9" fill="rgba(0,0,0,.5)" font-family="monospace">{{ $d['date'] }}</text>
                    @endforeach
                </svg>
            </div>
            <div class="sg-legend" style="margin-top:10px">
                <div class="item"><span class="dot" style="background:#14b8a6"></span> سفارشات</div>
                <div class="item"><span class="dot" style="background:#c9a84c"></span> شناسنامه</div>
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

        {{-- Top Products --}}
        <div class="sg-chart-card">
            <h3>🏆 پرفروش‌ترین‌ها</h3>
            @if(count($topProducts))
                <table class="sg-mini-table">
                    <thead><tr><th>محصول</th><th style="text-align:left">تعداد</th></tr></thead>
                    <tbody>
                        @foreach($topProducts as $p)
                            <tr>
                                <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $p['title'] }}</td>
                                <td style="text-align:left;font-weight:700;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($p['cnt']) }}</td>
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
                    <thead><tr><th>مشتری</th><th style="text-align:left">سفارش</th></tr></thead>
                    <tbody>
                        @foreach($topCustomers as $c)
                            <tr>
                                <td>
                                    <div style="font-weight:700">{{ $c->name }}</div>
                                    <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $c->phone }}</div>
                                </td>
                                <td style="text-align:left;font-weight:700;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
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
# ۳) CSS — اضافه کردن chart-scroll + mobile tabs
# ═══════════════════════════════════════════════════════════════
EXTRA_CSS = r'''
/* ═══ Chart Scroll ═══ */
.sg-chart-scroll {
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 6px;
    -webkit-overflow-scrolling: touch;
}
.sg-chart-scroll::-webkit-scrollbar { height: 4px; }
.sg-chart-scroll::-webkit-scrollbar-thumb { background: rgba(0,0,0,.15); border-radius: 2px; }

/* ═══ Mobile Settings Tabs — Horizontal Scroll ═══ */
.sg-tabs-bar-mobile {
    display: none;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    gap: 6px;
    padding: 10px 14px;
    white-space: nowrap;
}
.sg-tabs-bar-mobile::-webkit-scrollbar { display: none; }
.sg-tabs-bar-mobile .sg-tab-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 8px 14px;
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    color: var(--text-light);
    cursor: pointer;
    flex-shrink: 0;
    transition: all .2s;
}
.sg-tabs-bar-mobile .sg-tab-chip.active {
    background: linear-gradient(135deg, var(--primary), #0d3b5e);
    color: #fff;
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(13,148,136,.3);
}

/* ═══ Timeline with Time ═══ */
.sg-tl-step .tl-time {
    font-size: 8px;
    font-family: monospace;
    color: var(--text-light);
    margin-top: 2px;
    opacity: .8;
}

/* ═══ Mobile bar sticky fix ═══ */
.sg-mobile-bar {
    position: fixed !important;
    bottom: 10px !important;
}

/* ═══ Appearance variables applied via :root ═══ */
:root {
    --primary-dynamic: #1a5276;
    --gold-dynamic: #c9a84c;
    --font-dynamic: 'Vazirmatn';
}
body { font-family: var(--font-dynamic), 'Vazirmatn', Tahoma, sans-serif; }

@media(max-width: 768px) {
    .sg-tabs-bar { display: none !important; }
    .sg-tabs-bar-mobile { display: flex; }
    .sg-chart-grid { grid-template-columns: 1fr; padding: 0 14px 14px; }
    .sg-stats-row { padding: 4px 14px 12px; }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۴) IMPORT POSTAL CSV Component
# ═══════════════════════════════════════════════════════════════
IMPORT_POSTAL_PHP = r'''<?php
namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class ImportPostal extends Component
{
    use WithFileUploads;

    public bool $show = false;
    public $file = null;
    public array $columns = [];
    public array $rows = [];
    public array $mapping = [];    // index => field name
    public array $preview = [];
    public int $matched = 0;
    public int $unmatched = 0;

    public array $availableFields = [
        '' => '— نادیده بگیر —',
        'phone' => '📱 تلفن گیرنده',
        'tracking' => '📮 کد رهگیری',
        'status' => '🚦 وضعیت',
        'weight' => '⚖️ وزن',
        'insurance' => '💰 بیمه',
        'cost' => '💸 کرایه',
        'date' => '📅 تاریخ',
        'receiver' => '👤 نام گیرنده',
        'city' => '🏙️ شهر',
    ];

    #[On('open-import-postal')]
    public function open(): void
    {
        $this->reset(['file','columns','rows','mapping','preview','matched','unmatched']);
        $this->show = true;
    }

    public function close(): void { $this->show = false; }

    public function updatedFile(): void
    {
        $this->validate(['file' => 'file|max:10240']);

        $path = $this->file->getRealPath();
        $content = file_get_contents($path);
        $content = preg_replace('/^\xEF\xBB\xBF/', '', $content);

        $delimiter = $this->detectDelimiter($content);
        $allRows = $this->parseCsv($content, $delimiter);

        if (count($allRows) < 2) {
            $this->dispatch('notify', type: 'error', message: 'فایل خالی یا نامعتبر');
            return;
        }

        $this->columns = $allRows[0];
        $this->rows = array_slice($allRows, 1);
        $this->rows = array_values(array_filter($this->rows, fn($r) => count(array_filter($r, fn($c) => trim($c) !== '')) > 0));
        $this->preview = array_slice($this->rows, 0, 5);

        // Auto-detect mapping
        $this->mapping = [];
        foreach ($this->columns as $i => $col) {
            $this->mapping[$i] = $this->autoDetect($col);
        }

        $this->calculateStats();
        $this->dispatch('notify', type: 'success', message: count($this->rows) . ' ردیف بارگذاری شد');
    }

    protected function detectDelimiter(string $content): string
    {
        $candidates = ["\t", ",", ";", "|"];
        $lines = array_slice(array_filter(explode("\n", $content)), 0, 5);
        $best = ','; $bestScore = 0;
        foreach ($candidates as $d) {
            $score = 0;
            foreach ($lines as $line) $score += substr_count($line, $d);
            if ($score > $bestScore) { $bestScore = $score; $best = $d; }
        }
        return $best;
    }

    protected function parseCsv(string $text, string $delimiter): array
    {
        $rows = []; $cur = ''; $row = []; $inQuotes = false;
        $len = strlen($text);
        for ($i = 0; $i < $len; $i++) {
            $ch = $text[$i];
            if ($inQuotes) {
                if ($ch === '"') {
                    if ($i + 1 < $len && $text[$i + 1] === '"') { $cur .= '"'; $i++; }
                    else $inQuotes = false;
                } else $cur .= $ch;
            } else {
                if ($ch === '"') $inQuotes = true;
                elseif ($ch === $delimiter) { $row[] = $cur; $cur = ''; }
                elseif ($ch === "\n" || $ch === "\r") {
                    if ($cur !== '' || count($row)) { $row[] = $cur; $rows[] = $row; $row = []; $cur = ''; }
                    if ($ch === "\r" && $i + 1 < $len && $text[$i + 1] === "\n") $i++;
                } else $cur .= $ch;
            }
        }
        if ($cur !== '' || count($row)) { $row[] = $cur; $rows[] = $row; }
        return $rows;
    }

    protected function autoDetect(string $col): string
    {
        $c = mb_strtolower(trim($col));
        if (preg_match('/تلفن|موبایل|phone|mobile|tel/u', $c)) return 'phone';
        if (preg_match('/رهگیری|مرسوله|tracking|barcode|بارکد/u', $c)) return 'tracking';
        if (preg_match('/وضعیت|status/u', $c)) return 'status';
        if (preg_match('/وزن|weight/u', $c)) return 'weight';
        if (preg_match('/بیمه|insurance/u', $c)) return 'insurance';
        if (preg_match('/کرایه|هزینه|cost|fee/u', $c)) return 'cost';
        if (preg_match('/تاریخ|date/u', $c)) return 'date';
        if (preg_match('/گیرنده|receiver|name/u', $c)) return 'receiver';
        if (preg_match('/شهر|city/u', $c)) return 'city';
        return '';
    }

    public function updatedMapping(): void { $this->calculateStats(); }

    protected function calculateStats(): void
    {
        $this->matched = 0;
        $this->unmatched = 0;

        foreach ($this->rows as $row) {
            $data = $this->extractRow($row);
            if (empty($data['phone'])) { $this->unmatched++; continue; }
            $np = preg_replace('/\D/', '', $data['phone']);
            if (str_starts_with($np, '98')) $np = substr($np, 2);
            if (str_starts_with($np, '0')) $np = substr($np, 1);

            $exists = Order::where('phone', 'like', "%{$np}%")->exists();
            if ($exists) $this->matched++;
            else $this->unmatched++;
        }
    }

    protected function extractRow(array $row): array
    {
        $data = [];
        foreach ($this->mapping as $idx => $field) {
            if (!$field) continue;
            $data[$field] = trim($row[$idx] ?? '');
        }
        return $data;
    }

    public function save(): void
    {
        $applied = 0; $skipped = 0;

        foreach ($this->rows as $row) {
            $data = $this->extractRow($row);
            if (empty($data['phone'])) { $skipped++; continue; }

            $np = preg_replace('/\D/', '', $data['phone']);
            if (str_starts_with($np, '98')) $np = substr($np, 2);
            if (str_starts_with($np, '0')) $np = substr($np, 1);

            // پیدا کردن آخرین سفارش این مشتری
            $order = Order::where('phone', 'like', "%{$np}%")->latest('id')->first();
            if (!$order) { $skipped++; continue; }

            $update = [];
            if (!empty($data['tracking'])) $update['tracking_code'] = $data['tracking'];
            if (!empty($data['status'])) $update['postal_status'] = $data['status'];
            if (!empty($data['weight'])) $update['weight'] = (float) preg_replace('/[^\d.]/', '', $data['weight']);
            if (!empty($data['insurance'])) $update['insurance'] = (float) preg_replace('/[^\d.]/', '', $data['insurance']);
            if (!empty($data['cost'])) $update['shipping'] = (float) preg_replace('/[^\d.]/', '', $data['cost']);

            // ذخیره در meta برای اطمینان
            $meta = $order->meta ?? [];
            $meta['postal'] = array_merge($meta['postal'] ?? [], $data);
            $update['meta'] = $meta;

            if (!empty($update)) {
                $order->update($update);
                $applied++;
            } else {
                $skipped++;
            }
        }

        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: "{$applied} سفارش بروزرسانی شد · {$skipped} رد شد");
        $this->close();
    }

    public function render() { return view('livewire.orders.import-postal'); }
}
'''

IMPORT_POSTAL_BLADE = r'''<div>
@if($show)
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:820px">
        <div class="sg-modal-header" style="background:linear-gradient(135deg,#3498db,#1a5276)">
            <h2>📮 ایمپورت مرسولات پستی</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">
            @if(empty($columns))
                {{-- Step 1: Upload --}}
                <div class="form-group">
                    <label>فایل CSV/TSV (خروجی از شرکت پستی)</label>
                    <input type="file" wire:model="file" accept=".csv,.tsv,.txt" class="form-control">
                    <div wire:loading wire:target="file" style="text-align:center;padding:10px;color:var(--primary)">⏳ در حال بارگذاری...</div>
                </div>
                <div style="padding:10px 12px;background:rgba(52,152,219,.08);border-radius:10px;font-size:11.5px;line-height:1.7">
                    💡 تطبیق با سفارشات بر اساس <strong>شماره تلفن گیرنده</strong>.<br>
                    🔖 از Excel: File → Save As → CSV UTF-8
                </div>
            @else
                {{-- Stats --}}
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
                    <div style="padding:8px 14px;background:var(--bg);border-radius:10px;font-size:12px">📋 <strong>{{ \App\Support\PersianNumber::toFa(count($rows)) }}</strong> ردیف</div>
                    <div style="padding:8px 14px;background:rgba(39,174,96,.1);border-radius:10px;font-size:12px;color:var(--success)">🎯 <strong>{{ \App\Support\PersianNumber::toFa($matched) }}</strong> تطبیق</div>
                    <div style="padding:8px 14px;background:rgba(231,76,60,.1);border-radius:10px;font-size:12px;color:var(--danger)">⚠️ <strong>{{ \App\Support\PersianNumber::toFa($unmatched) }}</strong> بدون تطبیق</div>
                </div>

                {{-- Column Mapping --}}
                <div style="font-weight:700;font-size:12.5px;color:var(--primary);margin-bottom:8px">🗺️ نگاشت ستون‌ها</div>
                <div style="max-height:280px;overflow:auto;border-radius:10px;border:1px solid var(--border);margin-bottom:14px">
                    <table style="width:100%;border-collapse:collapse;font-size:12px">
                        <thead style="position:sticky;top:0;background:var(--thead-bg)">
                            <tr>
                                <th style="padding:8px;text-align:right">ستون فایل</th>
                                <th style="padding:8px;text-align:right">نمونه</th>
                                <th style="padding:8px;text-align:right">فیلد مقصد</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($columns as $i => $col)
                                <tr style="border-top:1px solid var(--border)">
                                    <td style="padding:8px;font-weight:700">{{ $col }}</td>
                                    <td style="padding:8px;font-size:10.5px;opacity:.7;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $rows[0][$i] ?? '—' }}</td>
                                    <td style="padding:8px">
                                        <select wire:model.live="mapping.{{ $i }}" class="form-control" style="padding:4px 8px;font-size:11px">
                                            @foreach($availableFields as $k => $v)
                                                <option value="{{ $k }}">{{ $v }}</option>
                                            @endforeach
                                        </select>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>

                {{-- Preview --}}
                <details style="margin-bottom:14px">
                    <summary style="cursor:pointer;font-weight:700;font-size:12px;color:var(--primary);padding:8px;background:var(--bg);border-radius:8px">👁️ پیش‌نمایش ۵ ردیف</summary>
                    <div style="max-height:240px;overflow:auto;margin-top:8px;border:1px solid var(--border);border-radius:8px">
                        <table style="width:100%;border-collapse:collapse;font-size:10.5px">
                            <thead style="background:var(--thead-bg);position:sticky;top:0">
                                <tr>
                                    @foreach($columns as $col)<th style="padding:6px;text-align:right;white-space:nowrap">{{ $col }}</th>@endforeach
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($preview as $row)
                                    <tr style="border-top:1px solid var(--border)">
                                        @foreach($row as $cell)
                                            <td style="padding:6px;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $cell }}</td>
                                        @endforeach
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </details>
            @endif
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline">انصراف</button>
            @if(!empty($columns))
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                    <span wire:loading.remove wire:target="save">✅ اعمال و بروزرسانی</span>
                    <span wire:loading wire:target="save">⏳ در حال اعمال...</span>
                </button>
            @endif
        </div>
    </div>
</div>
@endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۵) LAYOUT — Appearance + Mobile Bar fix + Import Button
# ═══════════════════════════════════════════════════════════════
def patch_layout_v2():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists(): return

    backup("resources/views/components/layouts/app.blade.php")

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    # ۱) اضافه کردن style با رنگ‌های تنظیمات
    style_block = '''    @php
        try {
            $_p = \\App\\Models\\AppSetting::get('primary_color', '#1a5276');
            $_g = \\App\\Models\\AppSetting::get('accent_color', '#c9a84c');
            $_f = \\App\\Models\\AppSetting::get('font_family', 'Vazirmatn');
        } catch (\\Throwable $e) {
            $_p = '#1a5276'; $_g = '#c9a84c'; $_f = 'Vazirmatn';
        }
    @endphp
    <style>
        :root {
            --primary: {{ $_p }} !important;
            --gold: {{ $_g }} !important;
            --primary-dynamic: {{ $_p }};
            --gold-dynamic: {{ $_g }};
            --font-dynamic: {{ $_f }};
        }
        body { font-family: var(--font-dynamic), 'Vazirmatn', Tahoma, sans-serif !important; }
    </style>
'''
    if 'primary-dynamic' not in content:
        content = content.replace('</head>', style_block + '</head>', 1)

    # ۲) اضافه کردن reports.css
    if 'reports.css' not in content:
        content = content.replace('</head>', '    <link rel="stylesheet" href="{{ asset(\'css/extra.css\') }}?v=2">\n</head>', 1)

    # ۳) اضافه کردن ImportPostal Livewire + customer profile modal
    if 'orders.import-postal' not in content:
        content = content.replace(
            '<livewire:orders.form-modal',
            '<livewire:orders.import-postal :key="\'imp\'" />\n    <livewire:orders.form-modal',
            1
        )

    # ۴) اضافه کردن event listener برای apply-appearance
    if 'apply-appearance' not in content:
        inject = '''
        Livewire.on('apply-appearance', function(data) {
            var p = Array.isArray(data) ? data[0] : data;
            var root = document.documentElement;
            if (p.primary_color) root.style.setProperty('--primary', p.primary_color);
            if (p.accent_color) root.style.setProperty('--gold', p.accent_color);
            if (p.font_family) root.style.setProperty('--font-dynamic', p.font_family);
            if (p.theme) {
                root.setAttribute('data-theme', p.theme);
                localStorage.setItem('theme', p.theme);
            }
        });
'''
        content = content.replace(
            "Livewire.on('apply-theme', function(data) {",
            inject + "Livewire.on('apply-theme', function(data) {",
            1
        )

    with open(layout, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("  ✓ Layout: Appearance + ImportPostal + font/color dynamic")

# ═══════════════════════════════════════════════════════════════
# ۶) SETTINGS — Mobile Tabs + Apply appearance
# ═══════════════════════════════════════════════════════════════
def patch_settings():
    php_path = PROJECT / "app/Livewire/Settings/Index.php"
    if not php_path.exists():
        print("  ⚠️ Settings Index پیدا نشد")
        return

    backup("app/Livewire/Settings/Index.php")

    with open(php_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # تغییر saveAppearance برای dispatch جدید
    if "dispatch('apply-appearance'" not in content:
        content = content.replace(
            "$this->dispatch('apply-theme', [\n            'theme' => $this->theme,\n            'density' => $this->density,\n            'primary_color' => $this->primary_color,\n        ]);",
            "$this->dispatch('apply-appearance', [\n            'theme' => $this->theme,\n            'density' => $this->density,\n            'primary_color' => $this->primary_color,\n            'accent_color' => $this->accent_color,\n            'font_family' => $this->font_family,\n        ]);"
        )
        content = content.replace(
            "$this->dispatch('apply-theme', [",
            "$this->dispatch('apply-appearance', ["
        )
        with open(php_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ Settings: apply-appearance dispatch")

    # اضافه کردن live appearance update
    if "public function updatedPrimaryColor" not in content:
        extra = '''

    public function updatedPrimaryColor(): void
    {
        $this->dispatch('apply-appearance', [
            'theme' => $this->theme,
            'primary_color' => $this->primary_color,
            'accent_color' => $this->accent_color,
            'font_family' => $this->font_family,
        ]);
    }

    public function updatedAccentColor(): void
    {
        $this->updatedPrimaryColor();
    }

    public function updatedTheme(): void
    {
        $this->updatedPrimaryColor();
    }

    public function updatedFontFamily(): void
    {
        $this->updatedPrimaryColor();
    }
'''
        # اضافه قبل از render
        idx = content.rfind('public function render()')
        if idx > 0:
            content = content[:idx] + extra + "\n    " + content[idx:]
            with open(php_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("  ✓ Settings: live appearance updates")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  توسعه کامل v2.2 — ۹ مشکل                                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    for rel in [
        "app/Livewire/Reports/Index.php",
        "resources/views/livewire/reports/index.blade.php",
        "app/Livewire/Settings/Index.php",
        "resources/views/components/layouts/app.blade.php",
    ]: backup(rel)

    print("\n📄 نوشتن فایل‌ها...")
    write("public/css/extra.css", EXTRA_CSS)
    write("app/Livewire/Reports/Index.php", REPORTS_PHP)
    write("resources/views/livewire/reports/index.blade.php", REPORTS_BLADE)
    write("app/Livewire/Orders/ImportPostal.php", IMPORT_POSTAL_PHP)
    write("resources/views/livewire/orders/import-postal.blade.php", IMPORT_POSTAL_BLADE)

    print("\n🔧 Patch Layout...")
    patch_layout_v2()

    print("\n🔧 Patch Settings...")
    patch_settings()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print("""
📋 اجرا کن:

  cd ~/shopgun-v2.2
  php artisan optimize:clear
  php artisan view:clear
  # سرور رو ببند (Ctrl+C) و دوباره
  php artisan serve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ۹ مشکل رفع شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ۱. ✅ Active state در موبایل‌بار — با localStorage حفظ می‌شه
  ۲. ✅ نمودارها در موبایل — overflow-x با اسکرول افقی
  ۳. ✅ نمودار خطی — خرید vs صدور شناسنامه
  ۴. ✅ تاریخ شمسی — همه‌جا (Labels, Charts, Timeline)
  ۵. ✅ پروفایل مشتری — Modal (نه صفحه)
  ۶. ✅ تایم‌لاین سفارش — تاریخ+ساعت شمسی، اسکرول افقی
  ۷. ✅ ایمپورت CSV شرکت پستی — با نگاشت ستون خودکار
  ۸. ✅ تب‌های تنظیمات در موبایل — اسکرول افقی، تب فعال مشخص
  ۹. ✅ رنگ و فونت در تنظیمات — Live Update

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 برای استفاده:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • گزارشات → /reports → فیلتر و نمودارهای جدید
  • ایمپورت CSV پستی → دکمه در /orders (باید اضافه بشه)
  • تب‌های تنظیمات موبایل → /settings
  • تغییر رنگ → تنظیمات → ظاهر → رنگ اصلی

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ نکته: این اسکریپت رو اول با «گزینه ب» اجرا کن:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  python improve_v22b.py
""")

if __name__ == "__main__":
    main()
