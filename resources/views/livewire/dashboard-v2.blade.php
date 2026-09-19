<div style="direction:rtl">

    {{-- Header --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px">
        <div>
            <h1 style="margin:0;font-size:22px;font-weight:800;color:var(--sg-text)">📊 داشبورد</h1>
            <p style="margin:4px 0 0;font-size:12px;color:var(--sg-text-muted)">{{ $rangeLabel }}</p>
        </div>
        <div style="display:flex;gap:4px;background:var(--sg-bg-soft);padding:4px;border-radius:10px">
            @foreach(['today'=>'امروز','week'=>'۷ روز','month'=>'۳۰ روز','year'=>'سال'] as $k=>$v)
                <button wire:click="setRange('{{ $k }}')"
                        style="padding:6px 14px;border-radius:8px;border:none;font-size:11.5px;font-weight:700;cursor:pointer;transition:var(--sg-t-fast);
                            background:{{ $range===$k ? 'var(--sg-primary)' : 'transparent' }};
                            color:{{ $range===$k ? 'var(--sg-text-inverse)' : 'var(--sg-text-secondary)' }}">
                    {{ $v }}
                </button>
            @endforeach
        </div>
    </div>

    {{-- KPI Cards --}}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:16px">
        @foreach($kpi as $k)
            <div class="sg-card" style="display:flex;align-items:center;gap:12px;min-width:0">
                <div style="width:46px;height:46px;border-radius:12px;background:{{ $k['color'] }};display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0">
                    {{ $k['icon'] }}
                </div>
                <div style="flex:1;min-width:0">
                    <div style="font-size:22px;font-weight:800;color:var(--sg-text);line-height:1.1;font-family:var(--sg-font-mono)">
                        @if(!empty($k['raw']))
                            {{ \App\Support\PersianNumber::toFa(number_format($k['num'])) }}
                        @else
                            {{ \App\Support\PersianNumber::toFa(number_format($k['num'], $k['dec'] ?? 1)) }}
                        @endif
                    </div>
                    <div style="font-size:11px;color:var(--sg-text-muted);margin-top:2px">{{ $k['lbl'] }}</div>
                </div>
            </div>
        @endforeach
    </div>

    {{-- Chart + Channels --}}
    <div style="display:grid;grid-template-columns:1fr;gap:14px;margin-bottom:16px">
        {{-- Chart --}}
        <div class="sg-card">
            <div class="sg-card-head"><h3>📈 نمودار سفارشات</h3></div>
            @php $maxCount = collect($series)->max('count') ?: 1; @endphp
            <div style="display:flex;align-items:flex-end;gap:6px;height:180px;padding-top:20px;overflow-x:auto">
                @foreach($series as $d)
                    <div style="flex:1;min-width:34px;display:flex;flex-direction:column;align-items:center;gap:4px;justify-content:flex-end;height:100%">
                        <div style="font-size:11px;font-weight:700;color:var(--sg-primary);font-family:var(--sg-font-mono)">
                            {{ $d['count'] > 0 ? \App\Support\PersianNumber::toFa($d['count']) : '' }}
                        </div>
                        <div style="width:100%;background:linear-gradient(to top,var(--sg-primary),var(--sg-accent));border-radius:6px 6px 0 0;transition:height .3s"
                             style="height:{{ max(4, $d['count']/$maxCount*100) }}%"></div>
                        <div style="font-size:9px;color:var(--sg-text-muted);font-family:var(--sg-font-mono);white-space:nowrap">{{ $d['date'] }}</div>
                    </div>
                @endforeach
            </div>
        </div>
    </div>

    {{-- Recent Orders --}}
    <div class="sg-card">
        <div class="sg-card-head">
            <h3>🕐 آخرین سفارشات</h3>
            <a href="{{ route('orders.index') }}" wire:navigate
               style="font-size:11px;color:var(--sg-primary);font-weight:700;text-decoration:none">مشاهده همه ←</a>
        </div>

        @if($recent->isEmpty())
            <div style="text-align:center;padding:30px;color:var(--sg-text-muted)">
                <div style="font-size:36px;opacity:.4">📦</div>
                <div style="font-size:12px;margin-top:8px">سفارشی نیست</div>
            </div>
        @else
            <div style="display:flex;flex-direction:column;gap:6px">
                @foreach($recent as $o)
                    <div wire:key="recent-{{ $o->id }}" style="padding:10px;background:var(--sg-bg-soft);border-radius:10px;cursor:pointer;transition:var(--sg-t-fast)"
                         onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o->id }}})"
                         onmouseover="this.style.background='var(--sg-bg-card)';this.style.boxShadow='var(--sg-shadow-sm)'"
                         onmouseout="this.style.background='var(--sg-bg-soft)';this.style.boxShadow='none'">
                        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
                            <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
                                <span style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-primary)">#{{ $o->order_number }}</span>
                                <span style="font-weight:700;font-size:12.5px" class="sg-truncate">{{ $o->customer_name ?? '—' }}</span>
                                @if($o->channel)
                                    <span style="padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700;color:#fff;background:{{ $o->channel->color ?? '#64748b' }}">{{ $o->channel->icon }} {{ $o->channel->name }}</span>
                                @endif
                            </div>
                            <div style="display:flex;align-items:center;gap:8px">
                                <span style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-success)">{{ number_format($o->amount ?? 0) }}</span>
                                <span style="padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700;color:#fff;background:{{ \App\Support\OrderStatus::color($o->status ?? 'pending') }}">{{ \App\Support\OrderStatus::label($o->status ?? 'pending') }}</span>
                            </div>
                        </div>
                    </div>
                @endforeach
            </div>
        @endif
    </div>
</div>
