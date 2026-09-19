<div style="display:flex;gap:8px;overflow-x:auto;padding:4px 2px 8px;scroll-snap-type:x mandatory;scrollbar-width:thin" class="sg-kpi-strip">
    @foreach($items as $k)
        @php
            $trend = $k['trend'] ?? ['dir' => 'flat', 'pct' => 0];
            $trendIcon = match($trend['dir']) {
                'up' => '▲',
                'down' => '▼',
                default => '◆',
            };
            $trendColor = match($trend['dir']) {
                'up' => '#10b981',
                'down' => '#ef4444',
                default => '#94a3b8',
            };
        @endphp
        <div wire:key="kpi-{{ $loop->index }}"
             style="flex:0 0 auto;min-width:150px;scroll-snap-align:start;
                    background:var(--sg-bg-card);border:1px solid var(--sg-border);
                    border-radius:12px;padding:10px 12px;
                    transition:var(--sg-t-fast)"
             onmouseover="this.style.boxShadow='var(--sg-shadow)';this.style.transform='translateY(-2px)'"
             onmouseout="this.style.boxShadow='';this.style.transform=''">

            {{-- Row 1: icon + label --}}
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
                <div style="width:24px;height:24px;border-radius:6px;background:{{ $k['color'] ?? 'rgba(26,82,118,.1)' }};display:flex;align-items:center;justify-content:center;font-size:13px">
                    {{ $k['icon'] }}
                </div>
                <div style="font-size:10.5px;font-weight:700;color:var(--sg-text-muted)">{{ $k['label'] }}</div>
            </div>

            {{-- Row 2: number --}}
            <div style="font-size:20px;font-weight:800;color:var(--sg-text);line-height:1;font-family:var(--sg-font-mono)">
                @if(!empty($k['raw']))
                    {{ \App\Support\PersianNumber::toFa(number_format($k['value'] ?? 0)) }}
                @else
                    {{ \App\Support\PersianNumber::toFa(number_format($k['value'] ?? 0, $k['dec'] ?? 1)) }}
                @endif
                @if(!empty($k['unit']))
                    <span style="font-size:10px;font-weight:600;color:var(--sg-text-muted)">{{ $k['unit'] }}</span>
                @endif
            </div>

            {{-- Row 3: trend + yesterday --}}
            <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin-top:6px">
                <span style="font-size:10px;font-weight:700;color:{{ $trendColor }};display:flex;align-items:center;gap:2px">
                    {{ $trendIcon }}
                    @if($trend['dir'] !== 'flat')
                        {{ \App\Support\PersianNumber::toFa($trend['pct']) }}%
                    @endif
                </span>
                @if(isset($k['yesterday']))
                    <span style="font-size:9.5px;color:var(--sg-text-muted)">
                        دیروز: {{ \App\Support\PersianNumber::toFa(number_format($k['yesterday'])) }}
                    </span>
                @endif
            </div>
        </div>
    @endforeach
</div>

<style>
.sg-kpi-strip::-webkit-scrollbar { height: 4px; }
.sg-kpi-strip::-webkit-scrollbar-thumb { background: var(--sg-border); border-radius: 2px; }
</style>
