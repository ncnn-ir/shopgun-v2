<div class="sg-dashboard">

    {{-- ═══ Header + Range ═══ --}}
    <div class="sg-dash-header">
        <h1 class="sg-dash-title">🏠 داشبورد</h1>
        <div class="sg-range-tabs">
            @foreach(['today'=>'امروز','week'=>'۷ روز','month'=>'۳۰ روز','year'=>'سال'] as $k => $lbl)
                <button wire:click="setRange('{{ $k }}')"
                        class="sg-range-btn {{ $range === $k ? 'active' : '' }}">
                    {{ $lbl }}
                </button>
            @endforeach
        </div>
    </div>

    {{-- ═══ KPI Strip — مینیمال یک‌خطی با اسکرول افقی ═══ --}}
    <div class="sg-kpi-strip">
        @foreach($kpi as $k)
            <a href="{{ $k['route'] }}" wire:navigate class="sg-kpi-card" style="--kpi-color:{{ $k['color'] }}">
                <div class="sg-kpi-head">
                    <span class="sg-kpi-icon">{{ $k['icon'] }}</span>
                    <span class="sg-kpi-label">{{ $k['label'] }}</span>
                </div>

                <div class="sg-kpi-value">
                    @if($k['format'] === 'money')
                        {{ number_format($k['value'] / 1000000, 1) }}<small>م</small>
                    @else
                        {{ \App\Support\PersianNumber::toFa($k['value']) }}
                    @endif
                </div>

                <div class="sg-kpi-foot">
                    @if($k['yesterday'] !== null)
                        <span class="sg-kpi-yest">
                            دیروز:
                            @if($k['format'] === 'money')
                                {{ number_format($k['yesterday'] / 1000000, 1) }}م
                            @else
                                {{ \App\Support\PersianNumber::toFa($k['yesterday']) }}
                            @endif
                        </span>

                        @php $t = $k['trend']; @endphp
                        @if($t['dir'] === 'up')
                            <span class="sg-kpi-trend up">▲ {{ \App\Support\PersianNumber::toFa($t['pct']) }}٪</span>
                        @elseif($t['dir'] === 'down')
                            <span class="sg-kpi-trend down">▼ {{ \App\Support\PersianNumber::toFa($t['pct']) }}٪</span>
                        @else
                            <span class="sg-kpi-trend flat">—</span>
                        @endif
                    @else
                        <span class="sg-kpi-yest">—</span>
                    @endif
                </div>
            </a>
        @endforeach
    </div>

    {{-- ═══ Chart ═══ --}}
    <div class="sg-card" style="margin-bottom:16px">
        <div class="sg-card-head">
            <h3>📈 روند {{ ['today'=>'امروز','week'=>'هفته','month'=>'ماه','year'=>'سال'][$range] ?? '' }}</h3>
            <span class="sg-card-sub">تعداد سفارش</span>
        </div>

        @php $maxVal = max(collect($series)->max('count') ?: 1, 1); @endphp

        <div class="sg-chart">
            @foreach($series as $d)
                @php $h = max(3, ($d['count'] / $maxVal) * 100); @endphp
                <div class="sg-chart-col" title="{{ $d['count'] }} سفارش">
                    <div class="sg-chart-val">{{ $d['count'] > 0 ? \App\Support\PersianNumber::toFa($d['count']) : '' }}</div>
                    <div class="sg-chart-bar" style="height:{{ $h }}%"></div>
                    <div class="sg-chart-lbl">{{ $d['date'] }}</div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- ═══ Channel Breakdown ═══ --}}
    @if(!empty($byChannel))
        <div class="sg-card" style="margin-bottom:16px">
            <div class="sg-card-head">
                <h3>🎯 فروش بر اساس کانال</h3>
            </div>
            <div class="sg-channel-list">
                @php $totalChannel = collect($byChannel)->sum('count') ?: 1; @endphp
                @foreach($byChannel as $ch)
                    @php $pct = round(($ch['count'] / $totalChannel) * 100, 1); @endphp
                    <div class="sg-channel-row">
                        <div class="sg-channel-info">
                            <span class="sg-channel-dot" style="background:{{ $ch['color'] }}"></span>
                            <span class="sg-channel-name">{{ $ch['name'] }}</span>
                            <span class="sg-channel-count">{{ \App\Support\PersianNumber::toFa($ch['count']) }}</span>
                        </div>
                        <div class="sg-channel-bar">
                            <div style="width:{{ $pct }}%;background:{{ $ch['color'] }}"></div>
                        </div>
                        <div class="sg-channel-pct">{{ \App\Support\PersianNumber::toFa($pct) }}٪</div>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- ═══ Recent Orders ═══ --}}
    <div class="sg-card">
        <div class="sg-card-head">
            <h3>🕐 آخرین سفارشات</h3>
            <a href="{{ route('orders.index') }}" wire:navigate class="sg-card-link">مشاهده همه →</a>
        </div>

        <div class="sg-recent-list">
            @forelse($recent as $o)
                <div class="sg-recent-row"
                     onclick="Livewire.dispatch('open-order-view', { orderId: {{ $o->id }} })">
                    <div class="sg-recent-right">
                        <span class="sg-recent-num">#{{ $o->order_number }}</span>
                        <span class="sg-recent-cust">{{ $o->customer?->name ?? '—' }}</span>
                    </div>

                    <div class="sg-recent-mid">
                        @php
                            $stColor = \App\Support\OrderStatus::color($o->status ?? 'pending');
                            $stLabel = \App\Support\OrderStatus::label($o->status ?? 'pending');
                        @endphp
                        <span class="sg-status-badge" style="color:{{ $stColor }};background:color-mix(in srgb,{{ $stColor }} 15%,transparent)">
                            {{ $stLabel }}
                        </span>
                    </div>

                    <div class="sg-recent-left">
                        <span class="sg-recent-amount">{{ number_format((float) $o->amount) }}</span>
                        <span class="sg-recent-date">{{ \App\Support\PersianDate::format($o->created_at, 'm/d') }}</span>
                    </div>
                </div>
            @empty
                <div class="sg-empty">سفارشی ثبت نشده</div>
            @endforelse
        </div>
    </div>
</div>