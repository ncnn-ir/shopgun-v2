#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Upgrade v3
صفحه سلامت + تست اتصال WooCommerce + تب‌های ریسپانسیو + ویرایشگر برچسب
"""

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

class C:
    OK='\033[92m'; WARN='\033[93m'; ERR='\033[91m'
    INFO='\033[96m'; BOLD='\033[1m'; END='\033[0m'

def log(msg, kind='info'):
    icons = {'info':'ℹ️','ok':'✅','warn':'⚠️','err':'❌'}
    colors = {'info':C.INFO,'ok':C.OK,'warn':C.WARN,'err':C.ERR}
    print(f"{colors[kind]} {icons[kind]} {msg}{C.END}")

def write(rel, content):
    full = ROOT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    if full.exists():
        full.rename(full.with_suffix(full.suffix + f'.bak-{datetime.now().strftime("%H%M%S")}'))
    full.write_text(content, encoding='utf-8')
    log(f"ساخته شد: {rel}", 'ok')

# ═══════════════════════════════════════════════════════════════
# 1. HEALTH.PHP - بازنویسی کامل با تست اتصال
# ═══════════════════════════════════════════════════════════════

HEALTH_PHP = r'''<?php

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
                    ->timeout(15)
                    ->get($base . "/{$ep}?per_page=1");
                $total = (int) ($r->header('X-WP-Total') ?: 0);
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
            'tivents/livewire-form-builder'          => ['FormBuilder',  'form'],
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
'''

# ═══════════════════════════════════════════════════════════════
# 2. HEALTH VIEW
# ═══════════════════════════════════════════════════════════════

HEALTH_VIEW = r'''<div class="p-4 md:p-6 space-y-4" dir="rtl" x-data="healthPage()">

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
            <button @click="copyText(@js($this->full_report))" class="btn btn-primary btn-sm">
                📋 کپی کامل
            </button>
            <button @click="copyText(@js($this->error_report))" class="btn btn-error btn-sm">
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
                <button @click="copyText(@js($this->full_report))" class="btn btn-primary btn-xs">
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
                                <button @click="copyText(@js($this->error_report))" class="btn btn-ghost btn-xs">📋</button>
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
                    <button @click="copyText(@js($reportText))" class="btn btn-primary btn-sm">📋 کپی</button>
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
'''

# ═══════════════════════════════════════════════════════════════
# 3. SETTINGS INDEX - بازنویسی کامل با تب‌های ریسپانسیو
# ═══════════════════════════════════════════════════════════════

SETTINGS_PHP_ADDITION = r'''
    public function setTab(string $tab): void
    {
        $allowed = [
            'general','appearance','commerce','certificate','label',
            'labels','assets','backup','logs','stones','monitor','health',
        ];
        if (!in_array($tab, $allowed, true)) $tab = 'general';

        $this->tab = $tab;
        if ($tab === 'monitor') $this->refreshMonitor();
        if ($tab === 'logs') $this->loadLogs();
        if ($tab === 'stones') $this->loadStonesMetals();
    }
'''

# ═══════════════════════════════════════════════════════════════
# 4. LABELS EDITOR - کامپوننت جدید
# ═══════════════════════════════════════════════════════════════

LABELS_PHP = r'''<?php

namespace App\Livewire\Settings;

use App\Models\AppSetting;
use Livewire\Component;

class Labels extends Component
{
    public int $width = 100;
    public int $height = 50;
    public string $template = 'default';
    public array $fonts = [
        'customer' => 16, 'insurance' => 12, 'address' => 14,
        'contactLabel' => 11, 'contactValue' => 16,
        'meta' => 11, 'footer' => 10,
    ];
    public bool $showInsurance = true;
    public bool $showPostal = true;
    public bool $showPhone = true;

    // نمونه پیش‌نمایش
    public string $sampleName = 'علی رضایی';
    public string $sampleAddress = 'نیشابور - خیابان امام - پلاک ۱۲، طبقه ۲';
    public string $samplePhone = '09151234567';
    public string $samplePostal = '9317613441';
    public string $sampleInsurance = '۲۵٬۰۰۰';
    public string $sampleOrder = '317401';

    public function mount(): void
    {
        $this->width  = (int) AppSetting::get('label_width', 100);
        $this->height = (int) AppSetting::get('label_height', 50);
        $fonts = AppSetting::get('label_fonts', null);
        if (is_array($fonts)) $this->fonts = array_merge($this->fonts, $fonts);
    }

    public function save(): void
    {
        AppSetting::putMany([
            'label_width'  => $this->width,
            'label_height' => $this->height,
            'label_fonts'  => $this->fonts,
            'label_template' => $this->template,
            'label_show_insurance' => $this->showInsurance,
            'label_show_postal' => $this->showPostal,
            'label_show_phone' => $this->showPhone,
        ], 'label');

        $this->dispatch('notify', type: 'success', message: 'تنظیمات برچسب ذخیره شد ✅');
    }

    public function reset(): void
    {
        $this->width = 100;
        $this->height = 50;
        $this->fonts = [
            'customer' => 16, 'insurance' => 12, 'address' => 14,
            'contactLabel' => 11, 'contactValue' => 16,
            'meta' => 11, 'footer' => 10,
        ];
        $this->dispatch('notify', type: 'info', message: 'بازنشانی شد');
    }

    public function render()
    {
        return view('livewire.settings.labels')
            ->layout('components.layouts.app');
    }
}
'''

LABELS_VIEW = r'''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🏷️ ویرایشگر برچسب پستی</h1>
            <p class="text-xs text-base-content/60 mt-1">پیش‌نمایش زنده — تغییرات بلافاصله اعمال می‌شوند</p>
        </div>
        <div class="flex gap-2">
            <button wire:click="reset" class="btn btn-ghost btn-sm">↺ بازنشانی</button>
            <button wire:click="save" class="btn btn-primary btn-sm">💾 ذخیره</button>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {{-- ستون تنظیمات --}}
        <div class="lg:col-span-1 space-y-3">
            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-3">
                    <h3 class="font-bold text-sm">📐 ابعاد</h3>
                    <div class="grid grid-cols-2 gap-2">
                        <label class="form-control">
                            <span class="label-text text-[10px] font-bold">عرض (mm)</span>
                            <input type="number" wire:model.live="width" dir="ltr"
                                   class="input input-bordered input-sm" />
                        </label>
                        <label class="form-control">
                            <span class="label-text text-[10px] font-bold">ارتفاع (mm)</span>
                            <input type="number" wire:model.live="height" dir="ltr"
                                   class="input input-bordered input-sm" />
                        </label>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-3">
                    <h3 class="font-bold text-sm">🔤 اندازه فونت‌ها</h3>
                    @foreach([
                        'customer' => 'نام مشتری',
                        'insurance' => 'بیمه',
                        'address' => 'آدرس',
                        'contactLabel' => 'برچسب تلفن',
                        'contactValue' => 'مقدار تلفن',
                        'meta' => 'اطلاعات پایین',
                        'footer' => 'پاصفحه',
                    ] as $key => $label)
                        <label class="form-control">
                            <div class="flex justify-between">
                                <span class="text-xs">{{ $label }}</span>
                                <span class="font-mono text-xs">{{ $fonts[$key] ?? 0 }}px</span>
                            </div>
                            <input type="range" min="6" max="30" wire:model.live="fonts.{{ $key }}"
                                   class="range range-xs range-primary" />
                        </label>
                    @endforeach
                </div>
            </div>

            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-2">
                    <h3 class="font-bold text-sm">👁️ نمایش المان‌ها</h3>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" wire:model.live="showInsurance" class="checkbox checkbox-primary checkbox-sm" />
                        <span class="text-xs">بیمه</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" wire:model.live="showPostal" class="checkbox checkbox-primary checkbox-sm" />
                        <span class="text-xs">کدپستی</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" wire:model.live="showPhone" class="checkbox checkbox-primary checkbox-sm" />
                        <span class="text-xs">تلفن</span>
                    </label>
                </div>
            </div>

            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-2">
                    <h3 class="font-bold text-sm">🧪 نمونه داده</h3>
                    <input type="text" wire:model.live="sampleName" placeholder="نام"
                           class="input input-bordered input-xs" />
                    <textarea wire:model.live="sampleAddress" rows="2" placeholder="آدرس"
                              class="textarea textarea-bordered textarea-xs"></textarea>
                    <div class="grid grid-cols-2 gap-2">
                        <input type="text" wire:model.live="samplePhone" placeholder="تلفن"
                               class="input input-bordered input-xs font-mono" dir="ltr" />
                        <input type="text" wire:model.live="samplePostal" placeholder="کدپستی"
                               class="input input-bordered input-xs font-mono" dir="ltr" />
                    </div>
                </div>
            </div>
        </div>

        {{-- پیش‌نمایش زنده --}}
        <div class="lg:col-span-2">
            <div class="card bg-base-100 shadow border-2 border-primary/30 sticky top-4">
                <div class="card-body p-4">
                    <h3 class="font-bold text-sm mb-3 flex items-center justify-between">
                        <span>👁️ پیش‌نمایش زنده</span>
                        <span class="badge badge-primary badge-sm font-mono">{{ $width }}×{{ $height }} mm</span>
                    </h3>

                    <div class="bg-base-200 rounded-lg p-4 flex items-center justify-center overflow-auto">
                        <div style="
                            width: {{ $width * 3.78 }}px;
                            height: {{ $height * 3.78 }}px;
                            background: #fff;
                            color: #000;
                            padding: 8px;
                            box-sizing: border-box;
                            border: 2px solid #000;
                            border-radius: 4px;
                            font-family: Vazirmatn, Tahoma, sans-serif;
                            display: flex;
                            flex-direction: column;
                            gap: 4px;
                            overflow: hidden;
                        ">
                            {{-- ردیف ۱: نام + بیمه --}}
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; border-bottom: 2px solid #000; padding-bottom: 4px;">
                                <div style="font-size: {{ $fonts['customer'] ?? 16 }}px; font-weight: bold; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                    {{ $sampleName ?: 'نام مشتری' }}
                                </div>
                                @if($showInsurance)
                                    <div style="font-size: {{ $fonts['insurance'] ?? 12 }}px; background: #000; color: #fff; padding: 2px 10px; border-radius: 20px; font-weight: bold; white-space: nowrap;">
                                        بیمه: {{ $sampleInsurance }}
                                    </div>
                                @endif
                            </div>

                            {{-- آدرس --}}
                            <div style="border: 2px solid #000; border-radius: 6px; padding: 6px; font-size: {{ $fonts['address'] ?? 14 }}px; line-height: 1.5; font-weight: 600; flex: 1; overflow: hidden;">
                                {{ $sampleAddress ?: 'آدرس گیرنده' }}
                            </div>

                            {{-- ردیف تلفن --}}
                            @if($showPhone || $showPostal)
                            <div style="display: flex; gap: 6px;">
                                @if($showPhone)
                                    <div style="flex: 1; display: flex; align-items: center; gap: 4px;">
                                        <span style="background: #000; color: #fff; padding: 2px 8px; border-radius: 5px; font-size: {{ $fonts['contactLabel'] ?? 11 }}px; font-weight: bold;">
                                            تلفن
                                        </span>
                                        <span style="flex: 1; border: 2px solid #000; border-radius: 5px; padding: 2px 8px; font-size: {{ $fonts['contactValue'] ?? 16 }}px; font-weight: bold; font-family: monospace; text-align: center;">
                                            {{ $samplePhone }}
                                        </span>
                                    </div>
                                @endif

                                @if($showPostal)
                                    <div style="flex: 1; display: flex; align-items: center; gap: 4px;">
                                        <span style="background: #000; color: #fff; padding: 2px 8px; border-radius: 5px; font-size: {{ $fonts['contactLabel'] ?? 11 }}px; font-weight: bold;">
                                            کدپستی
                                        </span>
                                        <span style="flex: 1; border: 2px solid #000; border-radius: 5px; padding: 2px 8px; font-size: {{ max(10, ($fonts['contactValue'] ?? 16) - 2) }}px; font-weight: bold; font-family: monospace; text-align: center;">
                                            {{ $samplePostal }}
                                        </span>
                                    </div>
                                @endif
                            </div>
                            @endif

                            {{-- پاصفحه --}}
                            <div style="display: flex; justify-content: space-between; font-size: {{ $fonts['meta'] ?? 11 }}px; margin-top: auto;">
                                <span style="background: #000; color: #fff; padding: 2px 10px; border-radius: 10px; font-weight: bold;">
                                    #{{ $sampleOrder }}
                                </span>
                                <span style="background: #000; color: #fff; padding: 2px 10px; border-radius: 10px; font-weight: bold; font-size: {{ $fonts['footer'] ?? 10 }}px;">
                                    جواهری مشاهیر
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="alert alert-info text-xs mt-3">
                        <span>💡 این پیش‌نمایش با ابعاد واقعی چاپ (mm) مقیاس شده. در چاپگر حرارتی مستقیم تست کن.</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# 5. CSS برای تب‌های ریسپانسیو
# ═══════════════════════════════════════════════════════════════

TAB_CSS = r'''

/* ═══════════════════════════════════════════════════════════
   Settings Tabs — Responsive Horizontal Scroll
   ═══════════════════════════════════════════════════════════ */

.sg-settings-tabs {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 8px 18px 12px;
    margin-bottom: 14px;
    scrollbar-width: thin;
    scroll-snap-type: x proximity;
    -webkit-overflow-scrolling: touch;
    border-bottom: 2px solid var(--border);
}

.sg-settings-tabs::-webkit-scrollbar { height: 4px; }
.sg-settings-tabs::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 2px;
}

.sg-settings-tab {
    flex: 0 0 auto;
    scroll-snap-align: start;
    padding: 8px 14px;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    background: var(--bg-card);
    font-family: inherit;
    font-size: 12.5px;
    font-weight: 700;
    color: var(--text-light);
    cursor: pointer;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    position: relative;
}

.sg-settings-tab:hover {
    border-color: var(--gold);
    color: var(--text);
    transform: translateY(-1px);
}

.sg-settings-tab.active {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark, #0d3b5e));
    color: #fff;
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(26, 82, 118, 0.25);
}

.sg-settings-tab.active::after {
    content: '';
    position: absolute;
    bottom: -13px;
    left: 50%;
    transform: translateX(-50%);
    width: 8px;
    height: 8px;
    background: var(--primary);
    border-radius: 50%;
}

.sg-settings-tab .badge-new {
    background: var(--gold);
    color: #fff;
    font-size: 8px;
    padding: 1px 5px;
    border-radius: 8px;
    font-weight: 800;
}

/* موبایل */
@media (max-width: 768px) {
    .sg-settings-tabs {
        padding: 6px 10px 10px;
        margin-bottom: 10px;
    }
    .sg-settings-tab {
        padding: 7px 11px;
        font-size: 11.5px;
    }
}

/* حالت Dark */
[data-theme="dark"] .sg-settings-tab {
    background: var(--bg-elevated, #1c2332);
    border-color: var(--border);
}
[data-theme="dark"] .sg-settings-tab:hover {
    border-color: var(--gold);
}
[data-theme="dark"] .sg-settings-tab.active {
    box-shadow: 0 4px 12px rgba(77, 166, 216, 0.3);
}
'''

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print(f"""
{C.BOLD}╔══════════════════════════════════════════════╗
║  ShopGun V2 — Upgrade v3                     ║
║  Health + Test + Labels + Settings Tabs      ║
╚══════════════════════════════════════════════╝{C.END}
""")

    # 1. Health
    write('app/Livewire/Settings/Health.php', HEALTH_PHP)
    write('resources/views/livewire/settings/health.blade.php', HEALTH_VIEW)

    # 2. Labels Editor
    write('app/Livewire/Settings/Labels.php', LABELS_PHP)
    write('resources/views/livewire/settings/labels.blade.php', LABELS_VIEW)

    # 3. CSS tabs
    css = ROOT / 'public/css/extra.css'
    if css.exists():
        content = css.read_text(encoding='utf-8')
        if 'sg-settings-tabs' not in content:
            css.write_text(content + '\n' + TAB_CSS, encoding='utf-8')
            log("CSS تب‌ها به extra.css اضافه شد", 'ok')

    # 4. Routes
    routes = ROOT / 'routes' / 'web.php'
    if routes.exists():
        content = routes.read_text(encoding='utf-8')
        marker = "Route::get('/health', \\App\\Livewire\\Settings\\Health::class)->name('health');"
        if "settings.labels" not in content:
            if marker in content:
                content = content.replace(
                    marker,
                    marker + "\n        Route::get('/labels', \\App\\Livewire\\Settings\\Labels::class)->name('labels');"
                )
                routes.write_text(content, encoding='utf-8')
                log("route settings.labels اضافه شد", 'ok')

    # 5. پاکسازی
    print(f"\n{C.BOLD}═══ پاکسازی ═══{C.END}")
    subprocess.run("php artisan optimize:clear", shell=True, cwd=ROOT)

    print(f"""
{C.OK}╔══════════════════════════════════════════════╗
║  ✅ تمام شد                                   ║
╚══════════════════════════════════════════════╝{C.END}

{C.INFO}📍 صفحات جدید:{C.END}
   🩺 /settings/health  → سلامت + تست اتصال
   🏷️ /settings/labels  → ویرایشگر برچسب

{C.INFO}🎯 ویژگی‌ها:{C.END}
   ✅ تست اتصال WooCommerce با شمارش محصول/سفارش/مشتری
   ✅ ۵ محصول آخر از سایت با وضعیت لوکال
   ✅ برچسب 🆕 روی صفحات جدید
   ✅ دکمه‌های کپی (کامل + فقط خطاها)
   ✅ Modal گزارش کامل
   ✅ ویرایشگر برچسب با پیش‌نمایش زنده

{C.INFO}💡 بعد از اجرا:{C.END}
   1. php artisan serve
   2. برو به /settings/health
   3. دکمه «⚡ تست اتصال» را بزن
""")

if __name__ == '__main__':
    main()
