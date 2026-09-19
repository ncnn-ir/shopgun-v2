@teleport('body')
<div>
@if($open && $order)
<div class="fixed inset-0 z-50 flex items-center justify-center p-2 md:p-6"
     x-data x-init="$nextTick(() => { if (window.L) window.__initOrderMap(@js($origin), @js($dest)); })"
     wire:key="otm-{{ $order->id }}">

    {{-- پرده --}}
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" wire:click="close"></div>

    {{-- کارت --}}
    <div class="relative w-full max-w-5xl max-h-[94vh] overflow-y-auto
                bg-white dark:bg-gray-900 rounded-2xl shadow-2xl">

        {{-- هدر --}}
        <div class="sticky top-0 z-20 flex items-center justify-between p-4
                    bg-white/95 dark:bg-gray-900/95 backdrop-blur
                    border-b border-gray-200 dark:border-gray-700">
            <div>
                <h2 class="text-lg font-bold text-gray-800 dark:text-gray-100">
                    🗺 وضعیت سفارش <span class="text-indigo-600">#{{ $order->id }}</span>
                </h2>
                <div class="mt-1 flex items-center gap-2">
                    <span class="text-xs text-gray-500">کانال:</span>
                    <x-channel-badge :channel="$order->sales_channel" />
                </div>

                <p class="text-xs text-gray-500 mt-0.5">
                    {{ trim(($order->customer->first_name ?? '') . ' ' . ($order->customer->last_name ?? '')) }}
                    — {{ $order->customer->phone ?? '' }}
                </p>
            </div>
            <button wire:click="close"
                class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500">
                ✕
            </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-0">

            {{-- نقشه --}}
            <div class="relative">
                <div id="order-map-{{ $order->id }}"
                     class="w-full h-[420px] lg:h-full min-h-[420px]
                            bg-gradient-to-br from-slate-100 to-slate-200
                            dark:from-slate-800 dark:to-slate-900"
                     style="filter: saturate(0.9);"
                     wire:ignore></div>

                {{-- کارت مبدا / مقصد --}}
                <div class="absolute top-3 right-3 left-3 flex flex-wrap gap-2 pointer-events-none">
                    <div class="pointer-events-auto bg-white/90 dark:bg-gray-900/90 backdrop-blur
                                rounded-lg px-3 py-1.5 text-xs shadow">
                        <span class="font-bold text-green-600">◉ مبدا:</span>
                        {{ $origin['name'] }}
                    </div>
                    <div class="pointer-events-auto bg-white/90 dark:bg-gray-900/90 backdrop-blur
                                rounded-lg px-3 py-1.5 text-xs shadow">
                        <span class="font-bold text-red-600">◉ مقصد:</span>
                        {{ $dest['name'] ?? '—' }}
                    </div>
                </div>

                {{-- فاصله --}}
                <div class="absolute bottom-3 left-3 bg-white/90 dark:bg-gray-900/90 backdrop-blur
                            rounded-lg px-3 py-1.5 text-xs shadow">
                    <span class="text-gray-500">فاصله تقریبی:</span>
                    <span id="order-distance" class="font-bold text-indigo-600">—</span>
                </div>
            </div>

            {{-- تایم‌لاین --}}
            <div class="p-4 md:p-6">
                <h3 class="font-bold text-gray-800 dark:text-gray-100 mb-4">
                    📅 مراحل سفارش
                </h3>

                <ol class="relative border-r-2 border-gray-200 dark:border-gray-700 pr-6 space-y-6">
                    @foreach($timeline as $i => $stage)
                        <li class="relative">
                            {{-- نقطه --}}
                            <span class="absolute -right-[33px] top-0 w-5 h-5 rounded-full border-2
                                flex items-center justify-center text-[10px]
                                {{ $stage['done']
                                    ? 'bg-green-500 border-green-500 text-white'
                                    : 'bg-white dark:bg-gray-900 border-gray-300 dark:border-gray-600 text-gray-400' }}">
                                @if($stage['done']) ✓ @else ○ @endif
                            </span>

                            <div class="rounded-xl border p-3
                                {{ $stage['done']
                                    ? 'bg-green-50/50 dark:bg-green-900/10 border-green-200 dark:border-green-900/50'
                                    : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 opacity-60' }}">
                                <div class="flex items-center justify-between gap-2">
                                    <div class="flex items-center gap-2">
                                        <span class="text-lg">{{ $stage['icon'] }}</span>
                                        <span class="font-semibold text-sm text-gray-800 dark:text-gray-100">
                                            {{ $stage['title'] }}
                                        </span>
                                    </div>
                                    @if($stage['done'])
                                        <span class="text-[10px] text-green-700 dark:text-green-300
                                                     bg-green-100 dark:bg-green-900/40 rounded-full px-2 py-0.5">
                                            انجام شد
                                        </span>
                                    @else
                                        <span class="text-[10px] text-gray-500">در انتظار</span>
                                    @endif
                                </div>

                                @if($stage['at'])
                                    <div class="mt-2 text-xs text-gray-600 dark:text-gray-400
                                                flex items-center gap-2 flex-wrap">
                                        <span class="font-mono">
                                            📆 {{ $stage['at']->format('Y/m/d') }}
                                        </span>
                                        <span class="font-mono">
                                            ⏰ {{ $stage['at']->format('H:i:s') }}
                                        </span>
                                        <span class="text-gray-400">
                                            ({{ $stage['at']->diffForHumans() }})
                                        </span>
                                    </div>
                                @endif
                            </div>
                        </li>
                    @endforeach
                </ol>
            </div>
        </div>
    </div>
</div>

{{-- Leaflet از CDN --}}
@once
    @push('styles')
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            .leaflet-container { font-family: inherit; }
            .sg-map-blur .leaflet-tile { filter: blur(0.4px) saturate(0.85) brightness(1.05); }
            .sg-dash { stroke-dasharray: 10 8; animation: sgdash 1.6s linear infinite; }
            @keyframes sgdash { to { stroke-dashoffset: -36; } }
        </style>
    @endpush

    @push('scripts')
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            window.__initOrderMap = function(origin, dest) {
                const el = document.querySelector('[id^="order-map-"]');
                if (!el || !window.L) return;
                if (el._sg_map) { el._sg_map.remove(); }
                if (!dest) return;

                const map = L.map(el, { zoomControl: true, attributionControl: false })
                             .addClass('sg-map-blur');
                el._sg_map = map;

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 18
                }).addTo(map);

                const oIcon = L.divIcon({
                    className: '', iconSize: [26, 26],
                    html: '<div style="background:#16a34a;width:22px;height:22px;border-radius:50%;' +
                          'border:3px solid #fff;box-shadow:0 0 0 3px rgba(22,163,74,.3);"></div>'
                });
                const dIcon = L.divIcon({
                    className: '', iconSize: [26, 26],
                    html: '<div style="background:#dc2626;width:22px;height:22px;border-radius:50%;' +
                          'border:3px solid #fff;box-shadow:0 0 0 3px rgba(220,38,38,.3);"></div>'
                });

                const o = [origin.lat, origin.lng];
                const d = [dest.lat, dest.lng];

                L.marker(o, { icon: oIcon }).addTo(map).bindPopup('<b>مبدا</b><br>' + origin.name);
                L.marker(d, { icon: dIcon }).addTo(map).bindPopup('<b>مقصد</b><br>' +
                    (dest.address || dest.name || ''));

                L.polyline([o, d], {
                    color: '#6366f1', weight: 3, opacity: 0.85, className: 'sg-dash'
                }).addTo(map);

                map.fitBounds([o, d], { padding: [40, 40] });

                const km = map.distance(o, d) / 1000;
                const el2 = document.getElementById('order-distance');
                if (el2) el2.textContent = km.toFixed(0) + ' کیلومتر';
            };
        </script>
    @endpush
@endonce
@endif
</div>
@endteleport
