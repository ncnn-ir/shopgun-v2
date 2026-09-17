from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"✅ {rel}")

# =========================================================
# ۱. form-modal — wrap در div
# =========================================================

write_file("resources/views/livewire/orders/form-modal.blade.php", r"""
<div>
    @if($show)
    <div class="fixed inset-0 z-[80] flex items-start justify-center p-4 overflow-y-auto"
         x-data="{ show: true }"
         x-init="$nextTick(() => show = true)">

        <div class="fixed inset-0 bg-black/60 backdrop-blur-md transition-opacity duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0"
             x-transition:enter-end="opacity-100"
             wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16
                    border border-base-300 transition-all duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-8 scale-95"
             x-transition:enter-end="opacity-100 translate-y-0 scale-100">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl sticky top-0 z-10 bg-base-100/95 backdrop-blur">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                        {{ $orderId ? '✏️' : '📦' }}
                    </div>
                    <h2 class="font-bold text-base">{{ $orderId ? 'ویرایش سفارش' : 'سفارش جدید' }}</h2>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-4 max-h-[calc(100vh-14rem)] overflow-y-auto">

                <div>
                    <label class="label pb-1"><span class="label-text font-bold text-sm">📱 تلفن <span class="text-error">*</span></span></label>
                    <livewire:components.phone-search wire:model="phone" :key="'phone-'.$orderId" />
                    @error('phone') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                        <label class="label pb-1"><span class="label-text text-xs font-bold">👤 نام</span></label>
                        <input type="text" wire:model="customerName" class="input input-bordered input-sm w-full" />
                    </div>
                    <div>
                        <label class="label pb-1"><span class="label-text text-xs font-bold">📮 کدپستی</span></label>
                        <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                    </div>
                </div>

                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">📍 آدرس</span></label>
                    <textarea wire:model="address" class="textarea textarea-bordered textarea-sm w-full" rows="2"></textarea>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                        <label class="label pb-1"><span class="label-text text-xs font-bold">📊 وضعیت</span></label>
                        <div class="flex flex-wrap gap-1">
                            @foreach(['pending' => '📝 ثبت', 'final-check' => '🔍 چک', 'courier' => '🚚 تحویل'] as $k => $v)
                                <button type="button" wire:click="$set('status', '{{ $k }}')"
                                        class="btn btn-xs {{ $status === $k ? 'btn-primary' : 'btn-outline' }}">{{ $v }}</button>
                            @endforeach
                        </div>
                    </div>
                    <div>
                        <label class="label pb-1"><span class="label-text text-xs font-bold">🌐 کانال</span></label>
                        <div class="flex flex-wrap gap-1">
                            @foreach($channels as $c)
                                <button type="button" wire:click="$set('channelId', {{ $c->id }})"
                                        class="btn btn-xs {{ $channelId === $c->id ? 'btn-primary' : 'btn-outline' }}">
                                    {{ $c->icon }}
                                </button>
                            @endforeach
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="label pb-1"><span class="label-text text-xs font-bold">💰 بیمه</span></label>
                        <input type="text" wire:model="insurance" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                    </div>
                    <label class="label cursor-pointer justify-start gap-2 pt-5">
                        <input type="checkbox" wire:model="invoiceNeeded" class="checkbox checkbox-sm checkbox-primary" />
                        <span class="label-text text-xs font-bold">📄 فاکتور</span>
                    </label>
                </div>

                <div class="divider my-1 text-xs">🛍️ محصولات</div>

                <div class="space-y-2">
                    @foreach($items as $idx => $it)
                        <div class="border border-base-300 rounded-lg p-2 bg-base-200/30" wire:key="item-{{ $idx }}">
                            <div class="grid grid-cols-12 gap-2 items-end">
                                <div class="col-span-6 md:col-span-3">
                                    <input type="text" wire:model="items.{{ $idx }}.sku" dir="ltr"
                                           placeholder="SKU" class="input input-bordered input-xs w-full font-mono" />
                                </div>
                                <div class="col-span-6 md:col-span-4">
                                    <input type="text" wire:model="items.{{ $idx }}.title"
                                           placeholder="عنوان" class="input input-bordered input-xs w-full" />
                                </div>
                                <div class="col-span-6 md:col-span-2">
                                    <input type="number" wire:model.live.debounce.500ms="items.{{ $idx }}.price"
                                           dir="ltr" placeholder="قیمت" class="input input-bordered input-xs w-full font-mono" />
                                </div>
                                <div class="col-span-3 md:col-span-1">
                                    <input type="number" wire:model.live="items.{{ $idx }}.qty" min="1"
                                           class="input input-bordered input-xs w-full text-center" />
                                </div>
                                <div class="col-span-2 md:col-span-1 flex flex-col items-center">
                                    <input type="checkbox" wire:model="items.{{ $idx }}.cert" class="checkbox checkbox-xs" title="شناسنامه" />
                                </div>
                                <div class="col-span-1">
                                    <button type="button" wire:click="removeItem({{ $idx }})"
                                            class="btn btn-error btn-xs btn-circle">✕</button>
                                </div>
                            </div>
                        </div>
                    @endforeach
                </div>

                <button type="button" wire:click="addItem" class="btn btn-outline btn-xs">➕ افزودن محصول</button>

                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">📝 یادداشت</span></label>
                    <textarea wire:model="notes" class="textarea textarea-bordered textarea-sm w-full" rows="2"></textarea>
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="close" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
""")

