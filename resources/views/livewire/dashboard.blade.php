<div style="padding:10px;direction:rtl;max-width:100%;overflow-x:hidden;box-sizing:border-box">

    {{-- ═══ Header + Range Filter ═══ --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px">
        <h1 style="margin:0;font-size:18px;font-weight:700">🏠 داشبورد</h1>
        <div style="display:flex;gap:4px;flex-wrap:wrap">
            @foreach(['today'=>'امروز','yesterday'=>'دیروز','week'=>'۷ روز','month'=>'۳۰ روز','year'=>'سال'] as $k => $lbl)
                <button wire:click="setRange('{{ $k }}')"
                        style="padding:5px 10px;border-radius:8px;font-weight:700;cursor:pointer;font-size:11px;border:1.5px solid {{ $range === $k ? '#1a5276' : '#e2e8f0' }};background:{{ $range === $k ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#fff' }};color:{{ $range === $k ? '#fff' : '#64748b' }}">
                    {{ $lbl }}
                </button>
            @endforeach
        </div>
    </div>

    {{-- ═══ KPI Cards (Horizontal Scroll) ═══ --}}
    <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:10px;margin-bottom:12px;scrollbar-width:thin;-webkit-overflow-scrolling:touch">
        @foreach($kpi as $k)
            <a href="{{ $k['route'] }}" wire:navigate
               style="flex:0 0 auto;min-width:125px;padding:10px;border-radius:12px;text-decoration:none;background:#fff;border:1.5px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,.04);transition:all .15s">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
                    <div style="width:28px;height:28px;border-radius:8px;background:{{ $k['color'] }}20;color:{{ $k['color'] }};display:flex;align-items:center;justify-content:center;font-size:14px">
                        {{ $k['icon'] }}
                    </div>
                </div>
                <div style="font-size:17px;font-weight:800;color:{{ $k['color'] }};line-height:1;font-variant-numeric:tabular-nums">
                    {{ \App\Support\PersianNumber::toFa(number_format($k['value'], is_int($k['value']) ? 0 : 1)) }}
                </div>
                <div style="font-size:10px;color:#64748b;font-weight:700;margin-top:3px">{{ $k['label'] }}</div>
            </a>
        @endforeach
    </div>

    {{-- ═══ Access Cards (Quick Links) ═══ --}}
    <div style="margin-bottom:12px">
        <h3 style="font-size:13px;font-weight:700;color:#1a5276;margin:0 0 8px">🚀 دسترسی سریع</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px">
            @foreach($accessCards as $card)
                <a href="{{ $card['route'] }}" wire:navigate
                   style="padding:10px 6px;border-radius:10px;background:#fff;border:1.5px solid #e2e8f0;text-decoration:none;text-align:center;transition:all .15s;display:block">
                    <div style="font-size:20px;margin-bottom:4px">{{ $card['icon'] }}</div>
                    <div style="font-size:10px;font-weight:700;color:{{ $card['color'] }}">{{ $card['label'] }}</div>
                </a>
            @endforeach
        </div>
    </div>

    {{-- ═══ Sales Trend Chart ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <h3 style="margin:0;font-size:13px;font-weight:700;color:#1a5276">📈 نمودار فروش — {{ $label }}</h3>
            <span style="font-size:10px;color:#94a3b8">میلیون تومان</span>
        </div>

        @php $maxVal = max(collect($salesTrend)->max('total') ?: 1, 0.1); @endphp

        @if(empty($salesTrend))
            <div style="text-align:center;padding:30px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
        @else
            <div style="display:flex;align-items:flex-end;gap:3px;height:140px;padding:10px 0;overflow-x:auto;scrollbar-width:thin">
                @foreach($salesTrend as $d)
                    @php
                        $pct = $maxVal > 0 ? ($d['total'] / $maxVal) * 100 : 0;
                        $h = max(2, $pct);
                    @endphp
                    <div style="flex:0 0 auto;min-width:20px;display:flex;flex-direction:column;align-items:center;gap:3px">
                        <div style="font-size:8.5px;color:#1a5276;font-weight:700;font-family:monospace">
                            {{ $d['total'] > 0 ? number_format($d['total'], 1) : '' }}
                        </div>
                        <div style="width:100%;height:{{ $h }}%;min-height:4px;background:linear-gradient(180deg,#14b8a6,#0891b2);border-radius:4px 4px 0 0"
                             title="{{ $d['count'] }} سفارش"></div>
                        <div style="font-size:8px;color:#94a3b8;font-family:monospace;white-space:nowrap">{{ $d['label'] }}</div>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- ═══ Channel Breakdown ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <h3 style="margin:0 0 12px;font-size:13px;font-weight:700;color:#1a5276">🎯 فروش بر اساس کانال</h3>

        @if(empty($salesByChannel))
            <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
        @else
            <div style="display:flex;flex-direction:column;gap:8px;max-height:230px;overflow-y:auto">
                @foreach($salesByChannel as $ch)
                    <div>
                        <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px;flex-wrap:wrap;gap:3px">
                            <span style="font-weight:700;color:#1e293b">
                                {{ $ch['label'] }}
                                <span style="color:#94a3b8;font-size:9.5px">({{ \App\Support\PersianNumber::toFa($ch['count']) }})</span>
                            </span>
                            <span style="color:{{ $ch['color'] }};font-weight:700;font-family:monospace;font-size:10.5px">
                                {{ number_format($ch['total'] / 1000000, 1) }}M
                                <span style="color:#94a3b8;font-size:9.5px">({{ \App\Support\PersianNumber::toFa($ch['percent']) }}%)</span>
                            </span>
                        </div>
                        <div style="height:5px;background:#f1f5f9;border-radius:3px;overflow:hidden">
                            <div style="height:100%;width:{{ $ch['percent'] }}%;background:{{ $ch['color'] }};border-radius:3px"></div>
                        </div>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- ═══ Cancel Ratio ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <h3 style="margin:0 0 12px;font-size:13px;font-weight:700;color:#1a5276">📊 نسبت سفارشات — {{ $label }}</h3>

        @php
            $pctSuccess = $cancelRatio['success_pct'];
            $pctCancelled = $cancelRatio['cancelled_pct'];
            $pctPending = $cancelRatio['pending_pct'];
        @endphp

        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px">
            <div style="padding:8px;background:#d1fae5;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($cancelRatio['success']) }}</div>
                <div style="font-size:9.5px;color:#065f46;font-weight:700">✅ {{ \App\Support\PersianNumber::toFa($pctSuccess) }}%</div>
            </div>
            <div style="padding:8px;background:#fee2e2;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($cancelRatio['cancelled']) }}</div>
                <div style="font-size:9.5px;color:#991b1b;font-weight:700">❌ {{ \App\Support\PersianNumber::toFa($pctCancelled) }}%</div>
            </div>
            <div style="padding:8px;background:#fef3c7;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($cancelRatio['pending']) }}</div>
                <div style="font-size:9.5px;color:#92400e;font-weight:700">⏳ {{ \App\Support\PersianNumber::toFa($pctPending) }}%</div>
            </div>
        </div>

        <div style="display:flex;height:14px;border-radius:7px;overflow:hidden;background:#f1f5f9">
            <div style="width:{{ $pctSuccess }}%;background:#10b981;height:100%"></div>
            <div style="width:{{ $pctCancelled }}%;background:#ef4444;height:100%"></div>
            <div style="width:{{ $pctPending }}%;background:#f59e0b;height:100%"></div>
        </div>
    </div>

    {{-- ═══ Top Products (5 rows + scroll) ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <h3 style="margin:0 0 10px;font-size:13px;font-weight:700;color:#1a5276">🏆 پرفروش‌ترین محصولات</h3>

        @if(empty($topProducts))
            <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
        @else
            <div style="display:flex;flex-direction:column;gap:4px;max-height:210px;overflow-y:auto;padding-right:4px">
                @foreach($topProducts as $i => $p)
                    <div wire:click="showProduct(@js($p['title']), '')"
                         style="display:flex;align-items:center;gap:6px;padding:5px 8px;background:#f8fafc;border-radius:6px;cursor:pointer;font-size:11px;flex-wrap:nowrap">
                        <span style="width:18px;height:18px;border-radius:50%;background:{{ $i < 3 ? '#c9a84c' : '#cbd5e1' }};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:9px;flex-shrink:0">
                            {{ \App\Support\PersianNumber::toFa($i + 1) }}
                        </span>
                        <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:700">{{ $p['title'] }}</span>
                        <span style="background:#dbeafe;color:#1e40af;padding:1px 6px;border-radius:6px;font-size:9.5px;font-weight:700;flex-shrink:0">
                            ×{{ \App\Support\PersianNumber::toFa($p['count']) }}
                        </span>
                        <span style="color:#16a34a;font-family:monospace;font-size:10px;font-weight:700;flex-shrink:0">
                            {{ number_format($p['total'] / 1000000, 1) }}M
                        </span>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- ═══ Top Customers (5 rows + scroll) ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <h3 style="margin:0 0 10px;font-size:13px;font-weight:700;color:#1a5276">⭐ بهترین مشتریان</h3>

        @if(empty($topCustomers))
            <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
        @else
            <div style="display:flex;flex-direction:column;gap:4px;max-height:210px;overflow-y:auto;padding-right:4px">
                @foreach($topCustomers as $c)
                    <div onclick="Livewire.dispatch('open-customer-profile', {customerId: {{ $c['id'] }}})"
                         style="display:flex;align-items:center;gap:6px;padding:5px 8px;background:#f8fafc;border-radius:6px;cursor:pointer;font-size:11px">
                        <div style="width:22px;height:22px;border-radius:50%;background:linear-gradient(135deg,#14b8a6,#0891b2);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:10px;flex-shrink:0">
                            {{ mb_substr($c['name'] ?? '?', 0, 1) }}
                        </div>
                        <div style="flex:1;min-width:0">
                            <div style="font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $c['name'] ?: 'بدون نام' }}</div>
                            <div style="font-family:monospace;font-size:9px;color:#94a3b8" dir="ltr">{{ $c['phone'] }}</div>
                        </div>
                        <span style="background:#d1fae5;color:#065f46;padding:1px 6px;border-radius:6px;font-size:9.5px;font-weight:700;flex-shrink:0">
                            {{ \App\Support\PersianNumber::toFa($c['orders_count']) }}
                        </span>
                        <span style="color:#16a34a;font-family:monospace;font-size:10px;font-weight:700;flex-shrink:0">
                            {{ number_format($c['total'] / 1000000, 1) }}M
                        </span>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- ═══ Pending Supply Orders (5 rows + scroll) ═══ --}}
    @if(!empty($pendingSupply))
        <div style="background:#fff;border:2px solid #f59e0b;border-radius:12px;padding:14px;margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:6px">
                <h3 style="margin:0;font-size:13px;font-weight:700;color:#92400e">
                    ⏳ در انتظار تامین ({{ \App\Support\PersianNumber::toFa(count($pendingSupply)) }})
                </h3>
                <a href="{{ route('orders.index') }}" wire:navigate style="font-size:10.5px;color:#1e40af;font-weight:700;text-decoration:none">مشاهده همه →</a>
            </div>

            <div style="display:flex;flex-direction:column;gap:6px;max-height:400px;overflow-y:auto;padding-right:4px">
                @foreach($pendingSupply as $o)
                    <div style="padding:8px;background:#fffbeb;border:1px solid #fef3c7;border-radius:8px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:4px">
                            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                                <span onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o['id'] }}})"
                                      style="font-family:monospace;font-weight:700;font-size:11.5px;cursor:pointer;color:#1e40af;text-decoration:underline dotted">
                                    #{{ $o['num'] }}
                                </span>
                                <span style="font-size:10.5px;color:#78350f">{{ $o['customer'] }}</span>
                            </div>
                            <button wire:click="markSupplied({{ $o['id'] }})"
                                    wire:confirm="تایید شد؟"
                                    style="padding:3px 10px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:10px">
                                ✓ تحویل واحد ارسال
                            </button>
                        </div>
                        <div style="display:flex;flex-direction:column;gap:2px">
                            @foreach($o['items'] as $it)
                                <div wire:click="showProduct(@js($it['title']), @js($it['sku'] ?? ''))"
                                     style="display:flex;align-items:center;gap:6px;padding:3px 6px;background:#fff;border-radius:5px;font-size:10.5px;cursor:pointer">
                                    <span style="width:18px;height:18px;background:#f1f5f9;border-radius:3px;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0">💎</span>
                                    <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:700">{{ $it['title'] }}</span>
                                    <span style="background:#fef3c7;color:#92400e;padding:0 5px;border-radius:5px;font-size:9px;font-weight:700;flex-shrink:0">×{{ \App\Support\PersianNumber::toFa($it['qty']) }}</span>
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- ═══ Recent Orders by Channel (5 rows scroll) ═══ --}}
    @if(!empty($recentByChannel))
        <div style="margin-bottom:12px">
            <h3 style="font-size:13px;font-weight:700;color:#1a5276;margin:0 0 8px">🕐 آخرین تراکنش‌ها به تفکیک کانال</h3>

            <div style="display:flex;flex-direction:column;gap:10px">
                @foreach($recentByChannel as $ch)
                    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;max-width:100%">
                        <div style="padding:6px 10px;background:linear-gradient(135deg,{{ $ch['color'] }}20,{{ $ch['color'] }}10);border-bottom:1px solid {{ $ch['color'] }}30;display:flex;justify-content:space-between;align-items:center">
                            <div style="display:flex;align-items:center;gap:6px">
                                <span style="width:8px;height:8px;border-radius:50%;background:{{ $ch['color'] }}"></span>
                                <span style="font-weight:700;color:#1e293b;font-size:11.5px">{{ $ch['label'] }}</span>
                                <span style="background:{{ $ch['color'] }}20;color:{{ $ch['color'] }};padding:1px 6px;border-radius:6px;font-size:9.5px;font-weight:700">
                                    {{ \App\Support\PersianNumber::toFa($ch['count']) }}
                                </span>
                            </div>
                        </div>
                        <div style="overflow-x:auto;overflow-y:auto;max-height:180px;scrollbar-width:thin">
                            <table style="width:100%;border-collapse:collapse;font-size:10.5px;min-width:400px">
                                <thead style="background:#fafafa;position:sticky;top:0;z-index:2">
                                    <tr>
                                        <th style="padding:4px 6px;text-align:right;color:#64748b;font-size:9.5px">#</th>
                                        <th style="padding:4px 6px;text-align:right;color:#64748b;font-size:9.5px">مشتری</th>
                                        <th style="padding:4px 6px;text-align:right;color:#64748b;font-size:9.5px">مبلغ</th>
                                        <th style="padding:4px 6px;text-align:right;color:#64748b;font-size:9.5px">وضعیت</th>
                                        <th style="padding:4px 6px;text-align:right;color:#64748b;font-size:9.5px">تاریخ</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach($ch['orders'] as $o)
                                        <tr onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o['id'] }}})"
                                            style="border-bottom:1px solid #f1f5f9;cursor:pointer">
                                            <td style="padding:4px 6px;font-family:monospace;font-weight:700;color:#1e40af">#{{ $o['num'] }}</td>
                                            <td style="padding:4px 6px;font-weight:700;max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $o['customer'] }}</td>
                                            <td style="padding:4px 6px;font-family:monospace;color:#16a34a">{{ number_format($o['amount']) }}</td>
                                            <td style="padding:4px 6px">
                                                @php
                                                    $stMap = ['pending'=>['📝','ثبت','#f59e0b'],'final-check'=>['🔍','چک','#3b82f6'],'courier'=>['🚚','مامور','#10b981']];
                                                    $st = $stMap[$o['status']] ?? ['📝','ثبت','#f59e0b'];
                                                @endphp
                                                <span style="background:{{ $st[2] }}20;color:{{ $st[2] }};padding:1px 5px;border-radius:5px;font-size:9px;font-weight:700;white-space:nowrap">
                                                    {{ $st[0] }} {{ $st[1] }}
                                                </span>
                                            </td>
                                            <td style="padding:4px 6px;font-family:monospace;font-size:9.5px;color:#94a3b8;white-space:nowrap">{{ $o['date'] }}</td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- ═══ Product Popup ═══ --}}
    @if($showProductPopup && $productDetail)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:95;display:flex;align-items:center;justify-content:center;padding:14px"
             wire:click="closeProduct" @keydown.escape.window="$wire.closeProduct()">
            <div style="background:#fff;border-radius:14px;max-width:340px;width:100%;overflow:hidden" wire:click.stop>
                <div style="aspect-ratio:1;background:#f8fafc;display:flex;align-items:center;justify-content:center;overflow:hidden">
                    @if($productDetail['image'])
                        <img src="{{ $productDetail['image'] }}" style="width:100%;height:100%;object-fit:cover">
                    @else
                        <span style="font-size:60px;color:#cbd5e1">💎</span>
                    @endif
                </div>
                <div style="padding:12px">
                    <div style="font-weight:700;font-size:14px;margin-bottom:6px;color:#1e293b">{{ $productDetail['title'] }}</div>
                    @if($productDetail['sku'])
                        <div style="font-family:monospace;font-size:11px;color:#94a3b8;margin-bottom:8px" dir="ltr">SKU: {{ $productDetail['sku'] }}</div>
                    @endif
                    <button wire:click="closeProduct" style="width:100%;padding:8px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">بستن</button>
                </div>
            </div>
        </div>
    @endif
</div>
