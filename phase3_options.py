#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  ShopGun V2 — گزینه ۱+۲+۳                                    ║
║  ۱) Order Form با CustomerPicker + ProductPicker              ║
║  ۲) Customer Profile با چند تلفن/آدرس                        ║
║  ۳) Customer Show کامل                                        ║
╚══════════════════════════════════════════════════════════════╝
"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌ مسیر پیدا نشد"); exit(1)

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
# ۱) Order FormModal — نسخه کامل با Pickers
# ═══════════════════════════════════════════════════════════════
ORDER_FORM_MODAL_PHP = r'''<?php

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
    public string $mode = 'create'; // create | edit

    /* ─── اطلاعات مشتری ─── */
    public ?int $customerId = null;
    public string $customerName = '';
    public string $customerPhone = '';
    public string $customerAddress = '';
    public string $customerPostal = '';

    /* ─── سبد محصولات ─── */
    public array $cart = [];

    /* ─── سایر فیلدها ─── */
    public string $insurance = '0';
    public string $discount  = '0';
    public string $shipping  = '0';
    public string $status    = 'pending';
    public ?int   $channelId = null;
    public string $notes     = '';
    public bool   $invoiceNeeded = false;

    /* ─── ابعاد/متادیتا ─── */
    public array $statusOptions = [
        ['id' => 'pending',     'name' => 'ثبت سفارش',    'icon' => '📝'],
        ['id' => 'final-check', 'name' => 'چک نهایی',     'icon' => '🔍'],
        ['id' => 'courier',     'name' => 'تحویل مامور',  'icon' => '🚚'],
    ];

    protected $listeners = [
        'open-order-form'      => 'open',
        'customer-selected'    => 'onCustomerSelected',
        'customer-cleared'     => 'onCustomerCleared',
        'products-updated'     => 'onProductsUpdated',
    ];

    /* ═══════════════════════════════════════════════════════════
       باز کردن فرم
       ═══════════════════════════════════════════════════════════ */
    public function open(?int $orderId = null): void
    {
        $this->resetForm();

        if ($orderId) {
            $this->mode = 'edit';
            $this->orderId = $orderId;
            $this->loadOrder($orderId);
        } else {
            $this->mode = 'create';
            $this->orderId = null;
            $this->dispatch('customer-picker-set', id: null);
            $this->dispatch('product-picker-set', cart: []);
        }

        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->customerId = null;
        $this->customerName = '';
        $this->customerPhone = '';
        $this->customerAddress = '';
        $this->customerPostal = '';
        $this->cart = [];
        $this->insurance = '0';
        $this->discount = '0';
        $this->shipping = '0';
        $this->status = 'pending';
        $this->channelId = null;
        $this->notes = '';
        $this->invoiceNeeded = false;
    }

    protected function loadOrder(int $orderId): void
    {
        $o = Order::with(['items', 'customer'])->find($orderId);
        if (!$o) return;

        $this->customerId = $o->customer_id;
        $this->customerName = $o->customer_name ?? $o->customer?->name ?? '';
        $this->customerPhone = $o->phone ?? '';
        $this->customerAddress = $o->address ?? '';
        $this->customerPostal = $o->postal_code ?? '';
        $this->insurance = (string) ($o->insurance ?? 0);
        $this->discount  = (string) ($o->discount ?? 0);
        $this->shipping  = (string) ($o->shipping ?? 0);
        $this->status    = $o->status ?? 'pending';
        $this->channelId = $o->channel_id;
        $this->notes     = $o->notes ?? '';
        $this->invoiceNeeded = (bool) $o->invoice_needed;

        // پر کردن سبد
        $this->cart = [];
        foreach ($o->items as $item) {
            $this->cart[] = [
                'product_id' => $item->product_id,
                'sku'        => $item->sku ?? '',
                'title'      => $item->name ?? $item->title ?? '',
                'price'      => (float) $item->price,
                'qty'        => (int) $item->quantity,
                'certNeeded' => (bool) $item->certificate_needed,
                'image'      => null,
            ];
        }

        // ارسال به pickerها
        $this->dispatch('customer-picker-set', id: $this->customerId);
        $this->dispatch('product-picker-set', cart: $this->cart);
    }

    /* ═══════════════════════════════════════════════════════════
       رویدادها از Pickers
       ═══════════════════════════════════════════════════════════ */
    public function onCustomerSelected(int $customerId, array $data): void
    {
        $this->customerId = $customerId;
        $this->customerName = $data['name'] ?? '';
        $this->customerPhone = $data['phone'] ?? '';
        $this->customerAddress = $data['address'] ?? '';
        $this->customerPostal = $data['postal_code'] ?? '';
    }

    public function onCustomerCleared(): void
    {
        $this->customerId = null;
        $this->customerName = '';
        $this->customerPhone = '';
        $this->customerAddress = '';
        $this->customerPostal = '';
    }

    public function onProductsUpdated(array $cart): void
    {
        $this->cart = $cart;
    }

    /* ═══════════════════════════════════════════════════════════
       محاسبه‌ها
       ═══════════════════════════════════════════════════════════ */
    public function getSubtotalProperty(): float
    {
        $s = 0;
        foreach ($this->cart as $it) {
            $s += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }
        return $s;
    }

    public function getInsuranceAmountProperty(): float
    {
        return (float) preg_replace('/[^\d.]/', '', $this->insurance ?: '0');
    }

    public function getDiscountAmountProperty(): float
    {
        return (float) preg_replace('/[^\d.]/', '', $this->discount ?: '0');
    }

    public function getShippingAmountProperty(): float
    {
        return (float) preg_replace('/[^\d.]/', '', $this->shipping ?: '0');
    }

    public function getTotalProperty(): float
    {
        return max(0, $this->subtotal
            + $this->insurance_amount
            + $this->shipping_amount
            - $this->discount_amount);
    }

    /* ═══════════════════════════════════════════════════════════
       ذخیره
       ═══════════════════════════════════════════════════════════ */
    public function save()
    {
        $rules = [
            'customerPhone'    => 'required|string|max:20',
            'customerName'     => 'required|string|max:120',
            'customerAddress'  => 'nullable|string|max:500',
            'customerPostal'   => 'nullable|string|max:20',
            'status'           => 'required|in:pending,final-check,courier',
            'cart'             => 'required|array|min:1',
            'insurance'        => 'nullable',
            'discount'         => 'nullable',
            'shipping'         => 'nullable',
        ];

        $this->validate($rules, [], [
            'customerPhone'   => 'تلفن',
            'customerName'    => 'نام مشتری',
            'customerAddress' => 'آدرس',
            'customerPostal'  => 'کدپستی',
            'status'          => 'وضعیت',
            'cart'            => 'سبد محصولات',
        ]);

        // پیدا یا ساخت مشتری
        $customer = null;
        if ($this->customerId) {
            $customer = Customer::find($this->customerId);
        }
        if (!$customer) {
            $customer = Customer::findByPhone($this->customerPhone);
        }
        if (!$customer) {
            $customer = Customer::create([
                'name'        => $this->customerName,
                'phone'       => Customer::normalizePhone($this->customerPhone),
                'address'     => $this->customerAddress,
                'postal_code' => $this->customerPostal,
            ]);
            $customer->addPhone($this->customerPhone, 'اصلی', true);
            if ($this->customerAddress || $this->customerPostal) {
                $customer->addAddress([
                    'address'     => $this->customerAddress,
                    'postal_code' => $this->customerPostal,
                ], true);
            }
        }

        // ذخیره/آپدیت سفارش
        $orderData = [
            'customer_id'    => $customer->id,
            'customer_name'  => $this->customerName,
            'phone'          => Customer::normalizePhone($this->customerPhone),
            'address'        => $this->customerAddress,
            'postal_code'    => $this->customerPostal,
            'status'         => $this->status,
            'channel_id'     => $this->channelId,
            'insurance'      => $this->insurance_amount,
            'discount'       => $this->discount_amount,
            'shipping'       => $this->shipping_amount,
            'amount'         => $this->total,
            'notes'          => $this->notes,
            'invoice_needed' => $this->invoiceNeeded,
        ];

        if ($this->orderId) {
            $order = Order::find($this->orderId);
            $order->update($orderData);
            $order->items()->delete();
        } else {
            $orderData['order_number'] = Order::generateNumber();
            $order = Order::create($orderData);
        }

        // ذخیره آیتم‌ها
        foreach ($this->cart as $it) {
            $order->items()->create([
                'product_id'          => $it['product_id'] ?? null,
                'sku'                 => $it['sku'] ?? null,
                'name'                => $it['title'] ?? '—',
                'price'               => (float) ($it['price'] ?? 0),
                'quantity'            => (int) ($it['qty'] ?? 1),
                'certificate_needed'  => !empty($it['certNeeded']),
            ]);
        }

        $this->dispatch('order-saved', orderId: $order->id);
        $this->dispatch('notify', type: 'success',
            message: $this->orderId ? 'سفارش ویرایش شد ✅' : 'سفارش ثبت شد ✅');

        $this->close();
    }

    public function render()
    {
        return view('livewire.orders.form-modal', [
            'channels' => Channel::orderBy('id')->get(),
            'subtotal' => $this->subtotal,
            'insuranceAmount' => $this->insurance_amount,
            'discountAmount'  => $this->discount_amount,
            'shippingAmount'  => $this->shipping_amount,
            'total'           => $this->total,
        ]);
    }
}
'''

