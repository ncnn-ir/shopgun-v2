#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  ShopGun V2 - Full Update Script                             ║
║  ساخت خودکار همه کامپوننت‌های ناقص + صفحه سلامت               ║
╚══════════════════════════════════════════════════════════════╝

اجرا:
    python3 shopgun_update.py
    python3 shopgun_update.py --dry-run
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')
DRY_RUN = False


class C:
    OK   = '\033[92m'
    WARN = '\033[93m'
    ERR  = '\033[91m'
    INFO = '\033[96m'
    BOLD = '\033[1m'
    END  = '\033[0m'


def log(msg, kind='info'):
    icons = {'info': 'ℹ️', 'ok': '✅', 'warn': '⚠️', 'err': '❌'}
    colors = {'info': C.INFO, 'ok': C.OK, 'warn': C.WARN, 'err': C.ERR}
    print(f"{colors[kind]} {icons[kind]} {msg}{C.END}")


def run(cmd):
    if DRY_RUN:
        print(f"{C.WARN}[DRY] $ {cmd}{C.END}")
        return 0
    r = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0 and r.stderr:
        print(f"   {C.ERR}{r.stderr[:200]}{C.END}")
    return r.returncode


def write_file(rel_path, content):
    full = PROJECT_ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)

    if DRY_RUN:
        print(f"{C.WARN}[DRY] write: {rel_path}{C.END}")
        return

    if full.exists():
        backup = full.with_suffix(
            full.suffix + f".bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        full.rename(backup)
        print(f"{C.WARN}   backup: {backup.name}{C.END}")

    full.write_text(content, encoding='utf-8')
    log(f"ساخته شد: {rel_path}", 'ok')


def append_route(route_line, marker):
    """اضافه کردن route در routes/web.php قبل از marker"""
    routes = PROJECT_ROOT / 'routes' / 'web.php'
    if not routes.exists():
        log("routes/web.php پیدا نشد", 'err')
        return

    content = routes.read_text(encoding='utf-8')
    route_name = route_line.split("->name('")[-1].split("')")[0] if "->name('" in route_line else None

    if route_name and f"name('{route_name}')" in content:
        log(f"route قبلاً هست: {route_name}", 'warn')
        return

    if marker not in content:
        log(f"marker پیدا نشد: {marker[:50]}", 'warn')
        return

    content = content.replace(marker, f"    {route_line}\n\n{marker}")

    if not DRY_RUN:
        routes.write_text(content, encoding='utf-8')
    log(f"route اضافه شد: {route_line[:60]}...", 'ok')


# ═══════════════════════════════════════════════════════════════
# 1. FILE MANAGER (جایگزین خودکفا)
# ═══════════════════════════════════════════════════════════════

def create_file_manager():
    print(f"\n{C.BOLD}═══ 1. File Manager ═══{C.END}")

    php = '''<?php

namespace App\\Livewire;

use Livewire\\Component;
use Livewire\\WithFileUploads;
use Illuminate\\Support\\Facades\\Storage;

class FileManagerPage extends Component
{
    use WithFileUploads;

    public array $files = [];
    public $upload = null;
    public string $folder = '';
    public string $search = '';

    public function mount(): void
    {
        $this->refresh();
    }

    public function refresh(): void
    {
        $disk = Storage::disk('public');
        $this->files = [];

        if (!$disk->exists($this->folder ?: 'uploads')) {
            $disk->makeDirectory($this->folder ?: 'uploads');
        }

        $allFiles = $disk->files($this->folder ?: 'uploads');
        foreach ($allFiles as $f) {
            $name = basename($f);

            if ($this->search && !str_contains(mb_strtolower($name), mb_strtolower($this->search))) {
                continue;
            }

            $this->files[] = [
                'name'  => $name,
                'path'  => $f,
                'size'  => $disk->size($f),
                'url'   => $disk->url($f),
                'mtime' => $disk->lastModified($f),
                'is_image' => (bool) preg_match('/\\.(jpg|jpeg|png|gif|webp|svg|bmp)$/i', $name),
            ];
        }
        usort($this->files, fn($a, $b) => $b['mtime'] <=> $a['mtime']);
    }

    public function updatedSearch(): void
    {
        $this->refresh();
    }

    public function updatedUpload(): void
    {
        $this->validate(['upload' => 'file|max:20480']);
        $name = $this->upload->getClientOriginalName();
        $name = preg_replace('/[^\\w\\d\\.\\-_\\x{0600}-\\x{06FF}]/u', '_', $name);
        $this->upload->storeAs($this->folder ?: 'uploads', $name, 'public');
        $this->upload = null;
        $this->refresh();
        $this->dispatch('notify', type: 'success', message: 'فایل آپلود شد ✅');
    }

    public function delete(string $path): void
    {
        Storage::disk('public')->delete($path);
        $this->refresh();
        $this->dispatch('notify', type: 'success', message: 'فایل حذف شد');
    }

    public function render()
    {
        return view('livewire.file-manager')
            ->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/FileManagerPage.php', php)

    view = '''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📁 مدیریت فایل‌ها</h1>
        <div class="flex gap-2">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="🔍 جستجو..."
                   class="input input-bordered input-sm w-40 md:w-56" />
            <button wire:click="refresh" class="btn btn-outline btn-sm">🔄</button>
        </div>
    </div>

    <div class="bg-base-100 rounded-lg shadow border border-base-300 p-4">
        <label class="label py-1">
            <span class="label-text font-bold text-sm">📤 آپلود فایل جدید (max 20 MB)</span>
        </label>
        <input type="file" wire:model="upload"
               class="file-input file-input-bordered w-full" />
        <div wire:loading wire:target="upload" class="text-xs text-info mt-2">
            ⏳ در حال آپلود...
        </div>
        @error('upload') <span class="text-error text-xs">{{ $message }}</span> @enderror
    </div>

    <div class="bg-base-100 rounded-lg shadow border border-base-300 overflow-hidden">
        <div class="p-3 border-b border-base-300 bg-base-200/50 flex items-center justify-between">
            <span class="font-bold text-sm">
                📂 فایل‌ها ({{ \\App\\Support\\PersianNumber::toFa(count($files)) }})
            </span>
        </div>

        <div class="p-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            @forelse($files as $f)
                <div class="card bg-base-100 border border-base-300 hover:shadow-lg transition"
                     wire:key="file-{{ md5($f['path']) }}">
                    <div class="aspect-square bg-base-200 rounded-t-lg flex items-center justify-center overflow-hidden">
                        @if($f['is_image'])
                            <img src="{{ $f['url'] }}" alt="" class="w-full h-full object-cover" loading="lazy">
                        @else
                            <span class="text-4xl">
                                @if(preg_match('/\\.pdf$/i', $f['name'])) 📄
                                @elseif(preg_match('/\\.(zip|rar|7z)$/i', $f['name'])) 📦
                                @elseif(preg_match('/\\.(mp4|avi|mov)$/i', $f['name'])) 🎬
                                @elseif(preg_match('/\\.(mp3|wav)$/i', $f['name'])) 🎵
                                @else 📎
                                @endif
                            </span>
                        @endif
                    </div>
                    <div class="p-2">
                        <div class="text-[10px] truncate font-bold" title="{{ $f['name'] }}">
                            {{ $f['name'] }}
                        </div>
                        <div class="text-[10px] text-base-content/50">
                            {{ number_format($f['size'] / 1024, 1) }} KB
                        </div>
                        <div class="flex gap-1 mt-1">
                            <a href="{{ $f['url'] }}" target="_blank"
                               class="btn btn-ghost btn-xs flex-1" title="دانلود">⬇️</a>
                            <button wire:click="delete('{{ $f['path'] }}')"
                                    wire:confirm="حذف شود؟"
                                    class="btn btn-ghost btn-xs text-error" title="حذف">🗑️</button>
                        </div>
                    </div>
                </div>
            @empty
                <div class="col-span-full text-center py-12 text-base-content/50">
                    <div class="text-5xl mb-3">📁</div>
                    <div class="text-sm">فایلی نیست</div>
                    <div class="text-xs mt-1 opacity-70">یک فایل آپلود کن تا اینجا نمایش داده شود</div>
                </div>
            @endforelse
        </div>
    </div>

    <div class="alert alert-info text-xs">
        <span>💡 فایل‌ها در <code>storage/app/public/uploads/</code> ذخیره می‌شوند.</span>
    </div>
</div>
'''
    write_file('resources/views/livewire/file-manager.blade.php', view)

    # symlink
    if not (PROJECT_ROOT / 'public' / 'storage').exists():
        run("php artisan storage:link")
        log("storage:link ساخته شد", 'ok')


# ═══════════════════════════════════════════════════════════════
# 2. HEALTH PAGE
# ═══════════════════════════════════════════════════════════════

def create_health():
    print(f"\n{C.BOLD}═══ 2. Health Page ═══{C.END}")

    php = '''<?php

namespace App\\Livewire\\Settings;

use Livewire\\Component;
use Illuminate\\Support\\Facades\\DB;
use Illuminate\\Support\\Facades\\Schema;
use Illuminate\\Support\\Facades\\Route;

class Health extends Component
{
    public array $packages = [];
    public array $features = [];
    public array $system = [];
    public array $database = [];

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
        $this->dispatch('notify', type: 'success', message: 'سلامت سیستم بروزرسانی شد ✅');
    }

    protected function loadPackages(): void
    {
        $lock = base_path('composer.lock');
        $installed = [];

        if (file_exists($lock)) {
            $data = json_decode(file_get_contents($lock), true) ?: [];
            foreach ($data['packages'] ?? [] as $p) {
                $installed[$p['name']] = $p['version'];
            }
            foreach ($data['packages-dev'] ?? [] as $p) {
                $installed[$p['name']] = $p['version'] . ' (dev)';
            }
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
            $version = $installed[$name] ?? null;
            $this->packages[$group][] = [
                'name'    => $name,
                'label'   => $label,
                'version' => $version,
                'ok'      => $version !== null,
            ];
        }
    }

    protected function loadFeatures(): void
    {
        $checks = [
            ['route' => 'dashboard',            'label' => 'داشبورد',             'icon' => '🏠', 'desc' => 'نمای کلی سیستم',        'new' => false],
            ['route' => 'orders.index',         'label' => 'سفارشات',             'icon' => '📦', 'desc' => 'لیست و مدیریت سفارشات',  'new' => false],
            ['route' => 'customers.index',      'label' => 'مشتریان',             'icon' => '👥', 'desc' => 'CRM مشتریان',           'new' => false],
            ['route' => 'certificates.index',   'label' => 'شناسنامه‌ها',         'icon' => '💎', 'desc' => 'مدیریت شناسنامه',       'new' => false],
            ['route' => 'certificates.designer','label' => 'ویرایشگر شناسنامه',   'icon' => '🎨', 'desc' => 'Fabric.js Designer',    'new' => false],
            ['route' => 'reports.index',        'label' => 'گزارش‌ها',            'icon' => '📊', 'desc' => 'آمار و نمودار',          'new' => false],
            ['route' => 'settings.index',       'label' => 'تنظیمات',             'icon' => '⚙️', 'desc' => 'پیکربندی کامل',         'new' => false],
            ['route' => 'activity-log',         'label' => 'لاگ فعالیت',          'icon' => '📜', 'desc' => 'تاریخچه تغییرات',       'new' => false],
            ['route' => 'about',                'label' => 'درباره سیستم',        'icon' => 'ℹ️', 'desc' => 'اطلاعات فنی',           'new' => true],
            ['route' => 'file-manager',         'label' => 'مدیریت فایل‌ها',      'icon' => '📁', 'desc' => 'آپلود و مدیریت فایل',   'new' => true],
            ['route' => 'users.index',          'label' => 'کاربران',             'icon' => '👤', 'desc' => 'مدیریت کاربران',        'new' => true],
            ['route' => 'roles.index',          'label' => 'نقش‌ها و مجوزها',     'icon' => '🔐', 'desc' => 'ماتریس دسترسی',         'new' => true],
            ['route' => 'shipments.index',      'label' => 'مرسولات',             'icon' => '📮', 'desc' => 'پیگیری مرسولات',        'new' => true],
            ['route' => 'settings.channels',    'label' => 'کانال‌های فروش',      'icon' => '🌐', 'desc' => 'اینستاگرام، تلگرام و...','new' => true],
            ['route' => 'settings.health',      'label' => 'سلامت سیستم',         'icon' => '🩺', 'desc' => 'همین صفحه',             'new' => true],
        ];

        $this->features = [];
        foreach ($checks as $c) {
            $exists = Route::has($c['route']);
            $this->features[] = array_merge($c, [
                'ok'  => $exists,
                'url' => $exists ? route($c['route']) : null,
            ]);
        }
    }

    protected function loadSystem(): void
    {
        $this->system = [
            ['label' => 'PHP',        'value' => PHP_VERSION,             'ok' => version_compare(PHP_VERSION, '8.2.0', '>=')],
            ['label' => 'Laravel',    'value' => app()->version(),         'ok' => true],
            ['label' => 'Environment','value' => app()->environment(),     'ok' => true],
            ['label' => 'DB',         'value' => config('database.default'),'ok' => true],
            ['label' => 'Debug',      'value' => config('app.debug') ? 'روشن' : 'خاموش','ok' => true],
            ['label' => 'Storage',    'value' => is_writable(storage_path()) ? 'قابل نوشتن' : 'غیرقابل','ok' => is_writable(storage_path())],
            ['label' => 'Cache',      'value' => config('cache.default'),  'ok' => true],
            ['label' => 'Queue',      'value' => config('queue.default'),  'ok' => true],
            ['label' => 'Timezone',   'value' => config('app.timezone'),   'ok' => true],
        ];
    }

    protected function loadDatabase(): void
    {
        $tables = [
            'users', 'customers', 'customer_phones', 'customer_addresses',
            'orders', 'order_items', 'channels', 'certificates',
            'stones', 'metals', 'products', 'app_settings',
            'api_logs', 'app_notifications', 'activity_log',
            'sessions', 'cache', 'jobs', 'shipments',
        ];

        $labels = [
            'users'              => 'کاربران',
            'customers'          => 'مشتریان',
            'customer_phones'    => 'تلفن مشتریان',
            'customer_addresses' => 'آدرس مشتریان',
            'orders'             => 'سفارشات',
            'order_items'        => 'آیتم سفارش',
            'channels'           => 'کانال‌ها',
            'certificates'       => 'شناسنامه‌ها',
            'stones'             => 'سنگ‌ها',
            'metals'             => 'فلزات',
            'products'           => 'محصولات',
            'app_settings'       => 'تنظیمات',
            'api_logs'           => 'لاگ API',
            'app_notifications'  => 'اعلان‌ها',
            'activity_log'       => 'لاگ فعالیت',
            'sessions'           => 'نشست‌ها',
            'cache'              => 'کش',
            'jobs'               => 'صف کارها',
            'shipments'          => 'مرسولات',
        ];

        $this->database = [];
        foreach ($tables as $t) {
            $exists = Schema::hasTable($t);
            $count = 0;
            if ($exists) {
                try { $count = DB::table($t)->count(); } catch (\\Throwable $e) {}
            }
            $this->database[] = [
                'name'   => $t,
                'label'  => $labels[$t] ?? $t,
                'exists' => $exists,
                'count'  => $count,
            ];
        }
    }

    public function render()
    {
        return view('livewire.settings.health')
            ->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/Settings/Health.php', php)

    view = '''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🩺 سلامت سیستم</h1>
            <p class="text-xs text-base-content/60 mt-1">نمای کلی از وضعیت پکیج‌ها، دیتابیس و صفحات</p>
        </div>
        <button wire:click="refresh" class="btn btn-primary btn-sm">
            <span wire:loading.remove wire:target="refresh">🔄 بروزرسانی</span>
            <span wire:loading wire:target="refresh">⏳...</span>
        </button>
    </div>

    {{-- ═══ لینک‌های سریع ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3 flex items-center gap-2">
                🚀 دسترسی سریع به بخش‌ها
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
                @foreach($features as $f)
                    @if($f['ok'])
                        <a href="{{ $f['url'] }}" wire:navigate
                           class="relative block p-3 rounded-lg border-2 border-success/30 bg-success/5 hover:bg-success/10 hover:shadow-md transition">
                            @if($f['new'] ?? false)
                                <span class="absolute -top-2 -left-2 badge badge-warning badge-xs font-bold">🆕</span>
                            @endif
                            <div class="flex items-center justify-between mb-1">
                                <span class="text-2xl">{{ $f['icon'] }}</span>
                                <span class="badge badge-success badge-xs">✓</span>
                            </div>
                            <div class="font-bold text-sm">{{ $f['label'] }}</div>
                            <div class="text-[10px] text-base-content/60 mt-0.5">{{ $f['desc'] }}</div>
                        </a>
                    @else
                        <div class="relative block p-3 rounded-lg border-2 border-error/30 bg-error/5 cursor-not-allowed opacity-60">
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

    {{-- ═══ اطلاعات سیستم ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">💻 اطلاعات سیستم</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                @foreach($system as $s)
                    <div class="p-3 rounded-lg {{ $s['ok'] ? 'bg-success/5 border border-success/30' : 'bg-warning/5 border border-warning/30' }} flex items-center justify-between">
                        <div class="min-w-0">
                            <div class="text-[10px] text-base-content/60">{{ $s['label'] }}</div>
                            <div class="font-mono font-bold text-xs mt-0.5 truncate" dir="ltr">{{ $s['value'] }}</div>
                        </div>
                        <span class="text-lg shrink-0">{{ $s['ok'] ? '✅' : '⚠️' }}</span>
                    </div>
                @endforeach
            </div>
        </div>
    </div>

    {{-- ═══ جداول دیتابیس ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">🗄️ جداول دیتابیس ({{ count($database) }} جدول)</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                @foreach($database as $t)
                    <div class="p-2 rounded-lg {{ $t['exists'] ? 'bg-success/5 border border-success/30' : 'bg-base-200/50 border border-base-300 opacity-60' }}">
                        <div class="flex items-center justify-between gap-2">
                            <div class="min-w-0 flex-1">
                                <div class="font-bold text-xs truncate">{{ $t['label'] }}</div>
                                <div class="font-mono text-[10px] text-base-content/50 truncate" dir="ltr">{{ $t['name'] }}</div>
                            </div>
                            @if($t['exists'])
                                <span class="badge badge-success badge-sm font-mono shrink-0">
                                    {{ \\App\\Support\\PersianNumber::toFa(number_format($t['count'])) }}
                                </span>
                            @else
                                <span class="badge badge-error badge-xs shrink-0">نبود</span>
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
                $groupLabels = [
                    'core'   => '🏗️ هسته',
                    'auth'   => '🔐 احراز هویت',
                    'table'  => '📊 جداول',
                    'log'    => '📜 لاگ',
                    'media'  => '🎨 رسانه',
                    'form'   => '📝 فرم',
                    'ui'     => '🎨 رابط کاربری',
                    'export' => '📤 خروجی',
                    'debug'  => '🐛 دیباگ',
                    'update' => '🔄 بروزرسانی',
                    'backup' => '💾 پشتیبان',
                    'js'     => '🟨 JavaScript',
                ];
            @endphp

            @foreach($packages as $group => $items)
                <div class="mb-4">
                    <div class="text-xs font-bold text-base-content/70 mb-2 pb-1 border-b border-base-300">
                        {{ $groupLabels[$group] ?? ('📦 '.$group) }}
                        <span class="badge badge-ghost badge-xs mr-2">
                            {{ \\App\\Support\\PersianNumber::toFa(count($items)) }}
                        </span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        @foreach($items as $p)
                            <div class="flex items-center justify-between p-2 rounded-lg {{ $p['ok'] ? 'bg-success/5 border border-success/20' : 'bg-base-200/30 opacity-60 border border-base-300' }}">
                                <div class="min-w-0">
                                    <div class="text-xs font-bold truncate">{{ $p['label'] }}</div>
                                    <div class="font-mono text-[10px] text-base-content/50 truncate" dir="ltr">
                                        {{ $p['version'] ?? 'نصب نیست' }}
                                    </div>
                                </div>
                                <span class="text-lg shrink-0">{{ $p['ok'] ? '✅' : '❌' }}</span>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- ═══ راهنما ═══ --}}
    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">📖 راهنمای بخش‌های جدید (🆕)</h2>

            <div class="space-y-3 text-sm">
                <div class="p-3 rounded-lg bg-info/5 border-r-4 border-info">
                    <div class="font-bold text-info mb-1">📁 مدیریت فایل‌ها — <code dir="ltr">/file-manager</code></div>
                    <div class="text-xs text-base-content/70">آپلود، مشاهده، دانلود و حذف فایل. پشتیبانی از تصویر، PDF، فیلم، صدا و آرشیو.</div>
                </div>

                <div class="p-3 rounded-lg bg-info/5 border-r-4 border-info">
                    <div class="font-bold text-info mb-1">👤 کاربران — <code dir="ltr">/users</code></div>
                    <div class="text-xs text-base-content/70">افزودن، ویرایش، حذف کاربر + تخصیص چند نقش به هر کاربر.</div>
                </div>

                <div class="p-3 rounded-lg bg-info/5 border-r-4 border-info">
                    <div class="font-bold text-info mb-1">🔐 نقش‌ها و مجوزها — <code dir="ltr">/roles</code></div>
                    <div class="text-xs text-base-content/70">ماتریس تعاملی نقش × مجوز. با کلیک، دسترسی فعال/غیرفعال می‌شود.</div>
                </div>

                <div class="p-3 rounded-lg bg-info/5 border-r-4 border-info">
                    <div class="font-bold text-info mb-1">📮 مرسولات — <code dir="ltr">/shipments</code></div>
                    <div class="text-xs text-base-content/70">پیگیری مرسولات پستی و تیپاکس با کد رهگیری و وضعیت.</div>
                </div>

                <div class="p-3 rounded-lg bg-info/5 border-r-4 border-info">
                    <div class="font-bold text-info mb-1">🌐 کانال‌های فروش — <code dir="ltr">/settings/channels</code></div>
                    <div class="text-xs text-base-content/70">مدیریت کانال‌های فروش: اینستاگرام، تلگرام، سایت، باسلام، تلفنی، حضوری.</div>
                </div>

                <div class="p-3 rounded-lg bg-info/5 border-r-4 border-info">
                    <div class="font-bold text-info mb-1">ℹ️ درباره — <code dir="ltr">/about</code></div>
                    <div class="text-xs text-base-content/70">آمار کلی، نسخه PHP/Laravel و لینک‌های مفید.</div>
                </div>
            </div>
        </div>
    </div>
</div>
'''
    write_file('resources/views/livewire/settings/health.blade.php', view)


# ═══════════════════════════════════════════════════════════════
# 3. ABOUT PAGE
# ═══════════════════════════════════════════════════════════════

def create_about():
    print(f"\n{C.BOLD}═══ 3. About Page ═══{C.END}")

    php = '''<?php

namespace App\\Livewire;

use Livewire\\Component;
use App\\Models\\Order;
use App\\Models\\Customer;
use App\\Models\\Product;
use App\\Models\\Certificate;

class About extends Component
{
    public function render()
    {
        $stats = [
            'orders'       => Order::count(),
            'customers'    => Customer::count(),
            'products'     => Product::count(),
            'certificates' => Certificate::count(),
        ];

        return view('livewire.about', compact('stats'))
            ->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/About.php', php)

    view = '''<div class="p-4 md:p-6 max-w-4xl mx-auto" dir="rtl">

    <div class="text-center mb-6">
        <div class="text-6xl mb-3">💎</div>
        <h1 class="text-3xl font-extrabold text-primary">ShopGun V2</h1>
        <p class="text-sm text-base-content/60 mt-1">جواهری مشاهیر — مدیریت سفارشات و شناسنامه</p>
        <p class="text-xs text-base-content/40 mt-1">گروه هنری اقاقیا</p>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">📦</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \\App\\Support\\PersianNumber::toFa($stats['orders']) }}
                </div>
                <div class="text-xs text-base-content/60">سفارش</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">👥</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \\App\\Support\\PersianNumber::toFa($stats['customers']) }}
                </div>
                <div class="text-xs text-base-content/60">مشتری</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">🛍️</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \\App\\Support\\PersianNumber::toFa($stats['products']) }}
                </div>
                <div class="text-xs text-base-content/60">محصول</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">💎</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \\App\\Support\\PersianNumber::toFa($stats['certificates']) }}
                </div>
                <div class="text-xs text-base-content/60">شناسنامه</div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border border-base-300 mb-4">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">⚙️ اطلاعات فنی</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">Laravel</span>
                    <span class="font-mono font-bold text-xs">{{ app()->version() }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">PHP</span>
                    <span class="font-mono font-bold text-xs">{{ PHP_VERSION }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">محیط</span>
                    <span class="font-mono text-xs">{{ app()->environment() }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">دیتابیس</span>
                    <span class="font-mono text-xs">{{ config('database.default') }}</span>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">🔗 لینک‌های مفید</h2>
            <div class="flex flex-wrap gap-2">
                <a href="https://laravel.com/docs" target="_blank" class="btn btn-outline btn-sm">📖 Laravel Docs</a>
                <a href="https://livewire.laravel.com/docs" target="_blank" class="btn btn-outline btn-sm">⚡ Livewire</a>
                <a href="https://daisyui.com" target="_blank" class="btn btn-outline btn-sm">🌸 DaisyUI</a>
                <a href="{{ route('settings.health') }}" wire:navigate class="btn btn-primary btn-sm">🩺 سلامت سیستم</a>
            </div>
        </div>
    </div>

    <div class="text-center mt-6 text-xs text-base-content/40">
        ساخته‌شده توسط گروه هنری اقاقیا — ۱۴۰۵
    </div>
</div>
'''
    write_file('resources/views/livewire/about.blade.php', view)


# ═══════════════════════════════════════════════════════════════
# 4. USERS INDEX
# ═══════════════════════════════════════════════════════════════

def create_users():
    print(f"\n{C.BOLD}═══ 4. Users Management ═══{C.END}")

    php = '''<?php

namespace App\\Livewire\\Users;

use App\\Models\\User;
use Illuminate\\Support\\Facades\\Hash;
use Livewire\\Component;
use Livewire\\WithPagination;
use Spatie\\Permission\\Models\\Role;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $filterRole = '';

    public bool $showForm = false;
    public ?int $editingId = null;

    public string $name = '';
    public string $email = '';
    public string $password = '';
    public array $selectedRoles = [];

    public function updatingSearch(): void  { $this->resetPage(); }
    public function updatingFilterRole(): void { $this->resetPage(); }

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $u = User::with('roles')->find($id);
            if ($u) {
                $this->name  = $u->name;
                $this->email = $u->email;
                $this->selectedRoles = $u->roles->pluck('name')->toArray();
            }
        }
    }

    public function closeForm(): void
    {
        $this->showForm = false;
        $this->resetForm();
    }

    public function resetForm(): void
    {
        $this->reset(['editingId', 'name', 'email', 'password', 'selectedRoles']);
    }

    public function save(): void
    {
        $rules = [
            'name'          => 'required|string|max:120',
            'email'         => 'required|email|unique:users,email' . ($this->editingId ? ',' . $this->editingId : ''),
            'selectedRoles' => 'array',
        ];
        $rules['password'] = $this->editingId
            ? 'nullable|string|min:6'
            : 'required|string|min:6';

        $this->validate($rules, [
            'name.required'     => 'نام الزامی است',
            'email.required'    => 'ایمیل الزامی است',
            'email.unique'      => 'این ایمیل قبلاً ثبت شده',
            'password.required' => 'رمز عبور الزامی است',
            'password.min'      => 'رمز حداقل ۶ کاراکتر',
        ]);

        $data = ['name' => $this->name, 'email' => $this->email];
        if ($this->password) {
            $data['password'] = Hash::make($this->password);
        }

        if ($this->editingId) {
            $user = User::find($this->editingId);
            $user->update($data);
            $user->syncRoles($this->selectedRoles);
            $this->dispatch('notify', type: 'success', message: 'کاربر ویرایش شد ✅');
        } else {
            $user = User::create($data);
            $user->syncRoles($this->selectedRoles);
            $this->dispatch('notify', type: 'success', message: 'کاربر ایجاد شد ✅');
        }

        $this->closeForm();
    }

    public function delete(int $id): void
    {
        if ($id === auth()->id()) {
            $this->dispatch('notify', type: 'error', message: 'نمی‌توانید خودتان را حذف کنید');
            return;
        }
        User::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'کاربر حذف شد');
    }

    public function render()
    {
        $users = User::query()
            ->with('roles')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('email', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filterRole, function ($q) {
                $q->whereHas('roles', fn($rq) => $rq->where('name', $this->filterRole));
            })
            ->latest('id')
            ->paginate(20);

        $roles = Role::orderBy('name')->get();

        return view('livewire.users.index', compact('users', 'roles'))
            ->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/Users/Index.php', php)

    view = '''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">👤 مدیریت کاربران</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ کاربر جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3 flex flex-wrap gap-2">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 نام یا ایمیل..."
               class="input input-bordered input-sm w-full md:w-72" />
        <select wire:model.live="filterRole" class="select select-bordered select-sm">
            <option value="">— همه نقش‌ها —</option>
            @foreach($roles as $r)
                <option value="{{ $r->name }}">{{ $r->name }}</option>
            @endforeach
        </select>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>نام</th>
                        <th>ایمیل</th>
                        <th>نقش‌ها</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($users as $u)
                        <tr wire:key="user-{{ $u->id }}">
                            <td class="font-mono text-xs">{{ $u->id }}</td>
                            <td class="font-bold">{{ $u->name }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $u->email }}</td>
                            <td>
                                @forelse($u->roles as $r)
                                    <span class="badge badge-primary badge-sm">{{ $r->name }}</span>
                                @empty
                                    <span class="badge badge-ghost badge-sm">بدون نقش</span>
                                @endforelse
                            </td>
                            <td>
                                <div class="flex gap-1">
                                    <button wire:click="openForm({{ $u->id }})" class="btn btn-ghost btn-xs">✏️</button>
                                    <button wire:click="delete({{ $u->id }})"
                                            wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="5" class="text-center py-8 text-base-content/50">کاربری نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $users->links() }}</div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-md my-8 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <h2 class="font-bold text-base">{{ $editingId ? '✏️ ویرایش کاربر' : '➕ کاربر جدید' }}</h2>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">نام *</span></label>
                    <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                    @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">ایمیل *</span></label>
                    <input type="email" wire:model="email" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('email') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1">
                        <span class="label-text text-xs font-bold">
                            رمز عبور {{ $editingId ? '(خالی=بدون تغییر)' : '*' }}
                        </span>
                    </label>
                    <input type="password" wire:model="password" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('password') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">نقش‌ها</span></label>
                    <div class="flex flex-wrap gap-2">
                        @foreach($roles as $r)
                            <label class="flex items-center gap-1 cursor-pointer bg-base-200/50 px-2 py-1 rounded">
                                <input type="checkbox" wire:model="selectedRoles" value="{{ $r->name }}"
                                       class="checkbox checkbox-xs checkbox-primary">
                                <span class="text-xs">{{ $r->name }}</span>
                            </label>
                        @endforeach
                    </div>
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
'''
    write_file('resources/views/livewire/users/index.blade.php', view)


# ═══════════════════════════════════════════════════════════════
# 5. ROLES INDEX
# ═══════════════════════════════════════════════════════════════

def create_roles():
    print(f"\n{C.BOLD}═══ 5. Roles & Permissions ═══{C.END}")

    php = '''<?php

namespace App\\Livewire\\Roles;

use Livewire\\Component;
use Spatie\\Permission\\Models\\Permission;
use Spatie\\Permission\\Models\\Role;
use Spatie\\Permission\\PermissionRegistrar;

class Index extends Component
{
    public array $permissions = [];
    public array $matrix = [];
    public array $roles = [];

    public function mount(): void
    {
        $this->load();
    }

    public function load(): void
    {
        $allPermissions = Permission::orderBy('name')->get();
        $allRoles = Role::with('permissions')->orderBy('name')->get();

        $this->permissions = $allPermissions->pluck('name')->toArray();
        $this->roles = $allRoles->pluck('name')->toArray();

        $this->matrix = [];
        foreach ($allRoles as $role) {
            $granted = $role->permissions->pluck('name')->toArray();
            foreach ($this->permissions as $perm) {
                $this->matrix[$role->name][$perm] = in_array($perm, $granted, true);
            }
        }
    }

    public function toggle(string $roleName, string $permissionName): void
    {
        $role = Role::findByName($roleName);
        if ($role->hasPermissionTo($permissionName)) {
            $role->revokePermissionTo($permissionName);
        } else {
            $role->givePermissionTo($permissionName);
        }
        app(PermissionRegistrar::class)->forgetCachedPermissions();
        $this->matrix[$roleName][$permissionName] = !$this->matrix[$roleName][$permissionName];
        $this->dispatch('notify', type: 'success', message: 'بروزرسانی شد');
    }

    public function saveAll(): void
    {
        foreach ($this->matrix as $roleName => $perms) {
            $role = Role::findByName($roleName);
            $granted = array_keys(array_filter($perms));
            $role->syncPermissions($granted);
        }
        app(PermissionRegistrar::class)->forgetCachedPermissions();
        $this->dispatch('notify', type: 'success', message: 'همه نقش‌ها ذخیره شد ✅');
    }

    public function render()
    {
        return view('livewire.roles.index')
            ->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/Roles/Index.php', php)

    view = '''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🔐 نقش‌ها و مجوزها</h1>
            <p class="text-xs text-base-content/60 mt-1">
                {{ \\App\\Support\\PersianNumber::toFa(count($roles)) }} نقش · {{ \\App\\Support\\PersianNumber::toFa(count($permissions)) }} مجوز
            </p>
        </div>
        <button wire:click="saveAll" class="btn btn-primary btn-sm">💾 ذخیره همه</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th style="min-width:200px">مجوز ↓ / نقش →</th>
                        @foreach($roles as $role)
                            <th class="text-center">{{ $role }}</th>
                        @endforeach
                    </tr>
                </thead>
                <tbody>
                    @foreach($permissions as $perm)
                        <tr wire:key="perm-{{ $perm }}">
                            <td class="font-mono text-xs">{{ $perm }}</td>
                            @foreach($roles as $role)
                                <td class="text-center">
                                    <input type="checkbox"
                                           wire:click="toggle('{{ $role }}', '{{ $perm }}')"
                                           {{ ($matrix[$role][$perm] ?? false) ? 'checked' : '' }}
                                           class="checkbox checkbox-xs checkbox-primary">
                                </td>
                            @endforeach
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>

    <div class="alert alert-info text-xs">
        <span>💡 هر تغییر بلافاصله اعمال و در کش ذخیره می‌شود.</span>
    </div>
</div>
'''
    write_file('resources/views/livewire/roles/index.blade.php', view)


# ═══════════════════════════════════════════════════════════════
# 6. SHIPMENTS
# ═══════════════════════════════════════════════════════════════

def create_shipments():
    print(f"\n{C.BOLD}═══ 6. Shipments ═══{C.END}")

    # Migration
    mig = '''<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('shipments')) return;

        Schema::create('shipments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('order_id')->nullable()->constrained('orders')->nullOnDelete();
            $table->string('tracking_code')->nullable()->index();
            $table->string('carrier', 50)->default('tipax')->index();
            $table->string('status', 50)->default('pending')->index();
            $table->string('receiver_name')->nullable();
            $table->string('receiver_phone', 20)->nullable();
            $table->text('address')->nullable();
            $table->string('postal_code', 20)->nullable();
            $table->decimal('weight', 10, 3)->nullable();
            $table->decimal('cost', 15, 2)->nullable();
            $table->json('events')->nullable();
            $table->timestamp('shipped_at')->nullable();
            $table->timestamp('delivered_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('shipments');
    }
};
'''
    ts = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    write_file(f'database/migrations/{ts}_create_shipments_table.php', mig)

    model = '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;

class Shipment extends Model
{
    protected $fillable = [
        'order_id', 'tracking_code', 'carrier', 'status',
        'receiver_name', 'receiver_phone', 'address', 'postal_code',
        'weight', 'cost', 'events', 'shipped_at', 'delivered_at',
    ];

    protected $casts = [
        'events'       => 'array',
        'weight'       => 'decimal:3',
        'cost'         => 'decimal:2',
        'shipped_at'   => 'datetime',
        'delivered_at' => 'datetime',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'pending'    => '📦 ثبت شده',
            'in_transit' => '🚚 در مسیر',
            'delivered'  => '✅ تحویل شد',
            'returned'   => '↩️ مرجوع',
            'failed'     => '❌ ناموفق',
            default      => $this->status,
        };
    }
}
'''
    write_file('app/Models/Shipment.php', model)

    php = '''<?php

namespace App\\Livewire\\Shipments;

use App\\Models\\Shipment;
use Livewire\\Component;
use Livewire\\WithPagination;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $filterStatus = '';

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingFilterStatus(): void { $this->resetPage(); }

    public function render()
    {
        $shipments = Shipment::query()
            ->with('order')
            ->when($this->search, function ($q) {
                $q->where('tracking_code', 'like', "%{$this->search}%")
                  ->orWhereHas('order', fn($oq) => $oq->where('order_number', 'like', "%{$this->search}%"))
                  ->orWhere('receiver_phone', 'like', "%{$this->search}%")
                  ->orWhere('receiver_name', 'like', "%{$this->search}%");
            })
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->latest('id')
            ->paginate(20);

        return view('livewire.shipments.index', compact('shipments'))
            ->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/Shipments/Index.php', php)

    view = '''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <h1 class="text-xl md:text-2xl font-bold">📮 مرسولات</h1>

    <div class="bg-base-100 rounded-lg shadow border p-3 flex flex-wrap gap-2">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 کد رهگیری / شماره سفارش / تلفن..."
               class="input input-bordered input-sm w-full md:w-80" />
        <select wire:model.live="filterStatus" class="select select-bordered select-sm">
            <option value="">— همه وضعیت‌ها —</option>
            <option value="pending">📦 ثبت شده</option>
            <option value="in_transit">🚚 در مسیر</option>
            <option value="delivered">✅ تحویل شد</option>
            <option value="returned">↩️ مرجوع</option>
            <option value="failed">❌ ناموفق</option>
        </select>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>سفارش</th>
                        <th>کد رهگیری</th>
                        <th>گیرنده</th>
                        <th>تلفن</th>
                        <th>حامل</th>
                        <th>وضعیت</th>
                        <th>تاریخ</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($shipments as $s)
                        <tr wire:key="ship-{{ $s->id }}">
                            <td class="font-mono text-xs">{{ $s->id }}</td>
                            <td>
                                @if($s->order)
                                    <a href="{{ route('orders.show', $s->order) }}"
                                       class="link link-primary font-bold">#{{ $s->order->order_number }}</a>
                                @else — @endif
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $s->tracking_code ?? '—' }}</td>
                            <td>{{ $s->receiver_name ?? $s->order?->customer?->name ?? '—' }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $s->receiver_phone ?? '—' }}</td>
                            <td><span class="badge badge-ghost badge-sm">{{ $s->carrier }}</span></td>
                            <td><span class="badge badge-info badge-sm">{{ $s->status_label }}</span></td>
                            <td class="text-xs font-mono">
                                {{ $s->created_at ? \\App\\Support\\PersianDate::format($s->created_at, 'Y/m/d') : '—' }}
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="8" class="text-center py-8 text-base-content/50">
                            مرسوله‌ای ثبت نشده — هنگام ایمپورت CSV پستی، مرسولات اینجا ظاهر می‌شوند
                        </td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $shipments->links() }}</div>
