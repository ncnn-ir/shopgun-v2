<div dir="rtl" class="sg-dash-wrap">

    {{-- ═══ هدر ═══ --}}
    <div class="sg-dash-head">
        <div>
            <h1>🏠 داشبورد</h1>
            <p>نمای کلی سیستم — {{ \App\Support\PersianDate::format(now(), 'Y/m/d') }}</p>
        </div>
    </div>

    {{-- ═══ ردیف اول: در انتظار تامین (تمام عرض) ═══ --}}
    @php
        try {
            $awaitingSupply = \App\Models\Order::where(function($q){
                $q->whereIn('supply_status', ['awaiting_supply','pending','default'])
                  ->orWhereNull('supply_status');
            })->count();
            $supplyToday = \App\Models\Order::where(fn($q) =>
                $q->whereIn('supply_status', ['found','delivered_to_shipping'])
            )->whereDate('updated_at', today())->count();
        } catch (\Throwable $e) { $awaitingSupply = 0; $supplyToday = 0; }
    @endphp

    <button type="button" wire:click="$dispatch('openSupplyModal')"
        class="sg-kpi-awaiting">
        <div class="sg-kpi-awaiting-left">
            <div class="sg-kpi-awaiting-icon">📦</div>
            <div>
                <div class="sg-kpi-awaiting-title">در انتظار تامین</div>
                <div class="sg-kpi-awaiting-sub">
                    {{ \App\Support\PersianNumber::toFa($supplyToday) }} مورد امروز تحویل ارسال شد
                </div>
            </div>
        </div>
        <div class="sg-kpi-awaiting-count">
            {{ \App\Support\PersianNumber::toFa($awaitingSupply) }}
        </div>
        <div class="sg-kpi-awaiting-arrow">←</div>
    </button>

    {{-- ═══ ردیف دوم: KPI های اصلی (۳×N) ═══ --}}
    @php
        try {
            $stats = [
                ['orders_today',   '📥', 'سفارش امروز',      \App\Models\Order::whereDate('created_at', today())->count(),                          '#3b82f6'],
                ['orders_pending', '⏳', 'در انتظار',         \App\Models\Order::where('status','pending')->count(),                                 '#f59e0b'],
                ['orders_courier', '🚚', 'تحویل مامور',      \App\Models\Order::where('status','courier')->count(),                                 '#10b981'],
                ['orders_check',   '🔍', 'چک نهایی',         \App\Models\Order::where('status','final-check')->count(),                             '#8b5cf6'],
                ['customers',      '👥', 'مشتریان',          \App\Models\Customer::count(),                                                         '#06b6d4'],
                ['certificates',   '💎', 'شناسنامه',         \App\Models\Certificate::count(),                                                      '#f43f5e'],
                ['products',       '📦', 'محصولات',          \App\Models\Product::count(),                                                          '#6366f1'],
                ['sales_today',    '💰', 'فروش امروز',       \App\Models\Order::whereDate('created_at', today())->sum('amount'),                    '#22c55e'],
                ['sales_month',    '📊', 'فروش ماه',         \App\Models\Order::where('created_at','>=', now()->subDays(30))->sum('amount'),        '#f97316'],
            ];
        } catch (\Throwable $e) { $stats = []; }
    @endphp

    <div class="sg-dash-grid">
        @foreach($stats as $s)
            <div class="sg-kpi-card" style="--c:{{ $s[4] }}">
                <div class="sg-kpi-card-top">
                    <span class="sg-kpi-card-icon">{{ $s[1] }}</span>
                    <span class="sg-kpi-card-label">{{ $s[2] }}</span>
                </div>
                <div class="sg-kpi-card-value">
                    @if(str_contains($s[0], 'sales'))
                        {{ \App\Support\PersianNumber::toFa(number_format($s[3] / 1000)) }}
                        <span class="sg-kpi-unit">هزار</span>
                    @else
                        {{ \App\Support\PersianNumber::toFa($s[3]) }}
                    @endif
                </div>
            </div>
        @endforeach
    </div>

    {{-- ═══ ردیف سوم: نمودار و جدول‌ها ═══ --}}
    <div class="sg-dash-sections">

        {{-- کانال فروش --}}
        @php
            try {
                $channels = \App\Models\Order::selectRaw('sales_channel, COUNT(*) as cnt, SUM(amount) as total')
                    ->groupBy('sales_channel')
                    ->orderByDesc('cnt')
                    ->limit(6)
                    ->get();
            } catch (\Throwable $e) { $channels = collect(); }
        @endphp

        @if($channels->count())
        <details class="sg-dash-section" open>
            <summary>
                <span class="sg-dash-sec-icon">🏷</span>
                <span class="sg-dash-sec-title">کانال‌های فروش</span>
                <span class="sg-dash-sec-badge">{{ \App\Support\PersianNumber::toFa($channels->count()) }}</span>
            </summary>
            <div class="sg-dash-section-body">
                <div class="sg-ch-list">
                    @foreach($channels as $ch)
                        @php $pct = $channels->sum('cnt') > 0 ? ($ch->cnt / $channels->sum('cnt')) * 100 : 0; @endphp
                        <div class="sg-ch-row">
                            <x-channel-badge :channel="$ch->sales_channel" />
                            <div class="sg-ch-bar">
                                <div class="sg-ch-bar-fill" style="width:{{ round($pct, 1) }}%"></div>
                            </div>
                            <div class="sg-ch-count">{{ \App\Support\PersianNumber::toFa($ch->cnt) }}</div>
                        </div>
                    @endforeach
                </div>
            </div>
        </details>
        @endif

        {{-- آخرین سفارشات --}}
        @php
            try {
                $recent = \App\Models\Order::with(['customer','items'])
                    ->orderByDesc('created_at')->limit(5)->get();
            } catch (\Throwable $e) { $recent = collect(); }
        @endphp

        @if($recent->count())
        <details class="sg-dash-section" open>
            <summary>
                <span class="sg-dash-sec-icon">🕐</span>
                <span class="sg-dash-sec-title">آخرین سفارشات</span>
                <span class="sg-dash-sec-badge">{{ \App\Support\PersianNumber::toFa($recent->count()) }}</span>
            </summary>
            <div class="sg-dash-section-body" style="padding:0">
                <table class="sg-dash-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>مشتری</th>
                            <th>کانال</th>
                            <th>مبلغ</th>
                            <th>تاریخ</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($recent as $o)
                            <tr onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o->id }}})" style="cursor:pointer">
                                <td class="mono">#{{ $o->order_number }}</td>
                                <td>
                                    <div style="font-weight:600">{{ $o->customer_name ?? '—' }}</div>
                                    <div style="font-size:10px;color:#94a3b8" dir="ltr">{{ $o->phone }}</div>
                                </td>
                                <td><x-channel-badge :channel="$o->sales_channel" /></td>
                                <td class="mono">{{ \App\Support\PersianNumber::toFa(number_format($o->amount)) }}</td>
                                <td style="font-size:10.5px;color:#64748b">
                                    {{ \App\Support\PersianDate::format($o->created_at, 'm/d H:i') }}
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </details>
        @endif

        {{-- بهترین مشتریان --}}
        @php
            try {
                $topCustomers = \App\Models\Customer::query()
                    ->withCount('orders')
                    ->withSum('orders', 'amount')
                    ->having('orders_count', '>', 0)
                    ->orderByDesc('orders_sum_amount')
                    ->limit(5)
                    ->get();
            } catch (\Throwable $e) { $topCustomers = collect(); }
        @endphp

        @if($topCustomers->count())
        <details class="sg-dash-section">
            <summary>
                <span class="sg-dash-sec-icon">🏆</span>
                <span class="sg-dash-sec-title">بهترین مشتریان</span>
                <span class="sg-dash-sec-badge">{{ \App\Support\PersianNumber::toFa($topCustomers->count()) }}</span>
            </summary>
            <div class="sg-dash-section-body" style="padding:0">
                <table class="sg-dash-table">
                    <thead>
                        <tr>
                            <th>مشتری</th>
                            <th>تعداد</th>
                            <th>مجموع خرید</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($topCustomers as $c)
                            <tr>
                                <td>
                                    <div style="font-weight:600">{{ trim($c->first_name.' '.$c->last_name) ?: '—' }}</div>
                                    <div style="font-size:10px;color:#94a3b8" dir="ltr">{{ $c->phone }}</div>
                                </td>
                                <td class="mono">{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
                                <td class="mono">{{ \App\Support\PersianNumber::toFa(number_format($c->orders_sum_amount / 1000)) }} هزار</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </details>
        @endif
    </div>

</div>