ORDER_FORM_MODAL_BLADE = r'''<div>
    @if($show)
    <div class="fixed inset-0 z-[80] flex items-start justify-center p-3 md:p-4 overflow-y-auto"
         @keydown.escape.window="$wire.close()">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md" wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-4xl my-4 md:my-8 border border-base-300">

            {{-- ═══ Header ═══ --}}
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-cyan-500/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg flex items-center justify-center text-white shadow"
                         style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                        {{ $mode === 'edit' ? '✏️' : '📦' }}
                    </div>
                    <div>
                        <h2 class="font-bold text-base">
                            {{ $mode === 'edit' ? 'ویرایش سفارش' : 'سفارش جدید' }}
                        </h2>
                        <div class="text-xs text-base-content/60">
                            {{ $mode === 'edit' ? '#'.$orderId : 'ثبت سفارش جدید' }}
                        </div>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            {{-- ═══ Body ═══ --}}
            <div class="p-4 md:p-5 space-y-5 max-h-[calc(100vh-13rem)] overflow-y-auto">

                {{-- ═══ بخش ۱: مشتری ═══ --}}
                <section class="card bg-base-100 border border-base-300">
                    <div class="card-body p-3 md:p-4">
                        <h3 class="font-bold text-sm mb-3 flex items-center gap-2">
                            <span class="badge badge-primary badge-sm">۱</span>
                            👤 مشتری
                        </h3>
                        <livewire:components.customer-picker
                            :customer-id="$customerId"
                            event-prefix="customer"
                            :key="'cp-' . ($orderId ?? 'new')" />
                    </div>
                </section>

                {{-- ═══ بخش ۲: محصولات ═══ --}}
                <section class="card bg-base-100 border border-base-300">
                    <div class="card-body p-3 md:p-4">
                        <h3 class="font-bold text-sm mb-3 flex items-center gap-2">
                            <span class="badge badge-primary badge-sm">۲</span>
                            🛍️ محصولات
                        </h3>
                        <livewire:components.product-picker
                            :cart="$cart"
                            event-prefix="products"
                            :key="'pp-' . ($orderId ?? 'new')" />
                    </div>
                </section>

                {{-- ═══ بخش ۳: مالی + وضعیت ═══ --}}
                <section class="card bg-base-100 border border-base-300">
                    <div class="card-body p-3 md:p-4">
                        <h3 class="font-bold text-sm mb-3 flex items-center gap-2">
                            <span class="badge badge-primary badge-sm">۳</span>
                            💰 مالی و وضعیت
                        </h3>

                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <div>
                                <label class="text-[11px] font-bold text-base-content/60">💰 بیمه</label>
                                <input type="text" wire:model.live.debounce.300ms="insurance" dir="ltr"
                                       class="input input-bordered input-sm w-full font-mono text-center">
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-base-content/60">📦 ارسال</label>
                                <input type="text" wire:model.live.debounce.300ms="shipping" dir="ltr"
                                       class="input input-bordered input-sm w-full font-mono text-center">
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-base-content/60">🏷️ تخفیف</label>
                                <input type="text" wire:model.live.debounce.300ms="discount" dir="ltr"
                                       class="input input-bordered input-sm w-full font-mono text-center">
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-base-content/60">🚦 وضعیت</label>
                                <select wire:model="status" class="select select-bordered select-sm w-full">
                                    @foreach($statusOptions as $s)
                                        <option value="{{ $s['id'] }}">{{ $s['icon'] }} {{ $s['name'] }}</option>
                                    @endforeach
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                            <div>
                                <label class="text-[11px] font-bold text-base-content/60">🌐 کانال فروش</label>
                                <select wire:model="channelId" class="select select-bordered select-sm w-full">
                                    <option value="">— انتخاب —</option>
                                    @foreach($channels as $ch)
                                        <option value="{{ $ch->id }}">{{ $ch->name }}</option>
                                    @endforeach
                                </select>
                            </div>
                            <div class="flex items-end">
                                <label class="flex items-center gap-2 cursor-pointer p-2 bg-base-200/50 rounded-lg w-full">
                                    <input type="checkbox" wire:model="invoiceNeeded"
                                           class="checkbox checkbox-sm checkbox-primary">
                                    <span class="text-xs font-bold">📄 فاکتور لازم است</span>
                                </label>
                            </div>
                        </div>

                        <div class="mt-3">
                            <label class="text-[11px] font-bold text-base-content/60">📝 یادداشت</label>
                            <textarea wire:model="notes" rows="2"
                                      class="textarea textarea-bordered textarea-sm w-full"
                                      placeholder="یادداشت داخلی..."></textarea>
                        </div>
                    </div>
                </section>

                {{-- ═══ جمع کل ═══ --}}
                <div class="bg-gradient-to-l from-primary/10 to-transparent border-2 border-primary/30 rounded-xl p-4">
                    <div class="space-y-1.5 text-sm">
                        <div class="flex justify-between">
                            <span class="text-base-content/60">جمع محصولات:</span>
                            <span class="font-mono">{{ number_format($subtotal) }} ت</span>
                        </div>
                        @if($insuranceAmount > 0)
                            <div class="flex justify-between">
                                <span class="text-base-content/60">💰 بیمه:</span>
                                <span class="font-mono">{{ number_format($insuranceAmount) }} ت</span>
                            </div>
                        @endif
                        @if($shippingAmount > 0)
                            <div class="flex justify-between">
                                <span class="text-base-content/60">📦 ارسال:</span>
                                <span class="font-mono">{{ number_format($shippingAmount) }} ت</span>
                            </div>
                        @endif
                        @if($discountAmount > 0)
                            <div class="flex justify-between text-warning">
                                <span>🏷️ تخفیف:</span>
                                <span class="font-mono">- {{ number_format($discountAmount) }} ت</span>
                            </div>
                        @endif
                        <div class="flex justify-between border-t-2 border-primary/30 pt-2 mt-2">
                            <span class="font-bold">💵 مبلغ نهایی:</span>
                            <span class="font-bold text-primary text-lg font-mono">{{ number_format($total) }} تومان</span>
                        </div>
                    </div>
                </div>
            </div>

            {{-- ═══ Footer ═══ --}}
            <div class="p-4 border-t border-base-300 flex items-center justify-between gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="close" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled"
                        class="btn btn-success btn-sm md:btn-md">
                    <span wire:loading.remove wire:target="save">
                        ✅ {{ $mode === 'edit' ? 'ویرایش' : 'ثبت سفارش' }}
                    </span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۲) Customer ProfileModal — چند تلفن/آدرس
# ═══════════════════════════════════════════════════════════════

CUSTOMER_PROFILE_MODAL_PHP = r'''<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use App\Models\CustomerAddress;
use App\Models\CustomerPhone;
use Livewire\Attributes\On;
use Livewire\Component;

