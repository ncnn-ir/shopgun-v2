<nav class="sg-mobile-bar">
    <div class="sg-mobile-bar-inner">
        @php
            $mobileItems = [
                ['dashboard', '🏠', 'داشبورد'],
                ['orders.index', '📦', 'سفارشات'],
                ['customers.index', '👥', 'مشتریان'],
                ['certificates.index', '💎', 'شناسنامه'],
                ['certificates.create', '✨', 'صدور'],
                ['products.bulk', '🚀', 'ثبت گروهی'],
                ['orders.supply-list', '📋', 'تأمین'],
                ['reports.index', '📈', 'گزارش'],
                ['activity-log', '📜', 'لاگ'],
                ['settings.index', '⚙️', 'تنظیمات'],
                ['about', 'ℹ️', 'درباره'],
            ];
        @endphp
        @foreach($mobileItems as $it)
            @php
                $base = explode('.', $it[0])[0];
                try {
                    $isActive = request()->routeIs($it[0]) || request()->routeIs($base . '.*');
                } catch (\Throwable $e) { $isActive = false; }
                try { $url = route($it[0]); } catch (\Throwable $e) { $url = '#'; }
            @endphp
            <a href="{{ $url }}" wire:navigate class="sg-mobile-bar-btn {{ $isActive ? 'active' : '' }}">
                <span class="ico">{{ $it[1] }}</span>
                <span>{{ $it[2] }}</span>
            </a>
        @endforeach
    </div>
</nav>
