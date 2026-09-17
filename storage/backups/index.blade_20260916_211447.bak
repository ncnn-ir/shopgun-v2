<div>
    <div style="padding:0 18px 14px">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
            <h1 style="font-size:20px;font-weight:700">📊 گزارش‌ها</h1>
            <a href="{{ route('reports.export.excel', ['range' => $range]) }}" class="btn btn-outline btn-sm">📥 CSV</a>
        </div>
    </div>

    <div class="sg-filters-bar">
        @foreach(['today'=>'امروز','week'=>'۷ روز','month'=>'۳۰ روز','year'=>'سال'] as $key => $label)
            <button wire:click="setRange('{{ $key }}')" class="sg-chip {{ $range === $key ? 'active' : '' }}">{{ $label }}</button>
        @endforeach
    </div>

    {{-- KPI Stats Row --}}
    <div class="sg-stats-row">
        @foreach($stats as $s)
            <div class="sg-stat-card">
                <div class="top-row">
                    <div class="icon" style="background:{{ $s['color'] }}">{{ $s['icon'] }}</div>
                    @php $t = $s['trend']; @endphp
                    @if($t['dir'] === 'up')
                        <span class="trend up">▲ {{ \App\Support\PersianNumber::toFa($t['pct']) }}%</span>
                    @elseif($t['dir'] === 'down')
                        <span class="trend down">▼ {{ \App\Support\PersianNumber::toFa($t['pct']) }}%</span>
                    @else
                        <span class="trend flat">—</span>
                    @endif
                </div>
                <div class="num">
                    @if(!empty($s['raw']))
                        {{ \App\Support\PersianNumber::toFa(number_format($s['num'])) }}
                    @else
                        {{ \App\Support\PersianNumber::toFa(number_format($s['num'], $s['dec'] ?? 1)) }}
                    @endif
                </div>
                <div class="lbl">{{ $s['lbl'] }}</div>
            </div>
        @endforeach
    </div>

    <div class="sg-chart-grid">
        {{-- Bar Chart with horizontal scroll --}}
        <div class="sg-chart-card">
            <h3>📈 سفارشات {{ $rangeLabel }}</h3>
            @php $maxOrders = collect($daily)->max('orders') ?: 1; @endphp
            <div class="sg-chart-scroll">
                <div class="sg-bar-chart" style="min-width:{{ count($daily) * 32 }}px">
                    @foreach($daily as $d)
                        <div class="bar-wrap" style="min-width:28px">
                            <div class="bar-val">{{ $d['orders'] > 0 ? \App\Support\PersianNumber::toFa($d['orders']) : '' }}</div>
                            <div class="bar" style="height:{{ max(4, $d['orders'] / $maxOrders * 100) }}%"></div>
                            <div class="bar-lbl">{{ $d['date'] }}</div>
                        </div>
                    @endforeach
                </div>
            </div>
        </div>

        {{-- Line Chart: Certificates vs Orders --}}
        <div class="sg-chart-card">
            <h3>💎 خط صدور شناسنامه vs خرید</h3>
            @php
                $maxVal = max(collect($daily)->max('certs') ?: 1, collect($daily)->max('orders') ?: 1);
                $n = count($daily);
                $w = max(400, $n * 34);
                $h = 140;
                $pad = 10;
                $stepX = ($w - $pad * 2) / max(1, $n - 1);
                $ordersPath = '';
                $certsPath = '';
                foreach ($daily as $i => $d) {
                    $x = $pad + ($i * $stepX);
                    $yO = $h - $pad - ($d['orders'] / $maxVal * ($h - $pad * 2));
                    $yC = $h - $pad - ($d['certs'] / $maxVal * ($h - $pad * 2));
                    $ordersPath .= ($i === 0 ? 'M' : 'L') . $x . ' ' . $yO . ' ';
                    $certsPath .= ($i === 0 ? 'M' : 'L') . $x . ' ' . $yC . ' ';
                }
            @endphp
            <div class="sg-chart-scroll">
                <svg width="{{ $w }}" height="{{ $h + 24 }}" style="display:block">
                    {{-- Grid lines --}}
                    @for($g = 0; $g <= 4; $g++)
                        @php $gy = $pad + (($h - $pad * 2) * $g / 4); @endphp
                        <line x1="{{ $pad }}" y1="{{ $gy }}" x2="{{ $w - $pad }}" y2="{{ $gy }}" stroke="rgba(0,0,0,.06)" stroke-width="1"/>
                    @endfor

                    {{-- Orders line --}}
                    <path d="{{ $ordersPath }}" fill="none" stroke="#14b8a6" stroke-width="2.5" stroke-linejoin="round"/>
                    {{-- Certs line --}}
                    <path d="{{ $certsPath }}" fill="none" stroke="#c9a84c" stroke-width="2.5" stroke-linejoin="round" stroke-dasharray="5,3"/>

                    {{-- Points + labels --}}
                    @foreach($daily as $i => $d)
                        @php
                            $x = $pad + ($i * $stepX);
                            $yO = $h - $pad - ($d['orders'] / $maxVal * ($h - $pad * 2));
                            $yC = $h - $pad - ($d['certs'] / $maxVal * ($h - $pad * 2));
                        @endphp
                        <circle cx="{{ $x }}" cy="{{ $yO }}" r="3" fill="#14b8a6"/>
                        <circle cx="{{ $x }}" cy="{{ $yC }}" r="3" fill="#c9a84c"/>
                        <text x="{{ $x }}" y="{{ $h + 18 }}" text-anchor="middle" font-size="9" fill="rgba(0,0,0,.5)" font-family="monospace">{{ $d['date'] }}</text>
                    @endforeach
                </svg>
            </div>
            <div class="sg-legend" style="margin-top:10px">
                <div class="item"><span class="dot" style="background:#14b8a6"></span> سفارشات</div>
                <div class="item"><span class="dot" style="background:#c9a84c"></span> شناسنامه</div>
            </div>
        </div>

        {{-- By Status --}}
        <div class="sg-chart-card">
            <h3>🚦 وضعیت سفارشات</h3>
            @php
                $total = array_sum($byStatus) ?: 1;
                $a1 = ($byStatus['pending'] / $total) * 360;
                $a2 = $a1 + (($byStatus['final-check'] / $total) * 360);
                $a3 = $a2 + (($byStatus['courier'] / $total) * 360);
            @endphp
            <div class="sg-donut" style="--a1:{{ $a1 }}deg;--a2:{{ $a2 }}deg;--a3:{{ $a3 }}deg">
                <div class="center-text">
                    <div class="num">{{ \App\Support\PersianNumber::toFa(array_sum($byStatus)) }}</div>
                    <div class="lbl">کل</div>
                </div>
            </div>
            <div class="sg-legend">
                <div class="item"><span class="dot" style="background:#f59e0b"></span> ثبت ({{ \App\Support\PersianNumber::toFa($byStatus['pending']) }})</div>
                <div class="item"><span class="dot" style="background:#3b82f6"></span> چک ({{ \App\Support\PersianNumber::toFa($byStatus['final-check']) }})</div>
                <div class="item"><span class="dot" style="background:#14b8a6"></span> مامور ({{ \App\Support\PersianNumber::toFa($byStatus['courier']) }})</div>
            </div>
        </div>

        {{-- By Channel --}}
        @if(count($byChannel))
            <div class="sg-chart-card">
                <h3>🌐 کانال‌های فروش</h3>
                @php $chTotal = collect($byChannel)->sum('count') ?: 1; @endphp
                @foreach($byChannel as $ch)
                    <div style="margin-bottom:8px">
                        <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:3px">
                            <span style="font-weight:700">{{ $ch['name'] }}</span>
                            <span style="color:{{ $ch['color'] }};font-weight:700">{{ \App\Support\PersianNumber::toFa($ch['count']) }} ({{ round($ch['count'] / $chTotal * 100) }}%)</span>
                        </div>
                        <div style="height:6px;background:rgba(0,0,0,.05);border-radius:3px;overflow:hidden">
                            <div style="height:100%;width:{{ $ch['count'] / $chTotal * 100 }}%;background:{{ $ch['color'] }};border-radius:3px"></div>
                        </div>
                    </div>
                @endforeach
            </div>
        @endif

        {{-- Top Products --}}
        <div class="sg-chart-card">
            <h3>🏆 پرفروش‌ترین‌ها</h3>
            @if(count($topProducts))
                <table class="sg-mini-table">
                    <thead><tr><th>محصول</th><th style="text-align:left">تعداد</th></tr></thead>
                    <tbody>
                        @foreach($topProducts as $p)
                            <tr>
                                <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $p['title'] }}</td>
                                <td style="text-align:left;font-weight:700;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($p['cnt']) }}</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            @else
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">داده‌ای نیست</p>
            @endif
        </div>

        {{-- Top Customers --}}
        <div class="sg-chart-card">
            <h3>⭐ بهترین مشتریان</h3>
            @if($topCustomers->count())
                <table class="sg-mini-table">
                    <thead><tr><th>مشتری</th><th style="text-align:left">سفارش</th></tr></thead>
                    <tbody>
                        @foreach($topCustomers as $c)
                            <tr>
                                <td>
                                    <div style="font-weight:700">{{ $c->name }}</div>
                                    <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $c->phone }}</div>
                                </td>
                                <td style="text-align:left;font-weight:700;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            @else
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">داده‌ای نیست</p>
            @endif
        </div>
    </div>
</div>
