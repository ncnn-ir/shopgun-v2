# -*- coding: utf-8 -*-
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

# ═══════════════════════════════════════════════════════════════
# 1. حذف global-search از layout
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    # حذف هر خط global-search
    txt = re.sub(r'\s*<livewire:global-search[^>]*/>\s*', '\n    ', txt)
    txt = re.sub(r'\s*<livewire:global-search\s*/>\s*', '\n    ', txt)

    layout.write_text(txt, encoding='utf-8')
    print("[OK] layout - global-search حذف شد")

# ═══════════════════════════════════════════════════════════════
# 2. چک route certificates.render
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')
    
    # مطمئن شو render route هست
    if '/render/{certificate}' not in txt:
        print("[WARN] route render پیدا نشد")
    else:
        print("[OK] route render OK")
    
    # حذف route های تکراری certificate.print/render
    # چون ممکنه چند بار اضافه شده باشه
    matches = re.findall(r"Route::get\('/print'", txt)
    if len(matches) > 1:
        print(f"[WARN] {len(matches)} تا route /print هست — پاکسازی می‌کنیم")
        # نگه‌داشتن فقط آخرین
        # ساده: جایگزینی کل بلوک
        old_block = re.search(
            r"Route::prefix\('certificates'\)->name\('certificates\.'\)->group\(function \(\) \{.*?\n    \}\);",
            txt,
            flags=re.DOTALL
        )
        if old_block:
            new_block = r'''Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');

        Route::get('/render/{certificate}', function (\App\Models\Certificate $certificate) {
            $html = \App\Services\CertRenderer::renderHtml($certificate);
            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('render');

        Route::get('/print', function () {
            $ids = trim((string) request('ids', ''));
            $auto = request('auto', '0') === '1';
            $ids_arr = array_values(array_filter(array_map('intval', explode(',', $ids))));
            if (empty($ids_arr)) abort(404);
            $certs = \App\Models\Certificate::whereIn('id', $ids_arr)->orderBy('id')->get()->all();
            if (empty($certs)) abort(404);
            $cols = count($certs) === 1 ? 1 : 3;
            $html = \App\Services\CertRenderer::renderBatchHtml($certs, $cols);
            if ($auto) {
                $script = '<script>window.addEventListener("load",function(){setTimeout(function(){window.print()},900)})</script>';
                $html = str_replace('</body></html>', $script . '</body></html>', $html);
            }
            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('print');

        Route::get('/table', \App\Livewire\Tables\CertificatesTable::class)->name('table');
        Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });'''
            txt = txt[:old_block.start()] + new_block + txt[old_block.end():]
            routes.write_text(txt, encoding='utf-8')
            print("[OK] certificates routes پاکسازی شد")

# ═══════════════════════════════════════════════════════════════
# 3. چک view-modal — route اشتباه
# ═══════════════════════════════════════════════════════════════

vm = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm.exists():
    txt = vm.read_text(encoding='utf-8')
    
    # هر route قدیمی
    txt = txt.replace(
        "{{ route('certificates.download-html', ['certificate' => $certificate->id ?? 0]) }}",
        "/certificates/{{ $certificate->id ?? 0 }}/render"
    )
    txt = re.sub(
        r"route\('certificates\.download-html'[^)]*\)",
        "'/certificates/' + {{ $certificate->id ?? 0 }} + '/render'",
        txt
    )
    
    vm.write_text(txt, encoding='utf-8')
    print("[OK] view-modal route fix")

# ═══════════════════════════════════════════════════════════════
# 4. حذف GlobalSearch.php موقت
# ═══════════════════════════════════════════════════════════════

gs = ROOT / 'app' / 'Livewire' / 'GlobalSearch.php'
if gs.exists():
    gs.rename(str(gs) + '.disabled-' + str(int(time.time())))
    print("[OK] GlobalSearch.php غیرفعال شد")

print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan route:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")