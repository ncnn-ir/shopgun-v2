#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Package Integrator
ادغام خودکار پکیج‌های نصب‌شده در پروژه Laravel

اجرا:
    python3 integrate_packages.py
    python3 integrate_packages.py --step 1
    python3 integrate_packages.py --dry-run
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(os.getenv('SHOPGUN_ROOT', '.')).resolve()
DRY_RUN = False

class C:
    OK    = '\033[92m'
    WARN  = '\033[93m'
    ERR   = '\033[91m'
    INFO  = '\033[96m'
    BOLD  = '\033[1m'
    END   = '\033[0m'

def log(msg, kind='info'):
    icon = {'info':'ℹ️', 'ok':'✅', 'warn':'⚠️', 'err':'❌'}[kind]
    color = {'info':C.INFO, 'ok':C.OK, 'warn':C.WARN, 'err':C.ERR}[kind]
    print(f"{color}{icon} {msg}{C.END}")

def run(cmd, cwd=None):
    if DRY_RUN:
        log(f"[DRY] $ {cmd}", 'warn')
        return 0
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_ROOT,
                          capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            log(f"خطا در: {cmd}", 'err')
            if r.stderr: print(f"  {r.stderr[:300]}")
        return r.returncode
    except Exception as e:
        log(f"Exception: {e}", 'err')
        return 1

