<aside class="sg-sidebar">
    <div style="padding:14px 12px">
        <a href="{{ route('dashboard') }}" wire:navigate
           style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:12px;text-decoration:none;background:linear-gradient(135deg,rgba(26,82,118,.12),rgba(26,82,118,.04));border:1px solid rgba(26,82,118,.15)">
            <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#1a5276,#0d3b5e);display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px">💎</div>
            <div style="flex:1;min-width:0">
                <div style="font-weight:800;font-size:13px;color:var(--sg-text)">جواهری مشاهیر</div>
                <div style="font-size:10px;color:var(--sg-text-muted);font-family:monospace">ShopGun v2.2</div>
            </div>
        </a>
    </div>

    @php
        $menuGroups = [
            'اصلی' => [
                ['route' => 'dashboard', 'icon' => '📊', 'label' => 'داشبورد'],
                ['route' => 'orders.index', 'icon' => '📦', 'label' => 'سفارشات'],
                ['route' => 'customers.index', 'icon' => '👥', 'label' => 'مشتریان'],
                ['route' => 'orders.supply-list', 'icon' => '📋', 'label' => 'لیست تأمین'],
            ],
            'شناسنامه' => [
                ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'لیست شناسنامه‌ها'],
                ['route' => 'certificates.create', 'icon' => '✨', 'label' => 'صدور شناسنامه'],
            ],
            'محصولات' => [
                ['route' => 'products.bulk', 'icon' => '🚀', 'label' => 'ثبت گروهی'],
            ],
            'تحلیل' => [
                ['route' => 'reports.index', 'icon' => '📈', 'label' => 'گزارش‌ها'],
                ['route' => 'activity-log', 'icon' => '📜', 'label' => 'لاگ فعالیت'],
            ],
            'سیستم' => [
                ['route' => 'settings.index', 'icon' => '⚙️', 'label' => 'تنظیمات'],
                ['route' => 'about', 'icon' => 'ℹ️', 'label' => 'درباره'],
            ],
        ];
    @endphp

    <nav style="padding:6px 8px 20px;overflow-y:auto;flex:1">
        @foreach($menuGroups as $groupName => $items)
            <div style="margin-bottom:12px">
                <div style="font-size:9.5px;font-weight:800;color:var(--sg-text-muted);padding:6px 10px;letter-spacing:.5px">{{ $groupName }}</div>
                @foreach($items as $item)
                    @php
                        $base = explode('.', $item['route'])[0];
                        try {
                            $isActive = request()->routeIs($item['route']) || request()->routeIs($base . '.*');
                        } catch (\Throwable $e) { $isActive = false; }
                        try { $url = route($item['route']); } catch (\Throwable $e) { $url = '#'; }
                    @endphp
                    <a href="{{ $url }}" wire:navigate
                       style="display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:10px;text-decoration:none;margin-bottom:2px;transition:var(--sg-t-fast);
                            {{ $isActive ? 'background:linear-gradient(135deg,var(--sg-primary),var(--sg-primary-hover));color:var(--sg-text-inverse);font-weight:700' : 'color:var(--sg-text-secondary)' }}"
                       onmouseover="if(!{{ $isActive ? 'true' : 'false' }})this.style.background='var(--sg-bg-soft)'"
                       onmouseout="if(!{{ $isActive ? 'true' : 'false' }})this.style.background='transparent'">
                        <span style="font-size:16px;width:22px;text-align:center">{{ $item['icon'] }}</span>
                        <span style="font-size:12.5px;font-weight:{{ $isActive ? '700' : '600' }}">{{ $item['label'] }}</span>
                    </a>
                @endforeach
            </div>
        @endforeach
    </nav>

    <div style="padding:12px;border-top:1px solid var(--sg-divider);display:flex;justify-content:space-between;align-items:center">
        <div style="display:flex;align-items:center;gap:8px">
            <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--sg-primary),var(--sg-primary-hover));display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:700">
                {{ mb_substr(auth()->user()->name ?? '?', 0, 1) }}
            </div>
            <div style="min-width:0">
                <div style="font-size:11.5px;font-weight:700;color:var(--sg-text)" class="sg-truncate">{{ auth()->user()->name ?? 'کاربر' }}</div>
                <div style="font-size:9.5px;color:var(--sg-text-muted)" class="sg-truncate" dir="ltr">{{ auth()->user()->email ?? '' }}</div>
            </div>
        </div>
        <form method="POST" action="{{ route('logout') }}" style="display:inline">
            @csrf
            <button type="submit" style="background:rgba(239,68,68,.1);color:#ef4444;border:none;padding:6px 8px;border-radius:8px;cursor:pointer;font-size:14px" title="خروج">🚪</button>
        </form>
    </div>
</aside>