# =========================================================
# ۲. shipment-timeline — wrap در div
# =========================================================

write_file("resources/views/livewire/components/shipment-timeline.blade.php", r"""
<div>
    @if($show && $order)
    <div class="fixed inset-0 z-[100] flex items-start justify-center p-4 overflow-y-auto"
         x-data="{ show: true }"
         x-init="$nextTick(() => show = true)">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md transition-opacity duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0"
             x-transition:enter-end="opacity-100"
             wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16
                    border border-primary/20 transition-all duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-8 scale-95"
             x-transition:enter-end="opacity-100 translate-y-0 scale-100">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white text-lg shadow-lg">
                        📮
                    </div>
                    <div>
                        <div class="font-bold text-sm">مرسوله تیپاکس</div>
                        <div class="text-xs text-base-content/60">سفارش #{{ $order->order_number }}</div>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-5">

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="bg-gradient-to-br from-cyan-500 to-teal-600 text-white rounded-xl p-4 shadow-lg">
                        <div class="text-[10px] opacity-80 mb-1">📮 کد رهگیری</div>
                        <div class="font-mono font-bold text-lg tracking-wider" dir="ltr">
                            {{ $order->tracking_code ?: '—' }}
                        </div>
                        @if($order->shipping_status)
                            <div class="inline-block mt-2 px-2 py-0.5 bg-white/20 rounded-full text-[10px] font-bold">
                                {{ $order->shipping_status }}
                            </div>
                        @endif
                    </div>

                    <div class="bg-base-200 rounded-xl p-4">
                        <div class="text-[10px] text-base-content/60 mb-1">👤 گیرنده</div>
                        <div class="font-bold text-sm">{{ $order->customer?->name ?? '—' }}</div>
                        <div class="text-xs text-base-content/60 font-mono mt-1" dir="ltr">{{ $order->phone }}</div>
                        <div class="text-xs text-base-content/60 mt-1 truncate">{{ $order->address }}</div>
                    </div>
                </div>

                <div>
                    <h3 class="font-bold text-sm mb-4 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                        مراحل ارسال
                    </h3>

                    @if(empty($events))
                        <div class="text-center py-8 text-base-content/40 text-sm">
                            هنوز رویدادی ثبت نشده
                        </div>
                    @else
                        <div class="overflow-x-auto pb-4 -mx-5 px-5">
                            <div class="flex items-start gap-0 min-w-max">
                                @foreach(array_reverse($events) as $i => $e)
                                    @php
                                        $isLast = $i === count($events) - 1;
                                        $s = mb_strtolower($e['status'] ?? '');
                                        $color = str_contains($s, 'تحویل') && ! str_contains($s, 'نشد')
                                            ? 'from-emerald-500 to-green-600'
                                            : (str_contains($s, 'مسیر') || str_contains($s, 'ارسال')
                                                ? 'from-cyan-500 to-blue-600'
                                                : 'from-amber-500 to-orange-500');
                                    @endphp

                                    <div class="flex items-start">
                                        <div class="flex flex-col items-center w-40" wire:key="event-{{ $i }}">
                                            <div class="relative">
                                                <div class="w-12 h-12 rounded-full bg-gradient-to-br {{ $color }} 
                                                            flex items-center justify-center text-white text-xl shadow-lg
                                                            {{ $isLast ? 'ring-4 ring-cyan-500/30 animate-pulse' : '' }}">
                                                    {{ $isLast ? '🚚' : ($i === 0 ? '📦' : '📍') }}
                                                </div>
                                                @if(! $isLast)
                                                    <div class="absolute top-1/2 -right-14 w-14 h-0.5 bg-gradient-to-l from-cyan-500 to-transparent"></div>
                                                @endif
                                            </div>
                                            <div class="mt-3 text-center w-36">
                                                <div class="text-xs font-bold text-base-content/80 leading-tight">
                                                    {{ \Illuminate\Support\Str::limit($e['status'] ?? '—', 30) }}
                                                </div>
                                                <div class="text-[10px] text-base-content/50 mt-1 font-mono" dir="ltr">
                                                    {{ $e['date'] ?? '' }}
                                                </div>
                                                @if(! empty($e['description']) && $e['description'] !== ($e['status'] ?? ''))
                                                    <div class="text-[10px] text-base-content/40 mt-1 leading-tight">
                                                        {{ \Illuminate\Support\Str::limit($e['description'], 60) }}
                                                    </div>
                                                @endif
                                            </div>
                                        </div>
                                    </div>
                                @endforeach
                            </div>
                        </div>
                    @endif
                </div>

                @if($order->tracking_code)
                    <a href="https://tipaxco.com/tracking?code={{ $order->tracking_code }}"
                       target="_blank"
                       class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-l from-cyan-500 to-teal-600 text-white text-xs font-bold hover:opacity-90 transition">
                        🔗 پیگیری در سایت تیپاکس
                    </a>
                @endif
            </div>
        </div>
    </div>
    @endif
</div>
""")

