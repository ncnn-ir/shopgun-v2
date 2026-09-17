<div class="customer-picker" wire:key="cp-{{ $this->getId() }}">
    {{-- ═══ حالت جستجو ═══ --}}
    @if($mode === 'search')
        <div class="relative">
            <div class="flex items-center gap-2 bg-base-100 border-2 border-base-300 focus-within:border-primary rounded-xl px-3 py-2 transition">
                <span class="text-base-content/40">🔍</span>
                <input type="text"
                       wire:model.live.debounce.250ms="query"
                       placeholder="تلفن یا نام مشتری..."
                       class="flex-1 bg-transparent border-0 outline-none text-sm"
                       autocomplete="off"
                       dir="auto">
                @if($query)
                    <button type="button" wire:click="$set('query','')" class="btn btn-ghost btn-xs btn-circle">✕</button>
                @endif
            </div>

            {{-- نتایج --}}
            @if(count($results) > 0)
                <div class="absolute z-50 top-full left-0 right-0 mt-2 bg-base-100 border border-base-300 rounded-xl shadow-2xl max-h-80 overflow-y-auto">
                    @foreach($results as $r)
                        <button type="button"
                                wire:click="selectCustomer({{ $r['id'] }})"
                                wire:key="cpr-{{ $r['id'] }}"
                                class="w-full text-right px-4 py-3 hover:bg-base-200 border-b border-base-200 last:border-0 transition">
                            <div class="flex items-center justify-between gap-3">
                                <div class="flex-1 min-w-0">
                                    <div class="font-bold text-sm truncate">{{ $r['name'] }}</div>
                                    <div class="text-xs font-mono text-base-content/60 mt-0.5" dir="ltr">
                                        {{ $r['phone'] }}
                                    </div>
                                    @if($r['address'])
                                        <div class="text-[10px] text-base-content/50 mt-0.5 truncate">
                                            📍 {{ $r['address'] }}
                                        </div>
                                    @endif
                                </div>
                                @if($r['orders'] > 0)
                                    <div class="badge badge-primary badge-sm shrink-0">
                                        {{ \App\Support\PersianNumber::toFa($r['orders']) }} سفارش
                                    </div>
                                @else
                                    <div class="badge badge-ghost badge-sm shrink-0">جدید</div>
                                @endif
                            </div>
                        </button>
                    @endforeach
                </div>
            @elseif(mb_strlen(trim($query)) >= 2)
                <div class="absolute z-50 top-full left-0 right-0 mt-2 bg-base-100 border border-base-300 rounded-xl shadow-2xl p-4">
                    <div class="text-center text-sm text-base-content/60 mb-3">
                        مشتری‌ای پیدا نشد
                    </div>
                    <button type="button" wire:click="startNew"
                            class="btn btn-primary btn-sm w-full">
                        ➕ ایجاد مشتری جدید با تلفن «{{ $query }}»
                    </button>
                </div>
            @endif
        </div>

        {{-- راهنمای سریع --}}
        <div class="text-[10px] text-base-content/40 mt-1 px-1">
            💡 با تایپ ۲ رقم به بالا جستجو شروع می‌شود
        </div>

    {{-- ═══ حالت مشتری جدید ═══ --}}
    @elseif($mode === 'new')
        <div class="border-2 border-primary/30 rounded-xl p-4 bg-primary/5 space-y-3">
            <div class="flex items-center justify-between mb-1">
                <div class="font-bold text-sm text-primary">➕ مشتری جدید</div>
                <button type="button" wire:click="cancelNew" class="btn btn-ghost btn-xs">انصراف</button>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="text-[10px] font-bold text-base-content/60">نام *</label>
                    <input type="text" wire:model="newName"
                           class="input input-bordered input-sm w-full" autofocus>
                    @error('newName') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                </div>
                <div>
                    <label class="text-[10px] font-bold text-base-content/60">📱 تلفن *</label>
                    <input type="text" wire:model="newPhone" dir="ltr"
                           class="input input-bordered input-sm w-full font-mono">
                    @error('newPhone') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                </div>
            </div>

            <div>
                <label class="text-[10px] font-bold text-base-content/60">📍 آدرس</label>
                <textarea wire:model="newAddress" rows="2"
                          class="textarea textarea-bordered textarea-sm w-full"></textarea>
            </div>

            <div>
                <label class="text-[10px] font-bold text-base-content/60">📮 کدپستی</label>
                <input type="text" wire:model="newPostal" dir="ltr"
                       class="input input-bordered input-sm w-full font-mono">
            </div>

            <button type="button" wire:click="createCustomer"
                    wire:loading.attr="disabled"
                    class="btn btn-success btn-sm w-full">
                <span wire:loading.remove wire:target="createCustomer">✅ ذخیره و انتخاب</span>
                <span wire:loading wire:target="createCustomer">⏳...</span>
            </button>
        </div>

    {{-- ═══ حالت انتخاب‌شده ═══ --}}
    @elseif($mode === 'selected')
        <div class="border-2 border-success/40 rounded-xl p-3 bg-success/5">
            <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                        <span class="badge badge-success badge-sm">✓</span>
                        <span class="font-bold text-sm truncate">{{ $selectedData['name'] ?? '—' }}</span>
                    </div>
                    <div class="text-xs font-mono text-base-content/70 mt-1" dir="ltr">
                        {{ $selectedData['phone_fmt'] ?? $selectedData['phone'] ?? '—' }}
                    </div>
                    @if(!empty($selectedData['address']))
                        <div class="text-[11px] text-base-content/60 mt-1">
                            📍 {{ $selectedData['address'] }}
                            @if(!empty($selectedData['postal_code']))
                                <span class="font-mono">({{ $selectedData['postal_code'] }})</span>
                            @endif
                        </div>
                    @endif
                    @if(count($selectedData['extra_phones'] ?? []) > 1)
                        <div class="text-[10px] text-base-content/40 mt-1">
                            📞 {{ count($selectedData['extra_phones']) }} شماره ثبت شده
                        </div>
                    @endif
                </div>
                <button type="button" wire:click="clearSelection"
                        class="btn btn-ghost btn-xs" title="تغییر مشتری">
                    🔄
                </button>
            </div>
        </div>
    @endif
</div>
