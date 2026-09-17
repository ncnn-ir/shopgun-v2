<div class="p-4 md:p-6 space-y-4" dir="rtl" >

    {{-- ═══ Header با دکمه‌ها ═══ --}}
    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🩺 سلامت سیستم</h1>
            <p class="text-xs text-base-content/60 mt-1">نمای کلی از وضعیت سیستم، اتصالات و پکیج‌ها</p>
        </div>
        <div class="flex flex-wrap gap-2">
            <button wire:click="refresh" class="btn btn-outline btn-sm">
                <span wire:loading.remove wire:target="refresh">🔄 بروزرسانی</span>
                <span wire:loading wire:target="refresh">⏳...</span>
            </button>
            <button @click="window.sgCopy(@js($this->full_report))" class="btn btn-primary btn-sm">
                📋 کپی کامل
            </button>
            <button @click="window.sgCopy(@js($this->error_report))" class="btn btn-error btn-sm">
                📋 فقط خطاها
            </button>
        </div>
    </div>

    {{-- ═══ تست اتصال WooCommerce ═══ --}}
    <div class="card bg-base-100 shadow border-2 border-primary/20">
        <div class="card-body p-4">
            <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
                <h2 class="font-bold text-base flex items-center gap-2">
                    🔌 تست اتصال به سایت (WooCommerce)
                </h2>
                <button wire:click="testConnection"
                        wire:loading.attr="disabled"
                        class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="testConnection">⚡ تست اتصال</span>
                    <span wire:loading wire:target="testConnection">⏳ در حال تست...</span>
                </button>
            </div>

            @if(!empty($connection))
                @if(($connection['status'] ?? '') === 'ok')
                    <div class="alert alert-success mb-3">
                        <div>
                            <div class="font-bold">✅ {{ $connection['message'] }}</div>
                            <div class="text-xs mt-1 grid grid-cols-2 md:grid-cols-4 gap-2">
                                <div>🌐 WP: <b>{{ $connection['wp_version'] ?? '?' }}</b></div>
                                <div>🛒 WC: <b>{{ $connection['wc_version'] ?? '?' }}</b></div>
                                <div>💵 ارز: <b>{{ $connection['currency'] ?? '?' }}</b></div>
                                <div>⏱️ پاسخ: <b>{{ $connection['time_ms'] ?? 0 }} ms</b></div>
                            </div>
                        </div>
                    </div>
                @elseif(($connection['status'] ?? '') === 'error')
                    <div class="alert alert-error mb-3">
                        <div>
                            <div class="font-bold">❌ {{ $connection['message'] }}</div>
                            @if(!empty($connection['hint']))
                                <div class="text-xs mt-1">💡 {{ $connection['hint'] }}</div>
                            @endif
                        </div>
                    </div>
                @endif
            @endif

            @if(!empty($wcCounts))
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                    @foreach($wcCounts as $key => $c)
                        <div class="p-3 rounded-lg bg-base-200/50 border border-base-300">
                            <div class="flex items-center justify-between mb-1">
                                <span class="font-bold text-sm">{{ $c['label'] }}</span>
                                <span class="text-lg">{{ $c['ok'] ? '✅' : '❌' }}</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2 mt-2 text-xs">
                                <div class="text-center p-2 bg-info/10 rounded">
                                    <div class="text-[10px] text-base-content/60">سایت</div>
                                    <div class="font-bold font-mono text-info">
                                        {{ \App\Support\PersianNumber::toFa(number_format($c['total'])) }}
                                    </div>
                                </div>
                                <div class="text-center p-2 bg-primary/10 rounded">
                                    <div class="text-[10px] text-base-content/60">لوکال</div>
                                    <div class="font-bold font-mono text-primary">
                                        {{ \App\Support\PersianNumber::toFa(number_format($c['local'])) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    @endforeach
                </div>

                @if(!empty($wcProducts))
                    <div class="divider my-2 text-xs">📦 ۵ محصول آخر از سایت</div>
                    <div class="overflow-x-auto">
                        <table class="table table-xs table-zebra">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>نام محصول</th>
                                    <th>SKU</th>
                                    <th>قیمت</th>
                                    <th>موجودی</th>
                                    <th>وضعیت سایت</th>
                                    <th>محلی</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($wcProducts as $p)
                                    <tr>
                                        <td class="font-mono text-[10px]">{{ $p['id'] }}</td>
                                        <td class="max-w-[180px] truncate text-xs">{{ $p['name'] }}</td>
                                        <td class="font-mono text-[10px]" dir="ltr">{{ $p['sku'] }}</td>
                                        <td class="font-mono text-[10px]">{{ number_format($p['price']) }}</td>
                                        <td class="font-mono text-[10px]">{{ $p['stock'] ?? '—' }}</td>
                                        <td><span class="badge badge-info badge-xs">{{ $p['status'] }}</span></td>
                                        <td>
                                            <span class="badge badge-xs {{ $p['local'] ? 'badge-success' : 'badge-ghost' }}">
                                                {{ $p['local'] ? '✓' : '—' }}
                                            </span>
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                @endif
            @else
                <div class="text-center py-6 text-base-content/50 text-sm">
                    دکمه «⚡ تست اتصال» را بزن تا وضعیت سایت بررسی شود
                </div>
            @endif
        </div>
    </div>

    {{-- ═══ اطلاعات سیستم ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">💻 اطلاعات سیستم</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                @foreach($system as $s)
                    <div class="p-2 rounded-lg {{ $s['ok'] ? 'bg-success/5 border border-success/30' : 'bg-warning/5 border border-warning/30' }}">
                        <div class="text-[10px] text-base-content/60">{{ $s['label'] }}</div>
                        <div class="font-mono font-bold text-xs mt-0.5 truncate" dir="ltr">{{ $s['value'] }}</div>
                    </div>
                @endforeach
            </div>
        </div>
    </div>

    {{-- ═══ صفحات با برچسب جدید ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3 flex items-center gap-2">
                🚀 صفحات
                <span class="badge badge-warning badge-sm">🆕 = ویژگی جدید</span>
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
                @foreach($features as $f)
                    @if($f['ok'])
                        <a href="{{ $f['url'] }}" wire:navigate
                           class="relative block p-3 rounded-lg border-2 {{ ($f['new'] ?? false) ? 'border-warning bg-warning/5' : 'border-success/30 bg-success/5' }} hover:shadow-md transition">
                            @if($f['new'] ?? false)
                                <span class="absolute -top-2 -right-2 badge badge-warning badge-xs font-bold">🆕</span>
                            @endif
                            <div class="flex items-center justify-between mb-1">
                                <span class="text-2xl">{{ $f['icon'] }}</span>
                                <span class="badge badge-success badge-xs">✓</span>
                            </div>
                            <div class="font-bold text-sm">{{ $f['label'] }}</div>
                            <div class="text-[10px] text-base-content/60 mt-0.5">{{ $f['desc'] }}</div>
                        </a>
                    @else
                        <div class="relative block p-3 rounded-lg border-2 border-error/30 bg-error/5 opacity-60">
                            <div class="flex items-center justify-between mb-1">
                                <span class="text-2xl">{{ $f['icon'] }}</span>
                                <span class="badge badge-error badge-xs">✕</span>
                            </div>
                            <div class="font-bold text-sm">{{ $f['label'] }}</div>
                            <div class="text-[10px] text-base-content/60 mt-0.5">ساخته نشده</div>
                        </div>
                    @endif
                @endforeach
            </div>
        </div>
    </div>

    {{-- ═══ جداول دیتابیس ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">
                🗄️ جداول دیتابیس ({{ \App\Support\PersianNumber::toFa(count($database)) }})
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                @foreach($database as $t)
                    <div class="p-2 rounded-lg {{ $t['exists'] ? 'bg-success/5 border border-success/30' : 'bg-error/5 border border-error/30 opacity-60' }}">
                        <div class="flex items-center justify-between gap-1">
                            <div class="min-w-0 flex-1">
                                <div class="font-bold text-xs truncate">{{ $t['label'] }}</div>
                                <div class="font-mono text-[9px] text-base-content/50 truncate" dir="ltr">{{ $t['name'] }}</div>
                            </div>
                            @if($t['exists'])
                                <span class="badge badge-success badge-xs font-mono shrink-0">
                                    {{ \App\Support\PersianNumber::toFa(number_format($t['count'])) }}
                                </span>
                            @else
                                <span class="badge badge-error badge-xs shrink-0">❌</span>
                            @endif
                        </div>
                    </div>
                @endforeach
            </div>
        </div>
    </div>

    {{-- ═══ پکیج‌ها ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">📦 پکیج‌های نصب‌شده</h2>
            @php
                $gl = [
                    'core'=>'🏗️ هسته','auth'=>'🔐 احراز هویت','table'=>'📊 جداول',
                    'log'=>'📜 لاگ','media'=>'🎨 رسانه','form'=>'📝 فرم',
                    'ui'=>'🎨 رابط کاربری','export'=>'📤 خروجی','debug'=>'🐛 دیباگ',
                    'update'=>'🔄 بروزرسانی','backup'=>'💾 پشتیبان','js'=>'🟨 JS',
                ];
            @endphp
            @foreach($packages as $group => $items)
                <div class="mb-3">
                    <div class="text-xs font-bold text-base-content/70 mb-2 pb-1 border-b border-base-300">
                        {{ $gl[$group] ?? $group }}
                        <span class="badge badge-ghost badge-xs mr-1">{{ \App\Support\PersianNumber::toFa(count($items)) }}</span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        @foreach($items as $p)
                            <div class="flex items-center justify-between p-2 rounded-lg {{ $p['ok'] ? 'bg-success/5 border border-success/20' : 'bg-error/5 border border-error/30' }}">
                                <div class="min-w-0">
                                    <div class="text-xs font-bold truncate">{{ $p['label'] }}</div>
                                    <div class="font-mono text-[10px] text-base-content/50 truncate" dir="ltr">
                                        {{ $p['version'] ?? 'نصب نیست' }}
                                    </div>
                                </div>
                                <span class="text-base shrink-0">{{ $p['ok'] ? '✅' : '❌' }}</span>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- ═══ جدول خلاصه با دکمه‌های کپی ═══ --}}
    <div class="card bg-base-100 shadow border-2 border-primary/30">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3 flex items-center justify-between">
                <span>📋 جدول خلاصه گزارش</span>
                <button @click="window.sgCopy(@js($this->full_report))" class="btn btn-primary btn-xs">
                    📋 کپی همه
                </button>
            </h2>
            <div class="overflow-x-auto">
                <table class="table table-xs table-zebra">
                    <thead>
                        <tr>
                            <th>مورد</th>
                            <th>وضعیت</th>
                            <th>جزئیات</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="font-bold text-xs">اتصال WooCommerce</td>
                            <td>
                                <span class="badge badge-xs {{ ($connection['status'] ?? '') === 'ok' ? 'badge-success' : (($connection['status'] ?? '') === 'error' ? 'badge-error' : 'badge-ghost') }}">
                                    {{ ($connection['status'] ?? '') === 'ok' ? '✓' : (($connection['status'] ?? '') === 'error' ? '✕' : '?') }}
                                </span>
                            </td>
                            <td class="text-xs">{{ $connection['message'] ?? 'تست نشده' }}</td>
                            <td>
                                <button wire:click="testConnection" class="btn btn-ghost btn-xs">تست</button>
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold text-xs">پکیج‌ها</td>
                            <td>
                                @php
                                    $total = 0; $ok = 0;
                                    foreach ($packages as $g) { foreach ($g as $p) { $total++; if ($p['ok']) $ok++; } }
                                @endphp
                                <span class="badge badge-xs {{ $ok === $total ? 'badge-success' : 'badge-warning' }}">
                                    {{ \App\Support\PersianNumber::toFa("$ok/$total") }}
                                </span>
                            </td>
                            <td class="text-xs">{{ $total - $ok }} مورد نصب نیست</td>
                            <td>
                                <button @click="window.sgCopy(@js($this->error_report))" class="btn btn-ghost btn-xs">📋</button>
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold text-xs">صفحات</td>
                            <td>
                                @php $okF = count(array_filter($features, fn($f) => $f['ok'])); @endphp
                                <span class="badge badge-xs {{ $okF === count($features) ? 'badge-success' : 'badge-warning' }}">
                                    {{ \App\Support\PersianNumber::toFa("$okF/" . count($features)) }}
                                </span>
                            </td>
                            <td class="text-xs">{{ count($features) - $okF }} صفحه ساخته نشده</td>
                            <td>
                                <button wire:click="openReportModal('full')" class="btn btn-ghost btn-xs">📋</button>
                            </td>
                        </tr>
                        <tr>
                            <td class="font-bold text-xs">جداول DB</td>
                            <td>
                                @php $okT = count(array_filter($database, fn($t) => $t['exists'])); @endphp
                                <span class="badge badge-xs {{ $okT === count($database) ? 'badge-success' : 'badge-warning' }}">
                                    {{ \App\Support\PersianNumber::toFa("$okT/" . count($database)) }}
                                </span>
                            </td>
                            <td class="text-xs">{{ count($database) - $okT }} جدول گم‌شده</td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- ═══ Modal گزارش ═══ --}}
    @if($showReportModal)
    <div class="fixed inset-0 z-[100] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/70 backdrop-blur-md" wire:click="closeReportModal"></div>
        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <h2 class="font-bold text-base">📋 گزارش کامل</h2>
                <div class="flex gap-2">
                    <button @click="window.sgCopy(@js($reportText))" class="btn btn-primary btn-sm">📋 کپی</button>
                    <button wire:click="closeReportModal" class="btn btn-ghost btn-sm btn-circle">✕</button>
                </div>
            </div>
            <div class="p-4 max-h-[70vh] overflow-auto">
                <pre class="text-[10px] md:text-xs font-mono whitespace-pre-wrap bg-base-200/50 p-3 rounded-lg" dir="ltr">{{ $reportText }}</pre>
            </div>
        </div>
    </div>
    @endif
</div>

<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('healthPage', () => ({
        async copyText(text) {
            try {
                await navigator.clipboard.writeText(text);
            } catch (e) {
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed'; ta.style.opacity = '0';
                document.body.appendChild(ta); ta.select();
                document.execCommand('copy'); document.body.removeChild(ta);
            }
            if (window.sgToast) window.sgToast('کپی شد ✅', 'success');
        }
    }));
});
</script>