# =========================================================
# ۳. print-a4 — بساز
# =========================================================

write_file("resources/views/livewire/certificates/print-a4.blade.php", r"""
<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html>
        <html lang='fa' dir='rtl'>
        <head>
            <meta charset='UTF-8'>
            <title>چاپ شناسنامه‌ها</title>
            <style>
                @page { size: A4; margin: 8mm; }
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { font-family: Tahoma, sans-serif; background: #fff; }
                .no-print { padding: 12px; text-align: center; background: #f0f0f0; margin-bottom: 8px; }
                .no-print button { padding: 8px 16px; cursor: pointer; font-family: inherit; margin: 0 4px; border: none; border-radius: 6px; background: #14b8a6; color: #fff; }
                .grid { display: grid; grid-template-columns: repeat(3, 65mm); gap: 3mm; justify-content: center; }
                .cert { width: 65mm; height: 65mm; border: 1px solid #b8860b; background: #fffef9; padding: 3mm; display: flex; flex-direction: column; overflow: hidden; page-break-inside: avoid; position: relative; }
                .cert-title { text-align: center; font-family: serif; font-size: 11px; font-weight: bold; color: #6b4423; margin-bottom: 1.5mm; border-bottom: 1px solid #b8860b; padding-bottom: 1mm; }
                .cert-img { width: 22mm; height: 22mm; object-fit: contain; float: left; margin: 0 0 1mm 1mm; border: 1px solid #b8860b; background: #fff; }
                .cert-row { font-size: 7.5px; line-height: 1.5; color: #2c3e50; }
                .cert-row b { color: #0369a1; }
                .cert-qr { position: absolute; bottom: 2mm; left: 2mm; width: 14mm; height: 14mm; }
                .cert-code { position: absolute; bottom: 2mm; right: 2mm; font-family: monospace; font-size: 7px; font-weight: bold; color: #8b6914; }
                .cert-serial { position: absolute; top: 1mm; left: 2mm; font-family: monospace; font-size: 5.5px; color: #999; direction: ltr; }
                @media print { .no-print { display: none !important; } }
            </style>
        </head>
        <body>
            <div class='no-print'>
                <button onclick='window.print()'>🖨️ چاپ A4</button>
                <span style='margin: 0 12px; font-size: 12px;'>{{ count($certificates) }} شناسنامه</span>
                <button onclick='history.back()' style='background:#eee;color:#333;'>✕ بستن</button>
            </div>
            @if(empty($certificates))
                <div style='text-align: center; padding: 40px; color: #999;'>شناسنامه‌ای انتخاب نشده</div>
            @else
                <div class='grid'>
                    @foreach($certificates as $cert)
                        <div class='cert'>
                            <div class='cert-serial'>{{ $cert->serial }}</div>
                            <div class='cert-title'>Certificate of Authenticity</div>
                            @if($cert->image_path)
                                <img src='{{ asset('storage/' . $cert->image_path) }}' class='cert-img' alt=''>
                            @endif
                            <div class='cert-row'><b>Stone:</b> {{ $cert->stone_en ?: $cert->stone_name }}</div>
                            <div class='cert-row'><b>Metal:</b> {{ $cert->metal_en ?: $cert->metal }} ({{ $cert->metal_carat }})</div>
                            <div class='cert-row'><b>Origin:</b> {{ $cert->stone_origin }}</div>
                            <div class='cert-row'><b>Size:</b> {{ $cert->length }}×{{ $cert->width }} mm</div>
                            <div class='cert-row'><b>Weight:</b> {{ $cert->weight }} gr</div>
                            <div class='cert-row'><b>Brilliant:</b> {{ $cert->brilliant }}</div>
                            <img src='{{ $cert->qr_url }}' class='cert-qr' alt=''>
                            <div class='cert-code'>#{{ $cert->code }}</div>
                        </div>
                    @endforeach
                </div>
            @endif
        </body>
        </html>
        ">
    </iframe>
</div>
""")

print()
print("═" * 60)
print("✅ ۳ ویو مشکل‌دار درست شدن")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