</div>
'''
    write_file('resources/views/livewire/shipments/index.blade.php', view)


# ═══════════════════════════════════════════════════════════════
# 7. CHANNELS SETTINGS
# ═══════════════════════════════════════════════════════════════

def create_channels():
    print(f"\n{C.BOLD}═══ 7. Channels Settings ═══{C.END}")

    php = '''<?php

namespace App\\Livewire\\Settings;

use App\\Models\\Channel;
use Livewire\\Component;

class Channels extends Component
{
    public bool $showForm = false;
    public ?int $editingId = null;

    public string $key = '';
    public string $name = '';
    public string $icon = '🌐';
    public string $color = '#1a5276';
    public bool $is_active = true;
    public int $sort_order = 0;

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $c = Channel::find($id);
            if ($c) {
                $this->key        = $c->key;
                $this->name       = $c->name;
                $this->icon       = $c->icon ?? '🌐';
                $this->color      = $c->color ?? '#1a5276';
                $this->is_active  = (bool) $c->is_active;
                $this->sort_order = (int) $c->sort_order;
            }
        }
    }

    public function closeForm(): void
    {
        $this->showForm = false;
        $this->resetForm();
    }

    public function resetForm(): void
    {
        $this->reset(['editingId', 'key', 'name', 'icon', 'color', 'is_active', 'sort_order']);
        $this->icon = '🌐';
        $this->color = '#1a5276';
        $this->is_active = true;
    }

    public function save(): void
    {
        $this->validate([
            'key'  => 'required|string|max:50|unique:channels,key' . ($this->editingId ? ',' . $this->editingId : ''),
            'name' => 'required|string|max:100',
            'icon' => 'nullable|string|max:10',
            'color'=> 'nullable|string|max:20',
        ], [
            'key.required'  => 'کلید الزامی است',
            'key.unique'    => 'این کلید قبلاً استفاده شده',
            'name.required' => 'نام الزامی است',
        ]);

        $data = [
            'key'        => $this->key,
            'name'       => $this->name,
            'icon'       => $this->icon,
            'color'      => $this->color,
            'is_active'  => $this->is_active,
            'sort_order' => $this->sort_order,
        ];

        if ($this->editingId) {
            Channel::find($this->editingId)?->update($data);
            $this->dispatch('notify', type: 'success', message: 'کانال ویرایش شد ✅');
        } else {
            Channel::create($data);
            $this->dispatch('notify', type: 'success', message: 'کانال اضافه شد ✅');
        }
        $this->closeForm();
    }

    public function delete(int $id): void
    {
        Channel::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'کانال حذف شد');
    }

    public function toggleActive(int $id): void
    {
        $c = Channel::find($id);
        if ($c) $c->update(['is_active' => !$c->is_active]);
    }

    public function render()
    {
        return view('livewire.settings.channels', [
            'channels' => Channel::orderBy('sort_order')->orderBy('id')->get(),
        ])->layout('components.layouts.app');
    }
}
'''
    write_file('app/Livewire/Settings/Channels.php', php)

    view = '''<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">🌐 مدیریت کانال‌ها</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ کانال جدید</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        @forelse($channels as $c)
            <div wire:key="ch-{{ $c->id }}"
                 class="card bg-base-100 shadow border {{ !$c->is_active ? 'opacity-50' : '' }}"
                 style="border-right: 4px solid {{ $c->color }};">
                <div class="card-body p-4">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                            <span class="text-2xl">{{ $c->icon }}</span>
                            <div>
                                <div class="font-bold text-sm">{{ $c->name }}</div>
                                <div class="text-[10px] font-mono text-base-content/50" dir="ltr">{{ $c->key }}</div>
                            </div>
                        </div>
                        <div class="w-4 h-4 rounded-full" style="background:{{ $c->color }}"></div>
                    </div>

                    <div class="flex gap-2 flex-wrap">
                        <button wire:click="toggleActive({{ $c->id }})"
                                class="btn btn-xs {{ $c->is_active ? 'btn-success' : 'btn-ghost' }}">
                            {{ $c->is_active ? '✓ فعال' : '— غیرفعال' }}
                        </button>
                        <button wire:click="openForm({{ $c->id }})" class="btn btn-ghost btn-xs">✏️</button>
                        <button wire:click="delete({{ $c->id }})"
                                wire:confirm="حذف شود؟"
                                class="btn btn-ghost btn-xs text-error">🗑️</button>
                    </div>
                </div>
            </div>
        @empty
            <div class="col-span-full text-center py-12 text-base-content/50">
                <div class="text-4xl mb-2">🌐</div>
                کانالی نیست — از Seeder بساز یا دستی اضافه کن
            </div>
        @endforelse
    </div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-md my-8 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <h2 class="font-bold text-base">{{ $editingId ? '✏️ ویرایش کانال' : '➕ کانال جدید' }}</h2>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3">
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">کلید *</span></label>
                        <input type="text" wire:model="key" dir="ltr"
                               class="input input-bordered input-sm w-full font-mono" />
                        @error('key') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام *</span></label>
                        <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                        @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون</span></label>
                        <input type="text" wire:model="icon"
                               class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">رنگ</span></label>
                        <input type="color" wire:model="color"
                               class="input input-bordered input-sm w-full h-10" />
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">ترتیب</span></label>
                    <input type="number" wire:model="sort_order" dir="ltr"
                           class="input input-bordered input-sm w-full" />
                </div>

                <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" wire:model="is_active" class="checkbox checkbox-primary checkbox-sm" />
                    <span class="text-sm font-bold">فعال باشد</span>
                </label>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" class="btn btn-primary btn-sm">✅ ذخیره</button>
            </div>
        </div>
    </div>
    @endif
