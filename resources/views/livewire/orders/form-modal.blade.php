<div>
@if($show)
<div class="sg-modal-overlay active" wire:key="ofm-{{ $orderId ?? 'new' }}" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:900px">
        <div class="sg-modal-header">
            <h2>{{ $mode === 'edit' ? '✏️ ویرایش سفارش #'.$orderId : '📦 سفارش جدید' }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">

            {{-- ═══ اطلاعات مشتری ═══ --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border)">
                👤 اطلاعات مشتری
            </div>

            <div class="form-grid">
                <div class="field col-6" style="position:relative">
                    <label>📱 تلفن <span class="req">*</span></label>
                    <input type="text" wire:model.live.debounce.400ms="phone" dir="ltr" autocomplete="off" placeholder="09151234567" />
                    @if(!empty($phoneSuggestions))
                        <div style="position:absolute;top:100%;right:0;left:0;margin-top:4px;background:var(--bg-card);border:2px solid var(--gold);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.15);z-index:50;max-height:240px;overflow-y:auto">
                            @foreach($phoneSuggestions as $s)
                                <div wire:click="selectPhoneSuggestion({{ $s['id'] }})"
                                     style="padding:10px 12px;cursor:pointer;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:8px;align-items:center">
                                    <div style="flex:1;min-width:0">
                                        <div style="font-weight:700;font-size:12px">{{ $s['name'] }}</div>
                                        <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $s['phone'] }}</div>
                                    </div>
                                    @if($s['orders_count'] > 0)
                                        <span style="background:rgba(201,168,76,.15);color:var(--gold-dark);padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700">
                                            {{ \App\Support\PersianNumber::toFa($s['orders_count']) }}
                                        </span>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    @endif
                </div>

                <div class="field col-6">
                    <label>👤 نام مشتری <span class="req">*</span></label>
                    <input type="text" wire:model="customerName" />
                </div>

                <div class="field col-8">
                    <label>📍 آدرس</label>
                    <input type="text" wire:model="address" />
                </div>

                <div class="field col-4">
                    <label>📮 کدپستی</label>
                    <input type="text" wire:model="postalCode" dir="ltr" />
                </div>
            </div>

            {{-- ═══ محصولات ═══ --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:14px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
                <span>🛍️ محصولات</span>
                <button type="button" wire:click="addItem" class="btn btn-outline btn-sm">➕ افزودن</button>
            </div>

            @foreach($items as $i => $item)
                <div class="order-item-row" wire:key="item-{{ $i }}">
                    <button type="button" class="remove-btn" wire:click="removeItem({{ $i }})">✕</button>

                    {{-- SKU --}}
                    <div class="field" style="position:relative">
                        <label>SKU</label>
                        <input type="text" wire:model.live.debounce.400ms="items.{{ $i }}.sku" dir="ltr" autocomplete="off" placeholder="جستجو...">
                        @if($activeSkuIndex === $i && !empty($skuSuggestions))
                            <div style="position:absolute;top:100%;right:0;left:0;margin-top:4px;background:var(--bg-card);border:2px solid var(--gold);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.15);z-index:60;max-height:240px;overflow-y:auto">
                                @foreach($skuSuggestions as $p)
                                    <div wire:click="selectSkuProduct({{ $p['id'] }})"
                                         style="padding:8px 10px;cursor:pointer;border-bottom:1px solid var(--border);font-size:11px">
                                        <div style="font-weight:700">{{ $p['name'] }}</div>
                                        <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $p['sku'] }}</div>
                                    </div>
                                @endforeach
                            </div>
                        @endif
                    </div>

                    {{-- Title --}}
                    <div class="field">
                        <label>عنوان <span class="req">*</span></label>
                        <input type="text" wire:model="items.{{ $i }}.title">
                    </div>

                    {{-- Price --}}
                    <div class="field">
                        <label>قیمت</label>
                        <input type="number" wire:model.live="items.{{ $i }}.price" dir="ltr" min="0">
                    </div>

                    {{-- Qty --}}
                    <div class="field">
                        <label>تعداد</label>
                        <input type="number" wire:model.live="items.{{ $i }}.quantity" dir="ltr" min="1">
                    </div>

                    {{-- Cert --}}
                    <div class="field">
                        <label>شناسنامه</label>
                        <label style="display:flex;align-items:center;justify-content:center;height:36px;cursor:pointer;background:var(--bg-soft);border-radius:8px">
                            <input type="checkbox" wire:model="items.{{ $i }}.certificate_needed" style="width:20px;height:20px;accent-color:var(--gold)">
                        </label>
                    </div>

                    {{-- Spacer --}}
                    <div></div>
                </div>
            @endforeach

            {{-- جمع کل --}}
            <div style="display:flex;justify-content:space-between;padding:12px 16px;background:linear-gradient(135deg,rgba(201,168,76,.12),rgba(201,168,76,.05));border:2px solid var(--gold);border-radius:12px;margin-top:10px;font-weight:700">
                <span>💰 جمع کل:</span>
                <span style="font-family:monospace">{{ number_format($this->total) }} تومان</span>
            </div>

            {{-- ═══ مالی ═══ --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:16px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border)">
                💰 اطلاعات مالی
            </div>

            <div class="form-grid">
                <div class="field col-3">
                    <label>💰 بیمه</label>
                    <input type="text" wire:model="insurance" dir="ltr">
                </div>
                <div class="field col-3">
                    <label>📦 ارسال</label>
                    <input type="text" wire:model="shipping" dir="ltr">
                </div>
                <div class="field col-3">
                    <label>🏷️ تخفیف</label>
                    <input type="text" wire:model="discount" dir="ltr">
                </div>
                <div class="field col-3">
                    <label>🚦 وضعیت</label>
                    <select wire:model="status">
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
                <div class="field col-6">
                    <label>🌐 کانال</label>
                    <select wire:model="channelId">
                        <option value="">— انتخاب —</option>
                        @foreach($channels as $ch)
                            <option value="{{ $ch->id }}">{{ $ch->icon ?? '' }} {{ $ch->name }}</option>
                        @endforeach
                    </select>
                </div>
                <div class="field col-6">
                    <label>📝 یادداشت</label>
                    <input type="text" wire:model="notes">
                </div>
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
