<div dir="rtl">

    {{-- ═══ Toolbar ═══ --}}
    <div class="sg-card" style="margin-bottom:12px;padding:10px 12px">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">

            {{-- Filters --}}
            <div style="display:flex;gap:6px;flex-wrap:wrap;flex:1;min-width:0">
                <input type="text" wire:model.live.debounce.400ms="search"
                       placeholder="🔍 شماره/نام/تلفن"
                       style="flex:1;min-width:140px;padding:7px 10px;border:1.5px solid var(--sg-border);border-radius:8px;font-size:12px;background:var(--sg-bg-soft);color:var(--sg-text);box-sizing:border-box">

                <select wire:model.live="filterStatus"
                        style="padding:7px 10px;border:1.5px solid var(--sg-border);border-radius:8px;font-size:12px;background:var(--sg-bg-soft);color:var(--sg-text)">
                    <option value="">همه وضعیت‌ها</option>
                    @foreach(\App\Support\OrderStatus::all() as $k => $s)
                        <option value="{{ $k }}">{{ $s['icon'] }} {{ $s['label'] }}</option>
                    @endforeach
                </select>

                <input type="text" wire:model.live="dateFrom" placeholder="از تاریخ" dir="ltr"
                       style="width:100px;padding:7px 10px;border:1.5px solid var(--sg-border);border-radius:8px;font-family:var(--sg-font-mono);font-size:11px;text-align:center;background:var(--sg-bg-soft);color:var(--sg-text);box-sizing:border-box">

                @if($search || $filterStatus || $dateFrom)
                    <button wire:click="clearFilters" class="sg-btn sg-btn-ghost sg-btn-sm" title="پاک کردن فیلترها">✕</button>
                @endif
            </div>

            {{-- Actions --}}
            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <a href="{{ route('orders.supply-list') }}" wire:navigate class="sg-btn sg-btn-sm" 
                   style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);color:#fff">
                    📋 لیست تأمین
                </a>
                <button type="button" onclick="Livewire.dispatch('open-order-form')" class="sg-btn sg-btn-primary sg-btn-sm">
                    ➕ سفارش جدید
                </button>
            </div>
        </div>
    </div>

    {{-- ═══ Bulk Actions ═══ --}}
    @if(count($selected) > 0)
        <div class="sg-card" style="margin-bottom:10px;padding:8px 12px;background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05));border:2px dashed var(--sg-accent)">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
                <span style="font-weight:700;color:#92400e;font-size:12px">
                    {{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد انتخاب شده
                </span>
                <div style="display:flex;gap:4px;flex-wrap:wrap">
                    <button wire:click="bulkStatus('pending')" class="sg-btn sg-btn-warn sg-btn-xs">📝 ثبت</button>
                    <button wire:click="bulkStatus('final-check')" class="sg-btn sg-btn-xs" style="background:#3b82f6;color:#fff">🔍 چک</button>
                    <button wire:click="bulkStatus('courier')" class="sg-btn sg-btn-success sg-btn-xs">🚚 مامور</button>
                    <button onclick="printSelected()" class="sg-btn sg-btn-xs" style="background:#7c3aed;color:#fff">🖨️ چاپ</button>
                    <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="sg-btn sg-btn-danger sg-btn-xs">🗑️ حذف</button>
                    <button wire:click="clearSelection" class="sg-btn sg-btn-ghost sg-btn-xs">✕</button>
                </div>
            </div>
        </div>
    @endif

    {{-- ═══ Table ═══ --}}
    <div class="sg-card" style="padding:0;overflow:hidden">
        <div style="padding:10px 14px;background:linear-gradient(135deg,var(--sg-primary),var(--sg-primary-hover));color:#fff;display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:700;font-size:13px">📦 سفارشات</span>
            <span style="background:var(--sg-accent);color:#fff;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700">
                {{ \App\Support\PersianNumber::toFa($orders->total()) }}
            </span>
        </div>

        <div class="sg-table-wrap" style="border:none;border-radius:0;max-height:none">
            <table class="sg-table">
                <thead>
                    <tr>
                        <th style="width:32px;text-align:center">
                            <input type="checkbox" wire:click="selectAllVisible" style="accent-color:var(--sg-accent)">
                        </th>
                        <th>#</th>
                        <th>مشتری</th>
                        <th>محصولات</th>
                        <th>کانال</th>
                        <th>وضعیت</th>
                        <th>تاریخ</th>
                        <th style="width:140px;text-align:center">عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}">
                            <td style="text-align:center">
                                <input type="checkbox" wire:click="toggleSelect({{ $order->id }})"
                                       @if(in_array($order->id, $selected)) checked @endif
                                       style="accent-color:var(--sg-accent)">
                            </td>
                            <td style="font-family:var(--sg-font-mono);font-weight:700;font-size:11.5px">
                                #{{ $order->order_number }}
                            </td>
                            <td>
                                <div style="font-weight:700;font-size:11.5px">{{ $order->customer_name ?? '—' }}</div>
                                <div style="font-family:var(--sg-font-mono);font-size:10px;color:var(--sg-text-muted)" dir="ltr">{{ $order->phone ?? '—' }}</div>
                            </td>
                            <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px">
                                @if($order->items->count())
                                    @foreach($order->items->take(2) as $item)
                                        <span class="order-item-link" 
                                              onclick="Livewire.dispatch('supply-show-product', { sku: '{{ addslashes($item->sku ?? '') }}' })"
                                              style="cursor:pointer;color:var(--sg-primary);text-decoration:underline dotted">
                                            {{ $item->title }}
                                        </span>
                                        @if(!$loop->last)،@endif
                                    @endforeach
                                    @if($order->items->count() > 2) <span style="opacity:.5">+{{ $order->items->count() - 2 }}</span> @endif
                                @else — @endif
                            </td>
                            <td>
                                @if($order->channel)
                                    <span style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700;color:#fff;background:{{ $order->channel->color ?? '#64748b' }};white-space:nowrap">
                                        {{ $order->channel->icon }} {{ $order->channel->name }}
                                    </span>
                                @else
                                    <span style="font-size:10px;color:var(--sg-text-muted)">—</span>
                                @endif
                            </td>
                            <td>
                                @php
                                    $st = \App\Support\OrderStatus::FLOW[$order->status ?? 'pending'] ?? \App\Support\OrderStatus::FLOW['pending'];
                                @endphp
                                <span style="display:inline-flex;align-items:center;gap:3px;padding:3px 10px;border-radius:99px;font-size:10.5px;font-weight:700;color:#fff;background:{{ $st['color'] }};white-space:nowrap">
                                    {{ $st['icon'] }} {{ $st['label'] }}
                                </span>
                            </td>
                            <td style="font-family:var(--sg-font-mono);font-size:10.5px;color:var(--sg-text-muted)">
                                {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}
                            </td>
                            <td style="text-align:center">
                                <div style="display:flex;gap:3px;justify-content:center">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})"
                                            style="background:rgba(59,130,246,.15);color:#1e40af;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;font-size:11px"
                                            title="نمایش">👁️</button>
                                    <button onclick="window.open('{{ route('orders.print-label', $order) }}', '_blank')"
                                            style="background:rgba(16,185,129,.15);color:#059669;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;font-size:11px"
                                            title="برچسب پستی">🏷️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: {{ $order->id }}})"
                                            style="background:rgba(168,85,247,.15);color:#7c3aed;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;font-size:11px"
                                            title="ویرایش">✏️</button>
                                    <button wire:click="delete({{ $order->id }})" wire:confirm="حذف شود؟"
                                            style="background:rgba(239,68,68,.15);color:#dc2626;border:none;width:26px;height:26px;border-radius:6px;cursor:pointer;font-size:11px"
                                            title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="8" style="text-align:center;padding:40px">
                                <div style="font-size:44px;opacity:.4">📦</div>
                                <div style="font-size:12.5px;color:var(--sg-text-muted);margin-top:8px">سفارشی نیست</div>
                                <button onclick="Livewire.dispatch('open-order-form')" class="sg-btn sg-btn-primary sg-btn-sm" style="margin-top:12px">
                                    ➕ اولین سفارش
                                </button>
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding:12px 14px;border-top:1px solid var(--sg-divider)">
            {{ $orders->links() }}
        </div>
    </div>
</div>

<script>
function printSelected() {
    var ids = [];
    document.querySelectorAll('tbody tr').forEach(function(tr) {
        var cb = tr.querySelector('input[type=checkbox]:checked');
        if (!cb) return;
        var num = tr.querySelector('td:nth-child(2)');
        if (!num) return;
        var m = num.textContent.match(/#(\d+)/);
        if (m) ids.push(m[1]);
    });
    if (!ids.length) { alert('موردی انتخاب نشده'); return; }
    // استفاده از شماره‌های سفارش برای پرینت
    window.open('{{ route("orders.bulk-print-labels") }}?ids=' + ids.join(','), '_blank');
}
</script>
