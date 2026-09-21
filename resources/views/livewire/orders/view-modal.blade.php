<div>
    @if($order)
        {{-- ═══ Main Popup ═══ --}}
        <div class="sg-popup-backdrop" wire:click="close" style="z-index:9000">
            <div class="sg-popup-panel" wire:click.stop style="max-width:820px;z-index:9001">

                {{-- Header --}}
                <div class="sg-popup-header">
                    <div style="display:flex;flex-direction:column;gap:2px">
                        <div style="display:flex;align-items:center;gap:8px">
                            <span style="font-family:monospace;font-weight:800;color:var(--sg-primary);font-size:14px">
                                #{{ $order->order_number }}
                            </span>
                            @php
                                $stColor = \App\Support\OrderStatus::color($order->status ?? 'pending');
                            @endphp
                            <span class="sg-status-badge"
                                  style="color:{{ $stColor }};background:color-mix(in srgb,{{ $stColor }} 15%,transparent)">
                                {{ \App\Support\OrderStatus::label($order->status ?? 'pending') }}
                            </span>
                        </div>
                        <div style="font-size:11px;color:var(--sg-text-muted)">
                            {{ $order->customer?->name ?? '—' }}
                            • {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}
                            • ساعت {{ $order->created_at?->format('H:i') }}
                        </div>
                    </div>
                    <button class="sg-btn-icon" wire:click="close" type="button">✕</button>
                </div>

                {{-- ═══ Horizontal Timeline ═══ --}}
                <div class="sg-timeline-wrap">
                    <div class="sg-timeline-track">
                        @foreach($statusFlow as $i => $s)
                            <div class="sg-timeline-step sg-tl-{{ $s['state'] }}"
                                 wire:click="changeStatus('{{ $s['key'] }}')"
                                 title="تنظیم به: {{ $s['label'] }}">
                                <div class="sg-timeline-dot" style="--stage-color:{{ $s['color'] }}">
                                    {{ $s['icon'] }}
                                </div>
                                <div class="sg-timeline-label">{{ $s['label'] }}</div>
                            </div>
                            @if(!$loop->last)
                                @php $lineDone = $s['state'] === 'done'; @endphp
                                <div class="sg-timeline-line {{ $lineDone ? 'done' : '' }}"></div>
                            @endif
                        @endforeach
                    </div>
                </div>

                {{-- ═══ Tabs ═══ --}}
                <div class="sg-popup-tabs">
                    <button type="button"
                            class="sg-popup-tab {{ $tab === 'details' ? 'active' : '' }}"
                            wire:click="setTab('details')">
                        📋 جزئیات سفارش
                    </button>
                    <button type="button"
                            class="sg-popup-tab {{ $tab === 'history' ? 'active' : '' }}"
                            wire:click="setTab('history')">
                        🕐 سابقه تغییرات
                        @if(count($history))
                            <span class="sg-tab-count">{{ \App\Support\PersianNumber::toFa(count($history)) }}</span>
                        @endif
                    </button>
                </div>

                {{-- Body --}}
                <div class="sg-popup-body" style="padding:0">

                    {{-- ═══ TAB: DETAILS ═══ --}}
                    @if($tab === 'details')

                        {{-- Info grid --}}
                        <div class="sg-info-grid">
                            <div class="sg-info-cell">
                                <span class="sg-info-lbl">مشتری</span>
                                <span class="sg-info-val">{{ $order->customer?->name ?? '—' }}</span>
                            </div>
                            <div class="sg-info-cell">
                                <span class="sg-info-lbl">مبلغ کل</span>
                                <span class="sg-info-val">{{ number_format((float) $order->amount) }} تومان</span>
                            </div>
                            <div class="sg-info-cell">
                                <span class="sg-info-lbl">تلفن</span>
                                <span class="sg-info-val" dir="ltr">{{ $order->phone ?: ($order->customer?->phone ?? '—') }}</span>
                            </div>
                            <div class="sg-info-cell">
                                <span class="sg-info-lbl">کد پستی</span>
                                <span class="sg-info-val" dir="ltr">{{ $order->postal_code ?: '—' }}</span>
                            </div>
                            <div class="sg-info-cell">
                                <span class="sg-info-lbl">کانال فروش</span>
                                <span class="sg-info-val">{{ $order->channel?->name ?? '—' }}</span>
                            </div>
                            <div class="sg-info-cell">
                                <span class="sg-info-lbl">تاریخ ثبت</span>
                                <span class="sg-info-val">
                                    {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}
                                    <small style="color:var(--sg-text-muted)">{{ $order->created_at?->format('H:i') }}</small>
                                </span>
                            </div>
                        </div>

                        @if($order->address)
                            <div class="sg-info-address">
                                <span class="sg-info-lbl">آدرس</span>
                                <span class="sg-info-val">{{ $order->address }}</span>
                            </div>
                        @endif

                        {{-- Items with product titles --}}
                        @if($order->items->count())
                            <div class="sg-items-section">
                                <div class="sg-section-title">
                                    🛒 اقلام سفارش
                                    <span style="color:var(--sg-text-subtle);font-weight:600;margin-right:6px">
                                        ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})
                                    </span>
                                </div>

                                @foreach($order->items as $item)
                                    <div class="sg-item-row" wire:click="showProduct({{ $item->id }})"
                                         title="برای جزئیات محصول کلیک کنید">
                                        <div class="sg-item-thumb">
                                            @if($item->image_url ?? $item->image_path ?? false)
                                                <img src="{{ $item->image_url ?? $item->image_path }}" alt="">
                                            @else
                                                <span>💎</span>
                                            @endif
                                        </div>

                                        <div class="sg-item-body">
                                            <div class="sg-item-title">{{ $item->title }}</div>
                                            @if($item->sku)
                                                <div class="sg-item-sku" dir="ltr">{{ $item->sku }}</div>
                                            @endif
                                        </div>

                                        <div class="sg-item-price">
                                            <span class="sg-item-amount">{{ number_format((float) $item->price) }}</span>
                                            <span class="sg-item-qty">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</span>
                                        </div>
                                    </div>
                                @endforeach
                            </div>
                        @else
                            <div class="sg-empty" style="padding:30px">آیتمی ثبت نشده</div>
                        @endif

                    @endif

                    {{-- ═══ TAB: HISTORY ═══ --}}
                    @if($tab === 'history')
                        <div class="sg-history-tab">
                            @forelse($history as $h)
                                <div class="sg-history-card">
                                    <div class="sg-history-head">
                                        <span class="sg-history-dot" style="background:{{ $h['color'] }}"></span>
                                        <div class="sg-history-transition">
                                            @if($h['from'])
                                                <span class="sg-hs-from">{{ $h['from'] }}</span>
                                                <span class="sg-hs-arrow">←</span>
                                            @endif
                                            <span class="sg-hs-to" style="color:{{ $h['color'] }}">{{ $h['to'] }}</span>
                                        </div>
                                        <div class="sg-history-when">
                                            <span>{{ $h['date'] }}</span>
                                            <span class="sg-history-time">{{ $h['time'] }}</span>
                                        </div>
                                    </div>
                                    @if($h['note'])
                                        <div class="sg-history-note">{{ $h['note'] }}</div>
                                    @endif
                                    @if($h['user'])
                                        <div class="sg-history-user">👤 {{ $h['user'] }}</div>
                                    @endif
                                </div>
                            @empty
                                <div class="sg-empty" style="padding:40px">
                                    <div style="font-size:32px;margin-bottom:8px">🕐</div>
                                    هنوز تغییری در این سفارش ثبت نشده
                                </div>
                            @endforelse
                        </div>
                    @endif

                </div>

                {{-- Footer --}}
                <div class="sg-popup-footer" style="display:flex;gap:8px;justify-content:flex-end">
                    <button type="button" class="sg-btn sg-btn-ghost" wire:click="close">بستن</button>
                    @if($order->tracking_code)
                        <button type="button" class="sg-btn sg-btn-primary">
                            📮 برچسب پستی
                        </button>
                    @endif
                </div>
            </div>
        </div>
    @endif

    {{-- ═══ Product Popup ═══ --}}
    @if($showProductPopup && !empty($productDetail))
        <div class="sg-popup-backdrop" wire:click="closeProduct" style="z-index:9100">
            <div class="sg-popup-panel" wire:click.stop style="max-width:440px;z-index:9101">
                <div class="sg-popup-header">
                    <h3 style="font-weight:700;font-size:13px">💎 جزئیات محصول</h3>
                    <button class="sg-btn-icon" wire:click="closeProduct" type="button">✕</button>
                </div>

                <div class="sg-popup-body" style="padding:0">
                    <div class="sg-prod-image">
                        @if($productDetail['image'])
                            <img src="{{ $productDetail['image'] }}" alt="">
                        @else
                            <span style="font-size:64px;color:#cbd5e1">💎</span>
                        @endif
                    </div>

                    <div style="padding:14px">
                        <div class="sg-prod-title">{{ $productDetail['title'] }}</div>
                        @if($productDetail['sku'])
                            <div class="sg-prod-sku" dir="ltr">SKU: {{ $productDetail['sku'] }}</div>
                        @endif

                        <div class="sg-prod-grid">
                            <div class="sg-prod-cell">
                                <span class="sg-prod-lbl">قیمت واحد</span>
                                <span class="sg-prod-val">{{ number_format((float) $productDetail['price']) }} ت</span>
                            </div>
                            <div class="sg-prod-cell">
                                <span class="sg-prod-lbl">تعداد</span>
                                <span class="sg-prod-val">{{ \App\Support\PersianNumber::toFa($productDetail['quantity']) }}</span>
                            </div>
                            <div class="sg-prod-cell" style="grid-column:span 2;background:rgba(16,185,129,.08)">
                                <span class="sg-prod-lbl">جمع این ردیف</span>
                                <span class="sg-prod-val" style="color:#10b981;font-size:14px">
                                    {{ number_format((float) $productDetail['total']) }} تومان
                                </span>
                            </div>

                            @if($productDetail['weight'])
                                <div class="sg-prod-cell">
                                    <span class="sg-prod-lbl">وزن</span>
                                    <span class="sg-prod-val">{{ $productDetail['weight'] }} گرم</span>
                                </div>
                            @endif
                            @if($productDetail['length'] || $productDetail['width'])
                                <div class="sg-prod-cell">
                                    <span class="sg-prod-lbl">ابعاد</span>
                                    <span class="sg-prod-val">
                                        {{ $productDetail['length'] ?? '—' }} × {{ $productDetail['width'] ?? '—' }} mm
                                    </span>
                                </div>
                            @endif
                            @if($productDetail['metal'])
                                <div class="sg-prod-cell">
                                    <span class="sg-prod-lbl">فلز</span>
                                    <span class="sg-prod-val">{{ $productDetail['metal'] }} @if($productDetail['carat']) - {{ $productDetail['carat'] }}@endif</span>
                                </div>
                            @endif
                            @if($productDetail['stone'])
                                <div class="sg-prod-cell">
                                    <span class="sg-prod-lbl">سنگ</span>
                                    <span class="sg-prod-val">{{ $productDetail['stone'] }}</span>
                                </div>
                            @endif
                            @if($productDetail['updated'])
                                <div class="sg-prod-cell">
                                    <span class="sg-prod-lbl">آخرین به‌روزرسانی</span>
                                    <span class="sg-prod-val">{{ $productDetail['updated'] }}</span>
                                </div>
                            @endif
                        </div>
                    </div>
                </div>

                <div class="sg-popup-footer" style="display:flex;gap:8px;justify-content:flex-end">
                    <button type="button" class="sg-btn sg-btn-ghost" wire:click="closeProduct">بستن</button>
                    @if($productDetail['site_url'])
                        <a href="{{ $productDetail['site_url'] }}" target="_blank"
                           class="sg-btn sg-btn-primary" style="text-decoration:none">
                            🔗 مشاهده در سایت
                        </a>
                    @endif
                </div>
            </div>
        </div>
    @endif
</div>