<div style="padding:0 18px 18px">
    <h1 style="font-size:20px;font-weight:700;margin-bottom:14px">🏠 داشبورد</h1>

    {{-- KPI Cards --}}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:16px">
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">📦</div>
            <div style="font-size:22px;font-weight:800;color:var(--primary);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">کل سفارشات</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">🆕</div>
            <div style="font-size:22px;font-weight:800;color:var(--success);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders_today']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">امروز</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">⏳</div>
            <div style="font-size:22px;font-weight:800;color:var(--warn);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders_pending']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">در انتظار</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">🚚</div>
            <div style="font-size:22px;font-weight:800;color:var(--gold-dark);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['orders_courier']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">تحویل مامور</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">👥</div>
            <div style="font-size:22px;font-weight:800;color:var(--primary);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['customers']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">مشتریان</div>
        </div>
        <div class="sg-settings-card" style="text-align:center;padding:14px 10px">
            <div style="font-size:26px">💎</div>
            <div style="font-size:22px;font-weight:800;color:var(--primary);margin-top:4px">{{ \App\Support\PersianNumber::toFa($stats['certificates']) }}</div>
            <div style="font-size:11px;opacity:.6;margin-top:2px">شناسنامه</div>
        </div>
    </div>

    {{-- Chart --}}
    <div class="sg-settings-card" style="margin-bottom:16px">
        <h3>📈 روند ۷ روز اخیر</h3>
        @php $max = collect($daily)->max('count') ?: 1; @endphp
        <div style="display:flex;align-items:flex-end;gap:6px;height:140px;padding-top:10px">
            @foreach($daily as $d)
                <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px">
                    <div style="font-size:10px;font-weight:700;color:var(--primary)">{{ $d['count'] ?: '' }}</div>
                    <div style="width:100%;background:linear-gradient(to top, #14b8a6, #0891b2);border-radius:6px 6px 0 0;transition:all .3s" style="height:{{ max(4, $d['count']/$max*100) }}%"></div>
                    <div style="font-size:9px;font-family:monospace;opacity:.6">{{ $d['date'] }}</div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- Recent --}}
    <div class="sg-settings-card">
        <h3>🕐 آخرین سفارشات</h3>
        @forelse($recent as $o)
            <div style="padding:10px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:8px;font-size:12px">
                <div>
                    <strong>#{{ $o->order_number }}</strong> — {{ $o->customer_name ?? '—' }}
                    <div style="font-size:10px;opacity:.5;font-family:monospace" dir="ltr">{{ $o->phone }}</div>
                </div>
                <div style="text-align:left">
                    <div style="font-weight:700;font-family:monospace">{{ number_format($o->amount ?? 0) }}</div>
                    <div style="font-size:10px;opacity:.5">{{ \App\Support\PersianDate::format($o->created_at, 'Y/m/d') }}</div>
                </div>
            </div>
        @empty
            <p style="text-align:center;padding:20px;opacity:.5">سفارشی نیست</p>
        @endforelse
    </div>
</div>