class ProfileModal extends Component
{
    public bool $show = false;
    public ?int $customerId = null;
    public ?Customer $customer = null;

    public string $tab = 'info'; // info | phones | addresses | orders

    /** فرم افزودن شماره جدید */
    public bool $addingPhone = false;
    public string $newPhone = '';
    public string $newPhoneLabel = '';

    /** فرم افزودن آدرس جدید */
    public bool $addingAddress = false;
    public array $newAddress = [
        'label' => '', 'province' => '', 'city' => '',
        'address' => '', 'postal_code' => '',
    ];

    /** فرم ویرایش اطلاعات پایه */
    public bool $editingInfo = false;
    public string $editName = '';
    public string $editEmail = '';

    protected $listeners = ['open-customer-profile' => 'open'];

    /* ═══════════════════════════════════════════════════════════ */

    public function open(int $customerId): void
    {
        $this->customerId = $customerId;
        $this->loadCustomer();
        $this->tab = 'info';
        $this->show = true;
    }

    public function openByPhone(string $phone): void
    {
        $c = Customer::findByPhone($phone);
        if (!$c) {
            $this->dispatch('notify', type: 'error', message: 'مشتری پیدا نشد');
            return;
        }
        $this->open($c->id);
    }

    public function loadCustomer(): void
    {
        if (!$this->customerId) return;
        $this->customer = Customer::with([
            'phones', 'addresses',
            'orders' => fn($q) => $q->latest()->limit(20),
        ])->find($this->customerId);

        if ($this->customer) {
            $this->editName  = $this->customer->name ?? '';
            $this->editEmail = $this->customer->email ?? '';
        }
    }

