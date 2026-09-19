#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║  ShopGun v2 — Phase 1 Hotfix                             ║
║  Fixes: bootstrap.js, AppSetting::set, fonts, popup      ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, re, shutil
from datetime import datetime
from pathlib import Path

PROJECT    = Path.home() / "shopgun-v2"
STAMP      = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = PROJECT / "backups" / f"hotfix1_{STAMP}"

class C:
    G='\033[92m'; Y='\033[93m'; R='\033[91m'; B='\033[94m'; E='\033[0m'

def log(msg, kind='info'):
    icon = {'info':'🔹','ok':'✅','warn':'⚠️ ','err':'❌'}.get(kind,'•')
    col  = {'info':C.B,'ok':C.G,'warn':C.Y,'err':C.R}.get(kind,C.E)
    print(f"{col}{icon} {msg}{C.E}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return None
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst

def write_file(rel, content):
    dst = PROJECT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding='utf-8')
    log(f"نوشته شد: {rel}", 'ok')

def read_file(rel):
    p = PROJECT / rel
    return p.read_text(encoding='utf-8') if p.exists() else None

def confirm(p):
    try:
        return input(f"{C.Y}{p} [y/N]: {C.E}").strip().lower() in ('y','yes')
    except EOFError:
        return False

# ─────────────────────────────────────────────
#  ۱. رفع خطای Vite — ساخت bootstrap.js
# ─────────────────────────────────────────────

BOOTSTRAP_CONTENT = r'''/**
 * Laravel Echo / Axios bootstrap
 * اگر Echo استفاده می‌کنی، اینجا تنظیمش کن
 */
import axios from 'axios';
window.axios = axios;
window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// --- اگر Laravel Echo داری، خطوط زیر را uncomment کن ---
// import Echo from 'laravel-echo';
// import Pusher from 'pusher-js';
// window.Pusher = Pusher;
// window.Echo = new Echo({
//     broadcaster: 'pusher',
//     key: import.meta.env.VITE_PUSHER_APP_KEY,
//     cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
//     forceTLS: true,
// });
'''

def fix_bootstrap():
    rel = "resources/js/bootstrap.js"
    if (PROJECT / rel).exists():
        log(f"bootstrap.js از قبل وجود دارد — دست‌نخورده ماند", 'warn')
        return
    write_file(rel, BOOTSTRAP_CONTENT)

# ─────────────────────────────────────────────
#  ۲. رفع AppSetting::set — بازنویسی متد updated
# ─────────────────────────────────────────────

def inspect_app_setting():
    """بررسی مدل AppSetting و پیدا کردن روش ذخیره‌سازی"""
    rel = "app/Models/AppSetting.php"
    src = read_file(rel)
    if src is None:
        log(f"مدل AppSetting پیدا نشد: {rel}", 'warn')
        return None

    info = {'has_set': False, 'has_get': False, 'fillable': [], 'table': None}

    if re.search(r'function\s+set\s*\(', src): info['has_set'] = True
    if re.search(r'function\s+get\s*\(', src): info['has_get'] = True

    # fillable
    m = re.search(r'\$fillable\s*=\s*\[([^\]]+)\]', src)
    if m:
        info['fillable'] = [x.strip().strip("'\"") for x in m.group(1).split(',') if x.strip()]

    # table
    m = re.search(r'\$table\s*=\s*[\'"]([^\'"]+)', src)
    if m: info['table'] = m.group(1)

    print(f"\n{C.B}─ بررسی AppSetting ─{C.E}")
    print(f"  جدول: {info['table'] or '(پیش‌فرض: app_settings)'}")
    print(f"  ستون‌های fillable: {info['fillable'] or '(تعریف نشده)'}")
    print(f"  متد set(): {'دارد ✅' if info['has_set'] else 'ندارد ❌'}")
    print(f"  متد get(): {'دارد ✅' if info['has_get'] else 'ندارد ❌'}")
    print()

    return info

def patch_settings_updated(info):
    """جایگزینی فراخوانی AppSetting::set با updateOrCreate"""
    rel = "app/Livewire/Settings/Index.php"
    src = read_file(rel)
    if src is None:
        log(f"فایل پیدا نشد: {rel}", 'warn')
        return

    backup(rel)
    original = src

    # بلوک جایگزین: از updateOrCreate استفاده می‌کنیم
    new_block = '''        $settings = [
            'primary_color' => $this->primary_color,
            'accent_color'  => $this->accent_color,
            'font_family'   => $this->font_family,
            'theme'         => $this->theme,
            'ui_style'      => $this->ui_style,
        ];

        foreach ($settings as $key => $value) {
            \\App\\Models\\AppSetting::updateOrCreate(
                ['key' => $key],
                ['value' => $value]
            );
        }

        \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');

        $this->dispatch('theme-changed', [
            'theme'   => $this->theme,
            'style'   => $this->ui_style,
            'primary' => $this->primary_color,
            'accent'  => $this->accent_color,
            'font'    => $this->font_family,
        ]);'''

    # پیدا کردن بلوک updated() که در فاز ۱ اضافه کردیم
    pattern = re.compile(
        r'(public function updated\(\$property\).*?\{\s*)'
        r'(.*?)'
        r'(\n\s*\}\s*\n)',
        re.DOTALL
    )
    m = pattern.search(src)
    if not m:
        log("متد updated() پیدا نشد — از صفر می‌سازیم", 'warn')
        method = f"\n    public function updated($property)\n    {{\n        if (! in_array($property, ['primary_color','accent_color','font_family','theme','ui_style'])) return;\n\n{new_block}\n    }}\n\n"
        if 'public function render(' in src:
            src = src.replace('public function render(', method + '    public function render(', 1)
        else:
            idx = src.rstrip().rfind('}')
            src = src[:idx] + method + src[idx:]
    else:
        src = src[:m.start()] + m.group(1) + new_block + m.group(3) + src[m.end():]

    if src != original:
        write_file(rel, src)
    else:
        log("تغییری اعمال نشد", 'warn')

