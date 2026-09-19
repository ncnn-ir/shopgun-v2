#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ShopGun — Hotfix 2: پاکسازی Settings و رفع axios"""

import re, sys, shutil
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "shopgun-v2"
STAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP  = PROJECT / "backups" / f"hotfix2_{STAMP}"

class C: G='\033[92m'; Y='\033[93m'; R='\033[91m'; B='\033[94m'; E='\033[0m'
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

# ─────── ۱. پاکسازی Settings/Index.php ───────
def fix_settings():
    rel = "app/Livewire/Settings/Index.php"
    f = PROJECT / rel
    src = f.read_text(encoding='utf-8')
    backup(rel)

    # حذف تمام خطوط AppSetting::set(...) که بعد از dispatch باقی مانده‌اند
    lines = src.split('\n')
    cleaned = []
    removed = 0
    for line in lines:
        stripped = line.strip()
        # اگر خط با AppSetting::set شروع می‌شود و فقط یک فراخوانی است، حذفش کن
        if re.match(r'^AppSetting::set\s*\(', stripped):
            removed += 1
            continue
        cleaned.append(line)

    src = '\n'.join(cleaned)

    # اگر بلوک کد یک { اضافی در انتهای متد updated دارد که باعث ParseError می‌شود،
    # باید ساختار متد را بررسی کنیم
    # الگو: dispatch('theme-changed', [...])  ];  }  <-- بسته‌ی درست متد
    # ساده: هر جایی که دو } پشت سر هم یا بعد از dispatch، مطمئن شو یه } برای متد داریم

    f.write_text(src, encoding='utf-8')
    log(f"{removed} خط AppSetting::set حذف شد", 'ok')

    # بررسی سینتکس با php -l
    import subprocess
    r = subprocess.run(['php', '-l', str(f)], capture_output=True, text=True)
    if r.returncode == 0:
        log("سینتکس PHP درست است", 'ok')
    else:
        log(f"هنوز خطای سینتکس: {r.stdout.strip()}", 'warn')
        # نمایش 15 خط آخر
        lines = src.split('\n')
        print(f"\n{C.Y}── آخرین ۲۰ خط فایل ──{C.E}")
        for i, l in enumerate(lines[-20:], start=len(lines)-19):
            print(f"  {i:4d}▕ {l}")

# ─────── ۲. رفع axios در bootstrap.js ───────
def fix_axios():
    rel = "resources/js/bootstrap.js"
    f = PROJECT / rel
    backup(rel)

    content = """/**
 * ShopGun JS bootstrap
 * axios اختیاری است — اگر لازم داری اول با `npm i axios` نصبش کن
 */

// --- اگر axios داری، این خطوط را uncomment کن ---
// import axios from 'axios';
// window.axios = axios;
// window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// --- Laravel Echo (اختیاری) ---
// import Echo from 'laravel-echo';
// import Pusher from 'pusher-js';
// window.Pusher = Pusher;
"""
    f.write_text(content, encoding='utf-8')
    log("bootstrap.js ساده‌سازی شد (بدون axios)", 'ok')

# ─────── ۳. Main ───────
def main():
    print(f"\n{C.B}══════════════════════════════════════{C.E}")
    print(f"{C.B}  ShopGun Hotfix 2{C.E}")
    print(f"{C.B}══════════════════════════════════════{C.E}\n")

    if not PROJECT.exists():
        log("پروژه پیدا نشد", 'err'); sys.exit(1)

    BACKUP.mkdir(parents=True, exist_ok=True)

    print(f"{C.B}── [1/2] پاکسازی Settings/Index.php{C.E}")
    fix_settings()

    print(f"\n{C.B}── [2/2] رفع axios در bootstrap.js{C.E}")
    fix_axios()

    print(f"\n{C.G}✅ Hotfix 2 اعمال شد{C.E}")
    print(f"\nبکاپ‌ها: {BACKUP}\n")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{C.Y}لغو{C.E}"); sys.exit(130)

