<div>
@if($show && $order)
<div style="position:fixed;inset:0;background:rgba(15,23,42,.75);backdrop-filter:blur(6px);z-index:9500;display:flex;align-items:center;justify-content:center;padding:12px"
     wire:click.self="$wire.close()">

    <div style="background:var(--sg-bg-card);width:100%;max-width:560px;border-radius:16px;box-shadow:var(--sg-shadow-xl);overflow:hidden;direction:rtl;display:flex;flex-direction:column;max-height:calc(100vh - 24px)"
         wire:click.stop>

        {{-- Header --}}
        <div style="padding:14px 18px;background:linear-gradient(135deg,var(--sg-primary),var(--sg-primary-hover));color:#fff;display:flex;justify-content:space-between;align-items:center;flex-shrink:0">
            <div>
                <div style="font-weight:700;font-size:14px">📋 سفارش #{{ $order->order_number }}</div>
                <div style="font-size:10.5px;opacity:.85;margin-top:2px">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}</div>
            </div>
            <button wire:click="close" style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.2);border:none;color:#fff;cursor:pointer;font-size:14px">✕</button>
        </div>

        <div style="padding:14px;overflow-y:auto;flex:1;min-height:0">

            {{-- Timeline --}}
            @php
                $steps = [
                    ['id'=>'pending','label'=>'ثبت','icon'=>'📝'],
                    ['id'=>'final-check','label'=>'چک','icon'=>'🔍'],
                    ['id'=>'courier','label'=>'مامور','icon'=>'🚚'],
                ];
                $currentIdx = array_search($order->status ?? 'pending', array_column($steps, 'id'));
                if ($currentIdx === false) $currentIdx = 0;
            @endphp
            <div style="display:flex;justify-content:space-between;padding:8px 4px;margin-bottom:12px;position:relative">
                @foreach($steps as $i => $s)
                    <div style="flex:1;text-align:center;position:relative;z-index:1">
                        <div style="width:30px;height:30px;border-radius:50%;margin:0 auto 4px;display:flex;align-items:center;justify-content:center;font-size:12px;transition:all .3s;
                            @if($i < $currentIdx) background:#10b981;color:#fff
                            @elseif($i === $currentIdx) background:var(--sg-accent);color:#fff;box-shadow:0 0 0 4px rgba(201,168,76,.25);animation:sgPulse 2s infinite
                            @else background:var(--sg-bg-soft);color:var(--sg-text-muted);border:2px solid var(--sg-border) @endif">
                            {{ $i < $currentIdx ? '✓' : $s['icon'] }}
                        </div>
                        <div style="font-size:10.5px;font-weight:700;color:{{ $i === $currentIdx ? 'var(--sg-accent)' : ($i < $currentIdx ? '#10b981' : 'var(--sg-text-muted)') }}">{{ $s['label'] }}</div>
                    </div>
                @endforeach
            </div>

            {{-- Customer (POPUP) --}}
            @if($order->customer)
                <div wire:click="openCustomerProfile({{ $order->customer->id }})"
                     style="padding:10px;background:var(--sg-bg-soft);border-radius:10px;margin-bottom:10px;display:flex;align-items:center;gap:10px;cursor:pointer;transition:var(--sg-t-fast)"
                     onmouseover="this.style.background='var(--sg-bg-card)';this.style.boxShadow='var(--sg-shadow-sm)'"
                     onmouseout="this.style.background='var(--sg-bg-soft)';this.style.boxShadow=''">
                    <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#14b8a6,#0891b2);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0">
                        {{ mb_substr($order->customer_name ?? $order->customer->name ?? '?', 0, 1) }}
                    </div>
                    <div style="flex:1;min-width:0">
                        <div style="font-weight:700;font-size:12.5px">{{ $order->customer_name ?? $order->customer->name }}</div>
                        <div style="font-family:var(--sg-font-mono);font-size:11px;color:var(--sg-text-muted)" dir="ltr">{{ $order->phone }}</div>
                    </div>
                    <span style="padding:3px 10px;border-radius:99px;background:var(--sg-primary);color:#fff;font-size:10px;font-weight:700">👤 پروفایل</span>
                </div>
            @endif

            {{-- Status + Insurance --}}
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;font-size:11px">
                @php $st = \App\Support\OrderStatus::FLOW[$order->status ?? 'pending'] ?? \App\Support\OrderStatus::FLOW['pending']; @endphp
                <span style="padding:4px 12px;border-radius:99px;background:{{ $st['color'] }};color:#fff;font-weight:700">
                    {{ $st['icon'] }} {{ $st['label'] }}
                </span>
                <span style="padding:4px 12px;border-radius:99px;background:var(--sg-bg-soft);color:var(--sg-text);font-family:var(--sg-font-mono);font-weight:700">
                    💰 بیمه: {{ \App\Support\PersianNumber::toFa(number_format((float) ($order->insurance ?? 0))) }}
                </span>
                @if($order->channel)
                    <span style="padding:4px 12px;border-radius:99px;background:{{ $order->channel->color ?? '#64748b' }};color:#fff;font-weight:700">
                        {{ $order->channel->icon }} {{ $order->channel->name }}
                    </span>
                @endif
            </div>

            {{-- Items (clickable) --}}
            @if($order->items->count())
                <div style="font-size:11.5px;font-weight:700;color:var(--sg-primary);margin-bottom:6px">
                    🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})
                </div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:10px">
                    @foreach($order->items as $item)
                        <div wire:key="it-{{ $item->id }}"
                             wire:click="openProductInfo('{{ addslashes($item->sku ?? '') }}')"
                             style="padding:6px 10px;background:var(--sg-bg-soft);border:1px solid transparent;border-radius:8px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:8px;transition:var(--sg-t-fast)"
                             onmouseover="this.style.borderColor='var(--sg-accent)';this.style.background='var(--sg-bg-card)'"
                             onmouseout="this.style.borderColor='transparent';this.style.background='var(--sg-bg-soft)'">
                            <div style="flex:1;min-width:0">
                                <div style="font-weight:700;font-size:11.5px" class="sg-truncate">{{ $item->title }}</div>
                                @if($item->sku)
                                    <div style="font-family:var(--sg-font-mono);font-size:9.5px;color:var(--sg-text-muted)" dir="ltr">{{ $item->sku }}</div>
                                @endif
                            </div>
                            <div style="font-family:var(--sg-font-mono);font-size:10.5px;color:var(--sg-text-secondary);flex-shrink:0">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                            <div style="font-family:var(--sg-font-mono);font-size:11px;font-weight:700;color:var(--sg-success);flex-shrink:0">{{ number_format($item->price) }}</div>
                            <span style="color:var(--sg-accent);font-size:13px">👁️</span>
                        </div>
                    @endforeach
                </div>
            @endif

            {{-- Address --}}
            @if($order->address)
                <div style="padding:8px 10px;background:var(--sg-bg-soft);border-radius:8px;margin-bottom:10px;font-size:11px;line-height:1.6;color:var(--sg-text-secondary)">
                    📍 {{ $order->address }}
                    @if($order->postal_code)
                        <br><span style="font-family:var(--sg-font-mono);color:var(--sg-text-muted)">📮 {{ $order->postal_code }}</span>
                    @endif
                </div>
            @endif

            {{-- Total --}}
            <div style="padding:10px 14px;background:linear-gradient(135deg,rgba(26,82,118,.08),rgba(26,82,118,.03));border-radius:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:700;font-size:12px;color:var(--sg-primary)">💰 جمع کل</span>
                <span style="font-family:var(--sg-font-mono);font-size:15px;font-weight:800;color:var(--sg-primary)">{{ number_format($order->amount ?? 0) }} ت</span>
            </div>
        </div>

        {{-- Footer --}}
        <div style="padding:10px 14px;background:var(--sg-bg-soft);border-top:1px solid var(--sg-divider);display:flex;justify-content:space-between;gap:6px;flex-wrap:wrap;flex-shrink:0">
            <div style="display:flex;gap:6px">
                <button wire:click="deleteOrder" wire:confirm="حذف شود؟" class="sg-btn sg-btn-danger sg-btn-sm">🗑️</button>
                <button onclick="window.open('{{ route('orders.print-label', $order) }}', '_blank')" class="sg-btn sg-btn-sm" style="background:#0891b2;color:#fff">🏷️ برچسب</button>
            </div>
            <div style="display:flex;gap:6px">
                <button wire:click="cycleStatus" class="sg-btn sg-btn-ghost sg-btn-sm">🔄 بعدی</button>
                <button wire:click="editOrder" class="sg-btn sg-btn-success sg-btn-sm">✏️ ویرایش</button>
            </div>
        </div>
    </div>
