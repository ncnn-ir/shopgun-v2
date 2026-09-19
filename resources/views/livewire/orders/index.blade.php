<div dir="rtl" style="padding:10px">
<div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">
  <button type="button" onclick="Livewire.dispatch('open-order-form')"
    style="padding:10px 18px;background:linear-gradient(135deg,#c9a84c,#a8873a);color:#fff;border:none;border-radius:10px;font-weight:800;cursor:pointer;font-size:13px;font-family:inherit">
    ➕ سفارش جدید
  </button>
  <button type="button" onclick="Livewire.dispatch('openSupplyModal')"
    style="padding:10px 18px;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px;font-family:inherit">
    📦 لیست تامین
  </button>
</div>


{{-- ═══ فیلترهای کم‌حجم ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:8px;margin-bottom:10px;display:grid;grid-template-columns:1fr;gap:6px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 شماره/نام/تلفن"
                   style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc;box-sizing:border-box">
            <select wire:model.live="filterStatus" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc">
                <option value="">همه وضعیت‌ها</option>
                <option value="pending">📝 ثبت</option>
                <option value="final-check">🔍 چک</option>
                <option value="courier">🚚 مامور</option>
            </select>
        </div>
        <div style="display:grid;grid-template-columns:1fr auto;gap:6px;align-items:center">
            <input type="text" wire:model.live="dateFrom" placeholder="از تاریخ (1403/01/01)" dir="ltr"
                   style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:11px;text-align:center;background:#f8fafc;box-sizing:border-box">
            <button wire:click="clearFilters" title="پاک کردن فیلترها"
                    style="padding:7px 12px;background:#f1f5f9;color:#dc2626;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">✕</button>
        </div>
    </div>

    {{-- ═══ انتخاب گروهی ═══ --}}
    @if(count($selected) > 0)
        <div style="background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05));border:2px dashed var(--gold);border-radius:10px;padding:8px 12px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap">
            <span style="font-weight:700;color:#78350f;font-size:12px">{{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد</span>
            <div style="display:flex;gap:4px;flex-wrap:wrap">
                <button wire:click="bulkStatus('pending')" style="padding:4px 10px;background:#fef3c7;color:#92400e;border:1px solid #fbbf24;border-radius:6px;font-weight:700;cursor:pointer;font-size:10.5px">📝</button>
                <button wire:click="bulkStatus('final-check')" style="padding:4px 10px;background:#dbeafe;color:#1e40af;border:1px solid #60a5fa;border-radius:6px;font-weight:700;cursor:pointer;font-size:10.5px">🔍</button>
                <button wire:click="bulkStatus('courier')" style="padding:4px 10px;background:#d1fae5;color:#065f46;border:1px solid #34d399;border-radius:6px;font-weight:700;cursor:pointer;font-size:10.5px">🚚</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" style="padding:4px 10px;background:#fee2e2;color:#dc2626;border:1px solid #fca5a5;border-radius:6px;font-weight:700;cursor:pointer;font-size:10.5px">🗑️</button>
                <button wire:click="clearSelection" style="padding:4px 8px;background:#fff;border:1px solid #cbd5e1;border-radius:6px;cursor:pointer;font-size:10.5px">✕</button>
            </div>
        </div>
    @endif

    {{-- ═══ جدول کم‌حجم ═══ --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
        <div style="padding:8px 12px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:700;font-size:12.5px">📦 سفارشات</span>
            <span style="background:#c9a84c;color:#1a5276;padding:2px 8px;border-radius:10px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($orders->total()) }}</span>
        </div>

        <div style="overflow-x:auto">
            {{-- Supply Modal --}}
<table style="width:100%;border-collapse:collapse;font-size:11px;min-width:640px">
                <thead style="background:#f8fafc">
                    <tr>
                        <th style="padding:6px;width:30px;text-align:center"><input type="checkbox" wire:click="selectAllVisible" style="accent-color:var(--gold)"></th>
                        <th style="padding:6px;text-align:right;color:#1a5276">#</th>
                        <th style="padding:6px;text-align:right;color:#1a5276">مشتری</th>
                        <th style="padding:6px;text-align:right;color:#1a5276">محصولات</th>
                        <th style="padding:6px;text-align:right;color:#1a5276">کانال</th>
                        <th style="padding:6px;text-align:right;color:#1a5276">وضعیت</th>
                        <th style="padding:6px;text-align:right;color:#1a5276">تاریخ</th>
                        <th style="padding:6px;width:60px;text-align:right;color:#1a5276"></th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}" style="border-bottom:1px solid #f1f5f9;cursor:pointer" onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})">
                            <td style="padding:6px;text-align:center" onclick="event.stopPropagation()">
                                <input type="checkbox" wire:click="toggleSelect({{ $order->id }})" @if(in_array($order->id, $selected)) checked @endif style="accent-color:var(--gold)">
                            </td>
                            <td style="padding:6px;font-family:monospace;font-weight:700;font-size:11px">#{{ $order->order_number }}</td>
                            <td style="padding:6px">
                                <div style="font-weight:700;font-size:11.5px">{{ $order->customer_name ?? '—' }}</div>
                                <div style="font-family:monospace;font-size:9.5px;color:#94a3b8" dir="ltr">{{ $order->phone ?? '—' }}</div>
                            </td>
                            <td style="padding:6px;max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10.5px;color:#475569">
                                @if($order->items->count())
                                    {{ $order->items->pluck('title')->take(2)->implode('، ') }}
                                    @if($order->items->count() > 2) <span style="color:#94a3b8">+{{ $order->items->count() - 2 }}</span> @endif
                                @else — @endif
                            </td>
                            <td style="padding:6px">
                                <x-channel-badge :channel="$order->sales_channel" />
                            </td>
                            <td style="padding:6px" onclick="event.stopPropagation()">
                                @php
                                    $stMap = [
                                        'pending' => ['📝','ثبت','#f59e0b','#fff'],
                                        'final-check' => ['🔍','چک','#3b82f6','#fff'],
                                        'courier' => ['🚚','مامور','#10b981','#fff'],
                                    ];
                                    $st = $stMap[$order->status ?? 'pending'] ?? ['📝','ثبت','#f59e0b','#fff'];
                                @endphp
                                <button type="button" wire:click="cycleStatus({{ $order->id }})"
                                        style="background:{{ $st[2] }};color:{{ $st[3] }};border:none;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:700;cursor:pointer;white-space:nowrap">
                                    {{ $st[0] }} {{ $st[1] }}
                                </button>
                            </td>
                            <td style="padding:6px;font-family:monospace;font-size:10px;color:#64748b">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}</td>
                            <td style="padding:6px" onclick="event.stopPropagation()">
                                <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})"
                                        style="background:#dbeafe;color:#1e40af;border:none;width:24px;height:24px;border-radius:6px;cursor:pointer;font-size:11px" title="نمایش">👁️</button>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="8" style="text-align:center;padding:30px;color:#94a3b8">
                                <div style="font-size:36px;opacity:.4">📦</div>
                                <div style="font-size:12px;margin-top:6px">سفارشی نیست</div>
                                <button onclick="Livewire.dispatch('open-order-form')"
                                        style="margin-top:8px;padding:6px 14px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:11px">
                                    ➕ اولین سفارش
                                </button>
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding:10px">{{ $orders->links() }}</div>
    </div>
</div>
