#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║  ShopGun v2 — Phase 2: Layout & Navigation               ║
║  • Fix mobile empty space (fixed margins)                ║
║  • Add wire:navigate for smooth transitions              ║
║  • Fix popup backdrop click                              ║
║  • Diagnostic report of layout files                     ║
╚══════════════════════════════════════════════════════════╝
"""

import re, sys, shutil, subprocess
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "shopgun-v2"
STAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP  = PROJECT / "backups" / f"phase2_{STAMP}"

class C: G='\033[92m'; Y='\033[93m'; R='\033[91m'; B='\033[94m'; D='\033[2m'; E='\033[0m'
def log(m,k='info'):
    i={'info':'🔹','ok':'✅','warn':'⚠️ ','err':'❌','head':'🎯'}.get(k,'•')
    c={'info':C.B,'ok':C.G,'warn':C.Y,'err':C.R,'head':C.B}.get(k,C.E)
    print(f"{c}{i} {m}{C.E}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return None
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst

def read_file(rel):
    p = PROJECT / rel
    return p.read_text(encoding='utf-8') if p.exists() else None

def write_file(rel, content):
    p = PROJECT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    log(f"نوشته شد: {rel}", 'ok')

def confirm(p):
    try: return input(f"{C.Y}{p} [y/N]: {C.E}").strip().lower() in ('y','yes')
    except EOFError: return False

# ─────────────────────────────────────────────
#  ۱. CSS — افزودنی‌های موبایل و x-cloak
# ─────────────────────────────────────────────

CSS_APPEND = r'''
/* ============================================================
   Phase 2 — Layout & Mobile Fixes
   ============================================================ */

/* جلوگیری از نمایش محتوای x-show قبل از Alpine */
[x-cloak] { display: none !important; }

/* رفع فضای خالی سمت چپ در موبایل
   (سایدبار دسکتاپ روی موبایل مخفی می‌شود و margin آن صفر می‌شود) */
@media (max-width: 1023px) {
  .sg-sidebar,
  aside.sg-sidebar,
  [data-sg-sidebar] {
    display: none !important;
  }
  .sg-main,
  main.sg-main,
  [data-sg-main] {
    margin-right: 0 !important;
    margin-left: 0 !important;
    padding-right: 1rem !important;
    padding-left: 1rem !important;
    width: 100% !important;
    max-width: 100% !important;
  }
}

/* همان اصلاح برای حالت RTL که ممکن است margin-left داشته باشد */
@media (max-width: 1023px) {
  [class*="mr-"][class*="240"],
  [class*="ml-"][class*="240"],
  [style*="margin-right: 240"],
  [style*="margin-left: 240"],
  [style*="margin-right:240"],
  [style*="margin-left:240"] {
    margin-right: 0 !important;
    margin-left: 0 !important;
  }
}

/* انیمیشن نرم انتقال صفحات با wire:navigate */
.sg-page-enter {
  animation: sgFadeIn 0.18s ease-out;
}

/* هدر چسبنده بالای صفحه */
.sg-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: color-mix(in srgb, var(--sg-bg) 85%, transparent);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--sg-border);
  min-height: var(--sg-header-h);
}

/* نوار پایین موبایل */
.sg-mobile-bar {
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
.sg-mobile-bar a .sg-mb-icon {
  font-size: 20px;
  line-height: 1;
}

/* فاصله پایین صفحه برای نوار موبایل */
@media (max-width: 1023px) {
  body { padding-bottom: 68px; }
}
'''

def add_css_block():
    rel = "resources/css/app.css"
    src = read_file(rel)
    if src is None:
        log(f"پیدا نشد: {rel}", 'err'); return
    if 'Phase 2 — Layout & Mobile Fixes' in src:
        log("بلوک فاز ۲ از قبل در app.css موجود است", 'warn'); return
    backup(rel)
    write_file(rel, src.rstrip() + "\n\n" + CSS_APPEND)

# ─────────────────────────────────────────────
#  ۲. app.blade.php — پچ margin و wire:navigate
# ─────────────────────────────────────────────

# الگوهای margin بزرگ که باید md: بگیرند
LARGE_MARGIN = re.compile(
    r'(?<![:\w-])(mr|ml)-(6[0-9]|7[0-9]|8[0-9]|9[0-9]|\[2[0-9][0-9]px\]|\[3[0-9][0-9]px\])'
)

def patch_margins(html):
    """افزودن md: به marginهای بزرگ که هنوز breakpoint ندارند"""
    def fix(m):
        return f"md:{m.group(1)}-{m.group(2)}"
    new, count = LARGE_MARGIN.subn(fix, html)
    return new, count

def add_wire_navigate(html):
    """افزودن wire:navigate به لینک‌های داخلی"""
    def replacer(m):
        tag = m.group(0)
        if 'wire:navigate' in tag:
            return tag
        # فقط اگر href داخلی باشد
        href_match = re.search(r'href="([^"]+)"', tag)
        if not href_match:
            return tag
        href = href_match.group(1)
        # رد کردن لینک‌های خارجی، mailto، anchors و لینک‌های logout
        if any(skip in href for skip in ['http://', 'https://', 'mailto:', 'tel:', '#', 'logout']):
            return tag
        return tag.replace('>', ' wire:navigate>', 1)
    
    pattern = re.compile(r'<a\s+[^>]*href="[^"]+"[^>]*>')
    new, count = pattern.subn(replacer, html)
    return new, count

def patch_app_blade():
    rel = "resources/views/components/layouts/app.blade.php"
    src = read_file(rel)
    if src is None:
        log(f"پیدا نشد: {rel}", 'err'); return
    backup(rel)

    original = src

    # ۱. اضافه کردن کلاس sg-main به main content و sg-sidebar به aside
    # این کار باعث می‌شود CSS فاز ۲ روی آن‌ها اعمال شود
    src = re.sub(
        r'<main(\s+[^>]*)?>',
        lambda m: (
            f'<main{m.group(1) or ""}'
            + (' sg-main' if 'sg-main' not in (m.group(1) or '') and 'class="' in (m.group(1) or '') else '')
            + '>'
        ) if 'class="' in (m.group(1) or '') else
        f'<main class="sg-main"{m.group(1) or ""}>',
        src, count=1
    )

    # اگر main پیدا نشد، div اصلی را بساز — اینجا سعی نمی‌کنیم

    # ۲. اصلاح marginهای بزرگ
    src, margin_count = patch_margins(src)
    if margin_count:
        log(f"{margin_count} margin بزرگ اصلاح شد (md: اضافه شد)", 'ok')

    # ۳. افزودن wire:navigate
    src, nav_count = add_wire_navigate(src)
    if nav_count:
        log(f"{nav_count} لینک داخلی wire:navigate گرفت", 'ok')

    if src != original:
        write_file(rel, src)
    else:
        log("تغییری در app.blade.php اعمال نشد", 'warn')

# ─────────────────────────────────────────────
#  ۳. modal.blade.php — رفع بسته شدن با کلیک بیرون
# ─────────────────────────────────────────────

def fix_modal_backdrop():
    """اطمینان از اینکه مودال‌های قدیمی با کلیک بیرون بسته می‌شوند"""
    candidates = [
        "resources/views/components/ui/modal.blade.php",
        "resources/views/components/modal.blade.php",
    ]
    fixed_any = False
    for rel in candidates:
        src = read_file(rel)
        if src is None: continue
        backup(rel)

        original = src

        # اگر backdrop با کلیک بسته می‌شود، skip کن
        if '@click="open = false"' in src or '@click.self="' in src or "@click=\"close" in src:
            log(f"{rel} از قبل درست است", 'warn'); continue

        # تلاش: اضافه کردن @click به backdrop
        # الگوی رایج: <div class="fixed inset-0 ..." بدون @click
        src = re.sub(
            r'(<div[^>]*class="[^"]*(?:backdrop|bg-black|fixed inset-0)[^"]*"[^>]*?)(>)',
            lambda m: m.group(1) + ' @click.self="open = false"' + m.group(2)
            if '@click' not in m.group(1) and 'wire:click' not in m.group(1)
            else m.group(1) + m.group(2),
            src
        )

        if src != original:
            write_file(rel, src)
            fixed_any = True

    if not fixed_any:
        log("فایل modal.blade.php پیدا نشد یا از قبل درست بود", 'warn')

# ─────────────────────────────────────────────
#  ۴. تشخیص: چاپ ساختار app.blade.php
# ─────────────────────────────────────────────

def diagnose_layout():
    print(f"\n{C.B}── گزارش ساختار app.blade.php ──{C.E}")
    rel = "resources/views/components/layouts/app.blade.php"
    src = read_file(rel)
    if src is None:
        log("app.blade.php پیدا نشد", 'err'); return

    lines = src.split('\n')
    print(f"{C.D}  کل خطوط: {len(lines)}{C.E}\n")

    # خطوطی که شامل عناصر ساختاری هستند
    keywords = ['<aside', '<main', '<nav', '<header', 'sg-sidebar', 'sidebar', 'mobile', 'fixed ', 'class="']
    for i, line in enumerate(lines, 1):
        for kw in keywords:
            if kw in line and len(line.strip()) > 3:
                preview = line.strip()[:100]
                print(f"  {i:4d}▕ {preview}")
                break

    print()

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    print(f"\n{C.B}══════════════════════════════════════════════════════{C.E}")
    print(f"{C.B}  ShopGun v2 — Phase 2: Layout & Navigation{C.E}")
    print(f"{C.B}══════════════════════════════════════════════════════{C.E}\n")

    if not PROJECT.exists():
        log("پروژه پیدا نشد", 'err'); sys.exit(1)

    log(f"بکاپ‌ها: {BACKUP}", 'info')

    if not confirm("ادامه می‌دهی؟"):
        log("لغو", 'warn'); sys.exit(0)

    BACKUP.mkdir(parents=True, exist_ok=True)

    # ۱. CSS
    print(f"\n{C.B}── [1/4] افزودن CSS فاز ۲{C.E}")
    add_css_block()

    # ۲. app.blade.php
    print(f"\n{C.B}── [2/4] پچ app.blade.php{C.E}")
    patch_app_blade()

    # ۳. modal backdrop
    print(f"\n{C.B}── [3/4] رفع بسته شدن مودال‌ها{C.E}")
    fix_modal_backdrop()

    # ۴. گزارش تشخیصی
    print(f"\n{C.B}── [4/4] گزارش ساختار{C.E}")
    diagnose_layout()

    print(f"{C.G}══════════════════════════════════════════════════════{C.E}")
    print(f"{C.G}  ✅ فاز ۲ اعمال شد{C.E}")
    print(f"{C.G}══════════════════════════════════════════════════════{C.E}")
    print(f"\nگام بعدی:")
    print(f"  {C.B}php artisan view:clear && php artisan optimize:clear{C.E}")
    print(f"  {C.B}npm run build{C.E}")
    print(f"  {C.B}php artisan serve{C.E}\n")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{C.Y}لغو{C.E}"); sys.exit(130)
