#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ShopGun — Hotfix 3: بازنویسی کامل متد updated()"""

import re, sys, shutil, subprocess
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "shopgun-v2"
STAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP  = PROJECT / "backups" / f"hotfix3_{STAMP}"

class C: G='\033[92m'; Y='\033[93m'; R='\033[91m'; B='\033[94m'; E='\033[0m'
def log(m,k='info'):
    i={'info':'🔹','ok':'✅','warn':'⚠️ ','err':'❌'}.get(k,'•')
    c={'info':C.B,'ok':C.G,'warn':C.Y,'err':C.R}.get(k,C.E)
    print(f"{c}{i} {m}{C.E}")

def main():
    print(f"\n{C.B}══════════════════════════════════════{C.E}")
    print(f"{C.B}  ShopGun Hotfix 3{C.E}")
    print(f"{C.B}══════════════════════════════════════{C.E}\n")

    rel = "app/Livewire/Settings/Index.php"
    f = PROJECT / rel
    if not f.exists():
        log(f"پیدا نشد: {rel}", 'err'); sys.exit(1)

    BACKUP.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, BACKUP / "Index.php")
    log(f"بکاپ: {BACKUP / 'Index.php'}", 'info')

    src = f.read_text(encoding='utf-8')
    original = src

    # الگو: از "public function updated" تا شروع "public function render"
    # و همه‌ی محتوای بین آن‌ها را با متد تمیز جایگزین می‌کنیم
    new_method = '''    public function updated($property)
    {
        if (! in_array($property, ['primary_color', 'accent_color', 'font_family', 'theme', 'ui_style'])) {
            return;
        }

        $settings = [
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
        ]);
    }

'''

    pattern = re.compile(
        r'    public function updated\s*\([^)]*\)\s*\{.*?(?=    public function render\s*\()',
        re.DOTALL
    )

    m = pattern.search(src)
    if not m:
        log("متد updated() پیدا نشد — از صفر اضافه می‌کنم", 'warn')
        # قبل از render اضافه کن
        if '    public function render(' in src:
            src = src.replace(
                '    public function render(',
                new_method + '    public function render(',
                1
            )
        else:
            log("حتی render هم پیدا نشد!", 'err'); sys.exit(1)
    else:
        src = src[:m.start()] + new_method + src[m.end():]
        log("متد updated() بازنویسی شد", 'ok')

    if src == original and m:
        log("تغییری اعمال نشد (از قبل درست بود)", 'warn')
    else:
        f.write_text(src, encoding='utf-8')
        log(f"نوشته شد: {rel}", 'ok')

    # تست سینتکس
    r = subprocess.run(['php', '-l', str(f)], capture_output=True, text=True)
    if r.returncode == 0:
        log("سینتکس PHP درست است ✅", 'ok')
        print(f"\n{C.G}✅ موفق — می‌توانی سرور را اجرا کنی{C.E}\n")
    else:
        log(f"هنوز خطا: {r.stdout.strip()}", 'err')
        lines = src.split('\n')
        print(f"\n{C.Y}── خطوط ۸۰۰ تا آخر ──{C.E}")
        start = max(0, 800)
        for i, l in enumerate(lines[start:start+80], start=start+1):
            print(f"  {i:4d}▕ {l}")
        sys.exit(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{C.Y}لغو{C.E}"); sys.exit(130)