    public function close(): void
    {
        $this->show = false;
        $this->customerId = null;
        $this->customer = null;
        $this->resetForms();
    }

    protected function resetForms(): void
    {
        $this->tab = 'info';
        $this->addingPhone = false;
        $this->newPhone = '';
        $this->newPhoneLabel = '';
        $this->addingAddress = false;
        $this->newAddress = ['label' => '', 'province' => '', 'city' => '', 'address' => '', 'postal_code' => ''];
        $this->editingInfo = false;
    }

    /* ═══════════════════════════════════════════════════════════
       تلفن‌ها
       ═══════════════════════════════════════════════════════════ */
    public function startAddPhone(): void
    {
        $this->addingPhone = true;
        $this->newPhone = '';
        $this->newPhoneLabel = '';
    }

    public function cancelAddPhone(): void
    {
        $this->addingPhone = false;
    }

    public function savePhone(): void
    {
        $this->validate([
            'newPhone' => 'required|string|min:10|max:20',
        ], [], ['newPhone' => 'شماره تلفن']);

        if (!$this->customer) return;

        $cp = $this->customer->addPhone($this->newPhone, $this->newPhoneLabel ?: null, false);
        if ($cp) {
            $this->addingPhone = false;
            $this->loadCustomer();
            $this->dispatch('notify', type: 'success', message: 'شماره اضافه شد ✅');
        }
    }

    public function setPrimaryPhone(int $phoneId): void
    {
        if (!$this->customer) return;
        $this->customer->phones()->update(['is_primary' => false]);
        CustomerPhone::where('id', $phoneId)
            ->where('customer_id', $this->customer->id)
            ->update(['is_primary' => true]);

        // همگام‌سازی فیلد قدیمی
        $primary = $this->customer->phones()->where('is_primary', true)->first();
        if ($primary) $this->customer->update(['phone' => $primary->phone]);

        $this->loadCustomer();
    }

    public function deletePhone(int $phoneId): void
    {
        if (!$this->customer) return;
        $cp = CustomerPhone::where('id', $phoneId)
            ->where('customer_id', $this->customer->id)
            ->first();

        if (!$cp) return;
        if ($this->customer->phones()->count() <= 1) {
            $this->dispatch('notify', type: 'error', message: 'حداقل یک شماره باید باشد');
            return;
        }

        $wasPrimary = $cp->is_primary;
        $cp->delete();

        if ($wasPrimary) {
            $next = $this->customer->phones()->first();
            if ($next) {
                $next->update(['is_primary' => true]);
                $this->customer->update(['phone' => $next->phone]);
            }
        }

        $this->loadCustomer();
        $this->dispatch('notify', type: 'success', message: 'شماره حذف شد');
    }

    /* ═══════════════════════════════════════════════════════════
       آدرس‌ها
       ═══════════════════════════════════════════════════════════ */
    public function startAddAddress(): void
    {
        $this->addingAddress = true;
        $this->newAddress = ['label' => '', 'province' => '', 'city' => '', 'address' => '', 'postal_code' => ''];
    }

    public function cancelAddAddress(): void
    {
        $this->addingAddress = false;
    }

    public function saveAddress(): void
    {
        $this->validate([
            'newAddress.address' => 'required|string|max:500',
        ], [], ['newAddress.address' => 'آدرس']);

        if (!$this->customer) return;

        $this->customer->addAddress([
            'label'       => $this->newAddress['label'] ?: null,
            'province'    => $this->newAddress['province'] ?: null,
            'city'        => $this->newAddress['city'] ?: null,
            'address'     => $this->newAddress['address'],
            'postal_code' => $this->newAddress['postal_code'] ?: null,
        ], false);

        $this->addingAddress = false;
        $this->loadCustomer();
        $this->dispatch('notify', type: 'success', message: 'آدرس اضافه شد ✅');
    }

    public function setPrimaryAddress(int $addressId): void
    {
        if (!$this->customer) return;
        $this->customer->addresses()->update(['is_primary' => false]);
        CustomerAddress::where('id', $addressId)
            ->where('customer_id', $this->customer->id)
            ->update(['is_primary' => true]);

        // همگام‌سازی
        $primary = $this->customer->addresses()->where('is_primary', true)->first();
        if ($primary) {
            $this->customer->update([
                'address'     => $primary->address,
                'postal_code' => $primary->postal_code,
            ]);
        }

        $this->loadCustomer();
    }

    public function deleteAddress(int $addressId): void
    {
        if (!$this->customer) return;
        $ca = CustomerAddress::where('id', $addressId)
            ->where('customer_id', $this->customer->id)
            ->first();
        if (!$ca) return;

        $wasPrimary = $ca->is_primary;
        $ca->delete();

        if ($wasPrimary) {
            $next = $this->customer->addresses()->first();
            if ($next) {
                $next->update(['is_primary' => true]);
                $this->customer->update([
                    'address'     => $next->address,
                    'postal_code' => $next->postal_code,
                ]);
            }
        }

        $this->loadCustomer();
        $this->dispatch('notify', type: 'success', message: 'آدرس حذف شد');
    }

    /* ═══════════════════════════════════════════════════════════
       ویرایش اطلاعات پایه
       ═══════════════════════════════════════════════════════════ */
    public function startEditInfo(): void
    {
        $this->editingInfo = true;
    }

    public function cancelEditInfo(): void
    {
        $this->editingInfo = false;
        $this->loadCustomer();
    }

    public function saveInfo(): void
    {
        if (!$this->customer) return;
        $this->validate([
            'editName'  => 'required|string|max:120',
            'editEmail' => 'nullable|email|max:150',
        ], [], ['editName' => 'نام', 'editEmail' => 'ایمیل']);

        $this->customer->update([
            'name'  => $this->editName,
            'email' => $this->editEmail ?: null,
        ]);
        $this->editingInfo = false;
        $this->loadCustomer();
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
    }

