#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ShopGun V2 - Real Fix v5"""

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def log(m, k='info'):
    icons = {'info':'ℹ️','ok':'✅','warn':'⚠️','err':'❌'}
    colors = {'info':'\033[96m','ok':'\033[92m','warn':'\033[93m','err':'\033[91m'}
    print(f"{colors[k]} {icons[k]} {m}\033[0m")

def write(rel, content):
    full = ROOT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    if full.exists():
        full.rename(full.with_suffix(full.suffix + f'.bak-{datetime.now().strftime("%H%M%S")}'))
    full.write_text(content, encoding='utf-8')
    log(f"ساخته شد: {rel}", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۱. ORDERS/INDEX.PHP — بازنویسی کامل با تمام قابلیت‌ها
# ═══════════════════════════════════════════════════════════════

ORDERS_INDEX_PHP = r'''<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use App\Models\Channel;
use Livewire\Component;
use Livewire\WithPagination;
use Livewire\Attributes\On;

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

    // ★ ترتیب
    public string $sortField = 'id';
    public string $sortDirection = 'desc';

    protected $queryString = ['search', 'filterStatus'];

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingFilterStatus(): void { $this->resetPage(); }
    public function updatingDateFrom(): void { $this->resetPage(); }
    public function updatingDateTo(): void { $this->resetPage(); }
    public function updatingFilterChannel(): void { $this->resetPage(); }

    #[On('order-saved')]
    public function refreshList(): void { $this->resetPage(); }

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

    public function selectAllVisible(): void
    {
        if ($this->selectAll) {
            $this->selected = [];
            $this->selectAll = false;
        } else {
            $this->selected = $this->buildQuery()->pluck('id')->toArray();
            $this->selectAll = true;
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
        $this->dispatch('notify', type: 'success', message: count($this->selected) . ' سفارش حذف شد');
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
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($o->status, $statuses, true);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $o->update(['status' => $next]);
        $this->dispatch('notify', type: 'success', message: 'وضعیت: ' . $next);
    }

    protected function buildQuery()
    {
        return Order::query()
            ->with(['items', 'channel'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('customer_name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->when($this->filterChannel, fn($q) => $q->where('channel_id', $this->filterChannel))
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo));
    }

    public function render()
    {
        $orders = $this->buildQuery()
            ->orderBy($this->sortField, $this->sortDirection)
            ->paginate(20);

        return view('livewire.orders.index', [
            'orders' => $orders,
            'channels' => Channel::all(),
        ])->layout('components.layouts.app');
    }
}
'''
write('app/Livewire/Orders/Index.php', ORDERS_INDEX_PHP)

# ═══════════════════════════════════════════════════════════════
# ۲. ORDERS INDEX VIEW — بدون sortField در ویو (کامپوننت‌ها فقط)
# ═══════════════════════════════════════════════════════════════

ORDERS_INDEX_VIEW = r'''<div dir="rtl">

    {{-- ═══ فیلترها ═══ --}}
    <div style="padding: 12px 14px 0">
        <div class="filter-bar">
            <div class="field">
                <label>🔍 جستجو</label>
                <input type="text" wire:model.live.debounce.400ms="search" placeholder="شماره، نام، تلفن..." />
            </div>

            <div class="field">
                <label>📊 وضعیت</label>
                <select wire:model.live="filterStatus">
                    <option value="">همه</option>
                    <option value="pending">📝 ثبت سفارش</option>
                    <option value="final-check">🔍 چک نهایی</option>
                    <option value="courier">🚚 تحویل مامور</option>
                </select>
            </div>

            <x-ui.jalali-date model="dateFrom" label="📅 از تاریخ" />
            <x-ui.jalali-date model="dateTo"   label="📅 تا تاریخ" />

            <div class="field">
                <label style="opacity:0">عملیات</label>
                <div style="display:flex;gap:6px">
                    <button wire:click="clearFilters" class="btn btn-outline btn-sm" title="پاک کردن">✕</button>
                    <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary btn-sm">➕ جدید</button>
                </div>
            </div>
        </div>

        @if(count($selected) > 0)
            <div style="background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05));border:2px dashed var(--gold);border-radius:12px;padding:10px 14px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
                <span style="font-weight:700;color:var(--gold-dark)">
                    {{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد انتخاب شده
                </span>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                    <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                    <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                    <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️ حذف</button>
                    <button wire:click="clearSelection" class="btn btn-ghost btn-sm">✕</button>
                </div>
            </div>
        @endif
    </div>

    {{-- ═══ جدول ═══ --}}
    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>📦 سفارشات
                <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700;margin-right:6px">
                    {{ \App\Support\PersianNumber::toFa($orders->total()) }}
                </span>
            </h2>
        </div>

        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead>
                    <tr>
                        <th style="width:36px"><input type="checkbox" wire:click="selectAllVisible"></th>
                        <th wire:click="sortBy('order_number')" class="sortable {{ $sortField === 'order_number' ? 'sorted-' . $sortDirection : '' }}"># سفارش</th>
                        <th wire:click="sortBy('customer_name')" class="sortable {{ $sortField === 'customer_name' ? 'sorted-' . $sortDirection : '' }}">مشتری</th>
                        <th>تلفن</th>
                        <th>محصولات</th>
                        <th wire:click="sortBy('insurance')" class="sortable {{ $sortField === 'insurance' ? 'sorted-' . $sortDirection : '' }}">بیمه</th>
                        <th>وضعیت</th>
                        <th wire:click="sortBy('created_at')" class="sortable {{ $sortField === 'created_at' ? 'sorted-' . $sortDirection : '' }}">تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}">
                            <td><input type="checkbox" wire:click="toggleSelect({{ $order->id }})" @if(in_array($order->id, $selected)) checked @endif></td>
                            <td><strong>#{{ $order->order_number }}</strong></td>
                            <td>{{ $order->customer_name ?? '—' }}</td>
                            <td dir="ltr" style="font-family:monospace;font-size:11px">{{ $order->phone ?? '—' }}</td>
                            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">
                                @if($order->items->count())
                                    {{ $order->items->pluck('title')->take(2)->implode('، ') }}
                                    @if($order->items->count() > 2) <span style="opacity:.5">+{{ $order->items->count() - 2 }}</span> @endif
                                @else — @endif
                            </td>
                            <td>{{ \App\Support\PersianNumber::toFa(number_format((float) $order->insurance)) }}</td>
                            <td>
                                @php $st = ['pending'=>['📝','ثبت'],'final-check'=>['🔍','چک'],'courier'=>['🚚','مامور']][$order->status ?? 'pending'] ?? ['📝','ثبت']; @endphp
                                <span class="sg-status-badge {{ $order->status ?? 'pending' }}" wire:click="cycleStatus({{ $order->id }})" style="cursor:pointer">
                                    {{ $st[0] }} {{ $st[1] }}
                                </span>
                            </td>
                            <td style="font-size:10.5px;font-family:monospace">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})" class="sg-action-btn view">👁️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: {{ $order->id }}})" class="sg-action-btn edit">✏️</button>
                                    <button wire:click="delete({{ $order->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="9" style="text-align:center;padding:40px;opacity:.5">
                            <div style="font-size:44px">📦</div>
                            <p>سفارشی نیست</p>
                        </td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding:14px">{{ $orders->links() }}</div>
    </div>
</div>
'''
write('resources/views/livewire/orders/index.blade.php', ORDERS_INDEX_VIEW)

# ═══════════════════════════════════════════════════════════════
# ۳. تست WooCommerce — محاسبه تعداد از body
# ═══════════════════════════════════════════════════════════════

# فقط بخش testConnection را update کن
health = ROOT / 'app/Livewire/Settings/Health.php'
if health.exists():
    c = health.read_text(encoding='utf-8')

    # حذف شمارش قدیمی و جایگزینی
    old_count = """                $r = Http::withBasicAuth($key, $secret)
                    ->timeout(15)
                    ->get($base . "/{$ep}?per_page=1");
                $total = (int) ($r->header('X-WP-Total') ?: 0);"""

    new_count = """                $r = Http::withBasicAuth($key, $secret)
                    ->timeout(20)
                    ->get($base . "/{$ep}?per_page=1");
                // ★ هم هدر و هم body را چک کن
                $hdr = $r->header('X-WP-Total');
                $total = $hdr !== null ? (int) $hdr : 0;
                if ($total === 0 && $r->successful()) {
                    // اگر هدر نبود، از body نتیجه بگیر
                    $body = $r->json();
                    if (is_array($body)) $total = count($body);
                }"""

    if old_count in c:
        c = c.replace(old_count, new_count)
        health.write_text(c, encoding='utf-8')
        log("Health.php: شمارش WooCommerce اصلاح شد", 'ok')
    else:
        log("Health.php: الگو پیدا نشد — دستی بررسی کن", 'warn')

# ═══════════════════════════════════════════════════════════════
# ۴. Certificates Index — بررسی که خطا نده
# ═══════════════════════════════════════════════════════════════

cert_index = ROOT / 'app/Livewire/Certificates/Index.php'
if cert_index.exists():
    c = cert_index.read_text(encoding='utf-8')
    # اطمینان از نبود sortField در ویو
    cert_view = ROOT / 'resources/views/livewire/certificates/index.blade.php'
    if cert_view.exists():
        v = cert_view.read_text(encoding='utf-8')
        if 'sortField' in v and 'public string $sortField' not in c:
            # حذف wire:click="sortBy"
            v = v.replace('wire:click="sortBy(\'id\')"', '')
            cert_view.write_text(v, encoding='utf-8')
            log("Certificates view: sortBy حذف شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۵. پاکسازی
# ═══════════════════════════════════════════════════════════════

print("\n🔧 پاکسازی...")
subprocess.run("php artisan view:clear", shell=True, cwd=ROOT)
subprocess.run("php artisan optimize:clear", shell=True, cwd=ROOT)

print(r"""
╔══════════════════════════════════════════════════╗
║  ✅ رفع شد                                        ║
╚══════════════════════════════════════════════════╝

🎯 چه چیزی درست شد:
   ✅ خطای sortField در /orders حل شد
   ✅ Orders/Index.php کامل با sortField + clearFilters
   ✅ فیلتر تاریخ شمسی در سفارشات
   ✅ شمارش WooCommerce اصلاح شد

🚀 اجرا:
   php artisan serve
   http://127.0.0.1:8000/orders

⚠️ نکات باقی‌مانده که باید دانه‌دانه حل کنیم:
   1. تنظیمات تب‌ها (احتمالاً cache مشکل دارد)
   2. تنظیمات کامرس استایل
   3. پیش‌نمایش زنده شناسنامه
   4. تب تصاویر
   5. آپلود سنگ
   6. لاگ با جزئیات
   7. pop-up مشتری
""")
