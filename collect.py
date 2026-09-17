#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import os

ROOT = Path.home() / "shopgun-v2.2"
OUT = ROOT / "SHOPGUN-V2-ACTUAL-CODE.txt"

# فایل‌ها و پوشه‌هایی که برای بررسی معماری واقعی پروژه مهم هستند
TARGETS = [
    "composer.json",
    "composer.lock",
    "package.json",
    "vite.config.js",
    "tailwind.config.js",
    "postcss.config.js",
    "routes/web.php",
    "routes/api.php",

    "app/Models",
    "app/Livewire",
    "app/Services",
    "app/Support",
    "app/Providers",
    "app/Observers",
    "app/Http",
    "app/Console/Commands",
    "app/Actions",
    "app/Policies",

    "database/migrations",
    "database/seeders",

    "resources/views",
    "resources/css",
    "resources/js",

    "public/css",
    "public/js",

    "config/auth.php",
    "config/permission.php",
    "config/activitylog.php",
    "config/filesystems.php",
    "config/database.php",
    "config/session.php",
    "config/cache.php",

    ".env.example",
]

# پسوندهایی که ارزش خواندن دارند
TEXT_EXTENSIONS = {
    ".php",
    ".blade.php",
    ".js",
    ".ts",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".txt",
    ".xml",
    ".yml",
    ".yaml",
    ".env",
    ".example",
    ".html",
    ".vue",
    ".sql",
}

# فایل‌های حجیم/بی‌فایده را وارد نکن
EXCLUDE_DIRS = {
    "node_modules",
    "vendor",
    ".git",
    "storage/logs",
    "storage/framework/cache",
    "storage/framework/sessions",
    "storage/framework/views",
}

EXCLUDE_FILES = {
    "database.sqlite",
}

def is_excluded(path: Path):
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return True

    parts = rel.parts

    for excluded in EXCLUDE_DIRS:
        ex_parts = Path(excluded).parts
        if len(parts) >= len(ex_parts):
            for i in range(len(parts) - len(ex_parts) + 1):
                if parts[i:i+len(ex_parts)] == ex_parts:
                    return True

    if path.name in EXCLUDE_FILES:
        return True

    return False


def should_read(path: Path):
    if is_excluded(path):
        return False

    if path.name.endswith(".blade.php"):
        return True

    return path.suffix.lower() in TEXT_EXTENSIONS


def collect_files():
    files = []

    for target in TARGETS:
        path = ROOT / target

        if not path.exists():
            continue

        if path.is_file():
            if should_read(path):
                files.append(path)
            continue

        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file() and should_read(p):
                    files.append(p)

    # حذف تکراری‌ها
    files = sorted(set(files), key=lambda x: str(x).lower())

    return files


def read_file(path: Path):
    try:
        # UTF-8
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except Exception:
            return "[خطا: فایل UTF-8 قابل خواندن نیست]"
    except Exception as e:
        return f"[خطا در خواندن فایل: {e}]"


def human_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.2f} MB"


def main():
    print("=" * 70)
    print("SHOPGUN V2 - ACTUAL CODE COLLECTOR")
    print("=" * 70)

    if not ROOT.exists():
        print()
        print("❌ پروژه پیدا نشد:")
        print(ROOT)
        print()
        print("اگر مسیر پروژه متفاوت است، مقدار ROOT را اصلاح کن.")
        return

    files = collect_files()

    print(f"📁 پروژه: {ROOT}")
    print(f"📄 تعداد فایل‌های انتخاب‌شده: {len(files)}")
    print(f"📝 خروجی: {OUT}")
    print()

    with OUT.open("w", encoding="utf-8") as out:

        out.write("=" * 100 + "\n")
        out.write("SHOPGUN V2 - ACTUAL PROJECT CODE HANDOVER\n")
        out.write("=" * 100 + "\n\n")

        out.write("این فایل توسط اسکریپت خودکار از پروژه واقعی ساخته شده است.\n")
        out.write("مبنای بررسی باید فایل‌های واقعی این خروجی باشد، نه حدس یا سندهای قبلی.\n\n")

        out.write(f"Project Root: {ROOT}\n")
        out.write(
            f"Generated At: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        out.write(f"Collected Files: {len(files)}\n\n")

        out.write("=" * 100 + "\n")
        out.write("PROJECT FILE INVENTORY\n")
        out.write("=" * 100 + "\n\n")

        for i, path in enumerate(files, 1):
            rel = path.relative_to(ROOT)

            try:
                size = human_size(path.stat().st_size)
            except Exception:
                size = "نامشخص"

            out.write(
                f"{i:04d}. {rel}    [{size}]\n"
            )

        out.write("\n\n")

        out.write("=" * 100 + "\n")
        out.write("ACTUAL FILE CONTENTS\n")
        out.write("=" * 100 + "\n\n")

        for i, path in enumerate(files, 1):
            rel = path.relative_to(ROOT)
            content = read_file(path)

            out.write("\n")
            out.write("#" * 100 + "\n")
            out.write(f"# FILE {i:04d}: {rel}\n")
            out.write("#" * 100 + "\n\n")

            out.write(content)

            if not content.endswith("\n"):
                out.write("\n")

            out.write("\n")
            out.write("#" * 100 + "\n")
            out.write(f"# END FILE: {rel}\n")
            out.write("#" * 100 + "\n\n")

        out.write("\n")
        out.write("=" * 100 + "\n")
        out.write("END OF ACTUAL PROJECT CODE\n")
        out.write("=" * 100 + "\n")

    print("✅ انجام شد.")
    print()
    print(f"📄 فایل ساخته شد:")
    print(OUT)
    print()
    print(f"📦 حجم فایل: {human_size(OUT.stat().st_size)}")
    print()
    print("حالا این فایل را در همین گفتگو آپلود کن.")
    print("بعد از دریافت آن، کد واقعی پروژه را بررسی می‌کنم و پارت بعدی را")
    print("بر اساس وضعیت واقعی پروژه می‌سازم؛ نه بر اساس HANDOVER قبلی.")
    print("=" * 70)


if __name__ == "__main__":
    main()
