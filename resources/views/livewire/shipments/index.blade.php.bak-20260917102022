<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <h1 class="text-xl md:text-2xl font-bold">📮 مرسولات</h1>

    <div class="bg-base-100 rounded-lg shadow border p-3 flex flex-wrap gap-2">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 کد رهگیری / شماره سفارش / تلفن..."
               class="input input-bordered input-sm w-full md:w-80" />
        <select wire:model.live="filterStatus" class="select select-bordered select-sm">
            <option value="">— همه وضعیت‌ها —</option>
            <option value="pending">📦 ثبت شده</option>
            <option value="in_transit">🚚 در مسیر</option>
            <option value="delivered">✅ تحویل شد</option>
            <option value="returned">↩️ مرجوع</option>
            <option value="failed">❌ ناموفق</option>
        </select>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>سفارش</th>
                        <th>کد رهگیری</th>
                        <th>گیرنده</th>
                        <th>تلفن</th>
                        <th>حامل</th>
                        <th>وضعیت</th>
                        <th>تاریخ</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($shipments as $s)
                        <tr wire:key="ship-{{ $s->id }}">
                            <td class="font-mono text-xs">{{ $s->id }}</td>
                            <td>
                                @if($s->order)
                                    <a href="{{ route('orders.show', $s->order) }}"
                                       class="link link-primary font-bold">#{{ $s->order->order_number }}</a>
                                @else — @endif
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $s->tracking_code ?? '—' }}</td>
                            <td>{{ $s->receiver_name ?? $s->order?->customer?->name ?? '—' }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $s->receiver_phone ?? '—' }}</td>
                            <td><span class="badge badge-ghost badge-sm">{{ $s->carrier }}</span></td>
                            <td><span class="badge badge-info badge-sm">{{ $s->status_label }}</span></td>
                            <td class="text-xs font-mono">
                                {{ $s->created_at ? \App\Support\PersianDate::format($s->created_at, 'Y/m/d') : '—' }}
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="8" class="text-center py-8 text-base-content/50">
                            مرسوله‌ای ثبت نشده — هنگام ایمپورت CSV پستی، مرسولات اینجا ظاهر می‌شوند
                        </td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $shipments->links() }}</div>
</div>