def write_file(rel_path, content, mode='append'):
    full = PROJECT_ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)

    if DRY_RUN:
        log(f"[DRY] {mode}: {rel_path}", 'warn')
        return

    if mode == 'append':
        existing = full.read_text(encoding='utf-8') if full.exists() else ''
        if content.strip() in existing:
            log(f"قبلاً اضافه شده: {rel_path}", 'warn')
            return
        with full.open('a', encoding='utf-8') as f:
            f.write(content)
        log(f"append: {rel_path}", 'ok')
    else:
        if full.exists():
            backup = full.with_suffix(full.suffix + f".bak-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            full.rename(backup)
        full.write_text(content, encoding='utf-8')
        log(f"created: {rel_path}", 'ok')

# ═══════════════════════════════════════════════════════════════
# STEP 1: انتشار Config و Migration پکیج‌ها
# ═══════════════════════════════════════════════════════════════

def step1_publish():
    print(f"\n{C.BOLD}═══ Step 1: انتشار Config و Migration ═══{C.END}")

    commands = [
        # PowerGrid
        "php artisan vendor:publish --provider='PowerComponents\\PowerGrid\\PowerGridServiceProvider' --tag=powergrid-config --force",
        "php artisan vendor:publish --provider='PowerComponents\\PowerGrid\\PowerGridServiceProvider' --tag=powergrid-lang --force",

        # Jalali Datepicker
        "php artisan vendor:publish --tag=jalali-datepicker-config --force",
        "php artisan vendor:publish --tag=jalali-datepicker-assets --force",

        # Livewire Filemanager
        "php artisan vendor:publish --tag=livewire-filemanager-migrations --force",
        "php artisan vendor:publish --tag=filemanager-config --force",

        # Laravel GitHub Updater
        "php artisan vendor:publish --provider='NawrasBukhari\\Updater\\UpdaterServiceProvider' --force",

        # Livewire Form Builder
        "php artisan vendor:publish --tag=livewire-form-builder-config --force",
        "php artisan livewire-form-builder:publish-stubs",

        # Laravel Settings
        "php artisan vendor:publish --tag=settings-migrations --force",
        "php artisan vendor:publish --tag=settings-config --force",

        # Medialibrary (پیش‌نیاز Filemanager)
        "php artisan vendor:publish --provider='Spatie\\MediaLibrary\\MediaLibraryServiceProvider' --tag=medialibrary-migrations --force",
        "php artisan vendor:publish --provider='Spatie\\MediaLibrary\\MediaLibraryServiceProvider' --tag=medialibrary-config --force",
    ]

    for cmd in commands:
        run(cmd)

# ═══════════════════════════════════════════════════════════════
# STEP 2: اجرای Migration
# ═══════════════════════════════════════════════════════════════

def step2_migrate():
    print(f"\n{C.BOLD}═══ Step 2: اجرای Migration ═══{C.END}")
    run("php artisan migrate --force")

# ═══════════════════════════════════════════════════════════════
# STEP 3: ادغام PowerGrid در Layout
# ═══════════════════════════════════════════════════════════════

POWERGRID_ASSETS = """
    {{-- PowerGrid Assets --}}
    @powerGridStyles
"""

POWERGRID_SCRIPTS = """
    {{-- PowerGrid Scripts --}}
    @powerGridScripts
"""

def step3_powergrid():
    print(f"\n{C.BOLD}═══ Step 3: ادغام PowerGrid ═══{C.END}")

    layout = PROJECT_ROOT / 'resources/views/components/layouts/app.blade.php'
    if not layout.exists():
        log("layout پیدا نشد", 'err')
        return

    content = layout.read_text(encoding='utf-8')

    # اضافه کردن @powerGridStyles قبل از </head>
    if '@powerGridStyles' not in content:
        content = content.replace('</head>', POWERGRID_ASSETS + '\n</head>')
        log("PowerGrid styles اضافه شد", 'ok')
    else:
        log("PowerGrid styles قبلاً اضافه شده", 'warn')

    # اضافه کردن @powerGridScripts قبل از </body>
    if '@powerGridScripts' not in content:
        content = content.replace('</body>', POWERGRID_SCRIPTS + '\n</body>')
        log("PowerGrid scripts اضافه شد", 'ok')
    else:
        log("PowerGrid scripts قبلاً اضافه شده", 'warn')

    if not DRY_RUN:
        layout.write_text(content, encoding='utf-8')
        log("layout بروزرسانی شد", 'ok')

    # ساخت یک جدول نمونه برای تست
    run("php artisan powergrid:create OrdersTable --model=Order --force")

# ═══════════════════════════════════════════════════════════════
# STEP 4: ادغام Livewire Filemanager
# ═══════════════════════════════════════════════════════════════

FILEMANAGER_COMPONENT = """<?php

namespace App\\Livewire;

use Livewire\\Component;

class FileManagerPage extends Component
{
    public function render()
    {
        return view('livewire.file-manager')
            ->layout('components.layouts.app');
    }
}
"""

FILEMANAGER_VIEW = """<div class="p-4 md:p-6">
    <h1 class="text-xl md:text-2xl font-bold mb-4">📁 مدیریت فایل‌ها</h1>

    <div class="bg-base-100 rounded-lg shadow border border-base-300 overflow-hidden">
        <x-livewire-filemanager />
    </div>
</div>

@filemanagerScripts
@filemanagerStyles
"""

def step4_filemanager():
    print(f"\n{C.BOLD}═══ Step 4: ادغام Livewire Filemanager ═══{C.END}")

    # ساخت کامپوننت
    write_file('app/Livewire/FileManagerPage.php', FILEMANAGER_COMPONENT, 'overwrite')
    write_file('resources/views/livewire/file-manager.blade.php', FILEMANAGER_VIEW, 'overwrite')

    # اضافه کردن route
    routes = PROJECT_ROOT / 'routes/web.php'
    if routes.exists():
        content = routes.read_text(encoding='utf-8')
        if 'file-manager' not in content:
            marker = "    Route::prefix('settings')->name('settings.')->group(function () {"
            new_route = "    Route::get('/file-manager', App\\\\Livewire\\\\FileManagerPage::class)->name('file-manager');\n\n"
            if marker in content:
                content = content.replace(marker, new_route + marker)
                if not DRY_RUN:
                    routes.write_text(content, encoding='utf-8')
                log("route /file-manager اضافه شد", 'ok')

    # اضافه کردن @source به Tailwind CSS
    tailwind = PROJECT_ROOT / 'resources/css/app.css'
    if tailwind.exists():
        content = tailwind.read_text(encoding='utf-8')
        source_line = "@source '../../vendor/livewire-filemanager/filemanager/resources/views/**/*.blade.php';"
        if source_line not in content:
            content = content + '\n' + source_line + '\n'
            if not DRY_RUN:
                tailwind.write_text(content, encoding='utf-8')
            log("@source Filemanager به CSS اضافه شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# STEP 5: ادغام Jalali Datepicker
# ═══════════════════════════════════════════════════════════════

JALALI_EXAMPLE = """{{-- نمونه استفاده از انتخابگر تاریخ شمسی --}}
<x-jalali-datepicker
    wire:model="date"
    format="YYYY-MM-DD"
    :with-time="false"
    placeholder="انتخاب تاریخ"
/>
"""

def step5_jalali():
    print(f"\n{C.BOLD}═══ Step 5: ادغام Jalali Datepicker ═══{C.END}")

    # اضافه کردن کامپوننت به Layout برای دسترسی در همه صفحات
    layout = PROJECT_ROOT / 'resources/views/components/layouts/app.blade.php'
    if layout.exists():
        content = layout.read_text(encoding='utf-8')
        if 'jalali-datepicker' not in content:
            # اضافه کردن scripts
            script = "\n    {{-- Jalali Datepicker --}}\n    @stack('jalali-scripts')\n"
            content = content.replace('@livewireScripts', script + '@livewireScripts')
            if not DRY_RUN:
                layout.write_text(content, encoding='utf-8')
            log("Jalali Datepicker در layout ادغام شد", 'ok')

    log("برای استفاده: <x-jalali-datepicker wire:model='date' />", 'info')

# ═══════════════════════════════════════════════════════════════
# STEP 6: ادغام Laravel Settings
# ═══════════════════════════════════════════════════════════════

SETTINGS_ENUM = """<?php

namespace App\\Settings;

use Abdelhamiderrahmouni\\LaravelSettings\\Contracts\\SettingDefinition;

enum GeneralSettings: string implements SettingDefinition
{
    case ShopName       = 'shop_name';
    case ShopPhone      = 'shop_phone';
    case ShopAddress    = 'shop_address';
    case ShopPostal     = 'shop_postal';
    case ShopEmail      = 'shop_email';
    case Currency       = 'currency';
    case Theme          = 'theme';
    case PrimaryColor   = 'primary_color';
    case AccentColor    = 'accent_color';
    case FontFamily     = 'font_family';
    case CertWidth      = 'cert_width';
    case CertHeight     = 'cert_height';
    case LabelWidth     = 'label_width';
    case LabelHeight    = 'label_height';
    case CommerceUrl    = 'commerce_url';
    case CommerceKey    = 'commerce_key';
    case CommerceSecret = 'commerce_secret';

    public function default(): mixed
    {
        return match ($this) {
            self::ShopName       => 'جواهری مشاهیر',
            self::ShopPhone      => '09151531301',
            self::Currency       => 'تومان',
            self::Theme          => 'light',
            self::PrimaryColor   => '#1a5276',
            self::AccentColor    => '#c9a84c',
            self::FontFamily     => 'Vazirmatn',
            self::CertWidth      => 6.5,
            self::CertHeight     => 6.5,
            self::LabelWidth     => 100,
            self::LabelHeight    => 50,
            default              => null,
        };
    }

    public function group(): string
    {
        return match ($this) {
            self::ShopName, self::ShopPhone, self::ShopAddress,
            self::ShopPostal, self::ShopEmail, self::Currency => 'general',
            self::Theme, self::PrimaryColor, self::AccentColor,
            self::FontFamily => 'appearance',
            self::CertWidth, self::CertHeight => 'certificate',
            self::LabelWidth, self::LabelHeight => 'label',
            self::CommerceUrl, self::CommerceKey, self::CommerceSecret => 'commerce',
        };
    }

    public function type(): string
    {
        return match ($this) {
            self::CertWidth, self::CertHeight => 'float',
            self::LabelWidth, self::LabelHeight => 'int',
            default => 'string',
        };
    }
}
"""

def step6_settings():
    print(f"\n{C.BOLD}═══ Step 6: ادغام Laravel Settings ═══{C.END}")

    write_file('app/Settings/GeneralSettings.php', SETTINGS_ENUM, 'overwrite')

    # ساخت enum با دستور
    run("php artisan settings:make GeneralSettings")

    log("Settings enum ساخته شد — می‌توانی AppSetting را به آن مهاجرت دهی", 'info')

# ═══════════════════════════════════════════════════════════════
# STEP 7: ادغام Form Builder
# ═══════════════════════════════════════════════════════════════

def step7_form_builder():
    print(f"\n{C.BOLD}═══ Step 7: ادغام Livewire Form Builder ═══{C.END}")

    # اضافه کردن route
    routes = PROJECT_ROOT / 'routes/web.php'
    if routes.exists():
        content = routes.read_text(encoding='utf-8')
        if 'livewire-form-builder' not in content:
            marker = "    Route::prefix('settings')->name('settings.')->group(function () {"
            new_route = "    Route::get('/forms', fn() => view('livewire.form-builder-page'))->name('forms.index');\n\n"
            if marker in content:
                content = content.replace(marker, new_route + marker)
                if not DRY_RUN:
                    routes.write_text(content, encoding='utf-8')
                log("route /forms اضافه شد", 'ok')

    # ساخت view
    view = """<div class="p-4 md:p-6">
    <h1 class="text-xl md:text-2xl font-bold mb-4">📝 فرم‌ساز</h1>

    <div class="bg-base-100 rounded-lg shadow border border-base-300 overflow-hidden"
         style="min-height: 70vh;">
        <livewire:livewire-form-builder />
    </div>
</div>
"""
    write_file('resources/views/livewire/form-builder-page.blade.php', view, 'overwrite')

    log("برای دسترسی به فرم‌ساز به /forms برو", 'info')

# ═══════════════════════════════════════════════════════════════
# STEP 8: ادغام GitHub Updater
# ═══════════════════════════════════════════════════════════════

def step8_updater():
    print(f"\n{C.BOLD}═══ Step 8: ادغام GitHub Updater ═══{C.END}")

    # بررسی config
    config_path = PROJECT_ROOT / 'config/self-updater.php'
    if not config_path.exists():
        config_path = PROJECT_ROOT / 'config/github-updater.php'

    if config_path.exists():
        log(f"config پیدا شد: {config_path.name}", 'ok')
    else:
        log("config پیدا نشد — دستی بررسی کن", 'warn')

    log("در .env اضافه کن:", 'info')
    log("  GITHUB_TOKEN=your_github_token", 'info')
    log("  GITHUB_USERNAME=your_username", 'info')
    log("  GITHUB_REPO_LINK=github.com/your/repo.git", 'info')

# ═══════════════════════════════════════════════════════════════
# STEP 9: ادغام Laravel Debugbar + Telescope
# ═══════════════════════════════════════════════════════════════

def step9_debug_tools():
    print(f"\n{C.BOLD}═══ Step 9: ادغام Debugbar + Telescope ═══{C.END}")

    commands = [
        "php artisan vendor:publish --provider='Barryvdh\\Debugbar\\ServiceProvider' --force",
        "php artisan telescope:install",
    ]
    for cmd in commands:
        run(cmd)

    log("Debugbar فعال است — در مرورگر پایین صفحه نمایش داده می‌شود", 'ok')
    log("Telescope: به /telescope برو", 'info')

# ═══════════════════════════════════════════════════════════════
# STEP 10: ادغام Ziggy
# ═══════════════════════════════════════════════════════════════

def step10_ziggy():
    print(f"\n{C.BOLD}═══ Step 10: ادغام Ziggy ═══{C.END}")

    # اضافه کردن @routes به layout
    layout = PROJECT_ROOT / 'resources/views/components/layouts/app.blade.php'
    if layout.exists():
        content = layout.read_text(encoding='utf-8')
        if '@routes' not in content:
            content = content.replace('@livewireScripts', '@routes\n    @livewireScripts')
            if not DRY_RUN:
                layout.write_text(content, encoding='utf-8')
            log("@routes به layout اضافه شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

STEPS = {
    1:  ('انتشار Config/Migration', step1_publish),
    2:  ('اجرای Migration',         step2_migrate),
    3:  ('ادغام PowerGrid',         step3_powergrid),
    4:  ('ادغام Filemanager',        step4_filemanager),
    5:  ('ادغام Jalali Datepicker',  step5_jalali),
    6:  ('ادغام Laravel Settings',   step6_settings),
    7:  ('ادغام Form Builder',       step7_form_builder),
    8:  ('ادغام GitHub Updater',     step8_updater),
    9:  ('ادغام Debugbar+Telescope', step9_debug_tools),
    10: ('ادغام Ziggy',              step10_ziggy),
}

def main():
    global DRY_RUN

    parser = argparse.ArgumentParser(description='ShopGun V2 - Package Integrator')
    parser.add_argument('--step', type=int, choices=list(STEPS.keys()),
                        help='فقط یک مرحله را اجرا کن')
    parser.add_argument('--from', type=int, dest='from_step',
                        help='از این مرحله شروع کن')
    parser.add_argument('--dry-run', action='store_true', help='فقط نمایش')
    parser.add_argument('--skip-migrate', action='store_true',
                        help='مرحله migration را رد کن')
    parser.add_argument('--root', help='مسیر پروژه')
    args = parser.parse_args()

    global PROJECT_ROOT
    if args.root:
        PROJECT_ROOT = Path(args.root).resolve()

    DRY_RUN = args.dry_run

    print(f"{C.BOLD}╔══════════════════════════════════════════════╗")
    print(f"║  ShopGun V2 - Package Integrator             ║")
    print(f"╚══════════════════════════════════════════════╝{C.END}")
    print(f"📁 {PROJECT_ROOT}")
    if DRY_RUN:
        print(f"{C.WARN}🧪 DRY RUN MODE{C.END}")

    # انتخاب مراحل
    if args.step:
        steps_to_run = [args.step]
    elif args.from_step:
        steps_to_run = [k for k in STEPS if k >= args.from_step]
    else:
        steps_to_run = list(STEPS.keys())

    if args.skip_migrate and 2 in steps_to_run:
        steps_to_run.remove(2)
        log("مرحله Migration رد شد", 'warn')

    # اجرا
    for k in steps_to_run:
        name, func = STEPS[k]
        try:
            func()
        except Exception as e:
            log(f"خطا در مرحله {k} ({name}): {e}", 'err')
            if not args.dry_run:
                if input("ادامه؟ (y/n): ").lower() != 'y':
                    break

    # پاکسازی
    print(f"\n{C.BOLD}═══ پاکسازی نهایی ═══{C.END}")
    run("php artisan optimize:clear")
    run("npm run build")

    print(f"\n{C.OK}╔══════════════════════════════════════════════╗")
    print(f"║  ✅ ادغام کامل شد                            ║")
    print(f"╚══════════════════════════════════════════════╝{C.END}")

    print(f"\n{C.INFO}📍 صفحات جدید:{C.END}")
    print("   /file-manager        → مدیریت فایل")
    print("   /forms               → فرم‌ساز Drag & Drop")
    print("   /telescope           → مانیتورینگ")
    print("   /livewire-form-builder → پنل ادمین فرم‌ساز")
    print()
    print(f"{C.INFO}💡 نمونه استفاده:{C.END}")
    print("   PowerGrid:    php artisan powergrid:create MyTable --model=Order")
    print("   Jalali:       <x-jalali-datepicker wire:model='date' />")
    print("   Filemanager:  <x-livewire-filemanager />")


if __name__ == '__main__':
    main()