    public function render()
    {
        return view('livewire.customers.profile-modal');
    }
}
'''

CUSTOMER_PROFILE_MODAL_BLADE = r'''<div>
    @if($show && $customer)
    <div class="fixed inset-0 z-[85] flex items-start justify-center p-3 md:p-4 overflow-y-auto"
         @keydown.escape.window="$wire.close()">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md" wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-4 md:my-8 border border-base-300">

            {{-- ═══ Header ═══ --}}
            <div class="p-4 border-b border-base-300 bg-gradient-to-l from-cyan-500/10 to-transparent rounded-t-2xl">
                <div class="flex items-start justify-between gap-3">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-full flex items-center justify-center text-white text-lg font-bold shadow"
                             style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                            {{ mb_substr($customer->name ?? '?', 0, 1) }}
                        </div>
                        <div class="flex-1 min-w-0">
                            <h2 class="font-bold text-base truncate">{{ $customer->name }}</h2>
                            <div class="text-xs text-base-content/60 font-mono" dir="ltr">
                                {{ $customer->primaryPhone()?->formatted ?? $customer->phone ?? '—' }}
                            </div>
                        </div>
                    </div>
                    <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
                </div>

                {{-- آمار سریع --}}
                <div class="grid grid-cols-3 gap-2 mt-3">
                    <div class="bg-base-200/50 rounded-lg p-2 text-center">
                        <div class="text-lg font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->orders->count()) }}</div>
                        <div class="text-[10px] text-base-content/60">سفارش</div>
                    </div>
                    <div class="bg-base-200/50 rounded-lg p-2 text-center">
                        <div class="text-lg font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->phones->count()) }}</div>
                        <div class="text-[10px] text-base-content/60">تلفن</div>
                    </div>
                    <div class="bg-base-200/50 rounded-lg p-2 text-center">
                        <div class="text-lg font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->addresses->count()) }}</div>
                        <div class="text-[10px] text-base-content/60">آدرس</div>
                    </div>
                </div>
            </div>

            {{-- ═══ Tabs ═══ --}}
            <div class="flex border-b border-base-300 bg-base-200/30 px-2 overflow-x-auto">
                @foreach([
                    'info'      => ['ℹ️', 'اطلاعات'],
                    'phones'    => ['📱', 'تلفن‌ها'],
                    'addresses' => ['📍', 'آدرس‌ها'],
                    'orders'    => ['📦', 'سفارشات'],
                ] as $key => $meta)
                    <button wire:click="$set('tab','{{ $key }}')"
                            class="px-4 py-2 text-xs font-bold whitespace-nowrap border-b-2 transition
                                   {{ $tab === $key ? 'border-primary text-primary' : 'border-transparent text-base-content/60 hover:text-base-content' }}">
                        {{ $meta[0] }} {{ $meta[1] }}
                    </button>
                @endforeach
            </div>

            {{-- ═══ Body ═══ --}}
            <div class="p-4 max-h-[calc(100vh-20rem)] overflow-y-auto">

                {{-- ═══ Tab: اطلاعات ═══ --}}
                @if($tab === 'info')
                    <div class="space-y-3">
                        @if($editingInfo)
                            <div class="bg-primary/5 border border-primary/30 rounded-lg p-3 space-y-2">
                                <div>
                                    <label class="text-[11px] font-bold">نام</label>
                                    <input type="text" wire:model="editName"
                                           class="input input-bordered input-sm w-full">
                                    @error('editName') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                                </div>
                                <div>
                                    <label class="text-[11px] font-bold">ایمیل</label>
                                    <input type="email" wire:model="editEmail" dir="ltr"
                                           class="input input-bordered input-sm w-full">
                                    @error('editEmail') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                                </div>
                                <div class="flex gap-2">
                                    <button wire:click="saveInfo" class="btn btn-success btn-sm flex-1">✅ ذخیره</button>
                                    <button wire:click="cancelEditInfo" class="btn btn-ghost btn-sm">انصراف</button>
                                </div>
                            </div>
                        @else
                            <div class="flex justify-end">
                                <button wire:click="startEditInfo" class="btn btn-outline btn-xs">✏️ ویرایش</button>
                            </div>
                        @endif

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div class="p-3 rounded-lg bg-base-200/50">
                                <div class="text-[10px] text-base-content/60">👤 نام</div>
                                <div class="font-bold mt-0.5">{{ $customer->name }}</div>
                            </div>
                            <div class="p-3 rounded-lg bg-base-200/50">
                                <div class="text-[10px] text-base-content/60">📧 ایمیل</div>
                                <div class="mt-0.5" dir="ltr">{{ $customer->email ?? '—' }}</div>
                            </div>
                            <div class="p-3 rounded-lg bg-base-200/50">
                                <div class="text-[10px] text-base-content/60">📅 عضویت</div>
                                <div class="mt-0.5 text-xs">{{ \App\Support\PersianDate::format($customer->created_at, 'Y/m/d') }}</div>
                            </div>
                            <div class="p-3 rounded-lg bg-base-200/50">
                                <div class="text-[10px] text-base-content/60">🕐 آخرین به‌روزرسانی</div>
                                <div class="mt-0.5 text-xs">{{ \App\Support\PersianDate::format($customer->updated_at, 'Y/m/d H:i') }}</div>
                            </div>
                        </div>

                        <a href="{{ route('customers.show', $customer) }}"
                           class="btn btn-outline btn-sm w-full">
                            👁️ صفحه کامل مشتری
                        </a>
                    </div>
                @endif

                {{-- ═══ Tab: تلفن‌ها ═══ --}}
                @if($tab === 'phones')
                    <div class="space-y-2">
                        @if($addingPhone)
                            <div class="bg-primary/5 border border-primary/30 rounded-lg p-3 space-y-2">
                                <div class="text-xs font-bold text-primary mb-1">➕ شماره جدید</div>
                                <div class="grid grid-cols-2 gap-2">
                                    <input type="text" wire:model="newPhone" dir="ltr" placeholder="09151531301"
                                           class="input input-bordered input-sm font-mono">
                                    <input type="text" wire:model="newPhoneLabel" placeholder="برچسب (منزل، کار)"
                                           class="input input-bordered input-sm">
                                </div>
                                @error('newPhone') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                                <div class="flex gap-2">
                                    <button wire:click="savePhone" class="btn btn-success btn-sm flex-1">✅ ذخیره</button>
                                    <button wire:click="cancelAddPhone" class="btn btn-ghost btn-sm">انصراف</button>
                                </div>
                            </div>
                        @else
                            <button wire:click="startAddPhone" class="btn btn-outline btn-sm w-full">
                                ➕ افزودن شماره جدید
                            </button>
                        @endif

                        @forelse($customer->phones as $phone)
                            <div class="flex items-center gap-2 p-3 rounded-lg border {{ $phone->is_primary ? 'border-success/50 bg-success/5' : 'border-base-300' }}"
                                 wire:key="ph-{{ $phone->id }}">
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center gap-2">
                                        @if($phone->is_primary)
                                            <span class="badge badge-success badge-xs">اصلی</span>
                                        @endif
                                        @if($phone->label)
                                            <span class="badge badge-ghost badge-xs">{{ $phone->label }}</span>
                                        @endif
                                    </div>
                                    <div class="font-mono text-sm mt-1" dir="ltr">{{ $phone->formatted }}</div>
                                </div>
                                <div class="flex gap-1">
                                    @if(!$phone->is_primary)
                                        <button wire:click="setPrimaryPhone({{ $phone->id }})"
                                                class="btn btn-ghost btn-xs" title="تعیین اصلی">
                                            ⭐
                                        </button>
                                    @endif
                                    <button wire:click="deletePhone({{ $phone->id }})"
                                            wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error" title="حذف">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        @empty
                            <div class="text-center py-6 text-sm text-base-content/50">
                                شماره‌ای ثبت نشده
                            </div>
                        @endforelse
                    </div>
                @endif

                {{-- ═══ Tab: آدرس‌ها ═══ --}}
                @if($tab === 'addresses')
                    <div class="space-y-2">
                        @if($addingAddress)
                            <div class="bg-primary/5 border border-primary/30 rounded-lg p-3 space-y-2">
                                <div class="text-xs font-bold text-primary mb-1">➕ آدرس جدید</div>
                                <div class="grid grid-cols-3 gap-2">
                                    <input type="text" wire:model="newAddress.label" placeholder="برچسب"
                                           class="input input-bordered input-sm">
                                    <input type="text" wire:model="newAddress.province" placeholder="استان"
                                           class="input input-bordered input-sm">
                                    <input type="text" wire:model="newAddress.city" placeholder="شهر"
                                           class="input input-bordered input-sm">
                                </div>
                                <textarea wire:model="newAddress.address" rows="2" placeholder="آدرس کامل..."
                                          class="textarea textarea-bordered textarea-sm w-full"></textarea>
                                @error('newAddress.address') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                                <input type="text" wire:model="newAddress.postal_code" dir="ltr" placeholder="کدپستی"
                                       class="input input-bordered input-sm font-mono">
                                <div class="flex gap-2">
                                    <button wire:click="saveAddress" class="btn btn-success btn-sm flex-1">✅ ذخیره</button>
                                    <button wire:click="cancelAddAddress" class="btn btn-ghost btn-sm">انصراف</button>
                                </div>
                            </div>
                        @else
                            <button wire:click="startAddAddress" class="btn btn-outline btn-sm w-full">
                                ➕ افزودن آدرس جدید
                            </button>
                        @endif

                        @forelse($customer->addresses as $addr)
                            <div class="p-3 rounded-lg border {{ $addr->is_primary ? 'border-success/50 bg-success/5' : 'border-base-300' }}"
                                 wire:key="addr-{{ $addr->id }}">
                                <div class="flex items-start justify-between gap-2">
                                    <div class="flex-1 min-w-0">
                                        <div class="flex items-center gap-2 mb-1">
                                            @if($addr->is_primary)
                                                <span class="badge badge-success badge-xs">اصلی</span>
                                            @endif
                                            @if($addr->label)
                                                <span class="badge badge-ghost badge-xs">{{ $addr->label }}</span>
                                            @endif
                                        </div>
                                        @if($addr->city || $addr->province)
                                            <div class="text-xs text-base-content/70">
                                                📍 {{ implode('، ', array_filter([$addr->city, $addr->province])) }}
                                            </div>
                                        @endif
                                        <div class="text-sm mt-1">{{ $addr->address }}</div>
                                        @if($addr->postal_code)
                                            <div class="text-xs font-mono text-base-content/60 mt-1" dir="ltr">
                                                📮 {{ $addr->postal_code }}
                                            </div>
                                        @endif
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        @if(!$addr->is_primary)
                                            <button wire:click="setPrimaryAddress({{ $addr->id }})"
                                                    class="btn btn-ghost btn-xs" title="تعیین اصلی">⭐</button>
                                        @endif
                                        <button wire:click="deleteAddress({{ $addr->id }})"
                                                wire:confirm="حذف شود؟"
                                                class="btn btn-ghost btn-xs text-error" title="حذف">🗑️</button>
                                    </div>
                                </div>
                            </div>
                        @empty
                            <div class="text-center py-6 text-sm text-base-content/50">
                                آدرسی ثبت نشده
                            </div>
                        @endforelse
                    </div>
                @endif

                {{-- ═══ Tab: سفارشات ═══ --}}
                @if($tab === 'orders')
                    <div class="space-y-2">
                        @forelse($customer->orders as $order)
                            <a href="{{ route('orders.show', $order) }}"
                               class="block p-3 rounded-lg border border-base-300 hover:border-primary/50 hover:bg-primary/5 transition"
                               wire:key="ord-{{ $order->id }}">
                                <div class="flex items-center justify-between">
                                    <div class="font-bold text-sm">#{{ $order->order_number ?? $order->id }}</div>
                                    <div class="text-xs text-base-content/60">
                                        {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}
                                    </div>
                                </div>
                                <div class="text-xs text-base-content/60 mt-1">
                                    💰 {{ number_format((float) ($order->amount ?? 0)) }} ت
                                </div>
                            </a>
                        @empty
                            <div class="text-center py-6 text-sm text-base-content/50">
                                سفارشی ثبت نشده
                            </div>
                        @endforelse
                    </div>
                @endif
            </div>

            {{-- ═══ Footer ═══ --}}
            <div class="p-3 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="close" class="btn btn-ghost btn-sm">بستن</button>
            </div>
        </div>
    </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Customer Show — صفحه کامل
