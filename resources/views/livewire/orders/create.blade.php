<div class="p-4 md:p-6 max-w-4xl mx-auto" dir="rtl">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">➕ سفارش جدید</h1>
    </div>

    <div class="sg-settings-card">

        {{-- ═══ مشتری ═══ --}}
        <h3>👤 اطلاعات مشتری</h3>

        <div class="form-grid">
            <div class="field col-8">
                <label>📱 تلفن مشتری <span class="req">*</span></label>
                <livewire:components.phone-search wire:model="phone" wire:key="phone-{{ rand() }}" />
                @if($customerFound)
                    <div class="hint" style="color:var(--success)">✅ مشتری موجود — ID: {{ $existingCustomerId }}</div>
                @elseif(strlen(preg_replace('/\D/', '', $phone)) >= 10)
                    <div class="hint" style="color:var(--info)">🆕 مشتری جدید ساخته می‌شود</div>
                @endif
                @error('phone') <div class="err">{{ $message }}</div> @enderror
            </div>

            <div class="field col-4">
                <label>👤 نام</label>
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

        {{-- ═══ وضعیت و کانال ═══ --}}
        <h3 style="margin-top:20px">🚦 وضعیت و کانال</h3>

        <div class="form-grid">
            <div class="field col-6">
                <label>📊 وضعیت</label>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    @foreach(['pending' => '📝 ثبت', 'final-check' => '🔍 چک', 'courier' => '🚚 تحویل'] as $k => $v)
                        <button type="button" wire:click="$set('status', '{{ $k }}')"
                                class="btn btn-sm {{ $status === $k ? 'btn-primary' : 'btn-outline' }}">{{ $v }}</button>
                    @endforeach
                </div>
            </div>

            <div class="field col-6">
                <label>🌐 کانال</label>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    @foreach($channels as $c)
                        <button type="button" wire:click="$set('channelId', {{ $c->id }})"
                                class="btn btn-sm {{ $channelId === $c->id ? 'btn-primary' : 'btn-outline' }}">{{ $c->icon }} {{ $c->name }}</button>
                    @endforeach
                </div>
            </div>

            <div class="field col-4">
                <label>💰 بیمه</label>
                <input type="text" wire:model="insurance" dir="ltr" />
            </div>

            <div class="field col-8">
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                    <input type="checkbox" wire:model="invoiceNeeded" style="width:18px;height:18px;accent-color:var(--gold)">
                    <span>📄 نیاز به فاکتور</span>
                </label>
            </div>
        </div>

        {{-- ═══ محصولات ═══ --}}
        <h3 style="margin-top:20px;display:flex;justify-content:space-between;align-items:center">
            <span>🛍️ محصولات</span>
            <button type="button" wire:click="addItem" class="btn btn-outline btn-sm">➕ افزودن</button>
        </h3>

        @foreach($items as $idx => $it)
            <div class="order-item-row" wire:key="item-{{ $idx }}">
                <button type="button" class="remove-btn"
                        wire:click="removeItem({{ $idx }})"
                        wire:confirm="این ردیف حذف شود؟">✕</button>

                <div class="field">
                    <label>SKU</label>
                    <input type="text" wire:model="items.{{ $idx }}.sku" dir="ltr" />
                </div>

                <div class="field">
                    <label>عنوان</label>
                    <input type="text" wire:model="items.{{ $idx }}.title" />
                </div>

                <div class="field">
                    <label>قیمت</label>
                    <input type="number" wire:model.live.debounce.500ms="items.{{ $idx }}.price" dir="ltr" min="0" />
                </div>

                <div class="field">
                    <label>تعداد</label>
                    <input type="number" wire:model.live="items.{{ $idx }}.qty" dir="ltr" min="1" />
                </div>

                <div class="field">
                    <label>شناسنامه</label>
                    <label style="display:flex;align-items:center;justify-content:center;height:36px;cursor:pointer;background:var(--bg-soft);border-radius:8px">
                        <input type="checkbox" wire:model="items.{{ $idx }}.cert" style="width:20px;height:20px;accent-color:var(--gold)">
                    </label>
                </div>
                <div></div>
            </div>
        @endforeach

        {{-- ═══ یادداشت ═══ --}}
        <div class="form-grid" style="margin-top:20px">
            <div class="field col-12">
                <label>📝 یادداشت</label>
                <textarea wire:model="notes" rows="2"></textarea>
            </div>
        </div>

        {{-- ═══ دکمه‌ها ═══ --}}
        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px;flex-wrap:wrap">
            <a href="{{ route('orders.index') }}" class="btn btn-ghost">انصراف</a>
            <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                <span wire:loading.remove wire:target="save">✅ ثبت سفارش</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