</div>
'''
    write_file('resources/views/livewire/settings/channels.blade.php', view)


# ═══════════════════════════════════════════════════════════════
# 8. ROUTES
# ═══════════════════════════════════════════════════════════════

def create_routes():
    print(f"\n{C.BOLD}═══ 8. Routes ═══{C.END}")

    routes = [
        ("Route::get('/about', App\\Livewire\\About::class)->name('about');",
         "Route::get('/activity-log', ActivityLog::class)->name('activity-log');"),
        ("Route::get('/users', App\\Livewire\\Users\\Index::class)->name('users.index');",
         "Route::get('/about', App\\Livewire\\About::class)->name('about');"),
        ("Route::get('/roles', App\\Livewire\\Roles\\Index::class)->name('roles.index');",
         "Route::get('/users', App\\Livewire\\Users\\Index::class)->name('users.index');"),
        ("Route::get('/shipments', App\\Livewire\\Shipments\\Index::class)->name('shipments.index');",
         "Route::get('/roles', App\\Livewire\\Roles\\Index::class)->name('roles.index');"),
        ("Route::get('/file-manager', App\\Livewire\\FileManagerPage::class)->name('file-manager');",
         "Route::get('/shipments', App\\Livewire\\Shipments\\Index::class)->name('shipments.index');"),
    ]

    for route_line, marker in routes:
        append_route(route_line, marker)

    # Route برای channels و health داخل settings prefix
    routes_file = PROJECT_ROOT / 'routes' / 'web.php'
    if routes_file.exists():
        content = routes_file.read_text(encoding='utf-8')
        marker = "Route::get('/metals', SettingsMetals::class)->name('metals');"

        if "settings.channels" not in content and marker in content:
            content = content.replace(
                marker,
                marker + "\n        Route::get('/channels', \\App\\Livewire\\Settings\\Channels::class)->name('channels');"
            )
            log("route settings.channels اضافه شد", 'ok')

        if "settings.health" not in content and marker in content:
            content = content.replace(
                marker,
                marker + "\n        Route::get('/health', \\App\\Livewire\\Settings\\Health::class)->name('health');"
            )
            log("route settings.health اضافه شد", 'ok')

        if not DRY_RUN:
            routes_file.write_text(content, encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# 9. NAV LINK در Header
# ═══════════════════════════════════════════════════════════════

def add_header_links():
    print(f"\n{C.BOLD}═══ 9. Header Links ═══{C.END}")

    layout = PROJECT_ROOT / 'resources/views/components/layouts/app.blade.php'
    if not layout.exists():
        log("layout پیدا نشد", 'warn')
        return

    content = layout.read_text(encoding='utf-8')

    # اضافه کردن لینک سلامت کنار آیکون لاگ
    if "settings.health" not in content:
        old = '<a href="{{ route(\'settings.index\') }}" wire:navigate class="sg-header-icon-btn" title="تنظیمات">⚙️</a>'
        new = old + '''
        <a href="{{ route('settings.health') }}" wire:navigate class="sg-header-icon-btn" title="سلامت سیستم">🩺</a>'''
        if old in content:
            content = content.replace(old, new)
            log("لینک سلامت به Header اضافه شد", 'ok')
        else:
            log("دکمه تنظیمات در Header پیدا نشد — دستی بررسی کن", 'warn')

    # اضافه کردن به Mobile Bar
    if "health" not in content.split('$items = [')[1].split('];')[0] if '$items = [' in content else False:
        pass

    if not DRY_RUN:
        layout.write_text(content, encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# 10. MIGRATION & FINALIZE
# ═══════════════════════════════════════════════════════════════

def migrate():
    print(f"\n{C.BOLD}═══ 10. اجرای Migration ═══{C.END}")
    run("php artisan migrate --force")


def finalize():
    print(f"\n{C.BOLD}═══ پاکسازی نهایی ═══{C.END}")
    run("php artisan optimize:clear")
    run("php artisan view:clear")
    run("php artisan route:clear")

    # symlink
    if not (PROJECT_ROOT / 'public' / 'storage').exists():
        run("php artisan storage:link")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    global DRY_RUN

    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--skip-migrate', action='store_true')
    args = parser.parse_args()

    DRY_RUN = args.dry_run

    print(f"""
{C.BOLD}╔══════════════════════════════════════════════════╗
║  ShopGun V2 - Full Update                        ║
║  ساخت همه کامپوننت‌ها + صفحه سلامت                ║
╚══════════════════════════════════════════════════╝{C.END}

📁 {PROJECT_ROOT}
""")

    if DRY_RUN:
        print(f"{C.WARN}🧪 DRY RUN MODE{C.END}\n")

    try:
        create_file_manager()
        create_health()
        create_about()
        create_users()
        create_roles()
        create_shipments()
        create_channels()
        create_routes()
        add_header_links()

        if not args.skip_migrate:
            migrate()

        finalize()

    except Exception as e:
        log(f"خطا: {e}", 'err')
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"""
{C.OK}╔══════════════════════════════════════════════════╗
║  ✅ تمام تغییرات اعمال شد                         ║
╚══════════════════════════════════════════════════╝{C.END}

{C.INFO}📍 صفحات جدید:{C.END}
   🩺 http://127.0.0.1:8000/settings/health   ← اول این را باز کن!
   📁 http://127.0.0.1:8000/file-manager
   👤 http://127.0.0.1:8000/users
   🔐 http://127.0.0.1:8000/roles
   📮 http://127.0.0.1:8000/shipments
   🌐 http://127.0.0.1:8000/settings/channels
   ℹ️ http://127.0.0.1:8000/about

{C.INFO}🎯 مرحله بعد:{C.END}
   1. php artisan serve
   2. برو به /settings/health
   3. همه لینک‌ها را چک کن

{C.INFO}💡 نکته:{C.END}
   در صفحه سلامت، همه بخش‌ها را با آیکون و لینک می‌بینی.
   هر بخشی که ساخته نشده، با ❌ مشخص شده.
""")

if __name__ == '__main__':
    main()