# ═══════════════════════════════════════════════════════════════

CUSTOMER_SHOW_PHP = r'''<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Show extends Component
{
    public Customer $customer;

    public function mount(Customer $customer): void
    {
        $this->customer = $customer->load([
            'phones', 'addresses',
            'orders' => fn($q) => $q->latest(),
        ]);
    }

    public function render()
    {
        return view('livewire.customers.show')
            ->layout('components.layouts.app');
    }
}
'''

CUSTOMER_SHOW_BLADE = r'''<div class="p-4 md:p-6 max-w-5xl mx-auto space-y-4">

    {{-- Header --}}
    <div class="flex items-center gap-3">
        <a href="{{ route('customers.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">پروفایل مشتری</h1>
    </div>

    {{-- Card: مشتری --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4 md:p-5">
            <div class="flex flex-col md:flex-row items-start md:items-center gap-4">

                <div class="w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg shrink-0"
                     style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                    {{ mb_substr($customer->name ?? '?', 0, 1) }}
                </div>

                <div class="flex-1 min-w-0">
                    <h2 class="text-lg font-bold">{{ $customer->name }}</h2>
                    <div class="text-sm font-mono text-base-content/60 mt-1" dir="ltr">
                        {{ $customer->primaryPhone()?->formatted ?? $customer->phone ?? '—' }}
                    </div>
                    @if($customer->email)
                        <div class="text-xs text-base-content/60 mt-1" dir="ltr">📧 {{ $customer->email }}</div>
                    @endif
                </div>

                <div class="flex gap-2">
                    <button wire:click="$dispatch('open-order-form')"
                            class="btn btn-primary btn-sm">➕ سفارش جدید</button>
                    <a href="{{ route('customers.edit', $customer) }}"
                       class="btn btn-outline btn-sm">✏️ ویرایش</a>
                </div>
            </div>

            {{-- آمار --}}
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->orders->count()) }}</div>
                    <div class="text-xs text-base-content/60">سفارش</div>
                </div>
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->phones->count()) }}</div>
                    <div class="text-xs text-base-content/60">تلفن</div>
                </div>
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->addresses->count()) }}</div>
                    <div class="text-xs text-base-content/60">آدرس</div>
                </div>
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">
                        {{ number_format($customer->orders->sum('amount') ?? 0) }}
                    </div>
                    <div class="text-xs text-base-content/60">مجموع خرید</div>
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        {{-- تلفن‌ها --}}
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4">
                <h3 class="font-bold text-sm mb-3 flex items-center gap-2">📱 شماره تلفن‌ها</h3>
                @forelse($customer->phones as $phone)
                    <div class="flex items-center gap-2 p-2 rounded-lg {{ $phone->is_primary ? 'bg-success/5 border border-success/30' : 'bg-base-200/50' }}"
                         wire:key="ph-{{ $phone->id }}">
                        @if($phone->is_primary)
                            <span class="badge badge-success badge-xs">اصلی</span>
                        @endif
                        @if($phone->label)
                            <span class="badge badge-ghost badge-xs">{{ $phone->label }}</span>
                        @endif
                        <div class="flex-1 font-mono text-sm text-right" dir="ltr">{{ $phone->formatted }}</div>
                    </div>
                @empty
                    <div class="text-center py-4 text-sm text-base-content/50">شماره‌ای نیست</div>
                @endforelse
            </div>
        </div>

        {{-- آدرس‌ها --}}
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4">
                <h3 class="font-bold text-sm mb-3 flex items-center gap-2">📍 آدرس‌ها</h3>
                @forelse($customer->addresses as $addr)
                    <div class="p-2 rounded-lg {{ $addr->is_primary ? 'bg-success/5 border border-success/30' : 'bg-base-200/50' }}"
                         wire:key="ad-{{ $addr->id }}">
                        <div class="flex items-center gap-2 mb-1">
                            @if($addr->is_primary)
                                <span class="badge badge-success badge-xs">اصلی</span>
                            @endif
                            @if($addr->label)
                                <span class="badge badge-ghost badge-xs">{{ $addr->label }}</span>
                            @endif
                            @if($addr->city)
                                <span class="text-[10px] text-base-content/50">{{ $addr->city }}</span>
                            @endif
                        </div>
                        <div class="text-xs">{{ $addr->address }}</div>
                        @if($addr->postal_code)
                            <div class="text-[10px] font-mono text-base-content/60 mt-1" dir="ltr">📮 {{ $addr->postal_code }}</div>
                        @endif
                    </div>
                @empty
                    <div class="text-center py-4 text-sm text-base-content/50">آدرسی نیست</div>
                @endforelse
            </div>
        </div>
    </div>

    {{-- سفارشات --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h3 class="font-bold text-sm mb-3 flex items-center gap-2">
                📦 تاریخچه سفارشات
                <span class="badge badge-primary badge-sm">{{ \App\Support\PersianNumber::toFa($customer->orders->count()) }}</span>
            </h3>

            @forelse($customer->orders as $order)
                <a href="{{ route('orders.show', $order) }}"
                   class="block p-3 rounded-lg border border-base-300 hover:border-primary/50 hover:bg-primary/5 transition mb-2"
                   wire:key="ord-{{ $order->id }}">
                    <div class="flex items-center justify-between">
                        <div class="font-bold">#{{ $order->order_number ?? $order->id }}</div>
                        <div class="text-xs text-base-content/60">
                            {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}
                        </div>
                    </div>
                    <div class="flex items-center gap-3 text-xs text-base-content/60 mt-1">
                        <span>💰 {{ number_format((float) ($order->amount ?? 0)) }} ت</span>
                        @if($order->status)
                            <span class="badge badge-ghost badge-xs">{{ $order->status }}</span>
                        @endif
                    </div>
                </a>
            @empty
                <div class="text-center py-6 text-sm text-base-content/50">سفارشی ثبت نشده</div>
            @endforelse
        </div>
    </div>

    {{-- کامپوننت Profile Modal --}}
    <livewire:customers.profile-modal />
</div>
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ShopGun V2 — گزینه ۱+۲+۳                                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Backup
    print("📦 Backup...")
    for rel in [
        "app/Livewire/Orders/FormModal.php",
        "resources/views/livewire/orders/form-modal.blade.php",
        "app/Livewire/Customers/ProfileModal.php",
        "resources/views/livewire/customers/profile-modal.blade.php",
        "app/Livewire/Customers/Show.php",
        "resources/views/livewire/customers/show.blade.php",
    ]:
        backup(rel)

    # ۱) Order Form
    print("\n📄 [۱] Order FormModal...")
    write("app/Livewire/Orders/FormModal.php", ORDER_FORM_MODAL_PHP)
    write("resources/views/livewire/orders/form-modal.blade.php", ORDER_FORM_MODAL_BLADE)

    # ۲) Customer Profile
    print("\n📄 [۲] Customer ProfileModal...")
    write("app/Livewire/Customers/ProfileModal.php", CUSTOMER_PROFILE_MODAL_PHP)
    write("resources/views/livewire/customers/profile-modal.blade.php", CUSTOMER_PROFILE_MODAL_BLADE)

    # ۳) Customer Show
    print("\n📄 [۳] Customer Show...")
    write("app/Livewire/Customers/Show.php", CUSTOMER_SHOW_PHP)
    write("resources/views/livewire/customers/show.blade.php", CUSTOMER_SHOW_BLADE)

    # بررسی Order model برای متد generateNumber
    print("\n🔧 بررسی Order model...")
    order_model = PROJECT / "app/Models/Order.php"
    if order_model.exists():
        with open(order_model, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'generateNumber' not in content:
            helper = r'''

    /* ═══════════════════════════════════════════════════════════
       تولید شماره سفارش یکتا
       ═══════════════════════════════════════════════════════════ */
    public static function generateNumber(): string
    {
        $last = static::orderByDesc('id')->value('order_number');
        $num = 10000;
        if ($last && is_numeric($last)) {
            $num = ((int) $last) + 1;
        }
        while (static::where('order_number', (string) $num)->exists()) {
            $num++;
        }
        return (string) $num;
    }
