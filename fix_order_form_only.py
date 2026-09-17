#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""فقط فرم سفارش - بدون CSS خارجی"""

from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

# ═══════════════════════════════════════════════════════════════
# فرم Modal سفارش — تمام inline style
# ═══════════════════════════════════════════════════════════════

ORDER_FORM_MODAL = '''<div>
@if($show)

{{-- overlay --}}
<div style="position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(6px);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:12px;overflow-y:auto" 
     wire:key="ofm-{{ $orderId ?? 'new' }}"
     @keydown.escape.window="$wire.close()">

    {{-- modal card --}}
    <div style="background:#fff;color:#2c3e50;width:100%;max-width:820px;margin:12px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden;font-family:Vazirmatn,Tahoma,sans-serif;direction:rtl">

        {{-- ═══ header ═══ --}}
        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">
                {{ $mode === 'edit' ? '✏️ ویرایش سفارش #' . $orderId : '📦 سفارش جدید' }}
            </h2>
            <button type="button" wire:click="close" 
                    style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center">
                ✕
            </button>
        </div>

        {{-- ═══ body ═══ --}}
        <div style="padding:16px 18px;max-height:calc(100vh - 200px);overflow-y:auto">

            {{-- ───── بخش ۱: مشتری ───── --}}
            <div style="margin-bottom:18px">
                <div style="font-size:13px;font-weight:700;color:#1a5276;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e2e8f0;display:flex;align-items:center;gap:6px">
                    <span style="background:#1a5276;color:#fff;width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px">1</span>
                    اطلاعات مشتری
                </div>

                <div style="display:grid;grid-template-columns:1fr;gap:10px">
                    {{-- phone --}}
                    <div style="position:relative">
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">
                            📱 تلفن <span style="color:#dc2626">*</span>
                        </label>
                        <input type="text" wire:model.live.debounce.400ms="phone" dir="ltr" autocomplete="off"
                               placeholder="09151234567"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box;outline:none" />
                        @if(!empty($phoneSuggestions))
                            <div style="position:absolute;top:100%;right:0;left:0;margin-top:4px;background:#fff;border:2px solid #c9a84c;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.15);z-index:100;max-height:220px;overflow-y:auto">
                                @foreach($phoneSuggestions as $s)
                                    <div wire:click="selectPhoneSuggestion({{ $s['id'] }})"
                                         style="padding:9px 12px;cursor:pointer;border-bottom:1px solid #f1f5f9;display:flex;justify-content:space-between;align-items:center">
                                        <div style="flex:1;min-width:0">
                                            <div style="font-weight:700;font-size:13px;color:#1e293b">{{ $s['name'] }}</div>
                                            <div style="font-family:monospace;font-size:11px;color:#64748b" dir="ltr">{{ $s['phone'] }}</div>
                                        </div>
                                        @if($s['orders_count'] > 0)
                                            <span style="background:#fef3c7;color:#b45309;padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700">
                                                {{ \App\Support\PersianNumber::toFa($s['orders_count']) }} سفارش
                                            </span>
                                        @endif
                                    </div>
                                @endforeach
                            </div>
                        @endif
                    </div>

                    <div style="display:grid;grid-template-columns:1fr;gap:10px" class="form-row-2">
                        <div>
                            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">
                                👤 نام مشتری <span style="color:#dc2626">*</span>
                            </label>
                            <input type="text" wire:model="customerName"
                                   style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:inherit;font-size:13px;background:#f8fafc;box-sizing:border-box;outline:none" />
                        </div>
                        <div>
                            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">
                                📮 کدپستی
                            </label>
                            <input type="text" wire:model="postalCode" dir="ltr"
                                   style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;outline:none" />
                        </div>
                    </div>

                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">
                            📍 آدرس
                        </label>
                        <textarea wire:model="address" rows="2"
                                  style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:inherit;font-size:13px;background:#f8fafc;box-sizing:border-box;outline:none;resize:vertical"></textarea>
                    </div>
                </div>
            </div>

            {{-- ───── بخش ۲: محصولات ───── --}}
            <div style="margin-bottom:18px">
                <div style="font-size:13px;font-weight:700;color:#1a5276;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between">
                    <div style="display:flex;align-items:center;gap:6px">
                        <span style="background:#1a5276;color:#fff;width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px">2</span>
                        محصولات
                    </div>
                    <button type="button" wire:click="addItem"
                            style="background:#f1f5f9;color:#1a5276;border:1.5px solid #cbd5e1;padding:5px 12px;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;font-family:inherit">
                        ➕ افزودن
                    </button>
                </div>

                @foreach($items as $i => $item)
                    <div wire:key="item-{{ $i }}"
                         style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:10px;margin-bottom:10px;position:relative">

                        <button type="button" wire:click="removeItem({{ $i }})"
                                wire:confirm="این ردیف حذف شود؟"
                                style="position:absolute;top:6px;left:6px;width:24px;height:24px;border-radius:50%;background:#fee2e2;color:#dc2626;border:none;cursor:pointer;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center">
                            ✕
                        </button>

                        <div style="display:grid;grid-template-columns:1fr;gap:8px" class="form-item-row">
                            <div style="position:relative">
                                <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">SKU</label>
                                <input type="text" wire:model.live.debounce.400ms="items.{{ $i }}.sku" dir="ltr" autocomplete="off" placeholder="جستجو..."
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:12px;background:#fff;box-sizing:border-box;outline:none" />
                                @if($activeSkuIndex === $i && !empty($skuSuggestions))
                                    <div style="position:absolute;top:100%;right:0;left:0;margin-top:4px;background:#fff;border:2px solid #c9a84c;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.15);z-index:100;max-height:200px;overflow-y:auto">
                                        @foreach($skuSuggestions as $p)
                                            <div wire:click="selectSkuProduct({{ $p['id'] }})"
                                                 style="padding:7px 10px;cursor:pointer;border-bottom:1px solid #f1f5f9;font-size:12px">
                                                <div style="font-weight:700">{{ $p['name'] }}</div>
                                                <div style="font-family:monospace;font-size:10px;color:#64748b" dir="ltr">{{ $p['sku'] }}</div>
                                            </div>
                                        @endforeach
                                    </div>
                                @endif
                            </div>

                            <div>
                                <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">عنوان *</label>
                                <input type="text" wire:model="items.{{ $i }}.title"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:inherit;font-size:12px;background:#fff;box-sizing:border-box;outline:none" />
                            </div>

                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                                <div>
                                    <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">قیمت</label>
                                    <input type="number" wire:model.live="items.{{ $i }}.price" dir="ltr" min="0"
                                           style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:12px;background:#fff;box-sizing:border-box;outline:none" />
                                </div>
                                <div>
                                    <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">تعداد</label>
                                    <input type="number" wire:model.live="items.{{ $i }}.quantity" dir="ltr" min="1"
                                           style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:12px;background:#fff;box-sizing:border-box;outline:none" />
                                </div>
                            </div>

                            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;background:#fff;padding:6px 10px;border-radius:6px;border:1.5px solid #cbd5e1">
                                <input type="checkbox" wire:model="items.{{ $i }}.certificate_needed"
                                       style="width:18px;height:18px;accent-color:#c9a84c" />
                                <span style="font-size:11px;font-weight:700;color:#475569">نیاز به شناسنامه</span>
                            </label>
                        </div>
                    </div>
                @endforeach

                {{-- جمع کل --}}
                <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);border:2px solid #c9a84c;border-radius:10px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;margin-top:10px">
                    <span style="font-weight:700;font-size:13px;color:#78350f">💰 جمع کل:</span>
                    <span style="font-family:monospace;font-size:15px;font-weight:800;color:#78350f">
                        {{ number_format($this->total) }} تومان
                    </span>
                </div>
            </div>

            {{-- ───── بخش ۳: مالی ───── --}}
            <div>
                <div style="font-size:13px;font-weight:700;color:#1a5276;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e2e8f0;display:flex;align-items:center;gap:6px">
                    <span style="background:#1a5276;color:#fff;width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px">3</span>
                    اطلاعات مالی و وضعیت
                </div>

                <div style="display:grid;grid-template-columns:1fr;gap:10px">
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px" class="form-money-row">
                        <div>
                            <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">💰 بیمه</label>
                            <input type="text" wire:model="insurance" dir="ltr"
                                   style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:12px;background:#f8fafc;box-sizing:border-box;outline:none" />
                        </div>
                        <div>
                            <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">📦 ارسال</label>
                            <input type="text" wire:model="shipping" dir="ltr"
                                   style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:12px;background:#f8fafc;box-sizing:border-box;outline:none" />
                        </div>
                        <div>
                            <label style="display:block;font-size:10px;font-weight:700;color:#64748b;margin-bottom:3px">🏷️ تخفیف</label>
                            <input type="text" wire:model="discount" dir="ltr"
                                   style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:12px;background:#f8fafc;box-sizing:border-box;outline:none" />
                        </div>
                    </div>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px" class="form-row-2">
                        <div>
                            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">🚦 وضعیت</label>
                            <select wire:model="status"
                                    style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:inherit;font-size:13px;background:#f8fafc;box-sizing:border-box;outline:none">
                                <option value="pending">📝 ثبت سفارش</option>
                                <option value="final-check">🔍 چک نهایی</option>
                                <option value="courier">🚚 تحویل مامور</option>
                            </select>
                        </div>
                        <div>
                            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">🌐 کانال</label>
                            <select wire:model="channelId"
                                    style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:inherit;font-size:13px;background:#f8fafc;box-sizing:border-box;outline:none">
                                <option value="">— انتخاب —</option>
                                @foreach($channels as $ch)
                                    <option value="{{ $ch->id }}">{{ $ch->icon ?? '' }} {{ $ch->name }}</option>
                                @endforeach
                            </select>
                        </div>
                    </div>

                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📝 یادداشت</label>
                        <textarea wire:model="notes" rows="2"
                                  style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:inherit;font-size:13px;background:#f8fafc;box-sizing:border-box;outline:none;resize:vertical"></textarea>
                    </div>
                </div>
            </div>
        </div>

        {{-- ═══ footer ═══ --}}
        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
            <button type="button" wire:click="close"
                    style="padding:9px 20px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-family:inherit;font-size:13px;font-weight:700;cursor:pointer">
                انصراف
            </button>
            <button type="button" wire:click="save" wire:loading.attr="disabled"
                    style="padding:9px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-family:inherit;font-size:13px;font-weight:700;cursor:pointer">
                <span wire:loading.remove wire:target="save">✅ {{ $mode === 'edit' ? 'ویرایش' : 'ثبت' }} سفارش</span>
                <span wire:loading wire:target="save">⏳ در حال ذخیره...</span>
            </button>
        </div>
    </div>
</div>

{{-- responsive: موبایل = یک ستونه، دسکتاپ = چندستونه --}}
<style>
@media (min-width: 640px) {
    .form-row-2 { grid-template-columns: 1fr 1fr !important; }
    .form-item-row { grid-template-columns: 130px 1fr 110px 80px !important; align-items: end; }
    .form-money-row { grid-template-columns: 1fr 1fr 1fr !important; }
}
.form-item-row > label { grid-column: 1 / -1; }
</style>

@endif
</div>
'''

path = ROOT / 'resources/views/livewire/orders/form-modal.blade.php'
if path.exists():
    path.rename(path.with_suffix('.blade.php.bak-' + datetime.now().strftime('%H%M%S')))

path.write_text(ORDER_FORM_MODAL, encoding='utf-8')
print("✅ فرم Modal سفارش بازنویسی شد (inline style، بخش‌بندی شده)")
print()
print("🎯 چی درست شد:")
print("   ✓ ۳ بخش: مشتری / محصولات / مالی")
print("   ✓ هر بخش با شماره و آیکون")
print("   ✓ موبایل: تک‌ستونه | دسکتاپ: چندستونه")
print("   ✓ هیچ وابستگی به CSS خارجی نداره")
print("   ✓ مودال حداکثر ۸۲۰px، کل صفحه رو نمی‌گیره")
print()
print("🚀 برای تست:")
print("   php artisan view:clear")
print("   php artisan serve")
print("   برو /orders و کلیک روی «➕ جدید»")
'''

# اجرا
exec(open(__file__).read()) if False else None

# ذخیره
import sys
sys.stdout.flush()
