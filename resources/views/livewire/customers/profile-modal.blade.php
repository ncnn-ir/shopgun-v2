<div>
@if($show && $customer)
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:600px">
        <div class="sg-modal-header">
            <h2>👤 پروفایل مشتری</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body" style="padding:14px">

            {{-- باکس مشتری --}}
            <div class="sg-compact-box">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
                    <div class="avatar" style="width:50px;height:50px;font-size:20px">
                        {{ mb_substr($customer->name ?? '?', 0, 1) }}
                    </div>
                    <div style="flex:1;min-width:0">
                        <div class="name" style="font-size:16px">{{ $customer->name }}</div>
                        <div class="phone" style="font-size:12px">{{ $customer->phone }}</div>
                    </div>
                </div>

                @if(!empty($stats))
                    <div class="grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:10px">
                        <div class="item" style="text-align:center">
                            <div class="val">{{ \App\Support\PersianNumber::toFa($stats['total']) }}</div>
                            <div class="lbl">سفارشات</div>
                        </div>
                        <div class="item" style="text-align:center">
                            <div class="val">{{ number_format($stats['sum'] / 1000000, 1) }}M</div>
                            <div class="lbl">مجموع</div>
                        </div>
                        <div class="item" style="text-align:center">
                            <div class="val">{{ number_format($stats['insurance']) }}</div>
                            <div class="lbl">بیمه</div>
                        </div>
                    </div>
                @endif
            </div>

            @if($customer->address)
                <div class="sg-inline-info">
                    <div class="item">📍 {{ $customer->address }}</div>
                    @if($customer->postal_code)
                        <div class="item">📮 <strong style="font-family:monospace">{{ $customer->postal_code }}</strong></div>
                    @endif
                </div>
            @endif

            {{-- تاریخچه سفارشات --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:14px 0 8px">
                📦 آخرین سفارشات
            </div>

            @forelse($orders as $o)
                <div wire:key="ord-{{ $o['id'] }}"
                     style="padding:10px;border:1px solid var(--border);border-radius:10px;margin-bottom:6px;cursor:pointer;transition:.15s"
                     wire:click="viewOrder({{ $o['id'] }})"
                     onmouseover="this.style.background='var(--bg-soft)'"
                     onmouseout="this.style.background='transparent'">
                    <div style="display:flex;justify-content:space-between;font-weight:700;font-size:12.5px;margin-bottom:4px">
                        <span>#{{ $o['num'] }}</span>
                        <span style="font-size:10.5px;opacity:.6;font-family:monospace">{{ $o['date'] }}</span>
                    </div>
                    @if($o['products'])
                        <div style="font-size:11px;opacity:.7;margin-bottom:3px">🛍️ {{ $o['products'] }}</div>
                    @endif
                    <div style="display:flex;justify-content:space-between;font-size:11px">
                        <span style="font-family:monospace">{{ number_format($o['amount']) }} ت</span>
                        <span class="sg-status-badge {{ $o['status'] }}" style="font-size:10px;padding:2px 8px">
                            {{ ['pending'=>'📝 ثبت','final-check'=>'🔍 چک','courier'=>'🚚 مامور'][$o['status']] ?? '📝' }}
                        </span>
                    </div>
                </div>
            @empty
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">سفارشی نیست</p>
            @endforelse
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline btn-sm">بستن</button>
            <a href="{{ route('customers.index') }}" class="btn btn-primary btn-sm">👥 همه مشتریان</a>
        </div>
    </div>
</div>
@endif
</div>
