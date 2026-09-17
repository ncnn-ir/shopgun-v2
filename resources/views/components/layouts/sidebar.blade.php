{{-- Sidebar for desktop --}}
<aside class="sg-sidebar">
    @php
        $sgMenu = [
            ['route' => 'dashboard',          'icon' => '🏠', 'label' => 'داشبورد'],
            ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارشات'],
            ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتریان'],
            ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'شناسنامه‌ها'],
            ['route' => 'products.bulk', 'icon' => '📦', 'label' => 'ثبت گروهی محصولات'],
            ['route' => 'reports.index',      'icon' => '📊', 'label' => 'گزارش‌ها'],
            ['route' => 'activity-log',       'icon' => '📜', 'label' => 'لاگ فعالیت'],
            ['route' => 'users.index',        'icon' => '👤', 'label' => 'کاربران'],
            ['route' => 'roles.index',        'icon' => '🔐', 'label' => 'نقش‌ها'],
            ['route' => 'shipments.index',    'icon' => '📮', 'label' => 'مرسولات'],
            ['route' => 'file-manager',       'icon' => '📁', 'label' => 'فایل‌ها'],
            ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیمات'],
            ['route' => 'about',              'icon' => 'ℹ️', 'label' => 'درباره'],
        ];
    @endphp

    <nav class="sg-sidebar-nav">
        <ul>
            @foreach($sgMenu as $m)
                @php
                    $active = false;
                    try {
                        $base = explode('.', $m['route'])[0];
                        $active = request()->routeIs($m['route']) || request()->routeIs($base . '.*');
                    } catch (\Throwable $e) {}
                @endphp
                <li>
                    <a href="{{ route($m['route']) }}" wire:navigate
                       class="sg-sidebar-link {{ $active ? 'active' : '' }}">
                        <span class="sg-sidebar-icon">{{ $m['icon'] }}</span>
                        <span class="sg-sidebar-label">{{ $m['label'] }}</span>
                    </a>
                </li>
            @endforeach
        </ul>
    </nav>
</aside>