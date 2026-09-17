<div class="p-6 max-w-4xl mx-auto">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div class="flex items-center gap-3">
            <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
            <h1 class="text-2xl font-bold">سفارش #{{ $order->order_number }}</h1>
            @if($order->invoice_needed)
                <span class="badge badge-warning">📄 فاکتور</span>
            @endif
        </div>
        <div class="flex gap-2">
            <a href="{{ route('orders.print-label', $order) }}" target="_blank" class="btn btn-info btn-sm">🏷️ برچسب</a>
            <a href="{{ route('orders.edit', $order) }}" class="btn btn-warning btn-sm">✏️ ویرایش</a>
            <button wire:click="delete" wire:confirm="حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4"><span>{{ session('success') }}</span></div>
    @endif

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📊 وضعیت</h2>
            <div class="flex flex-wrap gap-2">
                @foreach(['pending' => '📝 ثبت سفارش', 'final-check' => '🔍 چک نهایی', 'courier' => '🚚 تحویل مامور'] as $key => $label)
                    <button wire:click="changeStatus('{{ $key }}')" class="btn btn-sm {{ $order->status === $key ? 'btn-primary' : 'btn-outline' }}">{{ $label }}</button>
                @endforeach
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div class="card bg-base-100 shadow">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">👤 مشتری</h2>
                <div class="text-sm space-y-1">
                    <div class="flex justify-between"><span class="text-base-content/60">نام:</span><span class="font-bold">{{ $order->customer?->name ?? '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">تلفن:</span><span class="font-mono" dir="ltr">{{ $order->phone ?? '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">کدپستی:</span><span class="font-mono" dir="ltr">{{ $order->postal_code ?? '—' }}</span></div>
                </div>
            </div>
        </div>
        <div class="card bg-base-100 shadow">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">📦 اطلاعات</h2>
                <div class="text-sm space-y-1">
                    <div class="flex justify-between"><span class="text-base-content/60">کانال:</span><span>@if($order->channel)<span class="badge badge-outline">{{ $order->channel->icon }} {{ $order->channel->name }}</span>@else — @endif</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">بیمه:</span><span>{{ number_format((float) $order->insurance) }}</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">مبلغ کل:</span><span>{{ number_format((float) $order->amount) }}</span></div>
                </div>
            </div>
        </div>
    </div>

    @if($order->items->isNotEmpty())
        <div class="card bg-base-100 shadow mb-4">
            <div class="card-body">
                <h2 class="card-title text-base mb-3">🛍️ محصولات</h2>
                <div class="overflow-x-auto">
                    <table class="table table-zebra table-sm">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>عنوان</th>
                                <th>SKU</th>
                                <th>قیمت</th>
                                <th>تعداد</th>
                                <th>شناسنامه</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($order->items as $i => $item)
                                <tr>
                                    <td>{{ $i + 1 }}</td>
                                    <td class="font-bold">{{ $item->title }}</td>
                                    <td class="font-mono text-xs" dir="ltr">{{ $item->sku ?? '—' }}</td>
                                    <td>{{ number_format((float) $item->price) }}</td>
                                    <td>{{ $item->quantity }}</td>
                                    <td>{!! $item->cert_needed ? '<span class="badge badge-success badge-sm">✓</span>' : '<span class="badge badge-ghost badge-sm">—</span>' !!}</td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
                <div class="text-left mt-2 font-bold">
                    جمع کل: {{ number_format($order->items_total) }}
                </div>
            </div>
        </div>
    @endif

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📍 آدرس</h2>
            <p class="text-sm leading-7">{{ $order->address ?? '—' }}</p>
        </div>
    </div>

    @if($order->notes)
        <div class="card bg-base-100 shadow mb-4">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">📝 یادداشت</h2>
                <p class="text-sm leading-7">{{ $order->notes }}</p>
            </div>
        </div>
    @endif

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">📜 تاریخچه</h2>
            @if($activities->isEmpty())
                <p class="text-sm text-base-content/50">هنوز تغییری ثبت نشده.</p>
            @else
                <div class="space-y-3">
                    @foreach($activities as $a)
                        <div class="flex gap-3 text-sm border-r-2 border-primary/30 pr-3">
                            <div class="text-xs text-base-content/50 whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i') }}</div>
                            <div class="flex-1">
                                <div class="font-bold">{{ $a->description }}</div>
                                @if($a->causer)<div class="text-xs text-base-content/60 mt-1">توسط {{ $a->causer->name ?? 'کاربر' }}</div>@endif
                            </div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>
