<div x-data="{ open: @entangle('open') }"
     @keydown.window.prevent.ctrl.k="open = true; $wire.openSearch(); $nextTick(() => $refs.searchInput?.focus())"
     @keydown.window.escape="open = false; $wire.close()">

    <div x-show="open" x-transition.opacity
         class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
         @click="open = false; $wire.close()"></div>

    <div x-show="open" x-transition
         class="fixed inset-x-0 top-20 mx-auto max-w-2xl z-[101] px-4">
        <div class="card bg-base-100 shadow-2xl">
            <div class="card-body p-0">
                <div class="flex items-center gap-3 p-4 border-b border-base-300">
                    <span class="text-2xl">🔍</span>
                    <input x-ref="searchInput" type="text"
                           wire:model.live.debounce.300ms="query"
                           placeholder="جستجو..."
                           class="input input-ghost w-full text-lg" autofocus />
                    <kbd class="kbd kbd-sm">ESC</kbd>
                </div>

                <div class="max-h-96 overflow-y-auto p-2">
                    @if(strlen(trim($query)) < 2)
                        <div class="text-center py-8 text-base-content/50 text-sm">حداقل ۲ کاراکتر وارد کن</div>
                    @else
                        @if($orders->isNotEmpty())
                            <div class="text-xs text-base-content/60 px-3 pt-3 pb-1 font-bold">📦 سفارشات</div>
                            @foreach($orders as $order)
                                <a href="{{ route('orders.show', $order) }}" wire:navigate @click="open = false"
                                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-base-200">
                                    <span class="text-xl">📦</span>
                                    <div class="flex-1">
                                        <div class="font-bold text-sm">#{{ $order->order_number }} — {{ $order->customer?->name ?? 'بدون نام' }}</div>
                                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $order->phone }}</div>
                                    </div>
                                </a>
                            @endforeach
                        @endif

                        @if($customers->isNotEmpty())
                            <div class="text-xs text-base-content/60 px-3 pt-3 pb-1 font-bold">👥 مشتریان</div>
                            @foreach($customers as $customer)
                                <a href="{{ route('customers.show', $customer) }}" wire:navigate @click="open = false"
                                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-base-200">
                                    <span class="text-xl">👤</span>
                                    <div class="flex-1">
                                        <div class="font-bold text-sm">{{ $customer->name ?? 'بدون نام' }}</div>
                                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $customer->phone }}</div>
                                    </div>
                                </a>
                            @endforeach
                        @endif

                        @if($orders->isEmpty() && $customers->isEmpty())
                            <div class="text-center py-8 text-base-content/50 text-sm">نتیجه‌ای یافت نشد</div>
                        @endif
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
