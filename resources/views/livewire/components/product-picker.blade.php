<div class="product-picker space-y-3">
    {{-- ═══ جستجو ═══ --}}
    <div class="relative">
        <div class="flex items-center gap-2 bg-base-100 border-2 border-base-300 focus-within:border-primary rounded-xl px-3 py-2 transition">
            <span class="text-base-content/40">🛍️</span>
            <input type="text"
                   wire:model.live.debounce.250ms="query"
                   wire:keydown.enter="addBySku($event.target.value); $event.target.value=''; $wire.set('query','')"
                   placeholder="SKU، نام یا بارکد محصول..."
                   class="flex-1 bg-transparent border-0 outline-none text-sm font-mono"
                   autocomplete="off"
                   dir="auto">
            @if($query)
                <button type="button" wire:click="$set('query','')" class="btn btn-ghost btn-xs btn-circle">✕</button>
            @endif
        </div>

        @if(count($results) > 0)
            <div class="absolute z-50 top-full left-0 right-0 mt-2 bg-base-100 border border-base-300 rounded-xl shadow-2xl max-h-96 overflow-y-auto">
                @foreach($results as $r)
                    <button type="button"
                            wire:click="addProduct({{ $r['id'] }})"
                            wire:key="ppr-{{ $r['id'] }}"
                            class="w-full text-right px-3 py-3 hover:bg-base-200 border-b border-base-200 last:border-0 transition flex items-center gap-3">
                        @if($r['image'])
                            <img src="{{ $r['image'] }}" alt="" class="w-12 h-12 object-cover rounded-lg border border-base-300 bg-white shrink-0">
                        @else
                            <div class="w-12 h-12 rounded-lg border border-base-300 bg-base-200 flex items-center justify-center text-lg shrink-0">💎</div>
                        @endif
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-xs truncate">{{ $r['name'] }}</div>
                            <div class="text-[10px] font-mono text-base-content/50 mt-0.5" dir="ltr">{{ $r['sku'] }}</div>
                            @if($r['category'])
                                <div class="text-[10px] text-base-content/40 mt-0.5">🏷️ {{ $r['category'] }}</div>
                            @endif
                        </div>
                        <div class="text-left shrink-0">
                            <div class="text-xs font-bold text-primary">{{ $r['price_fmt'] }}</div>
                            @if($r['stock'] !== null)
                                <div class="text-[10px] {{ $r['stock'] > 0 ? 'text-success' : 'text-error' }}">
                                    موجودی: {{ \App\Support\PersianNumber::toFa($r['stock']) }}
                                </div>
                            @endif
                        </div>
                    </button>
                @endforeach
            </div>
        @endif
    </div>

    {{-- ═══ سبد ═══ --}}
    @if(count($cart) > 0)
        <div class="border border-base-300 rounded-xl overflow-hidden">
            <div class="bg-base-200/60 px-3 py-2 flex items-center justify-between">
                <span class="text-xs font-bold">🛒 سبد ({{ \App\Support\PersianNumber::toFa(count($cart)) }})</span>
                <button type="button" wire:click="clearCart" class="text-[10px] text-error hover:underline">پاک کردن</button>
            </div>
            <div class="divide-y divide-base-200">
                @foreach($cart as $i => $item)
                    <div class="p-3 space-y-2" wire:key="cart-{{ $i }}-{{ $item['product_id'] ?? '' }}">
                        <div class="flex items-start gap-2">
                            <div class="flex-1 min-w-0">
                                <div class="text-xs font-bold truncate">{{ $item['title'] ?? '—' }}</div>
                                @if(!empty($item['sku']))
                                    <div class="text-[10px] font-mono text-base-content/50" dir="ltr">{{ $item['sku'] }}</div>
                                @endif
                            </div>
                            <button type="button" wire:click="removeItem({{ $i }})"
                                    class="btn btn-ghost btn-xs text-error shrink-0">🗑️</button>
                        </div>
                        <div class="grid grid-cols-3 gap-2 items-end">
                            <div>
                                <label class="text-[10px] text-base-content/60">تعداد</label>
                                <input type="number" min="1" max="999"
                                       value="{{ $item['qty'] ?? 1 }}"
                                       wire:change="updateQty({{ $i }}, $event.target.value)"
                                       class="input input-bordered input-xs w-full text-center" dir="ltr">
                            </div>
                            <div>
                                <label class="text-[10px] text-base-content/60">قیمت</label>
                                <input type="text"
                                       value="{{ number_format((float) ($item['price'] ?? 0)) }}"
                                       wire:change="updatePrice({{ $i }}, $event.target.value)"
                                       class="input input-bordered input-xs w-full text-left font-mono" dir="ltr">
                            </div>
                            <div class="text-left pb-1">
                                <label class="text-[10px] text-base-content/60">جمع</label>
                                <div class="text-xs font-bold text-primary">
                                    {{ number_format(((float) ($item['price'] ?? 0)) * ((int) ($item['qty'] ?? 1))) }}
                                </div>
                            </div>
                        </div>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox"
                                   {{ !empty($item['certNeeded']) ? 'checked' : '' }}
                                   wire:change="toggleCert({{ $i }})"
                                   class="checkbox checkbox-xs checkbox-primary">
                            <span class="text-[10px] text-base-content/70">نیاز به شناسنامه</span>
                        </label>
                    </div>
                @endforeach
            </div>
            <div class="bg-primary/10 px-3 py-2 flex items-center justify-between border-t border-base-300">
                <span class="text-xs font-bold">جمع کل:</span>
                <span class="text-sm font-bold text-primary">
                    {{ number_format($total) }} تومان
                </span>
            </div>
        </div>
    @else
        <div class="border-2 border-dashed border-base-300 rounded-xl p-6 text-center">
            <div class="text-3xl mb-2 opacity-30">🛒</div>
            <div class="text-xs text-base-content/60">محصولی اضافه نشده</div>
            <div class="text-[10px] text-base-content/40 mt-1">
                SKU را تایپ کن و Enter بزن یا از نتایج انتخاب کن
            </div>
        </div>
    @endif
</div>
