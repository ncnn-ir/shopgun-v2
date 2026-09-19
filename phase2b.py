#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun v2 — Phase 2b: Fix Settings properties + Mobile + Popup
"""

import re, sys, shutil, subprocess
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "shopgun-v2"
STAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP  = PROJECT / "backups" / f"phase2b_{STAMP}"

class C: G='\033[92m'; Y='\033[93m'; R='\033[91m'; B='\033[94m'; D='\033[2m'; E='\033[0m'
def log(m,k='info'):
    i={'info':'🔹','ok':'✅','warn':'⚠️ ','err':'❌'}.get(k,'•')
    c={'info':C.B,'ok':C.G,'warn':C.Y,'err':C.R}.get(k,C.E)
    print(f"{c}{i} {m}{C.E}")

def backup(rel):
    src = PROJECT / rel
    if src.exists():
        dst = BACKUP / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def read(rel):
    p = PROJECT / rel
    return p.read_text(encoding='utf-8') if p.exists() else None

def write(rel, content):
    p = PROJECT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    log(f"نوشته شد: {rel}", 'ok')

def confirm(p):
    try: return input(f"{C.Y}{p} [y/N]: {C.E}").strip().lower() in ('y','yes')
    except EOFError: return False

# ─────────────────────────────────────────────
#  ۱. رفع خطای ui_style — بررسی پراپرتی‌های واقعی
# ─────────────────────────────────────────────

def inspect_properties(src):
    """پراپرتی‌های public کامپوننت را پیدا می‌کند"""
    props = {}
    for m in re.finditer(
        r'public\s+(?:\??\w+\s+)?\$(\w+)\s*(?:=\s*([^;]+))?;',
        src
    ):
        name = m.group(1)
        default = m.group(2).strip() if m.group(2) else 'null'
        props[name] = default
    return props

def fix_settings_properties():
    rel = "app/Livewire/Settings/Index.php"
    src = read(rel)
    if src is None:
        log(f"پیدا نشد: {rel}", 'err'); return

    backup(rel)

    props = inspect_properties(src)
    print(f"{C.D}  پراپرتی‌های فعلی: {', '.join(sorted(props.keys())[:20])}{C.E}")

    # پراپرتی‌های موردنیاز برای تم
    required = {
        'theme':         "'dark'",
        'ui_style':      "'material'",
        'primary_color': "'#1a5276'",
        'accent_color':  "'#c9a84c'",
        'font_family':   "'Vazirmatn'",
    }

    missing = {k: v for k, v in required.items() if k not in props}

    if not missing:
        log("تمام پراپرتی‌های لازم موجودند", 'ok')
        return

    log(f"پراپرتی‌های غایب: {', '.join(missing.keys())}", 'warn')

    # افزودن بلوک پراپرتی‌ها بعد از class declaration
    block_lines = ["\n    // ─── تنظیمات ظاهری (auto-added) ───"]
    for name, default in missing.items():
        block_lines.append(f"    public ${name} = {default};")
    block_lines.append("")

    # درج بعد از '{' اول کلاس
    class_match = re.search(r'class\s+\w+\s+extends\s+[\w\\]+\s*\{', src)
    if not class_match:
        log("کلاس پیدا نشد", 'err'); return

    insert_pos = class_match.end()
    new_src = src[:insert_pos] + "\n".join(block_lines) + src[insert_pos:]

    # همچنین متد mount() یا boot() را بررسی کن که مقادیر را از DB بخواند
    if 'public function mount' not in new_src:
        mount = '''
    public function mount()
    {
        $this->theme         = \\App\\Models\\AppSetting::get('theme', 'dark');
        $this->ui_style      = \\App\\Models\\AppSetting::get('ui_style', 'material');
        $this->primary_color = \\App\\Models\\AppSetting::get('primary_color', '#1a5276');
        $this->accent_color  = \\App\\Models\\AppSetting::get('accent_color', '#c9a84c');
        $this->font_family   = \\App\\Models\\AppSetting::get('font_family', 'Vazirmatn');
    }

'''
        # قبل از render اضافه کن
        if 'public function render' in new_src:
            new_src = new_src.replace('public function render', mount + '    public function render', 1)

    write(rel, new_src)

# ─────────────────────────────────────────────
#  ۲. رفع فضای خالی موبایل با کلاس‌های واقعی
# ─────────────────────────────────────────────

def fix_mobile_space():
    """CSS را با کلاس‌های واقعی sg-main-header و sg-content-area بازنویسی می‌کند"""
    rel = "resources/css/app.css"
    src = read(rel)
    if src is None: return
    backup(rel)

    # حذف بلوک فاز ۲ قبلی (اگر اضافه شده)
    src = re.sub(
        r'/\* =+\s*Phase 2 — Layout & Mobile Fixes.*?(?=/\*|\Z)',
        '',
        src,
        flags=re.DOTALL
    )

    new_block = '''
/* ============================================================
   Phase 2b — Layout & Mobile Fixes (with REAL class names)
   ============================================================ */

[x-cloak] { display: none !important; }

/* --- هدر چسبنده --- */
.sg-main-header,
header.sg-main-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: color-mix(in srgb, var(--sg-bg) 88%, transparent);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--sg-border);
}

/* --- رفع فضای خالی موبایل ---
   تمام wrapperهای اصلی در موبایل: بدون margin، padding کامل */
@media (max-width: 1023px) {
  body > *,
  .sg-app-shell,
  .sg-layout,
  .sg-wrapper,
  .sg-content-area,
  .sg-main,
  main.sg-main,
  main {
    margin-right: 0 !important;
    margin-left: 0 !important;
    padding-right: 0 !important;
    padding-left: 0 !important;
    width: 100% !important;
    max-width: 100vw !important;
    box-sizing: border-box;
  }

  .sg-content-area {
    padding: 12px !important;
  }

  /* سایدبار مخفی در موبایل */
  .sg-sidebar,
  aside.sg-sidebar,
  aside {
    display: none !important;
  }

  /* حذف هر margin بزرگی که ممکن است سایدبار را جبران کند */
  [class*="mr-"][class*="240"],
  [class*="ml-"][class*="240"],
  [class*="mr-"][class*="256"],
  [class*="ml-"][class*="256"],
  [class*="mr-"][class*="260"],
  [class*="ml-"][class*="260"],
  [class*="pr-"][class*="240"],
  [class*="pl-"][class*="240"],
  [style*="margin-right: 240"],
  [style*="margin-left: 240"],
  [style*="margin-right:240"],
  [style*="margin-left:240"] {
    margin-right: 0 !important;
    margin-left: 0 !important;
  }

  /* فاصله پایین برای نوار موبایل */
  body { padding-bottom: 72px; }
}

/* --- نوار پایین موبایل --- */
.sg-mobile-bar,
nav.sg-mobile-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: color-mix(in srgb, var(--sg-surface) 92%, transparent);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-top: 1px solid var(--sg-border);
  padding-bottom: env(safe-area-inset-bottom, 0);
  display: flex;
}
.sg-mobile-bar a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 4px;
  font-size: 10px;
  color: var(--sg-text-muted);
  text-decoration: none;
  transition: color 0.15s ease;
}
.sg-mobile-bar a.active,
.sg-mobile-bar a[aria-current="page"] {
  color: var(--sg-primary);
}

/* --- انیمیشن صفحه --- */
.sg-page-enter { animation: sgFadeIn 0.18s ease-out; }

/* --- پاپ‌آپ: بسته شدن با کلیک بیرون (fallback) --- */
.sg-popup-backdrop > .sg-popup-panel {
  pointer-events: auto;
}
.sg-popup-backdrop {
  pointer-events: auto;
}
'''

    write(rel, src.rstrip() + "\n" + new_block)

# ─────────────────────────────────────────────
#  ۳. رفع theme در تمام صفحات
# ─────────────────────────────────────────────

def fix_theme_globally():
    """
    مطمئن می‌شود app.blade.php مقادیر theme/ui_style را روی <html> اعمال می‌کند.
    """
    rel = "resources/views/components/layouts/app.blade.php"
    src = read(rel)
    if src is None:
        log("app.blade.php پیدا نشد", 'warn'); return

    backup(rel)
    original = src

    # اگر هنوز data-theme ندارد، اضافه کن
    if 'data-theme=' not in src:
        src = re.sub(
            r'<html([^>]*)>',
            lambda m: f'<html{m.group(1)} data-theme="{{{{ $_theme ?? \'dark\' }}}}" data-style="{{{{ $_style ?? \'material\' }}}}">',
            src, count=1
        )
        log("data-theme/data-style به <html> اضافه شد", 'ok')
    else:
        # اگر <html> hardcode است، dynamic کن
        src = re.sub(
            r'<html[^>]*data-theme="[^"]*"[^>]*data-style="[^"]*"[^>]*>',
            '<html lang="fa" dir="rtl" data-theme="{{ $_theme ?? \'dark\' }}" data-style="{{ $_style ?? \'material\' }}">',
            src, count=1
        )
        log("data-theme/data-style داینامیک شد", 'ok')

    # بلوک style زنده — چک وجود
    if '--sg-primary:' not in src:
        live_style = '''  <style>
    :root {
      --sg-primary:       {{ $_p ?? '#1a5276' }};
      --sg-accent:        {{ $_g ?? '#c9a84c' }};
      --sg-font:          '{{ $_f ?? 'Vazirmatn' }}', ui-sans-serif, system-ui, sans-serif;
    }
    html, body { font-family: var(--sg-font); }
  </style>

'''
        src = re.sub(r'(@vite\()', live_style + r'\1', src, count=1)
        log("بلوک style زنده اضافه شد", 'ok')

    # مطمئن شو متغیرهای $_theme و $_style و $_p و $_g و $_f تعریف شده‌اند
    if '$_theme' not in src or '$_p' not in src:
        # پیدا کردن @php قبلی
        php_block = '''@php
  $_theme = \\App\\Models\\AppSetting::get('theme', 'dark');
  $_style = \\App\\Models\\AppSetting::get('ui_style', 'material');
  $_p = \\App\\Models\\AppSetting::get('primary_color', '#1a5276');
  $_g = \\App\\Models\\AppSetting::get('accent_color', '#c9a84c');
  $_f = \\App\\Models\\AppSetting::get('font_family', 'Vazirmatn');
@endphp
'''
        # اگر @php وجود دارد، حذف و جایگزینی
        src = re.sub(r'@php.*?@endphp\s*', '', src, count=1, flags=re.DOTALL)
        # درج قبل از <html
        src = src.replace('<html', php_block + '<html', 1)
        log("بلوک @php داینامیک اضافه شد", 'ok')

    if src != original:
        write(rel, src)

# ─────────────────────────────────────────────
#  ۴. پاپ‌آپ — بسته شدن سراسری با کلیک بیرون
# ─────────────────────────────────────────────

def fix_popup_close():
    """
    JS سراسری که هر پاپ‌آپ با class .sg-popup-backdrop را با کلیک بیرون می‌بندد.
    """
    rel = "resources/js/app.js"
    src = read(rel)
    if src is None:
        log("app.js پیدا نشد", 'err'); return

    if 'sgGlobalPopupClose' in src:
        log("handler پاپ‌آپ از قبل موجود است", 'warn'); return

    backup(rel)

    handler = '''

/* ============================================================
   Global popup close — کلیک بیرون پاپ‌آپ را می‌بندد
   ============================================================ */
window.sgGlobalPopupClose = function () {
  document.addEventListener('click', function (e) {
    const backdrop = e.target.closest('.sg-popup-backdrop');
    if (!backdrop) return;

    // اگر کلیک روی خود backdrop یا child .absolute inset-0 بود (نه panel)
    const panel = e.target.closest('.sg-popup-panel');
    if (panel) return; // کلیک داخل پنل — بستن نکن

    // تلاش برای بستن با Alpine
    const alpineData = backdrop._x_dataStack && backdrop._x_dataStack[0];
    if (alpineData && typeof alpineData.open !== 'undefined') {
      alpineData.open = false;
      return;
    }

    // fallback: مخفی کردن مستقیم
    backdrop.style.display = 'none';
  });
};

document.addEventListener('DOMContentLoaded', window.sgGlobalPopupClose);
document.addEventListener('livewire:navigated', window.sgGlobalPopupClose);
'''

    write(rel, src.rstrip() + handler)

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    print(f"\n{C.B}══════════════════════════════════════════════════════{C.E}")
    print(f"{C.B}  ShopGun v2 — Phase 2b Fix{C.E}")
    print(f"{C.B}══════════════════════════════════════════════════════{C.E}\n")

    if not PROJECT.exists():
        log("پروژه پیدا نشد", 'err'); sys.exit(1)

    log(f"بکاپ‌ها: {BACKUP}", 'info')

    if not confirm("ادامه می‌دهی؟"):
        log("لغو", 'warn'); sys.exit(0)

    BACKUP.mkdir(parents=True, exist_ok=True)

    print(f"\n{C.B}── [1/4] رفع خطای ui_style{C.E}")
    fix_settings_properties()

    print(f"\n{C.B}── [2/4] رفع فضای خالی موبایل{C.E}")
    fix_mobile_space()

    print(f"\n{C.B}── [3/4] اعمال سراسری تم{C.E}")
    fix_theme_globally()

    print(f"\n{C.B}── [4/4] رفع بسته شدن پاپ‌آپ{C.E}")
    fix_popup_close()

    # تست سینتکس PHP
    print(f"\n{C.B}── تست سینتکس PHP{C.E}")
    r = subprocess.run(
        ['php', '-l', str(PROJECT / 'app/Livewire/Settings/Index.php')],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        log("Settings/Index.php سینتکس OK", 'ok')
    else:
        log(f"خطا: {r.stdout.strip()}", 'err')

    print(f"\n{C.G}══════════════════════════════════════════════════════{C.E}")
    print(f"{C.G}  ✅ Phase 2b اعمال شد{C.E}")
    print(f"{C.G}══════════════════════════════════════════════════════{C.E}")
    print(f"\nگام بعدی:")
    print(f"  {C.B}php artisan optimize:clear{C.E}")
    print(f"  {C.B}php artisan view:clear{C.E}")
    print(f"  {C.B}npm run build{C.E}")
    print(f"  {C.B}php artisan serve{C.E}\n")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{C.Y}لغو{C.E}"); sys.exit(130)