'''
            idx = content.rstrip().rfind('}')
            if idx > 0:
                new_content = content[:idx] + helper + "\n}\n"
                with open(order_model, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                print("  ✓ generateNumber به Order اضافه شد")
        else:
            print("  ⏭ generateNumber موجود است")

    # بررسی Channel model
    channel_model = PROJECT / "app/Models/Channel.php"
    if not channel_model.exists():
        print("\n📄 Channel model ساخته شد")
        write("app/Models/Channel.php", r'''<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Channel extends Model
{
    protected $fillable = ['name', 'slug', 'icon', 'color', 'is_active'];
    protected $casts = ['is_active' => 'boolean'];

    public function orders()
    {
        return $this->hasMany(Order::class);
    }
}
''')

    # بررسی Customer model برای فیلد email
    print("\n🔧 بررسی Customer model برای فیلد email...")
    # بررسی از طریق مایگریشن
    migrations_dir = PROJECT / "database/migrations"
    email_exists = False
    if migrations_dir.exists():
        for mig in migrations_dir.glob("*create_customers*"):
            with open(mig, 'r', encoding='utf-8') as f:
                if 'email' in f.read():
                    email_exists = True
                    break

    if not email_exists:
        # ساخت مایگریشن برای email
        ts = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        write(f"database/migrations/{ts}_add_email_to_customers.php", r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasColumn('customers', 'email')) return;
        Schema::table('customers', function (Blueprint $table) {
            $table->string('email', 150)->nullable()->after('name');
        });
    }

    public function down(): void
    {
        Schema::table('customers', function (Blueprint $table) {
            $table->dropColumn('email');
        });
    }
};
''')

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan migrate
  php artisan view:clear
  php artisan route:clear

  ⚠️ سرور رو ببند و دوباره باز کن:
  php artisan serve

