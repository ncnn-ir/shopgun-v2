#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""فقط صفحه سفارشات را درست می‌کند"""

from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

# ═══ ۱. Orders/Index.php — بدون PowerGrid، ساده و کارآمد ═══
ORDERS_PHP = r'''<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use App\Models\Channel;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $filterStatus = '';
    public ?int $filterChannel = null;
    public string $dateFrom = '';
    public string $dateTo = '';
    public array $selected = [];
    public bool $selectAll = false;
    public string $sortField = 'id';
    public string $sortDirection = 'desc';

    protected $queryString = ['search', 'filterStatus'];

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingFilterStatus(): void { $this->resetPage(); }
    public function updatingDateFrom(): void { $this->resetPage(); }
    public function updatingDateTo(): void { $this->resetPage(); }

    public function sortBy(string $field): void
    {
        if ($this->sortField === $field) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortField = $field;
            $this->sortDirection = 'asc';
        }
    }

    public function clearFilters(): void
    {
        $this->reset(['search', 'filterStatus', 'filterChannel', 'dateFrom', 'dateTo']);
        $this->resetPage();
    }

    public function toggleSelect(int $id): void
    {
        if (in_array($id, $this->selected, true)) {
            $this->selected = array_values(array_diff($this->selected, [$id]));
        } else {
            $this->selected[] = $id;
        }
    }

    public function clearSelection(): void
    {
        $this->selected = [];
        $this->selectAll = false;
    }

    public function bulkStatus(string $status): void
    {
        if (!in_array($status, ['pending', 'final-check', 'courier'], true)) return;
        Order::whereIn('id', $this->selected)->update(['status' => $status]);
        $this->dispatch('notify', type: 'success', message: count($this->selected) . ' سفارش تغییر کرد');
        $this->clearSelection();
    }

    public function bulkDelete(): void
    {
        if (empty($this->selected)) return;
        Order::whereIn('id', $this->selected)->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
        $this->clearSelection();
    }

    public function delete(int $id): void
    {
        Order::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function cycleStatus(int $id): void
    {
        $o = Order::find($id);
        if (!$o) return;
        $list = ['pending', 'final-check', 'courier'];
        $cur = array_search($o->status, $list, true);
        $o->update(['status' => $list[($cur === false ? 0 : ($cur + 1)) % 3]]);
    }

    public function render()
    {
        $orders = Order::query()
            ->with(['items', 'channel'])
            ->when($this->search, fn($q) => $q->where(function ($qq) {
                $qq->where('order_number', 'like', "%{$this->search}%")
                   ->orWhere('customer_name', 'like', "%{$this->search}%")
                   ->orWhere('phone', 'like', "%{$this->search}%");
            }))
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo))
            ->orderBy($this->sortField, $this->sortDirection)
            ->paginate(20);

        return view('livewire.orders.index', [
            'orders' => $orders,
            'channels' => Channel::all(),
        ])->layout('components.layouts.app');
    }
}
'''

path = ROOT / 'app/Livewire/Orders/Index.php'
if path.exists():
    path.rename(path.with_suffix('.php.bak-orders-' + datetime.now().strftime('%H%M%S')))
path.write_text(ORDERS_PHP, encoding='utf-8')
print("✅ Orders/Index.php بازنویسی شد")

