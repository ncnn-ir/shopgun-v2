#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 4
====================================
- BulkRunDetail (صفحه جزئیات هر Run)
- Reports Query Layer (Aggregates)
- Actions Layer (Domain Actions)
"""
from pathlib import Path
import time, subprocess

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)

def run(cmd):
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=ROOT).returncode


# ═══════════════════════════════════════════════════════════════
# 1. BulkRunDetail — صفحه جزئیات هر Run
# ═══════════════════════════════════════════════════════════════

write('app/Livewire/Products/BulkRunDetail.php', r'''<?php

namespace App\Livewire\Products;

use App\Application\Bulk\BulkEngine;
use App\Models\BulkItem;
use App\Models\BulkRun;
use Livewire\Component;
use Livewire\WithPagination;

/**
 * ★ BulkRunDetail — صفحه جزئیات یک Bulk Run
 * نمایش همه آیتم‌ها با فیلتر و صفحه‌بندی و retry
 */
class BulkRunDetail extends Component
{
    use WithPagination;

    public int $runId;
    public ?BulkRun $run = null;

    public string $filterStatus = '';
    public string $search = '';
    public string $sortBy = 'id';
    public string $sortDir = 'desc';

    public bool $showItemDetail = false;
    public ?array $itemDetail = null;

    public function mount(int $run): void
    {
        $this->runId = $run;
        $this->run = BulkRun::find($run);
        if (!$this->run) {
            abort(404, 'Run یافت نشد');
        }
    }

    public function updatingFilterStatus(): void { $this->resetPage(); }
    public function updatingSearch(): void { $this->resetPage(); }

    public function refresh(): void
    {
        $this->run = BulkRun::find($this->runId);
        if ($this->run) $this->run->recalcCounters();
        $this->dispatch('notify', type: 'success', message: 'بروزرسانی شد');
    }

    public function retryFailed(): void
    {
        if (!$this->run) return;
        try {
            (new BulkEngine())->retryFailed($this->run);
            $this->dispatch('notify', type: 'success', message: 'آیتم‌های ناموفق به صف جدید اضافه شدند');
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function cancel(): void
    {
        if (!$this->run) return;
        (new BulkEngine())->cancel($this->run);
        $this->run = BulkRun::find($this->runId);
        $this->dispatch('notify', type: 'success', message: 'لغو شد');
    }

    public function showItem(int $itemId): void
    {
        $item = BulkItem::find($itemId);
        if (!$item) return;

        $this->itemDetail = [
            'id' => $item->id,
            'sku' => $item->sku,
            'status' => $item->status,
            'woo_product_id' => $item->woo_product_id,
            'error_message' => $item->error_message,
            'error_code' => $item->error_code,
            'warnings' => $item->validation_warnings ?? [],
            'input' => $item->input_data ?? [],
            'request' => $item->request_payload,
            'response' => $item->response_payload,
            'diff' => $item->diff_data,
            'attempt' => $item->attempt,
            'edit_url' => $item->woo_edit_url,
            'view_url' => $item->woo_view_url,
            'started_at' => $item->started_at?->format('Y/m/d H:i:s'),
            'finished_at' => $item->finished_at?->format('Y/m/d H:i:s'),
        ];
        $this->showItemDetail = true;
    }

    public function closeItem(): void
    {
        $this->showItemDetail = false;
        $this->itemDetail = null;
    }

    public function render()
    {
        $items = BulkItem::query()
            ->where('run_id', $this->runId)
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->when($this->search, fn($q) => $q->where('sku', 'like', "%{$this->search}%"))
            ->orderBy($this->sortBy, $this->sortDir)
            ->paginate(30);

        $statusCounts = BulkItem::query()
            ->where('run_id', $this->runId)
            ->selectRaw('status, COUNT(*) as cnt')
            ->groupBy('status')
            ->pluck('cnt', 'status')
            ->toArray();

        return view('livewire.products.bulk-run-detail', [
            'items' => $items,
            'statusCounts' => $statusCounts,
        ])->layout('components.layouts.app');
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 2. BulkRunDetail View
# ═══════════════════════════════════════════════════════════════

write('resources/views/livewire/products/bulk-run-detail.blade.php', r'''<div style="padding:12px;direction:rtl" wire:poll.5s="refresh">

    @if(!$run)
        <div style="text-align:center;padding:40px;color:#94a3b8">Run پیدا نشد</div>
    @else

    {{-- Header --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:14px">
        <div>
            <h1 style="margin:0;font-size:19px;font-weight:700">📊 جزئیات اجرای #{{ $run->id }}</h1>
            <p style="margin:4px 0 0;font-size:11.5px;color:#64748b">
                شروع: {{ $run->started_at ? \App\Support\PersianDate::format($run->started_at, 'Y/m/d H:i') : '—' }}
                @if($run->finished_at)
                    · پایان: {{ \App\Support\PersianDate::format($run->finished_at, 'Y/m/d H:i') }}
                @endif
            </p>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
            @if(in_array($run->status, ['processing', 'queued']))
                <button wire:click="cancel" wire:confirm="لغو شود؟"
                        style="padding:7px 14px;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    🛑 لغو
                </button>
            @endif
            @if($run->failed_items > 0)
                <button wire:click="retryFailed" wire:confirm="آیتم‌های ناموفق مجدداً ارسال شوند؟"
                        style="padding:7px 14px;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    🔄 Retry ناموفق‌ها ({{ \App\Support\PersianNumber::toFa($run->failed_items) }})
                </button>
            @endif
            <a href="{{ route('products.bulk') }}" wire:navigate
               style="padding:7px 14px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none;font-size:12px">
                ← بازگشت
            </a>
        </div>
    </div>

    {{-- Progress --}}
    @php $pct = $run->progress_percent; @endphp
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:6px">
            <span>📤 پیشرفت</span>
            <span>{{ \App\Support\PersianNumber::toFa($pct) }}%</span>
        </div>
        <div style="height:12px;background:#e2e8f0;border-radius:6px;overflow:hidden;margin-bottom:12px">
            <div style="height:100%;width:{{ $pct }}%;background:linear-gradient(90deg,#16a34a,#10b981);transition:width .4s"></div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:8px">
            <div style="padding:10px;background:#f8fafc;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($run->total_items) }}</div>
                <div style="font-size:10px;color:#64748b;font-weight:700">کل</div>
            </div>
            <div style="padding:10px;background:#dbeafe;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#1e40af">{{ \App\Support\PersianNumber::toFa($run->queued_items) }}</div>
                <div style="font-size:10px;color:#1e40af;font-weight:700">در صف</div>
            </div>
            <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($run->processing_items) }}</div>
                <div style="font-size:10px;color:#92400e;font-weight:700">پردازش</div>
            </div>
            <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($run->success_items) }}</div>
                <div style="font-size:10px;color:#065f46;font-weight:700">موفق</div>
            </div>
            <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($run->failed_items) }}</div>
                <div style="font-size:10px;color:#991b1b;font-weight:700">ناموفق</div>
            </div>
        </div>
    </div>

    {{-- Filters --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:8px;margin-bottom:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px">
        <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجوی SKU..."
               style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc;box-sizing:border-box">
        <select wire:model.live="filterStatus" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc">
            <option value="">همه وضعیت‌ها ({{ array_sum($statusCounts) }})</option>
            @foreach(['pending'=>'⏸️ در انتظار','valid'=>'✓ معتبر','invalid'=>'⚠️ نامعتبر','queued'=>'🕐 در صف','processing'=>'⏳ پردازش','success'=>'✅ موفق','draft_created'=>'📝 پیش‌نویس','failed'=>'❌ ناموفق'] as $k => $lbl)
                @if(isset($statusCounts[$k]))
                    <option value="{{ $k }}">{{ $lbl }} ({{ $statusCounts[$k] }})</option>
                @endif
            @endforeach
        </select>
    </div>

    {{-- Items Table --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
        <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;font-size:11.5px;min-width:700px">
                <thead style="background:#f8fafc;position:sticky;top:0;z-index:2">
                    <tr>
                        <th wire:click="$set('sortBy','id')" style="padding:7px;text-align:right;color:#1a5276;cursor:pointer">#</th>
                        <th wire:click="$set('sortBy','sku')" style="padding:7px;text-align:right;color:#1a5276;cursor:pointer">SKU</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">عنوان</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">قیمت</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">وضعیت</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">جزئیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($items as $it)
                        @php
                            $stMap = [
                                'pending' => ['⏸️', 'در انتظار', '#f1f5f9', '#475569'],
                                'valid' => ['✓', 'معتبر', '#d1fae5', '#065f46'],
                                'invalid' => ['⚠️', 'نامعتبر', '#fef3c7', '#92400e'],
                                'queued' => ['🕐', 'در صف', '#dbeafe', '#1e40af'],
                                'processing' => ['⏳', 'پردازش', '#fef3c7', '#92400e'],
                                'success' => ['✅', 'موفق', '#d1fae5', '#065f46'],
                                'draft_created' => ['📝', 'پیش‌نویس', '#fef3c7', '#92400e'],
                                'failed' => ['❌', 'ناموفق', '#fee2e2', '#991b1b'],
                            ];
                            $st = $stMap[$it->status] ?? ['—', $it->status, '#f1f5f9', '#475569'];
                        @endphp
                        <tr wire:key="item-{{ $it->id }}" style="border-bottom:1px solid #f1f5f9;cursor:pointer"
                            wire:click="showItem({{ $it->id }})">
                            <td style="padding:6px;font-family:monospace;font-size:10.5px">{{ \App\Support\PersianNumber::toFa($it->id) }}</td>
                            <td style="padding:6px;font-family:monospace;font-weight:700;font-size:11px">{{ $it->sku }}</td>
                            <td style="padding:6px;font-size:11px;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                                {{ $it->input_data['title_fa'] ?? '—' }}
                            </td>
                            <td style="padding:6px;font-family:monospace;font-size:10.5px">
                                @if(!empty($it->input_data['regular_price']))
                                    {{ number_format((float) $it->input_data['regular_price']) }}
                                @else — @endif
                            </td>
                            <td style="padding:6px">
                                <span style="background:{{ $st[2] }};color:{{ $st[3] }};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;white-space:nowrap">
                                    {{ $st[0] }} {{ $st[1] }}
                                </span>
                            </td>
                            <td style="padding:6px;font-size:10.5px">
                                @if($it->error_message)
                                    <span style="color:#991b1b">{{ \Illuminate\Support\Str::limit($it->error_message, 40) }}</span>
                                @elseif($it->woo_product_id)
                                    <a href="{{ $it->woo_edit_url }}" target="_blank" style="color:#1e40af;text-decoration:none" onclick="event.stopPropagation()">✏️ ID {{ $it->woo_product_id }}</a>
                                @else
                                    <span style="color:#94a3b8">—</span>
                                @endif
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="6" style="text-align:center;padding:30px;color:#94a3b8">آیتمی با این فیلتر نیست</td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:10px">{{ $items->links() }}</div>
    </div>

    @endif

    {{-- ══════ Item Detail Modal ══════ --}}
    @if($showItemDetail && $itemDetail)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:8px;overflow-y:auto"
             @keydown.escape.window="$wire.closeItem()">

            <div style="background:#fff;width:100%;max-width:640px;margin:8px auto;border-radius:14px;overflow:hidden;direction:rtl">

                <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center">
                    <h2 style="margin:0;font-size:14px;font-weight:700">🔍 SKU {{ $itemDetail['sku'] }}</h2>
                    <button wire:click="closeItem" style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:14px">✕</button>
                </div>

                <div style="padding:14px;max-height:calc(100vh - 140px);overflow-y:auto">

                    {{-- Warnings --}}
                    @if(!empty($itemDetail['warnings']))
                        <div style="padding:10px;background:#fef3c7;border-radius:8px;margin-bottom:12px">
                            <div style="font-size:11.5px;font-weight:700;color:#92400e;margin-bottom:6px">⚠️ هشدارها</div>
                            @foreach($itemDetail['warnings'] as $w)
                                <div style="font-size:11px;color:#92400e">• {{ $w }}</div>
                            @endforeach
                        </div>
                    @endif

                    {{-- Error --}}
                    @if($itemDetail['error_message'])
                        <div style="padding:10px;background:#fee2e2;border-radius:8px;margin-bottom:12px">
                            <div style="font-size:11.5px;font-weight:700;color:#991b1b;margin-bottom:4px">❌ خطا ({{ $itemDetail['error_code'] ?? 'unknown' }})</div>
                            <div style="font-size:11px;color:#991b1b;font-family:monospace">{{ $itemDetail['error_message'] }}</div>
                        </div>
                    @endif

                    {{-- Success links --}}
                    @if($itemDetail['woo_product_id'])
                        <div style="padding:10px;background:#d1fae5;border-radius:8px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
                            <span style="font-size:11.5px;font-weight:700;color:#065f46">✅ Woo ID: {{ $itemDetail['woo_product_id'] }}</span>
                            <div style="display:flex;gap:6px">
                                @if($itemDetail['edit_url'])
                                    <a href="{{ $itemDetail['edit_url'] }}" target="_blank"
                                       style="padding:4px 12px;background:#065f46;color:#fff;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none">✏️ ویرایش</a>
                                @endif
                                @if($itemDetail['view_url'])
                                    <a href="{{ $itemDetail['view_url'] }}" target="_blank"
                                       style="padding:4px 12px;background:#16a34a;color:#fff;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none">🌐 مشاهده</a>
                                @endif
                            </div>
                        </div>
                    @endif

                    {{-- Input data --}}
                    <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:6px">📥 داده ورودی</div>
                    <div style="background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:12px;font-size:11px;font-family:monospace;direction:ltr;white-space:pre-wrap;overflow-x:auto;max-height:200px">
{{ json_encode($itemDetail['input'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}
                    </div>

                    {{-- Request --}}
                    @if($itemDetail['request'])
                        <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:6px">📤 درخواست</div>
                        <div style="background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:12px;font-size:10px;font-family:monospace;direction:ltr;white-space:pre-wrap;overflow-x:auto;max-height:200px">
{{ json_encode($itemDetail['request'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}
                        </div>
                    @endif

                    {{-- Response --}}
                    @if($itemDetail['response'])
                        <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:6px">📥 پاسخ</div>
                        <div style="background:#f8fafc;border-radius:8px;padding:10px;font-size:10px;font-family:monospace;direction:ltr;white-space:pre-wrap;overflow-x:auto;max-height:200px">
{{ json_encode($itemDetail['response'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}
                        </div>
                    @endif

                    {{-- Timing --}}
                    <div style="margin-top:12px;padding-top:12px;border-top:1px solid #e2e8f0;font-size:10.5px;color:#64748b;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px">
                        <span>شروع: {{ $itemDetail['started_at'] ?? '—' }}</span>
                        <span>پایان: {{ $itemDetail['finished_at'] ?? '—' }}</span>
                        <span>تلاش: {{ $itemDetail['attempt'] }}</span>
                    </div>
                </div>
            </div>
        </div>
    @endif
</div>
''')


# ═══════════════════════════════════════════════════════════════
# 3. REPORTS QUERY LAYER
# ═══════════════════════════════════════════════════════════════

write('app/Application/Reports/SalesMetrics.php', r'''<?php

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
''')

write('app/Application/Reports/CustomerMetrics.php', r'''<?php

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
''')

write('app/Application/Reports/ProductMetrics.php', r'''<?php

namespace App\Application\Reports;

use App\Models\Product;
use App\Models\Certificate;

class ProductMetrics
{
    public function __construct(
        public \Carbon\Carbon $from,
        public \Carbon\Carbon $to,
    ) {}

    public function totalProducts(): int
    {
        return Product::count();
    }

    public function activeProducts(): int
    {
        return Product::where('is_active', true)->count();
    }

    public function certificatesCount(): int
    {
        return Certificate::whereBetween('created_at', [$this->from, $this->to])->count();
    }

    public function topIssuedStones(int $limit = 5): array
    {
        return Certificate::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->select('stone_name', \Illuminate\Support\Facades\DB::raw('COUNT(*) as cnt'))
            ->groupBy('stone_name')
            ->orderByDesc('cnt')
            ->limit($limit)
            ->get()
            ->toArray();
    }
}
''')

write('app/Application/Reports/ReportEngine.php', r'''<?php

namespace App\Application\Reports;

use Carbon\Carbon;

/**
 * ★ ReportEngine — نقطه واحد دسترسی به همه metrics
 */
class ReportEngine
{
    public Carbon $from;
    public Carbon $to;
    public string $rangeLabel;

    public function __construct(public string $range = 'week')
    {
        [$from, $to, $label] = match ($range) {
            'today' => [now()->startOfDay(), now()->endOfDay(), 'امروز'],
            'week' => [now()->subDays(6)->startOfDay(), now()->endOfDay(), '۷ روز اخیر'],
            'month' => [now()->subDays(29)->startOfDay(), now()->endOfDay(), '۳۰ روز اخیر'],
            'year' => [now()->startOfYear(), now()->endOfDay(), 'سال جاری'],
            default => [now()->subDays(6)->startOfDay(), now()->endOfDay(), '۷ روز اخیر'],
        };

        $this->from = $from;
        $this->to = $to;
        $this->rangeLabel = $label;
    }

    public function sales(): SalesMetrics
    {
        return new SalesMetrics($this->from, $this->to);
    }

    public function customers(): CustomerMetrics
    {
        return new CustomerMetrics($this->from, $this->to);
    }

    public function products(): ProductMetrics
    {
        return new ProductMetrics($this->from, $this->to);
    }

    /**
     * همه KPI های صفحه گزارش
     */
    public function dashboardKpi(): array
    {
        $sales = $this->sales();
        $customers = $this->customers();
        $products = $this->products();

        return [
            [
                'icon' => '📦',
                'color' => 'rgba(41,128,185,.15)',
                'num' => $sales->ordersCount(),
                'lbl' => 'سفارشات',
                'raw' => true,
            ],
            [
                'icon' => '💰',
                'color' => 'rgba(39,174,96,.15)',
                'num' => $sales->totalRevenue() / 1000000,
                'lbl' => 'فروش (م)',
                'dec' => 1,
            ],
            [
                'icon' => '👥',
                'color' => 'rgba(155,89,182,.15)',
                'num' => $customers->newCustomersCount(),
                'lbl' => 'مشتریان جدید',
                'raw' => true,
            ],
            [
                'icon' => '💎',
                'color' => 'rgba(201,168,76,.2)',
                'num' => $products->certificatesCount(),
                'lbl' => 'شناسنامه',
                'raw' => true,
            ],
            [
                'icon' => '📊',
                'color' => 'rgba(230,126,34,.15)',
                'num' => $sales->avgOrderValue() / 1000,
                'lbl' => 'میانگین (ه)',
                'dec' => 0,
            ],
            [
                'icon' => '⏳',
                'color' => 'rgba(243,156,18,.15)',
                'num' => $sales->pendingOrdersCount(),
                'lbl' => 'در انتظار',
                'raw' => true,
            ],
        ];
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 4. ACTIONS LAYER — Domain Actions
# ═══════════════════════════════════════════════════════════════

write('app/Application/Actions/CreateOrderAction.php', r'''<?php

namespace App\Application\Actions;

use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use App\Application\Notifications\NotificationService;

/**
 * ★ CreateOrderAction
 * نقطه واحد ساخت سفارش — با منطق دامنه
 */
class CreateOrderAction
{
    /**
     * @param array $data {
     *   phone, name, address, postal_code, channel_id,
     *   insurance, discount, shipping, notes, invoice_needed,
     *   items: [{title, sku, price, quantity, cert_needed}]
     * }
     */
    public function execute(array $data): Order
    {
        // ۱. Resolve یا ایجاد مشتری
        $customer = $this->resolveCustomer($data);

        // ۲. محاسبه مبلغ کل
        $amount = 0;
        foreach ($data['items'] ?? [] as $it) {
            $amount += ((float) ($it['price'] ?? 0)) * ((int) ($it['quantity'] ?? 1));
        }

        // ۳. ایجاد سفارش
        $order = Order::create([
            'order_number' => Order::generateNumber(),
            'customer_id' => $customer->id,
            'customer_name' => $data['name'] ?? $customer->name,
            'phone' => $customer->phone,
            'address' => $data['address'] ?? $customer->address,
            'postal_code' => $data['postal_code'] ?? $customer->postal_code,
            'channel_id' => $data['channel_id'] ?? null,
            'status' => $data['status'] ?? 'pending',
            'amount' => $amount,
            'insurance' => (float) ($data['insurance'] ?? 0),
            'discount' => (float) ($data['discount'] ?? 0),
            'shipping' => (float) ($data['shipping'] ?? 0),
            'notes' => $data['notes'] ?? null,
            'invoice_needed' => (bool) ($data['invoice_needed'] ?? false),
        ]);

        // ۴. اقلام سفارش
        foreach (($data['items'] ?? []) as $idx => $it) {
            if (empty($it['title']) && empty($it['sku'])) continue;

            OrderItem::create([
                'order_id' => $order->id,
                'sku' => $it['sku'] ?? null,
                'title' => $it['title'] ?? 'محصول',
                'price' => (float) ($it['price'] ?? 0),
                'quantity' => (int) ($it['quantity'] ?? 1),
                'cert_needed' => (bool) ($it['cert_needed'] ?? true),
                'sort_order' => $idx,
            ]);
        }

        // ۵. اعلان
        try {
            NotificationService::toAll(
                type: 'order_created',
                title: "سفارش جدید #{$order->order_number}",
                message: ($customer->name ?? 'مشتری') . ' — ' . number_format($amount),
                icon: '📦',
                url: route('orders.show', $order),
                data: ['order_id' => $order->id],
            );
        } catch (\Throwable $e) {}

        return $order;
    }

    protected function resolveCustomer(array $data): Customer
    {
        $phone = Customer::normalizePhone($data['phone'] ?? '');
        if ($phone === '') {
            throw new \InvalidArgumentException('شماره تلفن معتبر نیست');
        }

        $customer = Customer::where('phone', $phone)->first();

        if (!$customer) {
            $customer = Customer::create([
                'name' => $data['name'] ?? 'بدون نام',
                'phone' => $phone,
                'address' => $data['address'] ?? null,
                'postal_code' => $data['postal_code'] ?? null,
            ]);
        } else {
            // بروزرسانی اطلاعات اگر داده جدید داشتیم
            $update = [];
            if (!empty($data['name']) && $data['name'] !== $customer->name) {
                $update['name'] = $data['name'];
            }
            if (!empty($data['address']) && $data['address'] !== $customer->address) {
                $update['address'] = $data['address'];
            }
            if (!empty($data['postal_code']) && $data['postal_code'] !== $customer->postal_code) {
                $update['postal_code'] = $data['postal_code'];
            }
            if (!empty($update)) $customer->update($update);
        }

        return $customer;
    }
}
''')

write('app/Application/Actions/IssueCertificateAction.php', r'''<?php

namespace App\Application\Actions;

use App\Application\Certificates\CertificateSnapshotService;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\ProductIdentity;
use App\Application\Notifications\NotificationService;

/**
 * ★ IssueCertificateAction
 * نقطه واحد صدور شناسنامه
 */
class IssueCertificateAction
{
    /**
     * @param array $data {
     *   stone_name, stone_en, stone_origin, stone_flag,
     *   metal, metal_en, metal_carat,
     *   length, width, weight, brilliant,
     *   image_path, image_url,
     *   customer_id, order_id, sku, design_data
     * }
     */
    public function execute(array $data): Certificate
    {
        // ۱. تولید کد و سریال
        $code = Certificate::generateCode();
        $serial = Certificate::generateSerial($code, $data['stone_en'] ?? $data['stone_name'] ?? 'XXX');

        // ۲. اگر SKU داشت، ProductIdentity را بروز کن
        if (!empty($data['sku'])) {
            $this->resolveProductIdentity($data['sku']);
        }

        // ۳. ایجاد شناسنامه
        $cert = Certificate::create([
            'code' => $code,
            'serial' => $serial,
            'sku' => $data['sku'] ?? null,
            'stone_name' => $data['stone_name'] ?? '',
            'stone_en' => $data['stone_en'] ?? null,
            'stone_origin' => $data['stone_origin'] ?? null,
            'stone_flag' => $data['stone_flag'] ?? null,
            'metal' => $data['metal'] ?? '',
            'metal_en' => $data['metal_en'] ?? null,
            'metal_carat' => $data['metal_carat'] ?? null,
            'length' => (float) ($data['length'] ?? 0),
            'width' => (float) ($data['width'] ?? 0),
            'weight' => (float) ($data['weight'] ?? 0),
            'brilliant' => (int) ($data['brilliant'] ?? 0),
            'image_path' => $data['image_path'] ?? null,
            'image_url' => $data['image_url'] ?? null,
            'customer_id' => $data['customer_id'] ?? null,
            'order_id' => $data['order_id'] ?? null,
            'design_data' => $data['design_data'] ?? null,
            'issued_at' => now(),
        ]);

        // ۴. Snapshot (خودکار توسط Observer انجام می‌شود — این fallback)
        try {
            CertificateSnapshotService::capture($cert, 'issued');
        } catch (\Throwable $e) {}

        // ۵. اعلان
        try {
            NotificationService::toAll(
                type: 'certificate_issued',
                title: "شناسنامه #{$code} صادر شد",
                message: ($data['stone_name'] ?? '') . ' — ' . ($data['metal'] ?? ''),
                icon: '💎',
                url: route('certificates.show', $cert),
                data: ['certificate_id' => $cert->id],
            );
        } catch (\Throwable $e) {}

        return $cert;
    }

    protected function resolveProductIdentity(string $sku): ?ProductIdentity
    {
        try {
            $resolver = new \App\Application\Products\ProductResolver();
            return $resolver->resolve($sku, true);
        } catch (\Throwable $e) {
            return null;
        }
    }
}
''')

write('app/Application/Actions/UpdateOrderStatusAction.php', r'''<?php

namespace App\Application\Actions;

use App\Models\Order;
use App\Application\Notifications\NotificationService;

/**
 * ★ UpdateOrderStatusAction — با اعتبارسنجی وضعیت
 */
class UpdateOrderStatusAction
{
    public const VALID_STATUSES = ['pending', 'final-check', 'courier'];

    /**
     * تغییر وضعیت سفارش با اعتبارسنجی و اعلان
     */
    public function execute(int $orderId, string $newStatus, ?int $userId = null): ?Order
    {
        if (!in_array($newStatus, self::VALID_STATUSES, true)) {
            throw new \InvalidArgumentException("وضعیت نامعتبر: {$newStatus}");
        }

        $order = Order::find($orderId);
        if (!$order) return null;

        $oldStatus = $order->status;
        if ($oldStatus === $newStatus) return $order;

        $order->update(['status' => $newStatus]);

        // اعلان
        try {
            NotificationService::toAll(
                type: 'order_status',
                title: "تغییر وضعیت سفارش #{$order->order_number}",
                message: "از «{$oldStatus}» به «{$order->status_label}»",
                icon: '🔄',
                url: route('orders.show', $order),
                data: ['order_id' => $order->id, 'old' => $oldStatus, 'new' => $newStatus],
            );
        } catch (\Throwable $e) {}

        return $order;
    }

    /**
     * چرخه وضعیت (برای کلیک)
     */
    public function cycle(int $orderId): ?Order
    {
        $order = Order::find($orderId);
        if (!$order) return null;

        $list = self::VALID_STATUSES;
        $cur = array_search($order->status, $list, true);
        $next = $list[($cur === false ? 0 : ($cur + 1)) % count($list)];

        return $this->execute($orderId, $next);
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 5. ROUTE — Bulk Run Detail
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')

    if 'products.bulk.run' not in txt:
        marker = "Route::get('/products/bulk', \\App\\Livewire\\Products\\BulkCreate::class)->name('products.bulk');"
        new_route = """Route::get('/products/bulk', \\App\\Livewire\\Products\\BulkCreate::class)->name('products.bulk');
    Route::get('/products/bulk/run/{run}', \\App\\Livewire\\Products\\BulkRunDetail::class)->name('products.bulk.run');"""
        if marker in txt:
            txt = txt.replace(marker, new_route, 1)
            routes.write_text(txt, encoding='utf-8')
            print("[OK] route products.bulk.run")


# ═══════════════════════════════════════════════════════════════
# 6. BULK CREATE VIEW — لینک به Run Detail
# ═══════════════════════════════════════════════════════════════

bv = ROOT / 'resources' / 'views' / 'livewire' / 'products' / 'bulk-create.blade.php'
if bv.exists():
    txt = bv.read_text(encoding='utf-8')

    # بعد از confirmSend موفق → برو به Run Detail
    # این منطق در کامپوننت انجام می‌شود

    # اضافه کردن لینک در Queue tab
    if 'مشاهده جزئیات Run' not in txt:
        marker = '<h3>📊 گزارش پیشرفت (auto-refresh)</h3>'
        new_marker = '''<h3 style="display:flex;justify-content:space-between;align-items:center">
                <span>📊 گزارش پیشرفت (auto-refresh)</span>
                @if($current_run_id)
                    <a href="{{ route('products.bulk.run', $current_run_id) }}" wire:navigate
                       style="padding:5px 12px;background:#7c3aed;color:#fff;border-radius:8px;font-size:11px;font-weight:700;text-decoration:none">
                        🔍 مشاهده جزئیات Run
                    </a>
                @endif
            </h3>'''
        txt = txt.replace(marker, new_marker, 1)
        bv.write_text(txt, encoding='utf-8')
        print("[OK] bulk-create — لینک Run Detail")


# ═══════════════════════════════════════════════════════════════
# 7. اجرا
# ═══════════════════════════════════════════════════════════════

print()
print("🔧 پاک‌سازی...")
run('php artisan optimize:clear')
run('php artisan route:clear')
run('php artisan view:clear')

print()
print("=" * 60)
print("DONE — Phase 4")
print("=" * 60)
print()
print("🎯 دستاوردهای فاز ۴:")
print("   ✅ BulkRunDetail — صفحه جزئیات هر Run با فیلتر و صفحه‌بندی")
print("   ✅ Reports Query Layer (SalesMetrics, CustomerMetrics, ProductMetrics)")
print("   ✅ ReportEngine — نقطه واحد دسترسی")
print("   ✅ Actions Layer (CreateOrderAction, IssueCertificateAction, UpdateOrderStatusAction)")
print()
print("🔗 دسترسی:")
print("   /products/bulk           → صفحه اصلی")
print("   /products/bulk/run/{id}  → جزئیات Run")
print()
print("🚀 php artisan serve")