مرورگر: Ctrl+Shift+R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی ساخته شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [۱] فرم سفارش جدید (FormModal):
      • بخش مشتری → CustomerPicker (جستجوی تلفن + ایجاد سریع)
      • بخش محصولات → ProductPicker (جستجو + سبد کامل)
      • جمع کل خودکار (محصولات + بیمه + ارسال - تخفیف)

  [۲] Customer ProfileModal:
      • ۴ تب: اطلاعات / تلفن‌ها / آدرس‌ها / سفارشات
      • افزودن/حذف/تعیین اصلی برای تلفن و آدرس
      • ویرایش نام و ایمیل

  [۳] Customer Show:
      • صفحه‌ی کامل با همه اطلاعات
      • کارت آمار (سفارش/تلفن/آدرس/مجموع خرید)
      • لیست کامل تلفن‌ها و آدرس‌ها
      • تاریخچه سفارشات

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 آدرس‌های تست:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  /dev/pickers             ← تست Pickerها (از فاز ۱)
  /customers               ← لیست مشتریان
  /customers/{{id}}         ← صفحه‌ی کامل مشتری
  /orders                  ← لیست سفارشات (دکمه + جدید)

📌 نکته: اگر خطای «Column not found: email» دیدی، یعنی مایگریشن email
اجرا نشده. دوباره `php artisan migrate` بزن.
""")

if __name__ == "__main__":
    main()