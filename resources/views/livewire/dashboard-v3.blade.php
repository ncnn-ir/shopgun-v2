<div style="direction:rtl">

    {{-- Header --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px">
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700;color:var(--sg-text)">📊 داشبورد</h1>
            <p style="margin:4px 0 0;font-size:11.5px;color:var(--sg-text-muted)">
                نمای کلی · {{ \App\Support\PersianDate::format(now(), 'Y/m/d') }}
            </p>
        </div>
        <div style="display:flex;gap:4px;background:var(--sg-bg-soft);padding:3px;border-radius:10px">
            @foreach(['today'=>'امروز','week'=>'۷ روز'] as $k=>$v)
                <button wire:click="setRange('{{ $k }}')"
                        style="padding:6px 14px;border-radius:8px;border:none;font-size:11.5px;font-weight:700;cursor:pointer;transition:var(--sg-t-fast);
                            background:{{ $range===$k ? 'var(--sg-primary)' : 'transparent' }};
                            color:{{ $range===$k ? '#fff' : 'var(--sg-text-secondary)' }}">
                    {{ $v }}
                </button>
            @endforeach
        </div>
    </div>

    {{-- ═══ KPI Strip — Minimal + Scrollable ═══ --}}
    <livewire:components.kpi-strip :items="$kpi" :key="'kpi-' . $range" />

    {{-- ═══ Chart ═══ --}}
    <div class="sg-card" style="margin:14px 0">
        <div class="sg-card-head">
            <h3>📈 نمودار سفارشات</h3>
            <span style="font-size:11px;color:var(--sg-text-muted)">
                جمع کل: {{ \App\Support\PersianNumber::toFa(collect($series)->sum('count')) }}
            </span>
        </div>

        @php 
            $maxCount = collect($series)->max('count') ?: 1; 
            $avgCount = count($series) > 0 ? collect($series)->avg('count') : 0;
        @endphp

        <div style="display:flex;align-items:flex-end;gap:6px;height:180px;padding-top:24px;overflow-x:auto;scrollbar-width:thin">
            @foreach($series as $d)
                @php 
                    $h = $maxCount > 0 ? ($d['count'] / $maxCount) * 100 : 0; 
                    $h = max(4, $h);
                    $isToday = $loop->last;
                    $isAboveAvg = $d['count'] > $avgCount;
                @endphp
                <div style="flex:1;min-width:36px;display:flex;flex-direction:column;align-items:center;gap:4px;justify-content:flex-end;height:100%">
                    <div style="font-size:11px;font-weight:700;color:{{ $isAboveAvg ? 'var(--sg-success)' : 'var(--sg-primary)' }};font-family:var(--sg-font-mono)">
                        {{ $d['count'] > 0 ? \App\Support\PersianNumber::toFa($d['count']) : '' }}
                    </div>
                    <div style="width:100%;background:{{ $isToday ? 'linear-gradient(to top,#c9a84c,#f0d68a)' : 'linear-gradient(to top,var(--sg-primary),var(--sg-primary-light, #2980b9))' }};border-radius:6px 6px 0 0;transition:all .3s;height:{{ $h }}%"></div>
                    <div style="font-size:9px;color:var(--sg-text-muted);font-family:var(--sg-font-mono);white-space:nowrap">{{ $d['date'] }}</div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- ═══ Row: Channels + Recent ═══ --}}
    <div style="display:grid;grid-template-columns:1fr;gap:14px">

        {{-- Channels --}}
        @if(count($byChannel))
            <div class="sg-card">
                <div class="sg-card-head">
                    <h3>🌐 کانال‌های فروش (۳۰ روز)</h3>
                </div>
                @php $chTotal = collect($byChannel)->sum('count') ?: 1; @endphp
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px">
                    @foreach($byChannel as $ch)
                        <div style="padding:10px;background:var(--sg-bg-soft);border-radius:10px;border-right:4px solid {{ $ch['color'] }}">
                            <div style="font-weight:700;font-size:12.5px">{{ $ch['name'] }}</div>
                            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:4px">
                                <span style="font-size:18px;font-weight:800;color:{{ $ch['color'] }};font-family:var(--sg-font-mono)">
                                    {{ \App\Support\PersianNumber::toFa($ch['count']) }}
                                </span>
                                <span style="font-size:10.5px;color:var(--sg-text-muted)">
                                    {{ \App\Support\PersianNumber::toFa(round(($ch['count'] / $chTotal) * 100)) }}%
                                </span>
                            </div>
                        </div>
                    @endforeach
                </div>
            </div>
        @endif

        {{-- Recent --}}
        <div class="sg-card">
            <div class="sg-card-head">
                <h3>🕐 آخرین سفارشات</h3>
                <a href="{{ route('orders.index') }}" wire:navigate style="font-size:11px;color:var(--sg-primary);font-weight:700;text-decoration:none">
                    مشاهده همه ←
                </a>
            </div>

            @if($recent->isEmpty())
                <div style="text-align:center;padding:30px;color:var(--sg-text-muted)">
                    <div style="font-size:36px;opacity:.4">📦</div>
                    <div style="font-size:12px;margin-top:6px">سفارشی نیست</div>
                </div>
            @else
                <div style="display:flex;flex-direction:column;gap:6px">
                    @foreach($recent as $o)
                        <div wire:key="r-{{ $o->id }}" 
                             onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o->id }}})"
                             style="padding:10px;background:var(--sg-bg-soft);border-radius:10px;cursor:pointer;transition:var(--sg-t-fast)"
                             onmouseover="this.style.background='var(--sg-bg-card)';this.style.boxShadow='var(--sg-shadow-sm)'"
                             onmouseout="this.style.background='var(--sg-bg-soft)';this.style.boxShadow=''">
                            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
                                <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
                                    <span style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-primary);font-size:11.5px">#{{ $o->order_number }}</span>
                                    <span style="font-weight:700;font-size:12px" class="sg-truncate">{{ $o->customer_name ?? '—' }}</span>
                                    @if($o->channel)
                                        <span style="padding:2px 8px;border-radius:99px;font-size:9.5px;font-weight:700;color:#fff;background:{{ $o->channel->color ?? '#64748b' }}">{{ $o->channel->icon }}</span>
                                    @endif
                                </div>
                                <div style="display:flex;align-items:center;gap:6px">
                                    <span style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-success);font-size:11px">{{ number_format($o->amount ?? 0) }}</span>
                                    @php $st = \App\Support\OrderStatus::FLOW[$o->status ?? 'pending'] ?? \App\Support\OrderStatus::FLOW['pending']; @endphp
                                    <span style="padding:2px 8px;border-radius:99px;font-size:9.5px;font-weight:700;color:#fff;background:{{ $st['color'] }}">{{ $st['icon'] }}</span>
                                </div>
                            </div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>
