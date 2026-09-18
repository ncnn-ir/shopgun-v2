<div>
@if($show && $order)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:93;display:flex;align-items:flex-start;justify-content:center;padding:8px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:600px;margin:8px auto;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:12px 14px;display:flex;align-items:center;justify-content:space-between">
            <div>
                <h2 style="margin:0;font-size:14px;font-weight:700">📋 سفارش #{{ $order->order_number }}</h2>
                <div style="font-size:10.5px;opacity:.85;margin-top:2px">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}</div>
            </div>
            <button wire:click="close" style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:14px">✕</button>
        </div>

        <div style="padding:12px;max-height:calc(100vh - 160px);overflow-y:auto">

            {{-- ═══ Timeline با انیمیشن نرم ═══ --}}
            <div style="display:flex;justify-content:space-between;padding:12px 4px;position:relative;margin-bottom:12px">
                <div style="position:absolute;top:24px;left:40px;right:40px;height:2px;background:#e2e8f0;z-index:0"></div>
                @foreach($timeline as $idx => $step)
                    <div style="flex:1;text-align:center;position:relative;z-index:1">
                        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 4px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;transition:all .3s;
                            {{ $step['state'] === 'done' ? 'background:#10b981;color:#fff;box-shadow:0 0 0 3px rgba(16,185,129,.2)' : '' }}
                            {{ $step['state'] === 'current' ? 'background:#c9a84c;color:#fff;box-shadow:0 0 0 5px rgba(201,168,76,.25);animation:pulseStep 2s infinite' : '' }}
                            {{ $step['state'] === '' ? 'background:#f1f5f9;color:#94a3b8;border:2px solid #e2e8f0' : '' }}">
                            {{ $step['state'] === 'done' ? '✓' : $step['icon'] }}
                        </div>
                        <div style="font-size:10.5px;font-weight:700;color:{{ $step['state'] === 'current' ? '#b45309' : ($step['state'] === 'done' ? '#16a34a' : '#94a3b8') }}">
                            {{ $step['label'] }}
                        </div>
                        @if($step['date'])
                            <div style="font-family:monospace;font-size:9px;color:#94a3b8;margin-top:2px">{{ $step['date'] }}</div>
                        @endif
                    </div>
                @endforeach
            </div>

            <style>
            @keyframes pulseStep {
                0%,100% { box-shadow: 0 0 0 5px rgba(201,168,76,.25); }
                50% { box-shadow: 0 0 0 10px rgba(201,168,76,.05); }
            }
            </style>

            {{-- ═══ مشتری ═══ --}}
            @if($order->customer)
                <div style="padding:8px 10px;background:#f8fafc;border-radius:10px;margin-bottom:10px;display:flex;align-items:center;gap:8px;cursor:pointer"
                     onclick="Livewire.dispatch('open-customer-profile', {customerId: {{ $order->customer->id }}})">
                    <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#14b8a6,#0891b2);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0">
                        {{ mb_substr($order->customer_name ?? $order->customer->name ?? '?', 0, 1) }}
                    </div>
                    <div style="flex:1;min-width:0">
                        <div style="font-weight:700;font-size:12px">{{ $order->customer_name ?? $order->customer->name }}</div>
                        <div style="font-family:monospace;font-size:10.5px;color:#64748b" dir="ltr">{{ $order->phone }}</div>
                    </div>
                    <span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700">👤 پروفایل</span>
                </div>
            @endif

                        {{-- ═══ کانال فروش + پرداخت ═══ --}}
            @if($order->sales_channel || $order->payment_title)
                <div style="padding:8px 10px;background:#eff6ff;border-radius:8px;margin-bottom:8px;font-size:11px">
                    <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
                        @if($order->sales_channel)
                            <span style="padding:2px 8px;border-radius:6px;background:{{ $order->sales_channel_color }}20;color:{{ $order->sales_channel_color }};font-weight:700">
                                {{ $order->sales_channel_label }}
                            </span>
                        @endif
                        @if($order->payment_title)
                            <span style="font-size:10.5px;color:#1e40af">
                                💳 {{ $order->payment_title }}
                            </span>
                        @endif
                    </div>
                    @if($order->customer_note)
                        <div style="margin-top:6px;padding:6px 8px;background:#fff;border-radius:6px;font-size:10.5px;color:#475569;line-height:1.6">
                            📝 <b>یادداشت مشتری:</b> {{ $order->customer_note }}
                        </div>
                    @endif
                    @if(!empty($order->channel_metadata))
                        <details style="margin-top:6px">
                            <summary style="cursor:pointer;font-size:10.5px;color:#64748b">📋 اطلاعات اضافی</summary>
                            <div style="margin-top:4px;font-size:10px;font-family:monospace;direction:ltr;background:#fff;padding:6px;border-radius:6px;max-height:120px;overflow-y:auto">
                                @foreach($order->channel_metadata as $k => $v)
                                    <div>{{ $k }}: {{ is_array($v) ? json_encode($v, JSON_UNESCAPED_UNICODE) : $v }}</div>
                                @endforeach
                            </div>
                        </details>
                    @endif
                </div>
            @endif

            {{-- ═══ تاریخچه مشتری ═══ --}}
            @if($order->customer_id)
                @php
                    $custOrders = \App\Models\Order::where('customer_id', $order->customer_id)->get();
                    $successCount = $custOrders->whereIn('status', ['final-check','courier'])->count();
                    $cancelCount = $custOrders->whereIn('woo_status', ['cancelled','refunded','failed'])->count();
                    $totalSpent = $custOrders->whereIn('status', ['final-check','courier'])->sum('amount');
                @endphp
                <div style="padding:8px 10px;background:#f0fdf4;border-radius:8px;margin-bottom:8px;font-size:10.5px">
                    <div style="font-weight:700;color:#065f46;margin-bottom:6px">📊 سابقه خرید این مشتری</div>
                    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px">
                        <div style="text-align:center">
                            <div style="font-size:14px;font-weight:800;color:#16a34a">{{ \App\Support\PersianNumber::toFa($successCount) }}</div>
                            <div style="font-size:9.5px;color:#065f46">موفق</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:14px;font-weight:800;color:#dc2626">{{ \App\Support\PersianNumber::toFa($cancelCount) }}</div>
                            <div style="font-size:9.5px;color:#991b1b">لغو</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:14px;font-weight:800;color:#16a34a">{{ \App\Support\PersianNumber::toFa($custOrders->count()) }}</div>
                            <div style="font-size:9.5px;color:#065f46">کل</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:12px;font-weight:800;color:#16a34a;font-family:monospace">{{ number_format($totalSpent / 1000000, 1) }}M</div>
                            <div style="font-size:9.5px;color:#065f46">مجموع</div>
                        </div>
                    </div>
                </div>
            @endif

