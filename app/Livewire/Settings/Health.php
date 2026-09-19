<?php

namespace App\Livewire\Settings;

use Livewire\Component;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Http;
use App\Models\AppSetting;

class Health extends Component
{
    public array $packages = [];
    public array $features = [];
    public array $system = [];
    public array $database = [];

    // ═══ تست اتصال WooCommerce ═══
    public bool $testing = false;
    public array $connection = [];
    public array $wcCounts = [];
    public array $wcProducts = [];
    public bool $showReportModal = false;
    public string $reportText = '';

    public function mount(): void
    {
        $this->loadPackages();
        $this->loadFeatures();
        $this->loadSystem();
        $this->loadDatabase();
    }

    public function refresh(): void
    {
        $this->mount();
        $this->dispatch('notify', type: 'success', message: 'سلامت سیستم بروزرسانی شد');
    }

    /* ═══════════════════════════════════════════════════════════
       تست اتصال WooCommerce
       ═══════════════════════════════════════════════════════════ */
    public function testConnection(): void
    {
        $this->testing = true;
        $this->connection = ['status' => 'testing'];
        $this->wcCounts = [];
        $this->wcProducts = [];

        $url    = trim((string) AppSetting::get('commerce_url', ''));
        $key    = trim((string) AppSetting::get('commerce_key', ''));
        $secret = trim((string) AppSetting::get('commerce_secret', ''));

        if (!$url || !$key || !$secret) {
            $this->connection = [
                'status' => 'error',
                'message' => 'اطلاعات اتصال کامل نیست. به تنظیمات → کامرس برو.',
            ];
            $this->testing = false;
            return;
        }

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) {
            $base .= '/wp-json/wc/v3';
        }

        // مرحله ۱: تست اتصال پایه
        try {
            $start = microtime(true);
            $r = Http::withBasicAuth($key, $secret)
                ->timeout(20)
                ->connectTimeout(10)
                ->get($base . '/system_status');
            $ms = (int) round((microtime(true) - $start) * 1000);

            if (!$r->successful()) {
                $this->connection = [
                    'status' => 'error',
                    'message' => "HTTP {$r->status()} — کلید یا آدرس اشتباه است",
                    'code' => $r->status(),
                ];
                $this->testing = false;
                return;
            }

            $data = $r->json();
            $this->connection = [
                'status' => 'ok',
                'message' => 'اتصال برقرار است',
                'wp_version' => $data['environment']['wp_version'] ?? '?',
                'wc_version' => $data['environment']['version'] ?? '?',
                'currency' => $data['settings']['currency'] ?? '?',
                'country' => $data['settings']['country'] ?? '?',
                'time_ms' => $ms,
                'url' => $base,
            ];
        } catch (\Throwable $e) {
            $this->connection = [
                'status' => 'error',
                'message' => 'اتصال برقرار نشد: ' . $e->getMessage(),
                'hint' => 'شبکه را چک کن یا از Import JSON استفاده کن',
            ];
            $this->testing = false;
            return;
        }

        // مرحله ۲: شمارش محصولات/سفارشات/مشتریان
        $endpoints = [
            'products'  => 'محصولات',
            'orders'    => 'سفارشات',
            'customers' => 'مشتریان',
        ];

        foreach ($endpoints as $ep => $label) {
            try {
                $r = Http::withBasicAuth($key, $secret)
                    ->timeout(20)
                    ->get($base . "/{$ep}?per_page=1");
                // ★ هم هدر و هم body را چک کن
                $hdr = $r->header('X-WP-Total');
                $total = $hdr !== null ? (int) $hdr : 0;
                if ($total === 0 && $r->successful()) {
                    // اگر هدر نبود، از body نتیجه بگیر
                    $body = $r->json();
                    if (is_array($body)) $total = count($body);
                }
                $this->wcCounts[$ep] = [
                    'label' => $label,
                    'total' => $total,
                    'local' => $this->localCount($ep),
                    'ok' => $r->successful(),
                ];
            } catch (\Throwable $e) {
                $this->wcCounts[$ep] = [
                    'label' => $label,
                    'total' => 0,
                    'local' => $this->localCount($ep),
                    'ok' => false,
                    'error' => $e->getMessage(),
                ];
            }
        }

