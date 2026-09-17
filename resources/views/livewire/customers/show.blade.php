<div class="p-4 md:p-6 max-w-5xl mx-auto space-y-4">

    {{-- Header --}}
    <div class="flex items-center gap-3">
        <a href="{{ route('customers.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">پروفایل مشتری</h1>
    </div>

    {{-- Card: مشتری --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4 md:p-5">
            <div class="flex flex-col md:flex-row items-start md:items-center gap-4">

                <div class="w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg shrink-0"
                     style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                    {{ mb_substr($customer->name ?? '?', 0, 1) }}
                </div>

                <div class="flex-1 min-w-0">
                    <h2 class="text-lg font-bold">{{ $customer->name }}</h2>
                    <div class="text-sm font-mono text-base-content/60 mt-1" dir="ltr">
                        {{ $customer->primaryPhone()?->formatted ?? $customer->phone ?? '—' }}
                    </div>
                    @if($customer->email)
                        <div class="text-xs text-base-content/60 mt-1" dir="ltr">📧 {{ $customer->email }}</div>
                    @endif
                </div>

                <div class="flex gap-2">
                    <button wire:click="$dispatch('open-order-form')"
                            class="btn btn-primary btn-sm">➕ سفارش جدید</button>
                    <a href="{{ route('customers.edit', $customer) }}"
                       class="btn btn-outline btn-sm">✏️ ویرایش</a>
                </div>
            </div>

            {{-- آمار --}}
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->orders->count()) }}</div>
                    <div class="text-xs text-base-content/60">سفارش</div>
                </div>
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->phones->count()) }}</div>
                    <div class="text-xs text-base-content/60">تلفن</div>
                </div>
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($customer->addresses->count()) }}</div>
                    <div class="text-xs text-base-content/60">آدرس</div>
                </div>
                <div class="bg-base-200/50 rounded-lg p-3 text-center">
                    <div class="text-2xl font-bold text-primary">
                        {{ number_format($customer->orders->sum('amount') ?? 0) }}
                    </div>
                    <div class="text-xs text-base-content/60">مجموع خرید</div>
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        {{-- تلفن‌ها --}}
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4">
                <h3 class="font-bold text-sm mb-3 flex items-center gap-2">📱 شماره تلفن‌ها</h3>
                @forelse($customer->phones as $phone)
                    <div class="flex items-center gap-2 p-2 rounded-lg {{ $phone->is_primary ? 'bg-success/5 border border-success/30' : 'bg-base-200/50' }}"
                         wire:key="ph-{{ $phone->id }}">
                        @if($phone->is_primary)
                            <span class="badge badge-success badge-xs">اصلی</span>
                        @endif
                        @if($phone->label)
                            <span class="badge badge-ghost badge-xs">{{ $phone->label }}</span>
                        @endif
                        <div class="flex-1 font-mono text-sm text-right" dir="ltr">{{ $phone->formatted }}</div>
                    </div>
                @empty
                    <div class="text-center py-4 text-sm text-base-content/50">شماره‌ای نیست</div>
                @endforelse
            </div>
        </div>

        {{-- آدرس‌ها --}}
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4">
                <h3 class="font-bold text-sm mb-3 flex items-center gap-2">📍 آدرس‌ها</h3>
                @forelse($customer->addresses as $addr)
                    <div class="p-2 rounded-lg {{ $addr->is_primary ? 'bg-success/5 border border-success/30' : 'bg-base-200/50' }}"
                         wire:key="ad-{{ $addr->id }}">
                        <div class="flex items-center gap-2 mb-1">
                            @if($addr->is_primary)
                                <span class="badge badge-success badge-xs">اصلی</span>
                            @endif
                            @if($addr->label)
                                <span class="badge badge-ghost badge-xs">{{ $addr->label }}</span>
                            @endif
                            @if($addr->city)
                                <span class="text-[10px] text-base-content/50">{{ $addr->city }}</span>
                            @endif
                        </div>
                        <div class="text-xs">{{ $addr->address }}</div>
                        @if($addr->postal_code)
                            <div class="text-[10px] font-mono text-base-content/60 mt-1" dir="ltr">📮 {{ $addr->postal_code }}</div>
                        @endif
                    </div>
                @empty
                    <div class="text-center py-4 text-sm text-base-content/50">آدرسی نیست</div>
                @endforelse
            </div>
        </div>
    </div>

    {{-- سفارشات --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h3 class="font-bold text-sm mb-3 flex items-center gap-2">
                📦 تاریخچه سفارشات
                <span class="badge badge-primary badge-sm">{{ \App\Support\PersianNumber::toFa($customer->orders->count()) }}</span>
            </h3>

            @forelse($customer->orders as $order)
                <a href="{{ route('orders.show', $order) }}"
                   class="block p-3 rounded-lg border border-base-300 hover:border-primary/50 hover:bg-primary/5 transition mb-2"
                   wire:key="ord-{{ $order->id }}">
                    <div class="flex items-center justify-between">
                        <div class="font-bold">#{{ $order->order_number ?? $order->id }}</div>
                        <div class="text-xs text-base-content/60">
                            {{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}
                        </div>
                    </div>
                    <div class="flex items-center gap-3 text-xs text-base-content/60 mt-1">
                        <span>💰 {{ number_format((float) ($order->amount ?? 0)) }} ت</span>
                        @if($order->status)
                            <span class="badge badge-ghost badge-xs">{{ $order->status }}</span>
                        @endif
                    </div>
                </a>
            @empty
                <div class="text-center py-6 text-sm text-base-content/50">سفارشی ثبت نشده</div>
            @endforelse
        </div>
    </div>

    {{-- کامپوننت Profile Modal --}}
    
</div>
