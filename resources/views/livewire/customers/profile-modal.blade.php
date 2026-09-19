@teleport('body')
<div>
@if($show && $customer)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:94;display:flex;align-items:flex-start;justify-content:center;padding:8px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:520px;margin:8px auto;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:12px 14px;display:flex;align-items:center;gap:10px">
            <div style="width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;flex-shrink:0">
                {{ mb_substr($customer->name ?? '?', 0, 1) }}
            </div>
            <div style="flex:1;min-width:0">
                <div style="font-size:14px;font-weight:700">{{ $customer->name }}</div>
                <div style="font-family:monospace;font-size:11px;opacity:.85" dir="ltr">{{ $customer->phone }}</div>
            </div>
            <button wire:click="close" style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:14px">✕</button>
        </div>

        <div style="padding:12px;max-height:calc(100vh - 160px);overflow-y:auto">

            {{-- آمار --}}
            @if(!empty($stats))
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px">
                    <div style="padding:8px;background:#f8fafc;border-radius:8px;text-align:center">
                        <div style="font-size:16px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($stats['total']) }}</div>
                        <div style="font-size:9.5px;color:#64748b;font-weight:700">سفارش</div>
                    </div>
                    <div style="padding:8px;background:#f0fdf4;border-radius:8px;text-align:center">
                        <div style="font-size:13px;font-weight:800;color:#16a34a;font-family:monospace">{{ number_format($stats['sum'] / 1000000, 1) }}M</div>
                        <div style="font-size:9.5px;color:#15803d;font-weight:700">مجموع خرید</div>
                    </div>
                    <div style="padding:8px;background:#fef3c7;border-radius:8px;text-align:center">
                        <div style="font-size:13px;font-weight:800;color:#92400e;font-family:monospace">{{ number_format($stats['insurance']) }}</div>
                        <div style="font-size:9.5px;color:#78350f;font-weight:700">بیمه</div>
                    </div>
                </div>
            @endif

            {{-- آدرس --}}
            @if($customer->address)
                <div style="padding:8px 10px;background:#f8fafc;border-radius:8px;margin-bottom:12px;font-size:11.5px;line-height:1.6">
                    📍 {{ $customer->address }}
                    @if($customer->postal_code)
                        <br><span style="font-family:monospace;color:#64748b">📮 {{ $customer->postal_code }}</span>
                    @endif
                </div>
            @endif

            {{-- اکشن‌ها --}}
            <div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap">
                <button wire:click="newOrder"
                        style="flex:1;min-width:120px;padding:8px 12px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    ➕ سفارش جدید
                </button>
                <a href="{{ route('customers.show', $customer) }}" wire:navigate
                   style="flex:1;min-width:120px;padding:8px 12px;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px;text-align:center;text-decoration:none">
                    📄 صفحه کامل
                </a>
                <a href="tel:{{ $customer->phone }}"
                   style="padding:8px 12px;background:#dbeafe;color:#1e40af;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px;text-decoration:none">📞</a>
            </div>

            {{-- سفارشات --}}
            <div style="font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                📦 آخرین سفارشات ({{ \App\Support\PersianNumber::toFa(count($orders)) }})
            </div>

            <div style="display:flex;flex-direction:column;gap:5px">
                @forelse($orders as $o)
                    <div wire:key="po-{{ $o['id'] }}"
                         onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o['id'] }}})"
                         style="padding:8px 10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;transition:all .15s"
                         onmouseover="this.style.background='#eff6ff'"
                         onmouseout="this.style.background='#f8fafc'">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
                            <span style="font-family:monospace;font-weight:700;font-size:11.5px">#{{ $o['num'] }}</span>
                            <span style="font-family:monospace;font-size:10px;color:#94a3b8">{{ $o['date'] }}</span>
                        </div>
                        @if($o['products'])
                            <div style="font-size:10.5px;color:#475569;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:3px">
                                🛍️ {{ $o['products'] }}
                                @if($o['items_count'] > 3) <span style="color:#94a3b8">+{{ $o['items_count'] - 3 }}</span> @endif
                            </div>
                        @endif
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <span style="font-family:monospace;font-size:10.5px;font-weight:700;color:#16a34a">{{ number_format($o['amount']) }}</span>
                            @php
                                $stMap = [
                                    'pending' => ['📝','ثبت','#f59e0b'],
                                    'final-check' => ['🔍','چک','#3b82f6'],
                                    'courier' => ['🚚','مامور','#10b981'],
                                ];
                                $st = $stMap[$o['status']] ?? ['📝','ثبت','#f59e0b'];
                            @endphp
                            <span style="background:{{ $st[2] }};color:#fff;padding:1px 7px;border-radius:8px;font-size:9.5px;font-weight:700">
                                {{ $st[0] }} {{ $st[1] }}
                            </span>
                        </div>
                    </div>
                @empty
                    <div style="text-align:center;padding:20px;color:#94a3b8;font-size:11.5px">
                        <div style="font-size:30px;opacity:.4">📦</div>
                        سفارشی ثبت نشده
                    </div>
                @endforelse
            </div>
        </div>
    </div>
</div>
@endif
</div>
@endteleport
