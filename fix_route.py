# -*- coding: utf-8 -*-
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

# ─── فیکس view-modal ───
vm = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm.exists():
    txt = vm.read_text(encoding='utf-8')

    # جایگزینی route قدیمی با جدید
    txt = txt.replace(
        "{{ route('certificates.download-html', ['certificate' => $certificate->id ?? 0]) }}",
        "/certificates/{{ $certificate->id ?? 0 }}/render"
    )
    txt = txt.replace(
        "route('certificates.download-html', ['certificate' => $certificate->id ?? 0])",
        "'/certificates/' + {{ $certificate->id ?? 0 }} + '/render'"
    )

    vm.write_text(txt, encoding='utf-8')
    print("[OK] view-modal fix")

# ─── حذف route قدیمی از web.php (اگه هست) ───
routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')
    if 'download-html' in txt:
        txt = re.sub(
            r"Route::get\([^)]*download-html[^)]*\)[^;]*;\s*",
            '',
            txt,
            flags=re.DOTALL
        )
        routes.write_text(txt, encoding='utf-8')
        print("[OK] route download-html حذف شد")

print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan route:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")