# ═══ ۲. View — بدون PowerGrid، با تاریخ شمسی دستی ساده ═══
ORDERS_VIEW = r'''<div dir="rtl" style="padding: 14px">

    {{-- ═══ فیلترها ═══ --}}
    <div style="background: var(--bg-card, #fff); border: 1px solid var(--border, #e2e8f0); border-radius: 12px; padding: 12px; margin-bottom: 14px;">
        <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">

            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">🔍 جستجو</label>
                    <input type="text" wire:model.live.debounce.400ms="search"
                           placeholder="شماره سفارش، نام مشتری، تلفن..."
                           style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft, #f8fafc); font-family: inherit; font-size: 13px; box-sizing: border-box;">
                </div>
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">📊 وضعیت</label>
                    <select wire:model.live="filterStatus"
                            style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft, #f8fafc); font-family: inherit; font-size: 13px; box-sizing: border-box;">
                        <option value="">همه</option>
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px;">
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">📅 از تاریخ (۱۴۰۳/۰۱/۰۱)</label>
                    <input type="text" wire:model.live="dateFrom" dir="ltr" placeholder="1403/01/01"
                           style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft); font-family: monospace; font-size: 13px; text-align: center; box-sizing: border-box;">
                </div>
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">📅 تا تاریخ</label>
                    <input type="text" wire:model.live="dateTo" dir="ltr" placeholder="1403/12/29"
                           style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft); font-family: monospace; font-size: 13px; text-align: center; box-sizing: border-box;">
                </div>
                <div style="display: flex; align-items: flex-end; gap: 6px;">
                    <button wire:click="clearFilters" class="btn btn-outline btn-sm" title="پاک کردن">✕</button>
                    <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary btn-sm">➕ جدید</button>
                </div>
            </div>
        </div>
    </div>

    {{-- ═══ نوار انتخاب گروهی ═══ --}}
    @if(count($selected) > 0)
        <div style="background: linear-gradient(135deg, rgba(201,168,76,.15), rgba(201,168,76,.05)); border: 2px dashed var(--gold); border-radius: 12px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <span style="font-weight: 700; color: var(--gold-dark, #b45309);">
                {{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد انتخاب شده
            </span>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️</button>
                <button wire:click="clearSelection" class="btn btn-ghost btn-sm">✕</button>
            </div>
        </div>
    @endif

    {{-- ═══ جدول ═══ --}}
    <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden;">
        <div style="padding: 12px 16px; background: linear-gradient(135deg, var(--primary), #0d3b5e); color: #fff;">
            <h2 style="margin: 0; font-size: 14px; font-weight: 700;">
                📦 سفارشات
                <span style="background: var(--gold); color: var(--primary); padding: 2px 10px; border-radius: 20px; font-size: 11px; margin-right: 8px;">
                    {{ \App\Support\PersianNumber::toFa($orders->total()) }}
                </span>
            </h2>
        </div>

        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; min-width: 900px;">
                <thead>
                    <tr style="background: var(--bg-soft, #f8fafc);">
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">
                            <input type="checkbox" onclick="this.checked ? Livewire.dispatch('selectAll') : null" style="accent-color: var(--gold);">
                        </th>
                        <th wire:click="sortBy('order_number')" style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px; cursor: pointer;">
                            # سفارش {{ $sortField === 'order_number' ? ($sortDirection === 'asc' ? '▲' : '▼') : '⇅' }}
                        </th>
                        <th wire:click="sortBy('customer_name')" style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px; cursor: pointer;">
                            مشتری {{ $sortField === 'customer_name' ? ($sortDirection === 'asc' ? '▲' : '▼') : '⇅' }}
                        </th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">تلفن</th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">محصولات</th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">بیمه</th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">وضعیت</th>
                        <th wire:click="sortBy('created_at')" style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px; cursor: pointer;">
                            تاریخ {{ $sortField === 'created_at' ? ($sortDirection === 'asc' ? '▲' : '▼') : '⇅' }}
                        </th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}" style="border-bottom: 1px solid var(--border);">
                            <td style="padding: 8px 10px;">
                                <input type="checkbox" wire:click="toggleSelect({{ $order->id }})"
                                       @if(in_array($order->id, $selected)) checked @endif
                                       style="accent-color: var(--gold);">
                            </td>
                            <td style="padding: 8px 10px;"><strong>#{{ $order->order_number }}</strong></td>
                            <td style="padding: 8px 10px;">{{ $order->customer_name ?? '—' }}</td>
                            <td style="padding: 8px 10px; font-family: monospace; font-size: 11px;" dir="ltr">{{ $order->phone ?? '—' }}</td>
                            <td style="padding: 8px 10px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                @if($order->items->count())
                                    {{ $order->items->pluck('title')->take(2)->implode('، ') }}
                                @else — @endif
                            </td>
                            <td style="padding: 8px 10px;">{{ \App\Support\PersianNumber::toFa(number_format((float) $order->insurance)) }}</td>
                            <td style="padding: 8px 10px;">
                                @php
                                    $stMap = ['pending'=>['📝','ثبت','#f59e0b'], 'final-check'=>['🔍','چک','#3b82f6'], 'courier'=>['🚚','مامور','#10b981']];
                                    $st = $stMap[$order->status ?? 'pending'] ?? ['📝','ثبت','#f59e0b'];
                                @endphp
                                <button wire:click="cycleStatus({{ $order->id }})"
                                        style="background: {{ $st[2] }}; color: #fff; border: none; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; cursor: pointer; font-family: inherit;">
                                    {{ $st[0] }} {{ $st[1] }}
                                </button>
                            </td>
                            <td style="padding: 8px 10px; font-family: monospace; font-size: 11px;">
                                {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}
                            </td>
                            <td style="padding: 8px 10px;">
                                <div style="display: flex; gap: 4px;">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})"
                                            class="btn-icon" title="نمایش">👁️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: {{ $order->id }}})"
                                            class="btn-icon" title="ویرایش">✏️</button>
                                    <button wire:click="delete({{ $order->id }})" wire:confirm="حذف شود؟"
                                            class="btn-icon" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="9" style="text-align: center; padding: 40px; opacity: .5;">
                                <div style="font-size: 44px;">📦</div>
                                <p>سفارشی نیست</p>
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding: 14px;">{{ $orders->links() }}</div>
    </div>
</div>

<style>
.btn-icon {
    width: 28px; height: 28px;
    border-radius: 8px; border: none;
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(0,0,0,.05); cursor: pointer; font-size: 13px;
    text-decoration: none;
}
.btn-icon:hover { background: rgba(201,168,76,.2); }
</style>
'''

path = ROOT / 'resources/views/livewire/orders/index.blade.php'
if path.exists():
    path.rename(path.with_suffix('.blade.php.bak-' + datetime.now().strftime('%H%M%S')))
path.write_text(ORDERS_VIEW, encoding='utf-8')
print("✅ Orders view بازنویسی شد")

# ═══ ۳. حذف PowerGrid route اگر اضافه شده ═══
routes = ROOT / 'routes/web.php'
if routes.exists():
    c = routes.read_text(encoding='utf-8')
    if '/table' in c and 'OrdersTable' in c:
        # حذف خط powergrid
        lines = [l for l in c.split('\n') if 'OrdersTable' not in l and "'/table'" not in l]
        routes.write_text('\n'.join(lines), encoding='utf-8')
        print("✅ route PowerGrid حذف شد")

# ═══ ۴. حذف فایل PowerGrid خرابکار ═══
pg_file = ROOT / 'app/Livewire/Tables/OrdersTable.php'
if pg_file.exists():
    pg_file.rename(pg_file.with_suffix('.php.broken-' + datetime.now().strftime('%H%M%S')))
    print("✅ OrdersTable.php غیرفعال شد")

print("\n╔══════════════════════════════════════════════╗")
print("║  ✅ سفارشات به حالت ساده و سالم برگشت         ║")
print("╚══════════════════════════════════════════════╝")
print("\n🚀 حالا: php artisan view:clear && php artisan serve")