        // مرحله ۳: ۵ محصول نمونه
        try {
            $r = Http::withBasicAuth($key, $secret)
                ->timeout(15)
                ->get($base . '/products?per_page=5&orderby=date&order=desc');
            if ($r->successful()) {
                $this->wcProducts = collect($r->json())->map(fn($p) => [
                    'id'    => $p['id'] ?? 0,
                    'name'  => $p['name'] ?? '—',
                    'sku'   => $p['sku'] ?? '—',
                    'price' => (float) ($p['price'] ?? 0),
                    'stock' => $p['stock_quantity'] ?? null,
                    'status'=> $p['status'] ?? '—',
                    'image' => $p['images'][0]['src'] ?? null,
                    'local' => \App\Models\Product::where('sku', $p['sku'] ?? '')->exists(),
                ])->toArray();
            }
        } catch (\Throwable $e) {}

        // مرحله ۴: تست دریافت سفارشات
        try {
            $r = Http::withBasicAuth($key, $secret)
                ->timeout(15)
                ->get($base . '/orders?per_page=1');
            $this->connection['orders_test'] = $r->successful() ? 'ok' : 'fail';
        } catch (\Throwable $e) {
            $this->connection['orders_test'] = 'fail';
        }

        $this->testing = false;
        $this->dispatch('notify', type: 'success', message: 'تست اتصال انجام شد ✅');
    }

    protected function localCount(string $ep): int
    {
        return match ($ep) {
            'products' => \App\Models\Product::count(),
            'orders'   => \App\Models\Order::count(),
            'customers'=> \App\Models\Customer::count(),
            default    => 0,
        };
    }

    /* ═══════════════════════════════════════════════════════════
       کپی گزارش‌ها
       ═══════════════════════════════════════════════════════════ */
    public function openReportModal(string $type = 'full'): void
    {
        $this->reportText = $type === 'error'
            ? $this->getErrorReportProperty()
            : $this->getFullReportProperty();
        $this->showReportModal = true;
    }

    public function closeReportModal(): void
    {
        $this->showReportModal = false;
        $this->reportText = '';
    }

    public function getFullReportProperty(): string
    {
        $l = [];
        $l[] = '╔══════════════════════════════════════════════╗';
        $l[] = '║  ShopGun V2 — گزارش سلامت سیستم              ║';
        $l[] = '╚══════════════════════════════════════════════╝';
        $l[] = '📅 ' . \App\Support\PersianDate::format(now(), 'Y/m/d H:i');
        $l[] = '';

        $l[] = '━━━ 💻 سیستم ━━━';
        foreach ($this->system as $s) {
            $l[] = ($s['ok'] ? '✅' : '⚠️') . " {$s['label']}: {$s['value']}";
        }

        $l[] = '';
        $l[] = '━━━ 🗄️ جداول ━━━';
        foreach ($this->database as $t) {
            $c = $t['exists'] ? number_format($t['count']) : '—';
            $l[] = ($t['exists'] ? '✅' : '❌') . " {$t['name']} ({$t['label']}): {$c}";
        }

        $l[] = '';
        $l[] = '━━━ 🚀 صفحات ━━━';
        foreach ($this->features as $f) {
            $new = ($f['new'] ?? false) ? ' 🆕' : '';
            $l[] = ($f['ok'] ? '✅' : '❌') . " {$f['label']}{$new} — {$f['desc']}";
        }

        $l[] = '';
        $l[] = '━━━ 📦 پکیج‌ها ━━━';
        foreach ($this->packages as $group => $items) {
            $l[] = "[{$group}]";
            foreach ($items as $p) {
                $v = $p['version'] ?? 'نصب نیست';
                $l[] = ($p['ok'] ? '✅' : '❌') . " {$p['label']}: {$v}";
            }
        }

        if (!empty($this->connection)) {
            $l[] = '';
            $l[] = '━━━ 🔌 اتصال WooCommerce ━━━';
            $l[] = 'وضعیت: ' . ($this->connection['status'] ?? '?');
            if (!empty($this->connection['message'])) $l[] = 'پیام: ' . $this->connection['message'];
            foreach ($this->wcCounts as $k => $c) {
                $l[] = "• {$c['label']}: سایت={$c['total']} / لوکال={$c['local']}";
            }
        }

        return implode("\n", $l);
    }

    public function getErrorReportProperty(): string
    {
        $l = [];
        $l[] = '╔══════════════════════════════════════════════╗';
        $l[] = '║  ShopGun V2 — خطاها و مشکلات                  ║';
        $l[] = '╚══════════════════════════════════════════════╝';
        $l[] = '📅 ' . \App\Support\PersianDate::format(now(), 'Y/m/d H:i');
        $l[] = '';
        $has = false;

        foreach ($this->system as $s) {
            if (!$s['ok']) { $l[] = "⚠️ {$s['label']}: {$s['value']}"; $has = true; }
        }

        foreach ($this->database as $t) {
            if (!$t['exists']) { $l[] = "❌ جدول: {$t['name']} ({$t['label']})"; $has = true; }
        }

        foreach ($this->features as $f) {
            if (!$f['ok']) { $l[] = "❌ صفحه: {$f['label']} — {$f['desc']}"; $has = true; }
        }

        foreach ($this->packages as $g => $items) {
            foreach ($items as $p) {
                if (!$p['ok']) { $l[] = "❌ پکیج: {$p['label']} ({$p['name']})"; $has = true; }
            }
        }

        if (($this->connection['status'] ?? '') === 'error') {
            $l[] = "❌ اتصال: " . ($this->connection['message'] ?? '?');
            $has = true;
        }

        if (!$has) $l[] = '✅ هیچ خطایی یافت نشد!';

        return implode("\n", $l);
    }

    /* ═══════════════════════════════════════════════════════════
       لودرها
       ═══════════════════════════════════════════════════════════ */
    protected function loadPackages(): void
    {
        $lock = base_path('composer.lock');
        $installed = [];
        if (file_exists($lock)) {
            $data = json_decode(file_get_contents($lock), true) ?: [];
            foreach ($data['packages'] ?? [] as $p) $installed[$p['name']] = $p['version'];
            foreach ($data['packages-dev'] ?? [] as $p) $installed[$p['name']] = $p['version'] . ' (dev)';
        }

        $checkList = [
            'laravel/framework'                      => ['Laravel',      'core'],
            'livewire/livewire'                      => ['Livewire',     'core'],
            'power-components/livewire-powergrid'    => ['PowerGrid',    'table'],
            'spatie/laravel-permission'              => ['Permission',   'auth'],
            'spatie/laravel-activitylog'             => ['ActivityLog',  'log'],
            'spatie/laravel-medialibrary'            => ['Medialibrary', 'media'],
            'spatie/laravel-backup'                  => ['Backup',       'backup'],
            'barryvdh/laravel-debugbar'              => ['Debugbar',     'debug'],
            'laravel/telescope'                      => ['Telescope',    'debug'],
            'maatwebsite/excel'                      => ['Excel',        'export'],
            'intervention/image'                     => ['Image',        'media'],
            'tightenco/ziggy'                        => ['Ziggy',        'js'],
            'mrezanomani/livewire-jalali-datepicker' => ['JalaliPicker', 'ui'],
            'nawrasbukhari/laravelgithubupdater'     => ['GitHubUpdater','update'],
        ];

        $this->packages = [];
        foreach ($checkList as $name => $meta) {
            [$label, $group] = $meta;
            $this->packages[$group][] = [
                'name' => $name,
                'label' => $label,
                'version' => $installed[$name] ?? null,
                'ok' => isset($installed[$name]),
            ];
        }
    }

    protected function loadFeatures(): void
    {
        $checks = [
            ['route' => 'dashboard',            'label' => 'داشبورد',           'icon' => '🏠', 'desc' => 'نمای کلی', 'new' => false],
            ['route' => 'orders.index',         'label' => 'سفارشات',           'icon' => '📦', 'desc' => 'مدیریت سفارش', 'new' => false],
            ['route' => 'customers.index',      'label' => 'مشتریان',           'icon' => '👥', 'desc' => 'CRM', 'new' => false],
            ['route' => 'certificates.index',   'label' => 'شناسنامه',          'icon' => '💎', 'desc' => 'صدور کارت', 'new' => false],
            ['route' => 'certificates.designer','label' => 'ویرایشگر شناسنامه', 'icon' => '🎨', 'desc' => 'Fabric.js', 'new' => true],
            ['route' => 'reports.index',        'label' => 'گزارش‌ها',          'icon' => '📊', 'desc' => 'آمار', 'new' => false],
            ['route' => 'settings.index',       'label' => 'تنظیمات',           'icon' => '⚙️', 'desc' => 'پیکربندی', 'new' => false],
            ['route' => 'activity-log',         'label' => 'لاگ فعالیت',        'icon' => '📜', 'desc' => 'تاریخچه', 'new' => false],
            ['route' => 'about',                'label' => 'درباره',            'icon' => 'ℹ️', 'desc' => 'اطلاعات فنی', 'new' => true],
            ['route' => 'file-manager',         'label' => 'مدیریت فایل',       'icon' => '📁', 'desc' => 'آپلود', 'new' => true],
            ['route' => 'users.index',          'label' => 'کاربران',           'icon' => '👤', 'desc' => 'CRUD', 'new' => true],
            ['route' => 'roles.index',          'label' => 'نقش‌ها',            'icon' => '🔐', 'desc' => 'مجوزها', 'new' => true],
            ['route' => 'shipments.index',      'label' => 'مرسولات',           'icon' => '📮', 'desc' => 'پیگیری', 'new' => true],
            ['route' => 'settings.channels',    'label' => 'کانال‌ها',          'icon' => '🌐', 'desc' => 'فروش', 'new' => true],
            ['route' => 'settings.health',      'label' => 'سلامت سیستم',       'icon' => '🩺', 'desc' => 'این صفحه', 'new' => true],
            ['route' => 'settings.labels',      'label' => 'ویرایشگر برچسب',    'icon' => '🏷️', 'desc' => 'چاپ برچسب', 'new' => true],
        ];

        $this->features = [];
        foreach ($checks as $c) {
            $ok = Route::has($c['route']);
            $this->features[] = array_merge($c, [
                'ok' => $ok,
                'url' => $ok ? route($c['route']) : null,
            ]);
        }
    }

    protected function loadSystem(): void
    {
        $this->system = [
            ['label'=>'PHP','value'=>PHP_VERSION,'ok'=>version_compare(PHP_VERSION,'8.2.0','>=')],
            ['label'=>'Laravel','value'=>app()->version(),'ok'=>true],
            ['label'=>'Environment','value'=>app()->environment(),'ok'=>true],
            ['label'=>'DB','value'=>config('database.default'),'ok'=>true],
            ['label'=>'Debug','value'=>config('app.debug')?'روشن':'خاموش','ok'=>true],
            ['label'=>'Storage','value'=>is_writable(storage_path())?'OK':'غیرقابل','ok'=>is_writable(storage_path())],
            ['label'=>'Cache','value'=>config('cache.default'),'ok'=>true],
            ['label'=>'Queue','value'=>config('queue.default'),'ok'=>true],
            ['label'=>'Timezone','value'=>config('app.timezone'),'ok'=>true],
        ];
    }

    protected function loadDatabase(): void
    {
        $tables = [
            'users'=>'کاربران', 'customers'=>'مشتریان',
            'customer_phones'=>'تلفن مشتری', 'customer_addresses'=>'آدرس مشتری',
            'orders'=>'سفارشات', 'order_items'=>'آیتم سفارش',
            'channels'=>'کانال‌ها', 'certificates'=>'شناسنامه',
            'stones'=>'سنگ‌ها', 'metals'=>'فلزات',
            'products'=>'محصولات', 'app_settings'=>'تنظیمات',
            'api_logs'=>'لاگ API', 'app_notifications'=>'اعلان',
            'activity_log'=>'لاگ فعالیت', 'sessions'=>'نشست',
            'cache'=>'کش', 'jobs'=>'صف', 'shipments'=>'مرسولات',
        ];

        $this->database = [];
        foreach ($tables as $name => $label) {
            $exists = Schema::hasTable($name);
            $count = 0;
            if ($exists) { try { $count = DB::table($name)->count(); } catch (\Throwable $e) {} }
            $this->database[] = ['name'=>$name,'label'=>$label,'exists'=>$exists,'count'=>$count];
        }
    }

    public function render()
    {
        return view('livewire.settings.health')->layout('components.layouts.app');
    }
}
