# -*- coding: utf-8 -*-
from pathlib import Path
import time

ROOT = Path(r'D:\prodo\shopgun-v2.2')

p = ROOT / 'app' / 'Livewire' / 'Certificates' / 'AutoCreate.php'
if p.exists():
    txt = p.read_text(encoding='utf-8')
    
    # حذف return redirect از متد void
    txt = txt.replace(
        "        return redirect()->route('certificates.index');\n",
        ""
    )
    # یا اگه یه همچین چیزی هست:
    txt = txt.replace(
        "        return redirect()->route('certificates.index');",
        ""
    )
    
    p.write_text(txt, encoding='utf-8')
    print("[OK] AutoCreate.php - return حذف شد")
else:
    print("[ERR] not found")

print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")