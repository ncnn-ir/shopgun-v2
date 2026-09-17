#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""رفع خطاهای v3"""

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def write(rel, content):
    full = ROOT / rel
    if full.exists():
        full.rename(full.with_suffix(full.suffix + f'.bak-{datetime.now().strftime("%H%M%S")}'))
    full.write_text(content, encoding='utf-8')
    print(f"✅ {rel}")

# ═══════════════════════════════════════════════════════════════
# ۱. رفع Labels.php — تغییر نام reset به resetDefaults
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

    /* ★ نام تغییر کرد از reset به resetDefaults (چون reset رزرو Livewire است) */
    public function resetDefaults(): void
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

write('app/Livewire/Settings/Labels.php', LABELS_PHP)

# ═══════════════════════════════════════════════════════════════
# ۲. رفع View — تغییر wire:click="reset" به resetDefaults
# ═══════════════════════════════════════════════════════════════

view_path = ROOT / 'resources/views/livewire/settings/labels.blade.php'
if view_path.exists():
    content = view_path.read_text(encoding='utf-8')
    content = content.replace('wire:click="reset"', 'wire:click="resetDefaults"')
    view_path.write_text(content, encoding='utf-8')
    print("✅ labels.blade.php بروزرسانی شد")

# ═══════════════════════════════════════════════════════════════
# ۳. حذف Excel قدیمی و نصب نسخه جدید (اختیاری)
# ═══════════════════════════════════════════════════════════════

print("\n⚠️ maatwebsite/excel نسخه ۱.۱.۵ (قدیمی) نصب شد. برای Laravel 13 نسخه ۳.x لازم است.\n")
print("اجرا کن برای اصلاح:")
print("  composer remove maatwebsite/excel phpoffice/phpexcel")
print("  composer require maatwebsite/excel:^3.1")
print()

# ═══════════════════════════════════════════════════════════════
# ۴. راهنمای GitHub Updater
# ═══════════════════════════════════════════════════════════════

print("\n📌 nawrasbukhari/laravelgithubupdater نصب نشد.")
print("   دلیل: نسخه stable نداشت (فقط dev-master).")
print()
print("   گزینه ۱: نصب با dev-master")
print("     composer require nawrasbukhari/laravelgithubupdater:dev-master --with-all-dependencies")
print()
print("   گزینه ۲: استفاده از پکیج جایگزین (پیشنهادی)")
print("     composer require codedge/laravel-selfupdater")
print()

# ═══════════════════════════════════════════════════════════════
# ۵. پاکسازی
# ═══════════════════════════════════════════════════════════════

print("\n🔧 پاکسازی...")
subprocess.run("php artisan optimize:clear", shell=True, cwd=ROOT)
subprocess.run("php artisan view:clear", shell=True, cwd=ROOT)

print("""
╔══════════════════════════════════════════════╗
║  ✅ رفع شد                                    ║
╚══════════════════════════════════════════════╝

🎯 حالا اجرا کن:

   php artisan serve

بعد برو به:

   http://127.0.0.1:8000/settings/health
   http://127.0.0.1:8000/settings/labels
""")