</div>

{{-- ═══ Product Info Popup ═══ --}}
@if($showProductInfo && $productInfo)
    <div style="position:fixed;inset:0;background:rgba(15,23,42,.85);backdrop-filter:blur(8px);z-index:9600;display:flex;align-items:center;justify-content:center;padding:12px"
         wire:click.self="closeProductInfo">
        <div style="background:var(--sg-bg-card);border-radius:16px;max-width:380px;width:100%;overflow:hidden" wire:click.stop>
            <div style="aspect-ratio:1;background:#f8fafc;display:flex;align-items:center;justify-content:center;overflow:hidden">
                @if(!empty($productInfo['image']))
                    <img src="{{ $productInfo['image'] }}" alt="" style="width:100%;height:100%;object-fit:cover" onerror="this.replaceWith(document.createTextNode('💎'))" crossorigin="anonymous">
                @else
                    <div style="font-size:64px;color:#cbd5e1">💎</div>
                @endif
            </div>
            <div style="padding:14px">
                <div style="font-weight:700;font-size:13.5px;margin-bottom:4px">{{ $productInfo['title'] }}</div>
                @if(!empty($productInfo['sku']))
                    <div style="font-family:var(--sg-font-mono);font-size:11px;color:var(--sg-text-muted);margin-bottom:10px" dir="ltr">SKU: {{ $productInfo['sku'] }}</div>
                @endif
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
                    <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                        <div style="font-size:9.5px;color:var(--sg-text-muted)">💰 قیمت</div>
                        <div style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-success);font-size:12px">{{ number_format($productInfo['price']) }}</div>
                    </div>
                    <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                        <div style="font-size:9.5px;color:var(--sg-text-muted)">⚖️ وزن</div>
                        <div style="font-family:var(--sg-font-mono);font-weight:700;font-size:12px">{{ $productInfo['weight'] ?: '—' }}</div>
                    </div>
                    <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                        <div style="font-size:9.5px;color:var(--sg-text-muted)">📐 ابعاد</div>
                        <div style="font-family:var(--sg-font-mono);font-weight:700;font-size:11px">
                            @if(!empty($productInfo['dimensions']))
                                {{ $productInfo['dimensions']['length'] ?: '—' }}×{{ $productInfo['dimensions']['width'] ?: '—' }}
                            @else — @endif
                        </div>
                    </div>
                    <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                        <div style="font-size:9.5px;color:var(--sg-text-muted)">📦 موجودی</div>
                        <div style="font-family:var(--sg-font-mono);font-weight:700;font-size:12px;
                            @if(($productInfo['stock_status'] ?? '') === 'instock') color:#10b981
                            @elseif(($productInfo['stock_status'] ?? '') === 'outofstock') color:#ef4444 @endif">
                            {{ $productInfo['stock'] !== null ? \App\Support\PersianNumber::toFa($productInfo['stock']) : '—' }}
                        </div>
                    </div>
                </div>
                <div style="display:flex;gap:6px;margin-top:12px">
                    <button wire:click="closeProductInfo" class="sg-btn sg-btn-ghost sg-btn-sm" style="flex:1">بستن</button>
                    @if(!empty($productInfo['view_url']))
                        <a href="{{ $productInfo['view_url'] }}" target="_blank" class="sg-btn sg-btn-primary sg-btn-sm" style="flex:1">🌐 سایت</a>
                    @endif
                </div>
            </div>
        </div>
    </div>
@endif
@endif
</div>

<style>
@keyframes sgPulse {
    0%,100% { box-shadow: 0 0 0 4px rgba(201,168,76,.25); }
    50% { box-shadow: 0 0 0 8px rgba(201,168,76,.08); }
}
</style>
