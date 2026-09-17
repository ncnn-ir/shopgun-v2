<div>
    @if($show && $order)
    <div class="fixed inset-0 z-[100] flex items-start justify-center p-4 overflow-y-auto"
         x-data="{ show: true }"
         x-init="$nextTick(() => show = true)">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md transition-opacity duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0"
             x-transition:enter-end="opacity-100"
             wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16
                    border border-primary/20 transition-all duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-8 scale-95"
             x-transition:enter-end="opacity-100 translate-y-0 scale-100">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white text-lg shadow-lg">
                        📮
                    </div>
                    <div>
                        <div class="font-bold text-sm">مرسوله تیپاکس</div>
                        <div class="text-xs text-base-content/60">سفارش #{{ $order->order_number }}</div>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-5">

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="bg-gradient-to-br from-cyan-500 to-teal-600 text-white rounded-xl p-4 shadow-lg">
                        <div class="text-[10px] opacity-80 mb-1">📮 کد رهگیری</div>
                        <div class="font-mono font-bold text-lg tracking-wider" dir="ltr">
                            {{ $order->tracking_code ?: '—' }}
                        </div>
                        @if($order->shipping_status)
                            <div class="inline-block mt-2 px-2 py-0.5 bg-white/20 rounded-full text-[10px] font-bold">
                                {{ $order->shipping_status }}
                            </div>
                        @endif
                    </div>

                    <div class="bg-base-200 rounded-xl p-4">
                        <div class="text-[10px] text-base-content/60 mb-1">👤 گیرنده</div>
                        <div class="font-bold text-sm">{{ $order->customer?->name ?? '—' }}</div>
                        <div class="text-xs text-base-content/60 font-mono mt-1" dir="ltr">{{ $order->phone }}</div>
                        <div class="text-xs text-base-content/60 mt-1 truncate">{{ $order->address }}</div>
                    </div>
                </div>

                <div>
                    <h3 class="font-bold text-sm mb-4 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                        مراحل ارسال
                    </h3>

                    @if(empty($events))
                        <div class="text-center py-8 text-base-content/40 text-sm">
                            هنوز رویدادی ثبت نشده
                        </div>
                    @else
                        <div class="overflow-x-auto pb-4 -mx-5 px-5">
                            <div class="flex items-start gap-0 min-w-max">
                                @foreach(array_reverse($events) as $i => $e)
                                    @php
                                        $isLast = $i === count($events) - 1;
                                        $s = mb_strtolower($e['status'] ?? '');
                                        $color = str_contains($s, 'تحویل') && ! str_contains($s, 'نشد')
                                            ? 'from-emerald-500 to-green-600'
                                            : (str_contains($s, 'مسیر') || str_contains($s, 'ارسال')
                                                ? 'from-cyan-500 to-blue-600'
                                                : 'from-amber-500 to-orange-500');
                                    @endphp

                                    <div class="flex items-start">
                                        <div class="flex flex-col items-center w-40" wire:key="event-{{ $i }}">
                                            <div class="relative">
                                                <div class="w-12 h-12 rounded-full bg-gradient-to-br {{ $color }} 
                                                            flex items-center justify-center text-white text-xl shadow-lg
                                                            {{ $isLast ? 'ring-4 ring-cyan-500/30 animate-pulse' : '' }}">
                                                    {{ $isLast ? '🚚' : ($i === 0 ? '📦' : '📍') }}
                                                </div>
                                                @if(! $isLast)
                                                    <div class="absolute top-1/2 -right-14 w-14 h-0.5 bg-gradient-to-l from-cyan-500 to-transparent"></div>
                                                @endif
                                            </div>
                                            <div class="mt-3 text-center w-36">
                                                <div class="text-xs font-bold text-base-content/80 leading-tight">
                                                    {{ \Illuminate\Support\Str::limit($e['status'] ?? '—', 30) }}
                                                </div>
                                                <div class="text-[10px] text-base-content/50 mt-1 font-mono" dir="ltr">
                                                    {{ $e['date'] ?? '' }}
                                                </div>
                                                @if(! empty($e['description']) && $e['description'] !== ($e['status'] ?? ''))
                                                    <div class="text-[10px] text-base-content/40 mt-1 leading-tight">
                                                        {{ \Illuminate\Support\Str::limit($e['description'], 60) }}
                                                    </div>
                                                @endif
                                            </div>
                                        </div>
                                    </div>
                                @endforeach
                            </div>
                        </div>
                    @endif
                </div>

                @if($order->tracking_code)
                    <a href="https://tipaxco.com/tracking?code={{ $order->tracking_code }}"
                       target="_blank"
                       class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-l from-cyan-500 to-teal-600 text-white text-xs font-bold hover:opacity-90 transition">
                        🔗 پیگیری در سایت تیپاکس
                    </a>
                @endif
            </div>
        </div>
    </div>
    @endif
</div>
