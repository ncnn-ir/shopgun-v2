<div class="p-4 md:p-6 space-y-4" dir="rtl">

    {{-- هدر --}}
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold text-gray-800 dark:text-gray-100">
                📦 لیست تامین خودکار
            </h1>
            <p class="text-sm text-gray-500 mt-1">
                تیک بزن یعنی محصول پیدا شد → بعد تحویل واحد ارسال
            </p>
        </div>

        <div class="flex flex-wrap gap-2">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="جستجو (شماره سفارش، نام، موبایل)..."
                   class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600
                          bg-white dark:bg-gray-800 text-sm w-64" />
        </div>
    </div>

    {{-- فلش پیام --}}
    @if (session()->has('message'))
        <div class="bg-green-50 dark:bg-green-900/30 border border-green-300 dark:border-green-700
                    text-green-800 dark:text-green-200 rounded-lg p-3 text-sm">
            {{ session('message') }}
        </div>
    @endif
    @if (session()->has('error'))
        <div class="bg-red-50 dark:bg-red-900/30 border border-red-300 dark:border-red-700
                    text-red-800 dark:text-red-200 rounded-lg p-3 text-sm">
            {{ session('error') }}
        </div>
    @endif

    {{-- آمار --}}
    <div class="grid grid-cols-3 gap-3">
        <button wire:click="$set('filter','pending')"
            class="rounded-xl p-3 text-center border transition
                   {{ $filter==='pending' ? 'bg-amber-500 text-white border-amber-600' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700' }}">
            <div class="text-2xl font-bold">{{ $stats['pending'] }}</div>
            <div class="text-xs opacity-90">⏳ در انتظار تامین</div>
        </button>
        <button wire:click="$set('filter','found')"
            class="rounded-xl p-3 text-center border transition
                   {{ $filter==='found' ? 'bg-blue-500 text-white border-blue-600' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700' }}">
            <div class="text-2xl font-bold">{{ $stats['found'] }}</div>
            <div class="text-xs opacity-90">✅ پیدا شده</div>
        </button>
        <button wire:click="$set('filter','delivered')"
            class="rounded-xl p-3 text-center border transition
                   {{ $filter==='delivered' ? 'bg-green-500 text-white border-green-600' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700' }}">
            <div class="text-2xl font-bold">{{ $stats['delivered'] }}</div>
            <div class="text-xs opacity-90">🚚 تحویل ارسال</div>
        </button>
    </div>

    {{-- اکشن دسته‌جمعی --}}
    @if(count($selected))
        <div class="bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-300 dark:border-indigo-700
                    rounded-lg p-3 flex flex-wrap gap-2 items-center text-sm">
            <span class="font-bold">{{ count($selected) }} مورد انتخاب شده</span>
            <button wire:click="bulkMarkFound"
                class="px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700">
                ✅ علامت «پیدا شد»
            </button>
            <button wire:click="bulkDeliver"
                class="px-3 py-1.5 rounded-lg bg-green-600 text-white hover:bg-green-700">
                🚚 تحویل به ارسال
            </button>
        </div>
    @endif

    {{-- جدول --}}
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50 dark:bg-gray-900/50 text-gray-600 dark:text-gray-300">
                    <tr>
                        <th class="p-3 w-8">
                            <input type="checkbox" wire:model.live="selected" value="__all__"
                                   onclick="if(this.checked){ @this.set('selected', @js($orders->pluck('id')->all())) } else { @this.set('selected', []) }" />
                        </th>
                        <th class="p-3 text-right">#</th>
                        <th class="p-3 text-right">مشتری</th>
                        <th class="p-3 text-right">اقلام</th>
                        <th class="p-3 text-right">وضعیت</th>
                        <th class="p-3 text-right">تاریخ</th>
                        <th class="p-3 text-right">عملیات</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                    @forelse($orders as $order)
                        <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/40 transition">
                            <td class="p-3">
                                <input type="checkbox" wire:model.live="selected" value="{{ $order->id }}" />
                            </td>
                            <td class="p-3 font-mono text-xs">
                                <button wire:click="$dispatch('showOrderTimeline', { orderId: {{ $order->id }} })"
                                        class="text-indigo-600 hover:underline">
                                    #{{ $order->id }}
                                </button>
                            </td>
                            <td class="p-3">
                                <div class="font-medium">
                                    {{ trim(($order->customer->first_name ?? '') . ' ' . ($order->customer->last_name ?? '')) ?: '—' }}
                                </div>
                                <div class="text-xs text-gray-500">{{ $order->customer->phone ?? '' }}</div>
                            </td>
                            <td class="p-3">
                                <div class="flex flex-col gap-1">
                                    @foreach(($order->items ?? collect())->take(2) as $it)
                                        <span class="text-xs text-gray-600 dark:text-gray-400">
                                            • {{ \Illuminate\Support\Str::limit($it->name ?? $it->title ?? '-', 30) }}
                                        </span>
                                    @endforeach
                                    @if(($order->items ?? collect())->count() > 2)
                                        <span class="text-xs text-gray-400">
                                            و {{ $order->items->count() - 2 }} مورد دیگر
                                        </span>
                                    @endif
                                </div>
                            </td>
                            <td class="p-3">
                                @if($order->isDeliveredToShipping())
                                    <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full
                                                 bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200 text-xs">
                                        🚚 تحویل ارسال
                                    </span>
                                @elseif($order->isSupplyFound())
                                    <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full
                                                 bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200 text-xs">
                                        ✅ پیدا شده
                                    </span>
                                @else
                                    <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full
                                                 bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200 text-xs">
                                        ⏳ در انتظار
                                    </span>
                                @endif
                            </td>
                            <td class="p-3 text-xs text-gray-500 whitespace-nowrap">
                                {{ optional($order->created_at)->format('Y/m/d H:i') }}
                            </td>
                            <td class="p-3">
                                <div class="flex items-center gap-2">
                                    @if($order->isAwaitingSupply())
                                        <button wire:click="markFound({{ $order->id }})"
                                            class="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs">
                                            ✅ پیدا شد
                                        </button>
                                    @elseif($order->isSupplyFound())
                                        <button wire:click="deliverToShipping({{ $order->id }})"
                                            class="px-3 py-1 rounded-lg bg-green-600 hover:bg-green-700 text-white text-xs">
                                            🚚 تحویل ارسال
                                        </button>
                                        <button wire:click="unmarkFound({{ $order->id }})"
                                            class="px-2 py-1 rounded-lg bg-gray-200 dark:bg-gray-700 text-xs">
                                            ↺
                                        </button>
                                    @else
                                        <span class="text-xs text-green-600">✓ تمام</span>
                                    @endif

                                    <button wire:click="$dispatch('showOrderTimeline', { orderId: {{ $order->id }} })"
                                        class="px-2 py-1 rounded-lg bg-indigo-100 dark:bg-indigo-900/40
                                               text-indigo-700 dark:text-indigo-200 text-xs">
                                        🗺 تایم‌لاین
                                    </button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="7" class="p-8 text-center text-gray-500">
                                🎉 چیزی برای تامین نیست
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div class="p-3 border-t border-gray-100 dark:border-gray-700">
            {{ $orders->links() }}
        </div>
    </div>

    {{-- مودال تایم‌لاین --}}
    <livewire:orders.order-timeline-modal />
</div>