{{-- ═══ اطلاعات فشرده در یک خط ═══ --}}
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;font-size:10.5px">
                @if($order->channel)
                    <span style="padding:3px 8px;border-radius:6px;background:{{ $order->channel->color ?? '#64748b' }};color:#fff;font-weight:700">
                        {{ $order->channel->icon }} {{ $order->channel->name }}
                    </span>
                @endif
                <span style="padding:3px 8px;border-radius:6px;background:#fef3c7;color:#78350f;font-weight:700;font-family:monospace">
                    💰 {{ number_format($order->insurance ?? 0) }}
                </span>
                @if($order->postal_code)
                    <span style="padding:3px 8px;border-radius:6px;background:#f1f5f9;color:#475569;font-family:monospace">
                        📮 {{ $order->postal_code }}
                    </span>
                @endif
            </div>

            {{-- ═══ محصولات (کلیک‌پذیر) ═══ --}}
            @if($order->items->count())
                <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:5px">
                    🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})
                </div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:10px">
                    @foreach($order->items as $item)
                        <div wire:key="it-{{ $item->id }}"
                             onclick="showProductPopup('{{ addslashes($item->title) }}', '{{ addslashes($item->sku ?? '') }}', {{ (float) $item->price }}, {{ (int) $item->quantity }}, '{{ addslashes($order->phone ?? '') }}')"
                             style="padding:6px 8px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:6px;transition:all .15s"
                             onmouseover="this.style.borderColor='#c9a84c';this.style.background='#fffbeb'"
                             onmouseout="this.style.borderColor='#e2e8f0';this.style.background='#fff'">
                            <div style="flex:1;min-width:0">
                                <div style="font-weight:700;font-size:11.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $item->title }}</div>
                                @if($item->sku)
                                    <div style="font-family:monospace;font-size:9.5px;color:#94a3b8" dir="ltr">{{ $item->sku }}</div>
                                @endif
                            </div>
                            <div style="font-family:monospace;font-size:10.5px;color:#64748b;flex-shrink:0">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                            <div style="font-family:monospace;font-size:11px;font-weight:700;color:#16a34a;flex-shrink:0">{{ number_format($item->price) }}</div>
                            <div style="color:#c9a84c;font-size:12px;flex-shrink:0">👁️</div>
                        </div>
                    @endforeach
                </div>
            @endif

            {{-- ═══ آدرس ═══ --}}
            @if($order->address)
                <div style="padding:8px 10px;background:#f8fafc;border-radius:8px;margin-bottom:10px;font-size:11px;line-height:1.6">
                    📍 {{ $order->address }}
                </div>
            @endif

            {{-- ═══ جمع کل ═══ --}}
            <div style="padding:10px 12px;background:linear-gradient(135deg,#dbeafe,#eff6ff);border-radius:10px;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <span style="font-weight:700;font-size:12px;color:#1e40af">💰 جمع کل</span>
                <span style="font-family:monospace;font-size:14px;font-weight:800;color:#1e40af">{{ number_format($order->amount ?? 0) }} ت</span>
            </div>
        </div>

        <div style="padding:10px 14px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:6px;flex-wrap:wrap">
            <button wire:click="deleteOrder" wire:confirm="حذف شود؟"
                    style="padding:7px 14px;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:11.5px">
                🗑️ حذف
            </button>
            <div style="display:flex;gap:6px">
                <button wire:click="cycleStatus"
                        style="padding:7px 14px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:11.5px">
                    🔄 وضعیت بعدی
                </button>
                <button wire:click="editOrder"
                        style="padding:7px 16px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:11.5px">
                    ✏️ ویرایش
                </button>
            </div>
        </div>
    </div>
