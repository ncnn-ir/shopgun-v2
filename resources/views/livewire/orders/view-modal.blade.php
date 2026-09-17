<div>
@if($show && $order)
<div class="sg-modal-overlay active" wire:key="ov-{{ $order->id }}" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:640px">
        <div class="sg-modal-header">
            <h2>📋 سفارش #{{ $order->order_number }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body" style="padding:14px">

            {{-- ═══ Timeline افقی با تاریخ/ساعت ═══ --}}
            <div class="sg-timeline">
                @foreach($timeline as $step)
                    <div class="sg-tl-step {{ $step['state'] }}">
                        <div class="tl-dot">{{ $step['state'] === 'done' ? '✓' : $step['icon'] }}</div>
                        <div class="tl-lbl">{{ $step['label'] }}</div>
                        @if($step['date'])
                            <div class="tl-date">{{ $step['date'] }}</div>
                        @endif
                        @if($step['time'])
                            <div class="tl-time">{{ $step['time'] }}</div>
                        @endif
                    </div>
                @endforeach
            </div>

            {{-- ═══ باکس مشتری ═══ --}}
            @if($order->customer)
                <div class="sg-compact-box">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                        <div class="avatar">
                            {{ mb_substr($order->customer_name ?? $order->customer->name ?? '?', 0, 1) }}
                        </div>
                        <div style="flex:1;min-width:0">
                            <div class="name">{{ $order->customer_name ?? $order->customer->name }}</div>
                            <div class="phone">{{ $order->phone }}</div>
                        </div>
                        @if(!empty($customerStats))
                            <div style="background:var(--gold);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">
                                {{ \App\Support\PersianNumber::toFa($customerStats['total']) }} سفارش
                            </div>
                        @endif
                    </div>

                    @if(!empty($customerStats))
                        <div class="grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:8px">
                            <div class="item" style="text-align:center">
                                <div class="val" style="font-size:14px;font-weight:800">
                                    {{ number_format($customerStats['sum'] / 1000000, 1) }}M
                                </div>
                                <div class="lbl" style="font-size:9.5px;margin-top:3px">مجموع خرید</div>
                            </div>
                            <div class="item" style="text-align:center">
                                <div class="val" style="font-size:11px;font-family:monospace">
                                    {{ \App\Support\PersianDate::format($customerStats['first'], 'Y/m/d') }}
                                </div>
                                <div class="lbl" style="font-size:9.5px;margin-top:3px">اولین</div>
                            </div>
                            <div class="item" style="text-align:center">
                                <div class="val" style="font-size:11px;font-family:monospace">
                                    {{ \App\Support\PersianDate::format($customerStats['last'], 'Y/m/d') }}
                                </div>
                                <div class="lbl" style="font-size:9.5px;margin-top:3px">آخرین</div>
                            </div>
                        </div>
                    @endif
                </div>
            @endif

            {{-- ═══ اطلاعات در یک خط ═══ --}}
            <div class="sg-inline-info">
                <div class="item">📅 <strong>{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</strong></div>
                @if($order->channel)
                    <div class="item">🌐 <span class="sg-channel-cell {{ $order->channel->slug ?? 'default' }}" style="font-size:10px">{{ $order->channel->name }}</span></div>
                @endif
                <div class="item">💰 <strong>{{ \App\Support\PersianNumber::toFa(number_format($order->insurance ?? 0)) }}</strong></div>
                @if($order->postal_code)
                    <div class="item">📮 <strong style="font-family:monospace">{{ $order->postal_code }}</strong></div>
                @endif
            </div>

            {{-- ═══ محصولات ═══ --}}
            @if($order->items->count())
                <div style="margin-bottom:10px">
                    <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:6px">🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})</div>
                    <div style="border:1px solid var(--border);border-radius:10px;overflow:hidden">
                        @foreach($order->items as $item)
                            <div style="padding:8px 10px;border-bottom:1px solid var(--border-soft);display:flex;gap:8px;align-items:center;font-size:12px">
                                <div style="flex:1;min-width:0">
                                    <div style="font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $item->title }}</div>
                                    @if($item->sku) <div style="font-family:monospace;font-size:9.5px;opacity:.5" dir="ltr">{{ $item->sku }}</div> @endif
                                </div>
                                <div style="opacity:.6;font-size:11px">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                                <div style="font-weight:700;font-family:monospace;font-size:11.5px">{{ number_format($item->price) }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- ═══ آدرس ═══ --}}
            @if($order->address)
                <div style="background:var(--bg-soft);padding:10px;border-radius:10px;margin-bottom:10px;font-size:11.5px;line-height:1.6">
                    📍 {{ $order->address }}
                </div>
            @endif

            {{-- ═══ Totals ═══ --}}
            <div style="background:linear-gradient(135deg,rgba(13,148,136,.08),rgba(8,145,178,.03));padding:10px 14px;border-radius:10px">
                <div style="display:flex;gap:14px;justify-content:space-between;flex-wrap:wrap;font-size:11.5px">
                    @if(($order->shipping ?? 0) > 0)
                        <div>📦 ارسال: <strong style="font-family:monospace">{{ number_format($order->shipping) }}</strong></div>
                    @endif
                    @if(($order->discount ?? 0) > 0)
                        <div style="color:var(--warn)">🏷️ تخفیف: <strong style="font-family:monospace">-{{ number_format($order->discount) }}</strong></div>
                    @endif
                    <div style="font-size:14px;margin-right:auto">💵 <strong style="color:var(--primary);font-size:15px">{{ number_format($order->amount ?? 0) }} ت</strong></div>
                </div>
            </div>

            @if($order->notes)
                <div style="background:rgba(201,168,76,.08);padding:8px 12px;border-radius:10px;margin-top:10px;font-size:11.5px">
                    📝 {{ $order->notes }}
                </div>
            @endif
        </div>

        <div class="sg-modal-footer" style="padding:10px 14px">
            <button wire:click="deleteOrder" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">🗑️</button>
            <div style="display:flex;gap:6px">
                <button wire:click="cycleStatus" class="btn btn-outline btn-sm">🔄 وضعیت بعدی</button>
                <button wire:click="editOrder" class="btn btn-primary btn-sm">✏️ ویرایش</button>
            </div>
        </div>
    </div>
</div>
@endif
</div>
