<div class="flex flex-col h-full w-full overflow-hidden">

    {{-- ═══ لوگو ═══ --}}
    <div class="px-2.5 pt-2.5 pb-2">
        <a href="{{ route('dashboard') }}" wire:navigate
           class="flex items-center gap-2 p-2 rounded-xl"
           style="background: linear-gradient(135deg, rgba(13,148,136,0.15), rgba(8,145,178,0.08)); border: 1px solid rgba(13,148,136,0.2);">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-extrabold shadow"
                 style="background: linear-gradient(135deg, #14b8a6, #0891b2);">💎</div>
            <div class="flex-1 min-w-0">
                <div class="font-extrabold text-[12px] truncate">شاپگان</div>
                <div class="text-[9px] opacity-60">v2.1</div>
            </div>
        </a>
    </div>

    {{-- ═══ تاریخ ═══ --}}
    <div class="px-2.5 pb-2">
        <div class="flex items-center justify-between p-1.5 rounded-lg bg-black/5 dark:bg-white/5 text-[10.5px]">
            <div class="flex items-center gap-1">
                <span>📅</span>
                <span class="font-mono font-bold">{{ $today }}</span>
            </div>
            <span class="opacity-55 text-[9.5px]">{{ $dayOfWeek }}</span>
        </div>
    </div>

    {{-- ═══ KPI افقی ═══ --}}
    <div class="px-2 pb-2">
        <div class="text-[9.5px] font-bold opacity-45 mb-1 px-1">📊 امروز</div>
        <div class="sg-kpi-scroll">
            <a href="{{ route('orders.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['orders_today'] ?? 0) }}</div>
                <div class="lbl">امروز</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'pending']) }}" wire:navigate class="sg-kpi-card">
                <div class="num" style="color:#ea580c">{{ \App\Support\PersianNumber::toFa($stats['orders_pending'] ?? 0) }}</div>
                <div class="lbl">در انتظار</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'final-check']) }}" wire:navigate class="sg-kpi-card">
                <div class="num" style="color:#2563eb">{{ \App\Support\PersianNumber::toFa($stats['orders_check'] ?? 0) }}</div>
                <div class="lbl">چک</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'courier']) }}" wire:navigate class="sg-kpi-card">
                <div class="num" style="color:#16a34a">{{ \App\Support\PersianNumber::toFa($stats['orders_courier'] ?? 0) }}</div>
                <div class="lbl">مامور</div>
            </a>
            <a href="{{ route('customers.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['customers'] ?? 0) }}</div>
                <div class="lbl">مشتری</div>
            </a>
            <a href="{{ route('certificates.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['certificates'] ?? 0) }}</div>
                <div class="lbl">کارت</div>
            </a>
            <a href="{{ route('settings.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['products'] ?? 0) }}</div>
                <div class="lbl">محصول</div>
            </a>
        </div>
    </div>

    {{-- ═══ منو ═══ --}}
    <nav class="flex-1 overflow-y-auto px-2 pb-2">
        <ul class="space-y-0.5">
            @php
                $menu = [
                    ['route' => 'dashboard',          'icon' => '🏠', 'label' => 'داشبورد'],
                    ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارشات',   'badge' => $stats['orders_pending'] ?? 0],
                    ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتریان'],
                    ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'شناسنامه'],
        ['route' => 'products.bulk', 'icon' => '📦', 'label' => 'ثبت گروهی محصولات'],
                    ['route' => 'reports.index',      'icon' => '📊', 'label' => 'گزارش‌ها'],
                    ['route' => 'activity-log',       'icon' => '📜', 'label' => 'لاگ'],
                    ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیمات'],
                ];
            @endphp
            @foreach($menu as $m)
                @php $isActive = request()->routeIs($m['route']) || request()->routeIs(explode('.', $m['route'])[0] . '.*'); @endphp
                <li>
                    <a href="{{ route($m['route']) }}" wire:navigate
                       class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[12px] transition-all
                              {{ $isActive
                                  ? 'bg-primary/15 text-primary font-bold'
                                  : 'opacity-75 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5' }}">
                        <span class="text-[14px] leading-none">{{ $m['icon'] }}</span>
                        <span class="flex-1 truncate">{{ $m['label'] }}</span>
                        @if(!empty($m['badge']) && $m['badge'] > 0)
                            <span class="badge badge-warning badge-xs font-mono">{{ \App\Support\PersianNumber::toFa($m['badge']) }}</span>
                        @endif
                    </a>
                </li>
            @endforeach
        </ul>
    </nav>

    {{-- ═══ اعلان ═══ --}}
    @if($notifCount > 0)
        <div class="px-2 pb-2">
            <div class="rounded-lg p-2"
                 style="background: linear-gradient(135deg, rgba(251,146,60,0.12), rgba(248,113,113,0.08)); border: 1px solid rgba(251,146,60,0.25);">
                <div class="flex items-center gap-1.5 text-[10.5px] font-bold text-warning">
                    🔔 {{ \App\Support\PersianNumber::toFa($notifCount) }} اعلان
                </div>
            </div>
        </div>
    @endif

    {{-- ═══ فوتر ═══ --}}
    <div class="px-2 py-1.5 border-t border-black/5 dark:border-white/5 text-[9px] text-center opacity-45">
        اقاقیا · ۱۴۰۵
    </div>
</div>