</div>

{{-- ═══ Product Popup ═══ --}}
<div id="product-popup-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:97;align-items:center;justify-content:center;padding:20px" onclick="closeProductPopup()">
    <div style="background:#fff;border-radius:14px;max-width:340px;width:100%;overflow:hidden;text-align:center" onclick="event.stopPropagation()">
        <div id="popup-image-wrap" style="aspect-ratio:1;background:#f8fafc;display:flex;align-items:center;justify-content:center;overflow:hidden">
            <div id="popup-image-placeholder" style="font-size:60px;color:#cbd5e1">💎</div>
            <img id="popup-image" style="width:100%;height:100%;object-fit:cover;display:none">
        </div>
        <div style="padding:12px">
            <div id="popup-title" style="font-weight:700;font-size:14px;margin-bottom:6px;color:#1e293b"></div>
            <div id="popup-sku" style="font-family:monospace;font-size:11px;color:#94a3b8;margin-bottom:8px" dir="ltr"></div>
            <div style="display:flex;justify-content:space-between;padding:6px 10px;background:#f8fafc;border-radius:8px;font-size:11.5px;margin-bottom:8px">
                <span>تعداد: <b id="popup-qty">1</b></span>
                <span>قیمت: <b id="popup-price" style="font-family:monospace">—</b></span>
            </div>
            <button onclick="closeProductPopup()" style="width:100%;padding:8px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">بستن</button>
        </div>
    </div>
</div>

<script>
function showProductPopup(title, sku, price, qty, phone) {
    document.getElementById('popup-title').textContent = title;
    document.getElementById('popup-sku').textContent = sku ? 'SKU: ' + sku : '';
    document.getElementById('popup-qty').textContent = qty;
    document.getElementById('popup-price').textContent = Number(price).toLocaleString('fa-IR') + ' ت';

    var img = document.getElementById('popup-image');
    var ph = document.getElementById('popup-image-placeholder');

    // تلاش برای گرفتن عکس از سرور
    if (sku) {
        fetch('https://mashahir.jewelry/wp-json/wc/v3/products?sku=' + encodeURIComponent(sku) + '&consumer_key=ck_5fee84b14f07617a4f32f4e2b4c9c8281aedbdaa&consumer_secret=cs_3006a2bfa4de57717994d241db72498d8302ca64')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data && data[0] && data[0].images && data[0].images[0]) {
                    img.src = data[0].images[0].src;
                    img.style.display = 'block';
                    ph.style.display = 'none';
                }
            }).catch(function() {});
    }

    document.getElementById('product-popup-overlay').style.display = 'flex';
}
function closeProductPopup() {
    document.getElementById('product-popup-overlay').style.display = 'none';
}
</script>

@endif
</div>