# ─────────────────────────────────────────────
#  ۳. رفع خطای فونت — حذف @font-face (استفاده از fallback)
# ─────────────────────────────────────────────

def fix_fonts():
    rel = "resources/css/app.css"
    src = read_file(rel)
    if src is None: return

    if '@font-face' not in src:
        log("font-face از قبل حذف شده", 'warn')
        return

    backup(rel)

    # حذف تمام بلوک‌های @font-face
    src = re.sub(
        r'@font-face\s*\{[^}]*\}\s*',
        '',
        src,
        flags=re.DOTALL
    )
    write_file(rel, src)
    log("font-face حذف شد — فونت از فالبک سیستمی استفاده می‌کند", 'ok')

    # پچ app.blade.php برای اضافه کردن Google Fonts
    blade_rel = "resources/views/components/layouts/app.blade.php"
    blade = read_file(blade_rel)
    if blade and 'fonts.googleapis.com' not in blade:
        backup(blade_rel)
        gf = '  <link rel="preconnect" href="https://fonts.googleapis.com">\n' \
             '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n' \
             '  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700&display=swap" rel="stylesheet">\n\n'
        # درج قبل از @vite
        if '@vite(' in blade:
            blade = blade.replace('@vite(', gf + '@vite(', 1)
            write_file(blade_rel, blade)
            log("Vazirmatn از Google Fonts به app.blade.php اضافه شد", 'ok')

# ─────────────────────────────────────────────
#  ۴. پاپ‌آپ استاندارد — کامپوننت قابل استفاده مجدد
# ─────────────────────────────────────────────

POPUP_BLADE = r'''{{--
   کامپوننت پاپ‌آپ استاندارد ShopGun
   استفاده:
     <x-ui.popup id="product-{{ $id }}" title="عنوان">
        محتوا
        <x-slot:footer>... دکمه‌ها ...</x-slot:footer>
     </x-ui.popup>
   باز کردن:  Livewire: $this->dispatch('open-popup-product-5')
               JS: window.dispatchEvent(new CustomEvent('open-popup-product-5'))
--}}

@props([
    'id'       => 'popup',
    'title'    => 'عنوان',
    'maxWidth' => '32rem',
    'zIndex'   => 9000,
])

<div
    x-data="{ open: false }"
    x-on:open-popup-{{ $id }}.window="open = true"
    x-on:close-popup-{{ $id }}.window="open = false"
    x-show="open"
    x-cloak
    @keydown.escape.window="open = false"
    class="sg-popup-backdrop"
    style="z-index: {{ $zIndex }};"
    x-transition:enter="transition ease-out duration-200"
    x-transition:enter-start="opacity-0"
    x-transition:enter-end="opacity-100"
>
    {{-- Backdrop — کلیک بیرون => بستن --}}
    <div class="absolute inset-0" @click="open = false"></div>

    {{-- Panel --}}
    <div
        class="sg-popup-panel sg-anim-scale"
        style="max-width: {{ $maxWidth }}; z-index: {{ $zIndex + 1 }};"
        @click.stop
    >
        <div class="sg-popup-header">
            <h3 class="font-bold text-base">{{ $title }}</h3>
            <button type="button" class="sg-btn-icon" @click="open = false" aria-label="بستن">✕</button>
        </div>

        <div class="sg-popup-body">
            {{ $slot }}
        </div>

        @isset($footer)
            <div class="sg-popup-footer">
                {{ $footer }}
            </div>
        @endisset
    </div>
</div>
'''

def create_popup_component():
    write_file("resources/views/components/ui/popup.blade.php", POPUP_BLADE)

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    print(f"\n{C.B}══════════════════════════════════════════════════════{C.E}")
    print(f"{C.B}  ShopGun v2 — Phase 1 Hotfix{C.E}")
    print(f"{C.B}══════════════════════════════════════════════════════{C.E}\n")

    if not PROJECT.exists():
        log(f"پروژه پیدا نشد: {PROJECT}", 'err'); sys.exit(1)

    log(f"بکاپ‌ها در: {BACKUP_DIR}", 'info')

    if not confirm("ادامه می‌دهی؟"):
        log("لغو شد", 'warn'); sys.exit(0)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # ۱
    print(f"\n{C.B}── [1/4] رفع خطای Vite (bootstrap.js){C.E}")
    fix_bootstrap()

    # ۲
    print(f"\n{C.B}── [2/4] رفع AppSetting::set{C.E}")
    info = inspect_app_setting()
    if info is None or not info['has_set']:
        patch_settings_updated(info or {})

    # ۳
    print(f"\n{C.B}── [3/4] رفع فونت{C.E}")
    fix_fonts()

    # ۴
    print(f"\n{C.B}── [4/4] کامپوننت پاپ‌آپ استاندارد{C.E}")
    create_popup_component()

    print(f"\n{C.G}══════════════════════════════════════════════════════{C.E}")
    print(f"{C.G}  ✅ Hotfix اعمال شد{C.E}")
    print(f"{C.G}══════════════════════════════════════════════════════{C.E}")
    print(f"\nگام بعدی:")
    print(f"  {C.B}php artisan optimize:clear{C.E}")
    print(f"  {C.B}npm run build{C.E}")
    print(f"  {C.B}php artisan serve{C.E}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.Y}لغو شد{C.E}"); sys.exit(130)
