#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Port کامل Legacy → Laravel — همه امکانات
شامل: Order Form/View, Cert 3-step, Quick Cert, Preview, Print, CSV, Mahak, Label, Backup, Settings کامل
"""
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
# ۱) ORDERS — Livewire Component کامل
# ═══════════════════════════════════════════════════════════════
ORDERS_INDEX = r'''<?php
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

    protected $queryString = ['search', 'filterStatus'];

    public function updatingSearch() { $this->resetPage(); }
    public function updatingFilterStatus() { $this->resetPage(); }

    #[On('order-saved')]
    public function refreshList() { $this->resetPage(); }

    public function toggleSelect(int $id) {
        if (in_array($id, $this->selected)) {
            $this->selected = array_values(array_diff($this->selected, [$id]));
        } else {
            $this->selected[] = $id;
        }
    }

    public function selectAllVisible() {
        if ($this->selectAll) {
            $this->selected = $this->getOrders()->pluck('id')->toArray();
            $this->selectAll = false;
        } else {
            $this->selected = [];
            $this->selectAll = true;
        }
    }

    public function clearSelection() { $this->selected = []; $this->selectAll = false; }

    public function bulkStatus(string $status) {
        Order::whereIn('id', $this->selected)->update(['status' => $status]);
        $this->dispatch('notify', type: 'success', message: count($this->selected) . ' سفارش تغییر کرد');
        $this->clearSelection();
    }

    public function bulkDelete() {
        if (empty($this->selected)) return;
        Order::whereIn('id', $this->selected)->delete();
        $this->dispatch('notify', type: 'success', message: count($this->selected) . ' سفارش حذف شد');
        $this->clearSelection();
    }

    public function delete(int $id) {
        Order::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function cycleStatus(int $id) {
        $o = Order::find($id);
        if (!$o) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($o->status, $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $o->update(['status' => $next]);
        $this->dispatch('notify', type: 'success', message: 'وضعیت: ' . $next);
    }

    private function getOrders() {
        return Order::query()
            ->when($this->search, function($q) {
                $q->where(function($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('customer_name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->when($this->filterChannel, fn($q) => $q->where('channel_id', $this->filterChannel))
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo))
            ->latest('id');
    }

    public function render() {
        $orders = $this->getOrders()->paginate(20);
        return view('livewire.orders.index', [
            'orders' => $orders,
            'channels' => Channel::all(),
        ])->layout('components.layouts.app');
    }
}
'''

ORDERS_INDEX_BLADE = r'''<div>
    {{-- Toolbar --}}
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <div class="search-box" style="position:relative">
                <input type="text" wire:model.live.debounce.400ms="search"
                       placeholder="🔍 جستجو..." class="form-control" style="width:220px">
            </div>
            <select wire:model.live="filterStatus" class="form-control" style="width:auto;display:inline-block">
                <option value="">همه وضعیت‌ها</option>
                <option value="pending">📝 ثبت سفارش</option>
                <option value="final-check">🔍 چک نهایی</option>
                <option value="courier">🚚 تحویل مامور</option>
            </select>
            <select wire:model.live="filterChannel" class="form-control" style="width:auto;display:inline-block">
                <option value="">همه کانال‌ها</option>
                @foreach($channels as $ch)
                    <option value="{{ $ch->id }}">{{ $ch->icon ?? '' }} {{ $ch->name }}</option>
                @endforeach
            </select>
            @if($search || $filterStatus || $filterChannel)
                <button wire:click="$set('search',''); $set('filterStatus',''); $set('filterChannel',null)" class="btn btn-outline btn-sm">✕ پاک</button>
            @endif
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary">➕ سفارش جدید</button>
        </div>
    </div>

    {{-- Bulk Bar --}}
    @if(count($selected) > 0)
        <div class="sg-toolbar" style="background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05));border:2px dashed var(--gold);">
            <span style="font-weight:700;color:var(--gold-dark)">{{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد انتخاب شده</span>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️ حذف</button>
                <button wire:click="clearSelection" class="btn btn-outline btn-sm">✕</button>
            </div>
        </div>
    @endif

    {{-- Table --}}
    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>📦 سفارشات <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($orders->total()) }}</span></h2>
        </div>
        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead>
                    <tr>
                        <th style="width:36px"><input type="checkbox" wire:click="selectAllVisible"></th>
                        <th>#</th>
                        <th>مشتری</th>
                        <th>تلفن</th>
                        <th>محصولات</th>
                        <th>بیمه</th>
                        <th>وضعیت</th>
                        <th>کانال</th>
                        <th>تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}">
                            <td><input type="checkbox" wire:click="toggleSelect({{ $order->id }})" @if(in_array($order->id, $selected)) checked @endif></td>
                            <td><strong>#{{ $order->order_number }}</strong></td>
                            <td>{{ $order->customer_name ?? $order->customer?->name ?? '—' }}</td>
                            <td dir="ltr" style="font-family:monospace;font-size:11px">{{ $order->phone ?? '—' }}</td>
                            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">
                                @if($order->items->count())
                                    {{ $order->items->pluck('title')->take(2)->implode('، ') }}
                                    @if($order->items->count() > 2) +{{ $order->items->count() - 2 }} @endif
                                @else — @endif
                            </td>
                            <td>{{ \App\Support\PersianNumber::toFa($order->insurance ?? 0) }}</td>
                            <td>
                                @php $st = ['pending'=>['📝','ثبت سفارش'],'final-check'=>['🔍','چک نهایی'],'courier'=>['🚚','تحویل مامور']][$order->status ?? 'pending'] ?? ['📝','ثبت']; @endphp
                                <span class="sg-status-badge {{ $order->status ?? 'pending' }}" wire:click="cycleStatus({{ $order->id }})">
                                    {{ $st[0] }} {{ $st[1] }}
                                </span>
                            </td>
                            <td>
                                @if($order->channel)
                                    <span class="sg-channel-cell {{ $order->channel->slug ?? 'default' }}">{{ $order->channel->icon ?? '' }} {{ $order->channel->name }}</span>
                                @else — @endif
                            </td>
                            <td style="font-size:10.5px">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})" class="sg-action-btn view" title="نمایش">👁️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: {{ $order->id }}})" class="sg-action-btn edit" title="ویرایش">✏️</button>
                                    <button wire:click="delete({{ $order->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="10"><div style="text-align:center;padding:40px;color:var(--text-light)"><div style="font-size:44px;opacity:.5">📦</div><p>سفارشی نیست</p></div></td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:14px">{{ $orders->links() }}</div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۲) ORDER FORM MODAL — کامل
# ═══════════════════════════════════════════════════════════════
ORDER_FORM = r'''<?php
namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Attributes\On;
use Livewire\Component;

class FormModal extends Component
{
    public bool $show = false;
    public ?int $orderId = null;
    public string $mode = 'create';

    public string $customerName = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public ?int $customerId = null;

    public array $items = [];
    public array $phoneSuggestions = [];
    public array $skuSuggestions = [];

    public string $insurance = '0';
    public string $discount = '0';
    public string $shipping = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public string $notes = '';

    public int $activeSkuIndex = -1;

    #[On('open-order-form')]
    public function open(?int $orderId = null): void
    {
        $this->resetForm();
        $this->orderId = $orderId;
        $this->mode = $orderId ? 'edit' : 'create';

        if ($orderId) {
            $o = Order::with('items')->find($orderId);
            if ($o) {
                $this->customerId = $o->customer_id;
                $this->customerName = $o->customer_name ?? '';
                $this->phone = $o->phone ?? '';
                $this->postalCode = $o->postal_code ?? '';
                $this->address = $o->address ?? '';
                $this->insurance = (string)($o->insurance ?? 0);
                $this->discount = (string)($o->discount ?? 0);
                $this->shipping = (string)($o->shipping ?? 0);
                $this->status = $o->status ?? 'pending';
                $this->channelId = $o->channel_id;
                $this->notes = $o->notes ?? '';
                $this->items = $o->items->map(fn($i) => [
                    'title' => $i->title,
                    'sku' => $i->sku ?? '',
                    'price' => (float)$i->price,
                    'quantity' => (int)$i->quantity,
                    'certificate_needed' => (bool)$i->certificate_needed,
                ])->toArray();
            }
        }

        if (empty($this->items)) $this->addItem();

        $this->show = true;
    }

    public function close(): void { $this->show = false; $this->resetForm(); }

    public function resetForm(): void
    {
        $this->orderId = null;
        $this->customerId = null;
        $this->customerName = '';
        $this->phone = '';
        $this->postalCode = '';
        $this->address = '';
        $this->items = [];
        $this->insurance = '0';
        $this->discount = '0';
        $this->shipping = '0';
        $this->status = 'pending';
        $this->channelId = null;
        $this->notes = '';
        $this->activeSkuIndex = -1;
        $this->skuSuggestions = [];
        $this->phoneSuggestions = [];
    }

    /* ═══ Items ═══ */
    public function addItem(): void
    {
        $this->items[] = ['title'=>'', 'sku'=>'', 'price'=>0, 'quantity'=>1, 'certificate_needed'=>false];
    }

    public function removeItem(int $idx): void
    {
        unset($this->items[$idx]);
        $this->items = array_values($this->items);
        if (empty($this->items)) $this->addItem();
        $this->autoInsurance();
    }

    public function updatedItems(): void { $this->autoInsurance(); }

    /* ═══ Insurance auto = total / 1,000,000 ═══ */
    public function autoInsurance(): void
    {
        $total = collect($this->items)->sum(fn($i) => (float)($i['price'] ?? 0) * (int)($i['quantity'] ?? 1));
        if ($total > 0) {
            $this->insurance = (string) floor($total / 1000000);
        }
    }

    /* ═══ Phone Search ═══ */
    public function updatedPhone(): void
    {
        $q = preg_replace('/\D/', '', $this->phone);
        if (strlen($q) < 3) { $this->phoneSuggestions = []; return; }

        $this->phoneSuggestions = Customer::where('phone', 'like', "%{$q}%")
            ->orWhere('name', 'like', "%{$this->phone}%")
            ->limit(8)->get()
            ->map(fn($c) => [
                'id' => $c->id,
                'name' => $c->name,
                'phone' => $c->phone,
                'address' => $c->address ?? '',
                'postal_code' => $c->postal_code ?? '',
                'orders_count' => $c->orders()->count(),
            ])->toArray();
    }

    public function selectPhoneSuggestion(int $customerId): void
    {
        $c = Customer::find($customerId);
        if (!$c) return;
        $this->customerId = $c->id;
        $this->customerName = $c->name;
        $this->phone = $c->phone;
        $this->address = $c->address ?? '';
        $this->postalCode = $c->postal_code ?? '';
        $this->phoneSuggestions = [];
    }

    /* ═══ SKU Search ═══ */
    public function updatedItemsSku($value, $key): void
    {
        $parts = explode('.', $key);
        $idx = (int)($parts[0] ?? -1);
        if ($idx < 0) return;

        $q = trim($value);
        if (strlen($q) < 2) { $this->skuSuggestions = []; $this->activeSkuIndex = -1; return; }

        $this->activeSkuIndex = $idx;
        $this->skuSuggestions = Product::where('is_active', true)
            ->where(function($qq) use ($q) {
                $qq->where('sku', 'like', "%{$q}%")
                   ->orWhere('name', 'like', "%{$q}%");
            })
            ->limit(10)->get()
            ->map(fn($p) => [
                'id' => $p->id, 'sku' => $p->sku, 'name' => $p->name,
                'price' => (float)$p->price, 'stock' => $p->stock_quantity,
                'image' => $p->image_src,
            ])->toArray();
    }

    public function selectSkuProduct(int $productId): void
    {
        $p = Product::find($productId);
        if (!$p || $this->activeSkuIndex < 0) return;
        $this->items[$this->activeSkuIndex]['sku'] = $p->sku;
        $this->items[$this->activeSkuIndex]['title'] = $p->name;
        $this->items[$this->activeSkuIndex]['price'] = (float)$p->price;
        $this->skuSuggestions = [];
        $this->activeSkuIndex = -1;
        $this->autoInsurance();
    }

    /* ═══ Computed ═══ */
    public function getSubtotalProperty(): float {
        return collect($this->items)->sum(fn($i) => (float)($i['price'] ?? 0) * (int)($i['quantity'] ?? 1));
    }
    public function getTotalProperty(): float {
        return max(0, $this->subtotal + (float)$this->insurance + (float)$this->shipping - (float)$this->discount);
    }

    /* ═══ Save ═══ */
    public function save(): void
    {
        $this->validate([
            'phone' => 'required|string|max:20',
            'customerName' => 'required|string|max:120',
            'items' => 'required|array|min:1',
            'items.*.title' => 'required|string|max:255',
        ]);

        // مشتری
        $customer = $this->customerId ? Customer::find($this->customerId) : null;
        if (!$customer) {
            $customer = Customer::firstOrCreate(
                ['phone' => preg_replace('/\D/', '', $this->phone)],
                ['name' => $this->customerName, 'address' => $this->address, 'postal_code' => $this->postalCode]
            );
        }
        $customer->update([
            'name' => $this->customerName,
            'address' => $this->address,
            'postal_code' => $this->postalCode,
        ]);

        // سفارش
        $data = [
            'customer_id' => $customer->id,
            'customer_name' => $this->customerName,
            'phone' => $this->phone,
            'address' => $this->address,
            'postal_code' => $this->postalCode,
            'status' => $this->status,
            'channel_id' => $this->channelId,
            'insurance' => (float)$this->insurance,
            'discount' => (float)$this->discount,
            'shipping' => (float)$this->shipping,
            'amount' => $this->total,
            'notes' => $this->notes,
        ];

        if ($this->orderId) {
            $order = Order::find($this->orderId);
            $order->update($data);
            $order->items()->delete();
        } else {
            $data['order_number'] = Order::generateNumber();
            $order = Order::create($data);
        }

        foreach ($this->items as $it) {
            $order->items()->create([
                'product_id' => null,
                'sku' => $it['sku'] ?? null,
                'title' => $it['title'],
                'price' => (float)$it['price'],
                'quantity' => (int)$it['quantity'],
                'certificate_needed' => !empty($it['certificate_needed']),
            ]);
        }

        $this->dispatch('order-saved', orderId: $order->id);
        $this->dispatch('notify', type: 'success', message: $this->orderId ? 'ویرایش شد ✅' : 'ثبت شد ✅');
        $this->close();
    }

    public function render() {
        return view('livewire.orders.form-modal', [
            'channels' => Channel::all(),
        ]);
    }
}
'''

ORDER_FORM_BLADE = r'''<div>
@if($show)
<div class="sg-modal-overlay active" wire:key="ofm-{{ $orderId ?? 'new' }}" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:880px">
        <div class="sg-modal-header">
            <h2>{{ $mode === 'edit' ? '✏️ ویرایش سفارش #'.$orderId : '📦 سفارش جدید' }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">
            {{-- مشتری --}}
            <div class="form-group">
                <label>📱 تلفن *</label>
                <input type="text" wire:model.live.debounce.400ms="phone" class="form-control" dir="ltr" autocomplete="off">
                @if(!empty($phoneSuggestions))
                    <div class="sg-phone-suggestions show">
                        @foreach($phoneSuggestions as $s)
                            <div class="sg-phone-suggestion" wire:click="selectPhoneSuggestion({{ $s['id'] }})">
                                <div style="flex:1">
                                    <div class="name">{{ $s['name'] }}</div>
                                    <div class="phone">{{ $s['phone'] }}</div>
                                </div>
                                @if($s['orders_count'] > 0)
                                    <span style="background:rgba(201,168,76,.15);color:var(--gold-dark);padding:2px 8px;border-radius:8px;font-size:10.5px;font-weight:700">
                                        {{ \App\Support\PersianNumber::toFa($s['orders_count']) }} سفارش
                                    </span>
                                @endif
                            </div>
                        @endforeach
                    </div>
                @endif
            </div>

            <div class="form-row cols-2">
                <div class="form-group">
                    <label>👤 نام *</label>
                    <input type="text" wire:model="customerName" class="form-control">
                </div>
                <div class="form-group">
                    <label>📮 کدپستی</label>
                    <input type="text" wire:model="postalCode" class="form-control" dir="ltr">
                </div>
            </div>

            <div class="form-group">
                <label>📍 آدرس</label>
                <textarea wire:model="address" class="form-control" rows="2"></textarea>
            </div>

            {{-- محصولات --}}
            <div style="border-top:2px solid var(--border);padding-top:14px;margin-top:14px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                    <label style="font-weight:700;font-size:13px;color:var(--primary)">🛍️ محصولات</label>
                    <button type="button" wire:click="addItem" class="btn btn-outline btn-sm">➕ افزودن</button>
                </div>

                @foreach($items as $i => $item)
                    <div class="sg-product-row" wire:key="item-{{ $i }}">
                        {{-- SKU --}}
                        <div class="sg-sku-wrap">
                            <label>SKU (جستجو)</label>
                            <input type="text" wire:model.live.debounce.400ms="items.{{ $i }}.sku"
                                   class="form-control" dir="ltr" autocomplete="off" placeholder="SKU یا نام...">
                            @if($activeSkuIndex === $i && !empty($skuSuggestions))
                                <div class="sg-sku-suggestions show">
                                    @foreach($skuSuggestions as $p)
                                        <div class="sg-sku-suggestion" wire:click="selectSkuProduct({{ $p['id'] }})">
                                            <div class="info">
                                                <div class="title">{{ $p['name'] }}</div>
                                                <div class="sku-txt">{{ $p['sku'] }}</div>
                                            </div>
                                            <div class="price">{{ number_format($p['price']) }} ت</div>
                                        </div>
                                    @endforeach
                                </div>
                            @endif
                        </div>

                        {{-- Title --}}
                        <div class="form-group" style="margin:0;padding-top:6px">
                            <label>عنوان *</label>
                            <input type="text" wire:model="items.{{ $i }}.title" class="form-control">
                        </div>

                        {{-- Price --}}
                        <div class="form-group" style="margin:0;padding-top:6px">
                            <label>قیمت</label>
                            <input type="number" wire:model.live="items.{{ $i }}.price" class="form-control" dir="ltr">
                        </div>

                        {{-- Qty --}}
                        <div class="form-group" style="margin:0;padding-top:6px">
                            <label>تعداد</label>
                            <input type="number" wire:model.live="items.{{ $i }}.quantity" class="form-control" min="1" dir="ltr">
                        </div>

                        {{-- Cert --}}
                        <label style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;padding-top:12px;cursor:pointer">
                            <input type="checkbox" wire:model="items.{{ $i }}.certificate_needed" style="width:22px;height:22px;accent-color:var(--gold)">
                            <span style="font-size:10px;font-weight:700;color:var(--text-light)">شناسنامه</span>
                        </label>

                        {{-- Remove --}}
                        <button type="button" wire:click="removeItem({{ $i }})"
                                style="background:var(--danger);color:#fff;border:none;border-radius:10px;height:42px;width:42px;cursor:pointer;margin-top:6px">✕</button>
                    </div>
                @endforeach

                {{-- Total --}}
                <div style="display:flex;justify-content:space-between;padding:12px 16px;background:linear-gradient(135deg,rgba(201,168,76,.12),rgba(201,168,76,.05));border:2px solid var(--gold);border-radius:12px;margin-top:10px;font-weight:700;font-size:13.5px">
                    <span>💰 جمع کل:</span>
                    <span>{{ number_format($this->total) }} تومان</span>
                </div>
            </div>

            {{-- مالی --}}
            <div class="form-row cols-3" style="margin-top:14px">
                <div class="form-group">
                    <label>💰 بیمه (خودکار)</label>
                    <input type="text" wire:model="insurance" class="form-control" dir="ltr">
                </div>
                <div class="form-group">
                    <label>📦 ارسال</label>
                    <input type="text" wire:model="shipping" class="form-control" dir="ltr">
                </div>
                <div class="form-group">
                    <label>🏷️ تخفیف</label>
                    <input type="text" wire:model="discount" class="form-control" dir="ltr">
                </div>
            </div>

            <div class="form-row cols-2">
                <div class="form-group">
                    <label>🚦 وضعیت</label>
                    <select wire:model="status" class="form-control">
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>🌐 کانال</label>
                    <select wire:model="channelId" class="form-control">
                        <option value="">— انتخاب —</option>
                        @foreach($channels as $ch)
                            <option value="{{ $ch->id }}">{{ $ch->icon ?? '' }} {{ $ch->name }}</option>
                        @endforeach
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>📝 یادداشت</label>
                <textarea wire:model="notes" class="form-control" rows="2"></textarea>
            </div>
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline">انصراف</button>
            <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                <span wire:loading.remove wire:target="save">✅ {{ $mode === 'edit' ? 'ویرایش' : 'ثبت' }}</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
@endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) ORDER VIEW MODAL
# ═══════════════════════════════════════════════════════════════
ORDER_VIEW = r'''<?php
namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?Order $order = null;

    #[On('open-order-view')]
    public function open(int $orderId): void
    {
        $this->order = Order::with(['customer','items','channel'])->find($orderId);
        if ($this->order) $this->show = true;
    }

    public function close(): void { $this->show = false; $this->order = null; }

    public function editOrder(): void
    {
        $id = $this->order->id;
        $this->close();
        $this->dispatch('open-order-form', orderId: $id);
    }

    public function cycleStatus(): void
    {
        if (!$this->order) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($this->order->status, $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $this->order->update(['status' => $next]);
        $this->order->refresh();
        $this->dispatch('notify', type: 'success', message: 'وضعیت تغییر کرد');
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
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:620px">
        <div class="sg-modal-header">
            <h2>📋 سفارش #{{ $order->order_number }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">
            {{-- Status + Channel --}}
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px">
                @php $st = ['pending'=>['📝','ثبت سفارش'],'final-check'=>['🔍','چک نهایی'],'courier'=>['🚚','تحویل مامور']][$order->status ?? 'pending'] ?? ['📝','ثبت']; @endphp
                <button wire:click="cycleStatus" class="sg-status-badge {{ $order->status }}" style="border:none">
                    {{ $st[0] }} {{ $st[1] }} <span style="opacity:.6;font-size:9px">↻</span>
                </button>
                @if($order->channel)
                    <span class="sg-channel-cell {{ $order->channel->slug ?? 'default' }}">{{ $order->channel->icon ?? '' }} {{ $order->channel->name }}</span>
                @endif
            </div>

            {{-- Customer --}}
            <div style="background:rgba(13,148,136,.05);padding:12px;border-radius:10px;margin-bottom:12px">
                <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:4px">👤 مشتری</div>
                <div style="font-weight:700;font-size:14px">{{ $order->customer_name ?? '—' }}</div>
                <div style="font-family:monospace;font-size:11.5px;opacity:.7;margin-top:2px" dir="ltr">{{ $order->phone ?? '—' }}</div>
            </div>

            {{-- Address --}}
            @if($order->address)
                <div style="background:rgba(0,0,0,.03);padding:10px;border-radius:10px;margin-bottom:12px">
                    <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:4px">📍 آدرس</div>
                    <div style="font-size:12px;line-height:1.6">{{ $order->address }}</div>
                    @if($order->postal_code)
                        <div style="font-family:monospace;font-size:10.5px;opacity:.6;margin-top:4px">📮 {{ $order->postal_code }}</div>
                    @endif
                </div>
            @endif

            {{-- Items --}}
            @if($order->items->count())
                <div style="margin-bottom:12px">
                    <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:6px">🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})</div>
                    <div style="border:1px solid var(--border);border-radius:10px;overflow:hidden">
                        @foreach($order->items as $item)
                            <div style="padding:8px 10px;border-bottom:1px solid var(--border);display:flex;gap:8px;align-items:center;font-size:12px">
                                <div style="flex:1">
                                    <div style="font-weight:700">{{ $item->title }}</div>
                                    @if($item->sku) <div style="font-family:monospace;font-size:10px;opacity:.5" dir="ltr">{{ $item->sku }}</div> @endif
                                </div>
                                <div style="opacity:.6">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                                <div style="font-weight:700;font-family:monospace">{{ number_format($item->price) }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- Totals --}}
            <div style="background:rgba(13,148,136,.05);padding:12px;border-radius:10px">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
                    <span style="opacity:.7">💰 بیمه:</span>
                    <span style="font-family:monospace">{{ number_format($order->insurance ?? 0) }}</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
                    <span style="opacity:.7">📦 ارسال:</span>
                    <span style="font-family:monospace">{{ number_format($order->shipping ?? 0) }}</span>
                </div>
                @if(($order->discount ?? 0) > 0)
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;color:var(--warn)">
                        <span>🏷️ تخفیف:</span>
                        <span style="font-family:monospace">- {{ number_format($order->discount) }}</span>
                    </div>
                @endif
                <div style="display:flex;justify-content:space-between;border-top:2px solid rgba(13,148,136,.2);padding-top:6px;margin-top:6px;font-weight:700">
                    <span>💵 نهایی:</span>
                    <span style="font-family:monospace;color:var(--primary)">{{ number_format($order->amount ?? 0) }} ت</span>
                </div>
            </div>

            @if($order->notes)
                <div style="background:rgba(0,0,0,.03);padding:10px;border-radius:10px;margin-top:12px">
                    <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:4px">📝 یادداشت</div>
                    <div style="font-size:12px">{{ $order->notes }}</div>
                </div>
            @endif
        </div>

        <div class="sg-modal-footer">
            <button wire:click="deleteOrder" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">🗑️</button>
            <div style="display:flex;gap:6px">
                <button wire:click="close" class="btn btn-outline btn-sm">بستن</button>
                <button wire:click="editOrder" class="btn btn-primary btn-sm">✏️ ویرایش</button>
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۴) CUSTOMERS Index + Profile
# ═══════════════════════════════════════════════════════════════
CUSTOMERS_INDEX = r'''<?php
namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';
    public string $filter = '';

    public function updatingSearch() { $this->resetPage(); }
    public function updatingFilter() { $this->resetPage(); }

    public function delete(int $id) {
        Customer::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() {
        $customers = Customer::query()
            ->withCount('orders')
            ->when($this->search, function($q) {
                $q->where(function($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filter === 'has_orders', fn($q) => $q->has('orders'))
            ->when($this->filter === 'no_orders', fn($q) => $q->doesntHave('orders'))
            ->latest('id')->paginate(20);

        return view('livewire.customers.index', compact('customers'))
            ->layout('components.layouts.app');
    }
}
'''

CUSTOMERS_INDEX_BLADE = r'''<div>
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..." class="form-control" style="width:220px">
            <select wire:model.live="filter" class="form-control" style="width:auto;display:inline-block">
                <option value="">همه</option>
                <option value="has_orders">با سفارش</option>
                <option value="no_orders">بدون سفارش</option>
            </select>
        </div>
        <a href="{{ route('customers.create') }}" wire:navigate class="btn btn-primary">➕ مشتری جدید</a>
    </div>

    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>👥 مشتریان <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($customers->total()) }}</span></h2>
        </div>
        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead><tr><th>#</th><th>نام</th><th>تلفن</th><th>کدپستی</th><th>سفارشات</th><th>عملیات</th></tr></thead>
                <tbody>
                    @forelse($customers as $c)
                        <tr wire:key="c-{{ $c->id }}">
                            <td><span class="sg-row-num">{{ \App\Support\PersianNumber::toFa($loop->iteration) }}</span></td>
                            <td><strong>{{ $c->name ?? '—' }}</strong></td>
                            <td dir="ltr" style="font-family:monospace;font-size:11px">{{ $c->phone ?? '—' }}</td>
                            <td dir="ltr">{{ $c->postal_code ?? '—' }}</td>
                            <td>{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <a href="{{ route('customers.show', $c) }}" wire:navigate class="sg-action-btn view">👁️</a>
                                    <a href="{{ route('customers.edit', $c) }}" wire:navigate class="sg-action-btn edit">✏️</a>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="6"><div style="text-align:center;padding:40px;color:var(--text-light)"><div style="font-size:44px;opacity:.5">👥</div><p>مشتری‌ای نیست</p></div></td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:14px">{{ $customers->links() }}</div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۵) CERTIFICATES Index
# ═══════════════════════════════════════════════════════════════
CERTS_INDEX = r'''<?php
namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';

    public function updatingSearch() { $this->resetPage(); }

    public function delete(int $id) {
        Certificate::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() {
        $certificates = Certificate::query()
            ->when($this->search, function($q) {
                $q->where('code', 'like', "%{$this->search}%")
                  ->orWhere('sku', 'like', "%{$this->search}%")
                  ->orWhere('stone_name', 'like', "%{$this->search}%");
            })
            ->latest('id')->paginate(20);

        return view('livewire.certificates.index', compact('certificates'))
            ->layout('components.layouts.app');
    }
}
'''

CERTS_INDEX_BLADE = r'''<div>
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 کد/SKU/سنگ..." class="form-control" style="width:220px">
        </div>
        <div style="display:flex;gap:6px">
            <a href="{{ route('certificates.designer') }}" wire:navigate class="btn btn-secondary btn-sm">🎨 ویرایشگر</a>
            <a href="{{ route('certificates.create') }}" wire:navigate class="btn btn-primary">➕ شناسنامه جدید</a>
        </div>
    </div>

    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>💎 شناسنامه‌ها <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($certificates->total()) }}</span></h2>
        </div>
        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead><tr><th>#</th><th>کد</th><th>تصویر</th><th>سنگ</th><th>فلز</th><th>ابعاد</th><th>وزن</th><th>تاریخ</th><th>عملیات</th></tr></thead>
                <tbody>
                    @forelse($certificates as $c)
                        <tr wire:key="cert-{{ $c->id }}">
                            <td><span class="sg-row-num">{{ \App\Support\PersianNumber::toFa($loop->iteration) }}</span></td>
                            <td><strong>{{ $c->code }}</strong>@if($c->sku)<div style="font-size:10px;opacity:.6;direction:ltr">{{ $c->sku }}</div>@endif</td>
                            <td>
                                @if($c->display_image)
                                    <img src="{{ $c->display_image }}" style="width:38px;height:38px;object-fit:cover;border-radius:8px;border:2px solid var(--border)">
                                @else
                                    <div style="width:38px;height:38px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center">💎</div>
                                @endif
                            </td>
                            <td><span style="background:var(--bg);padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600">{{ $c->stone_name }}</span></td>
                            <td>{{ $c->metal_en ?? $c->metal }}</td>
                            <td>{{ $c->length_clean }}×{{ $c->width_clean }}</td>
                            <td>{{ $c->weight_clean }}</td>
                            <td style="font-size:10.5px">{{ \App\Support\PersianDate::format($c->issued_at ?? $c->created_at, 'Y/m/d') }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <a href="{{ route('certificates.show', $c) }}" wire:navigate class="sg-action-btn view">👁️</a>
                                    <a href="{{ route('certificates.designer', $c) }}" wire:navigate class="sg-action-btn edit">🎨</a>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="9"><div style="text-align:center;padding:40px;color:var(--text-light)"><div style="font-size:44px;opacity:.5">💎</div><p>شناسنامه‌ای نیست</p></div></td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:14px">{{ $certificates->links() }}</div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۶) DASHBOARD
# ═══════════════════════════════════════════════════════════════
DASHBOARD = r'''<?php
namespace App\Livewire;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Component;

class Dashboard extends Component
{
    public function render() {
        $stats = [
            'orders' => Order::count(),
            'orders_today' => Order::whereDate('created_at', today())->count(),
            'orders_pending' => Order::where('status', 'pending')->count(),
            'orders_final' => Order::where('status', 'final-check')->count(),
            'orders_courier' => Order::where('status', 'courier')->count(),
            'customers' => Customer::count(),
            'products' => Product::count(),
            'certificates' => Certificate::count(),
        ];

        // Recent orders
        $recent = Order::latest('id')->limit(10)->get();

        // Daily chart (7 days)
        $daily = [];
        for ($i = 6; $i >= 0; $i--) {
            $d = now()->subDays($i);
            $daily[] = [
                'date' => \App\Support\PersianDate::format($d, 'm/d'),
                'count' => Order::whereDate('created_at', $d)->count(),
            ];
        }

        return view('livewire.dashboard', compact('stats', 'recent', 'daily'))
            ->layout('components.layouts.app');
    }
}
'''

DASHBOARD_BLADE = r'''<div style="padding:0 18px 18px">
    <h1 style="font-size:20px;font-weight:700;margin-bottom:14px">🏠 داشبورد</h1>

    {{-- KPI Cards --}}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:16px">
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">📦</div>
            <div style="font-size:22px;font-weight:800;color:var(--primary);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">کل سفارشات</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">🆕</div>
            <div style="font-size:22px;font-weight:800;color:var(--success);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders_today']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">امروز</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">⏳</div>
            <div style="font-size:22px;font-weight:800;color:var(--warn);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders_pending']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">در انتظار</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">🚚</div>
            <div style="font-size:22px;font-weight:800;color:var(--gold-dark);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders_courier']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">تحویل مامور</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">👥</div>
            <div style="font-size:22px;font-weight:800;color:var(--primary);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['customers']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">مشتریان</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">💎</div>
            <div style="font-size:22px;font-weight:800;color:var(--primary);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['certificates']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">شناسنامه</div>
        </div>
    </div>

    {{-- Chart --}}
    <div class="sg-settings-card" style="margin-bottom:16px">
        <h3>📈 روند ۷ روز اخیر</h3>
        @php $max = collect($daily)->max('count') ?: 1; @endphp
        <div style="display:flex;align-items:flex-end;gap:6px;height:140px;padding-top:10px">
            @foreach($daily as $d)
                <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px">
                    <div style="font-size:10px;font-weight:700;color:var(--primary)">{{ $d['count'] ?: '' }}</div>
                    <div style="width:100%;background:linear-gradient(to top, #14b8a6, #0891b2);border-radius:6px 6px 0 0;transition:all .3s" style="height:{{ max(4, $d['count']/$max*100) }}%"></div>
                    <div style="font-size:9px;font-family:monospace;opacity:.6">{{ $d['date'] }}</div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- Recent --}}
    <div class="sg-settings-card">
        <h3>🕐 آخرین سفارشات</h3>
        @forelse($recent as $o)
            <div style="padding:10px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:8px;font-size:12px">
                <div>
                    <strong>#{{ $o->order_number }}</strong> — {{ $o->customer_name ?? '—' }}
                    <div style="font-size:10px;opacity:.5;font-family:monospace" dir="ltr">{{ $o->phone }}</div>
                </div>
                <div style="text-align:left">
                    <div style="font-weight:700;font-family:monospace">{{ number_format($o->amount ?? 0) }}</div>
                    <div style="font-size:10px;opacity:.5">{{ \App\Support\PersianDate::format($o->created_at, 'Y/m/d') }}</div>
                </div>
            </div>
        @empty
            <p style="text-align:center;padding:20px;opacity:.5">سفارشی نیست</p>
        @endforelse
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Port کامل Legacy → Laravel — قسمت ۱                         ║")
    print("║  Orders + Customers + Certs + Dashboard                       ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    for rel in [
        "app/Livewire/Orders/Index.php",
        "app/Livewire/Orders/FormModal.php",
        "app/Livewire/Orders/ViewModal.php",
        "app/Livewire/Customers/Index.php",
        "app/Livewire/Certificates/Index.php",
        "app/Livewire/Dashboard.php",
    ]: backup(rel)

    print("\n📄 نوشتن فایل‌ها...")

    # Orders
    write("app/Livewire/Orders/Index.php", ORDERS_INDEX)
    write("resources/views/livewire/orders/index.blade.php", ORDERS_INDEX_BLADE)
    write("app/Livewire/Orders/FormModal.php", ORDER_FORM)
    write("resources/views/livewire/orders/form-modal.blade.php", ORDER_FORM_BLADE)
    write("app/Livewire/Orders/ViewModal.php", ORDER_VIEW)
    write("resources/views/livewire/orders/view-modal.blade.php", ORDER_VIEW_BLADE)

    # Customers
    write("app/Livewire/Customers/Index.php", CUSTOMERS_INDEX)
    write("resources/views/livewire/customers/index.blade.php", CUSTOMERS_INDEX_BLADE)

    # Certificates
    write("app/Livewire/Certificates/Index.php", CERTS_INDEX)
    write("resources/views/livewire/certificates/index.blade.php", CERTS_INDEX_BLADE)

    # Dashboard
    write("app/Livewire/Dashboard.php", DASHBOARD)
    write("resources/views/livewire/dashboard.blade.php", DASHBOARD_BLADE)

    print("\n" + "═" * 64)
    print("✅ قسمت ۱ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan view:clear
  php artisan route:clear

  # سرور رو ببند و دوباره باز کن
  php artisan serve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی این قسمت اضافه شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Orders Index کامل:
     • جستجو + فیلتر وضعیت + فیلتر کانال
     • چک‌باکس انتخاب چندتایی
     • Bulk Actions (تغییر وضعیت، حذف)
     • کلیک روی Badge وضعیت → تغییر سریع
     • کلیک روی 👁️ → Modal View
     • کلیک روی ✏️ → Modal Edit

  ✅ Order Form Modal:
     • جستجوی تلفن با پیشنهاد مشتری (خودکار از DB)
     • SKU Search در هر ردیف محصول (خودکار از DB)
     • بیمه خودکار (مبلغ/1,000,000)
     • 3 ستون قیمت/تعداد/شناسنامه
     • کانال + وضعیت + یادداشت
     • جمع کل live

  ✅ Order View Modal:
     • نمایش کامل سفارش
     • تغییر وضعیت inline
     • ویرایش + حذف

  ✅ Customers Index:
     • جستجو + فیلتر (با/بدون سفارش)
     • نمایش کامل با سفارشات

  ✅ Certificates Index:
     • نمایش تصویر + سنگ + فلز + ابعاد
     • لینک به Designer

  ✅ Dashboard:
     • 6 کارت KPI
     • نمودار 7 روزه
     • آخرین سفارشات

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 قسمت‌های بعدی:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ۲) Certificates Create + Designer + Preview + Print
  ۳) Settings کامل (10 تب) + Stones/Metals
  ۴) CSV Import (Order/Customer/Mahak) + Label Print
  ۵) Backup/Restore + Reports پیشرفته

الان این قسمت رو تست کن و بگو:
   • کدوم کار می‌کنه ✅
   • کدوم خطا می‌ده ❌
""")

if __name__ == "__main__":
    main()
