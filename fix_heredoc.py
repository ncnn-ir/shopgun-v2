# -*- coding: utf-8 -*-
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # ★ فیکس: تعریف متغیرها قبل از heredoc
    txt = txt.replace(
        '<col style="width:{$__c1 = (CertConfig::cols()[0] ?? 25)}%">',
        '<col style="width:{$c1}%">'
    )
    txt = txt.replace(
        '<col style="width:{$__c2 = (CertConfig::cols()[1] ?? 25)}%">',
        '<col style="width:{$c2}%">'
    )
    txt = txt.replace(
        '<col style="width:{$__c3 = (CertConfig::cols()[2] ?? 25)}%">',
        '<col style="width:{$c3}%">'
    )
    txt = txt.replace(
        '<col style="width:{$__c4 = (CertConfig::cols()[3] ?? 25)}%">',
        '<col style="width:{$c4}%">'
    )

    # اضافه کردن تعریف متغیرها قبل از $card = <<<HTML
    marker = "$card = <<<HTML"
    if marker in txt and '$c1 = ' not in txt:
        before = '''$_cols = CertConfig::cols();
        $c1 = $_cols[0] ?? 25;
        $c2 = $_cols[1] ?? 25;
        $c3 = $_cols[2] ?? 25;
        $c4 = $_cols[3] ?? 25;

        '''
        txt = txt.replace(marker, before + marker, 1)

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer.php - heredoc fixed")
else:
    print("[ERR] CertRenderer.php not found")

print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")