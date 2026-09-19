<div dir="rtl" style="padding:10px">

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:8px;margin-bottom:10px;display:grid;grid-template-columns:2fr 1fr;gap:6px">
        <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 نام یا تلفن"
               style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc;box-sizing:border-box">
        <select wire:model.live="filter" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc">
            <option value="">همه</option>
            <option value="has_orders">با سفارش</option>
            <option value="no_orders">بدون سفارش</option>
        </select>
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
        <div style="padding:8px 12px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:700;font-size:12.5px">👥 مشتریان</span>
            <span style="background:#c9a84c;color:#1a5276;padding:2px 8px;border-radius:10px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($customers->total()) }}</span>
        </div>

        <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;font-size:11.5px;min-width:520px">
                <thead style="background:#f8fafc">
                    <tr>
                        <th style="padding:7px;text-align:right;color:#1a5276">نام</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">تلفن</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">سفارش</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">مجموع</th>
                        <th style="padding:7px;text-align:right;color:#1a5276"></th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($customers as $c)
                        <tr wire:key="c-{{ $c->id }}" style="border-bottom:1px solid #f1f5f9;cursor:pointer"
                            onclick="Livewire.dispatch('open-customer-profile', {customerId: {{ $c->id }}})">
                            <td style="padding:7px">
                                <div style="display:flex;align-items:center;gap:8px">
                                    <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#14b8a6,#0891b2);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;flex-shrink:0">
                                        {{ mb_substr($c->name ?? '?', 0, 1) }}
                                    </div>
                                    <div style="font-weight:700">{{ $c->name ?? '—' }}</div>
                                </div>
                            </td>
                            <td style="padding:7px;font-family:monospace;font-size:11px" dir="ltr">{{ $c->phone ?? '—' }}</td>
                            <td style="padding:7px">
                                <span style="background:{{ $c->orders_count > 0 ? '#d1fae5' : '#f1f5f9' }};color:{{ $c->orders_count > 0 ? '#065f46' : '#64748b' }};padding:2px 8px;border-radius:10px;font-size:10.5px;font-weight:700">
                                    {{ \App\Support\PersianNumber::toFa($c->orders_count) }}
                                </span>
                            </td>
                            <td style="padding:7px;font-family:monospace;font-size:11px;color:#16a34a;font-weight:700">
                                {{ number_format((float) ($c->orders_sum_amount ?? 0) / 1000000, 1) }}M
                            </td>
                            <td style="padding:7px" onclick="event.stopPropagation()">
                                <div style="display:flex;gap:3px">
                                    <button onclick="Livewire.dispatch('open-customer-profile', {customerId: {{ $c->id }}})"
                                            style="background:#dbeafe;color:#1e40af;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;font-size:11px" title="مشاهده">👁️</button>
                                    <a href="{{ route('customers.show', $c) }}" wire:navigate
                                       style="background:#ede9fe;color:#5b21b6;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;font-size:11px;display:flex;align-items:center;justify-content:center;text-decoration:none" title="صفحه کامل">📄</a>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="5" style="text-align:center;padding:30px;color:#94a3b8">
                            <div style="font-size:36px;opacity:.4">👥</div>
                            <div style="font-size:12px;margin-top:6px">مشتری‌ای نیست</div>
                        </td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding:10px">{{ $customers->links() }}</div>
    </div>
</div>
