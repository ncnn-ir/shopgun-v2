# -*- coding: utf-8 -*-
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. CertificatesTable.php — حذف header() که actions نداره
# ═══════════════════════════════════════════════════════════════

PG = r'''<?php

namespace App\Livewire\Tables;

use App\Models\Certificate;
use Illuminate\Database\Eloquent\Builder;
use PowerComponents\LivewirePowerGrid\Column;
use PowerComponents\LivewirePowerGrid\Facades\Filter;
use PowerComponents\LivewirePowerGrid\Facades\PowerGrid;
use PowerComponents\LivewirePowerGrid\PowerGridComponent;
use PowerComponents\LivewirePowerGrid\PowerGridFields;

final class CertificatesTable extends PowerGridComponent
{
    public string $tableName = 'certificates-table';
    public string $sortField = 'id';
    public string $sortDirection = 'desc';

    public function setUp(): array
    {
        return [
            PowerGrid::header()
                ->showSearchInput()
                ->showToggleColumns(),

            PowerGrid::footer()
                ->showPerPage(perPage: 20, perPageValues: [10, 20, 50, 100])
                ->showRecordCount(),
        ];
    }

    public function datasource(): Builder
    {
        return Certificate::query()->with(['customer']);
    }

    public function fields(): PowerGridFields
    {
        return PowerGrid::fields()
            ->add('id')
            ->add('code')
            ->add('image_html', function ($row) {
                if ($row->image_path) {
                    $url = e(asset('storage/' . $row->image_path));
                    return '<img src="' . $url . '" style="width:38px;height:38px;object-fit:cover;border-radius:8px;border:2px solid #ddd">';
                }
                return '<div style="width:38px;height:38px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px">💎</div>';
            })
            ->add('stone_name')
            ->add('metal')
            ->add('dimension', fn($row) => ($row->length_clean ?? '0') . '×' . ($row->width_clean ?? '0'))
            ->add('weight_clean')
            ->add('serial')
            ->add('issued_fmt', function ($row) {
                $d = $row->issued_at ?? $row->created_at;
                return $d ? \App\Support\PersianDate::format($d, 'Y/m/d H:i') : '—';
            })
            ->add('actions', function ($row) {
                $id = $row->id;
                $code = e($row->code);
                return '<div style="display:flex;gap:4px;justify-content:center">'
                    . '<button type="button" onclick="Livewire.dispatch(\'open-cert-view\', { certId: ' . $id . ' })" class="sg-action-btn view" title="نمایش">👁️</button>'
                    . '<button type="button" onclick="Livewire.dispatch(\'open-cert-form\', { certId: ' . $id . ' })" class="sg-action-btn edit" title="ویرایش">✏️</button>'
                    . '<button type="button" onclick="downloadCert(' . $id . ', \'' . $code . '\')" class="sg-action-btn" style="background:rgba(8,145,178,.15);color:#0891b2" title="دانلود">📥</button>'
                    . '<button type="button" onclick="window.open(\'/certificates/print?ids=' . $id . '&auto=1\',\'_blank\')" class="sg-action-btn" style="background:rgba(26,82,118,.15);color:#1a5276" title="چاپ">🖨️</button>'
                    . '</div>';
            });
    }

    public function columns(): array
    {
        return [
            Column::add()->title('کد')->field('code')->searchable()->sortable(),
            Column::add()->title('تصویر')->field('image_html'),
            Column::add()->title('سنگ')->field('stone_name')->searchable()->sortable(),
            Column::add()->title('فلز')->field('metal')->searchable(),
            Column::add()->title('ابعاد')->field('dimension'),
            Column::add()->title('وزن')->field('weight_clean')->sortable(),
            Column::add()->title('سریال')->field('serial')->searchable()->hidden(),
            Column::add()->title('تاریخ و ساعت')->field('issued_fmt')->sortable(),
            Column::action('actions')->title('عملیات'),
        ];
    }

    public function filters(): array
    {
        return [
            Filter::inputText('code')->operators(['contains', 'starts_with'])->placeholder('کد...'),
            Filter::inputText('stone_name')->operators(['contains', 'starts_with'])->placeholder('سنگ...'),
            Filter::inputText('metal')->operators(['contains', 'starts_with'])->placeholder('فلز...'),
            Filter::inputText('serial')->operators(['contains', 'starts_with'])->placeholder('سریال...'),
        ];
    }
}
'''

write('app/Livewire/Tables/CertificatesTable.php', PG)


# ═══════════════════════════════════════════════════════════════
# 2. VIEW برای جدول — با دکمه‌های هم‌اندازه بالای جدول
# ═══════════════════════════════════════════════════════════════

TABLE_PAGE = r'''<div style="padding:14px" dir="rtl">

    <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;flex-wrap:wrap">
        <h1 style="margin:0;font-size:20px;font-weight:700">💎 شناسنامه‌ها — جدول حرفه‌ای</h1>

        <div style="display:flex;gap:8px;flex-wrap:wrap">
            <a href="{{ route('certificates.index') }}" wire:navigate class="btn btn-outline btn-sm"
               style="padding:8px 14px;font-size:13px">← بازگشت</a>

            <button type="button" onclick="Livewire.dispatch('open-cert-form')"
                    class="btn btn-primary"
                    style="padding:8px 18px;font-size:13px;font-weight:700;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;cursor:pointer;height:38px">
                ➕ شناسنامه جدید
            </button>

            <button type="button" onclick="Livewire.dispatch('open-auto-cert')"
                    style="padding:8px 18px;font-size:13px;font-weight:700;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;cursor:pointer;height:38px">
                ⚡ صدور خودکار
            </button>

            <button type="button" onclick="printAllCerts()"
                    style="padding:8px 18px;font-size:13px;font-weight:700;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;cursor:pointer;height:38px">
                🖨️ چاپ همه
            </button>
        </div>
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
        <livewire:tables.certificates-table />
    </div>
</div>

<script>
function printAllCerts() {
    var ids = Array.from(document.querySelectorAll('table tbody tr'))
        .map(function(tr) {
            var btn = tr.querySelector('[onclick*="open-cert-view"]');
            if (!btn) return null;
            var m = btn.getAttribute('onclick').match(/certId:\s*(\d+)/);
            return m ? m[1] : null;
        })
        .filter(Boolean);

    if (!ids.length) { alert('شناسنامه‌ای در صفحه نیست'); return; }
    window.open('/certificates/print?ids=' + ids.join(',') + '&auto=1', '_blank');
}
</script>
'''

write('resources/views/livewire/tables/certificates-table-page.blade.php', TABLE_PAGE)


# ═══════════════════════════════════════════════════════════════
# 3. ROUTE — table به view جدید
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')
    # حذف route قدیمی table
    txt = re.sub(
        r"Route::get\('/table',\s*\\App\\Livewire\\Tables\\CertificatesTable::class\)->name\('table'\);\s*",
        "",
        txt
    )
    # اضافه کردن view wrapper
    marker = "Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');"
    new_route = """Route::get('/table', fn() => view('livewire.tables.certificates-table-page'))->name('table');

        """
    if marker in txt:
        txt = txt.replace(marker, new_route + marker, 1)
    routes.write_text(txt, encoding='utf-8')
    print("[OK] routes - table wrapper")


# ═══════════════════════════════════════════════════════════════
# 4. DOWNLOAD PNG — روش مستقیم بدون iframe
# ═══════════════════════════════════════════════════════════════

# اضافه به cert index
idx = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if idx.exists():
    txt = idx.read_text(encoding='utf-8')

    # حذف اسکریپت قدیمی
    txt = re.sub(
        r'<script[^>]*html2canvas[^>]*></script>\s*<script>.*?</script>\s*$',
        '',
        txt,
        flags=re.DOTALL
    )

    DOWNLOAD = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCert(id, code) {
    // استفاده از پنجره مخفی + html2canvas
    var w = window.open('', '_blank', 'width=900,height=900');
    if (!w) { alert('پاپ‌آپ بلاک شده — لطفا اجازه بده'); return; }

    // لود HTML کارت
    fetch('/certificates/' + id + '/render')
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        })
        .then(function(html) {
            w.document.open();
            w.document.write(html);
            w.document.close();

            // صبر کن چیزها لود بشن
            setTimeout(function() {
                var card = w.document.querySelector('.certificate');
                if (!card) {
                    w.close();
                    alert('کارت در HTML نبود');
                    return;
                }

                html2canvas(card, {
                    scale: 3,
                    backgroundColor: '#fffef9',
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    onclone: function(clonedDoc) {
                        var c = clonedDoc.querySelector('.certificate');
                        if (!c) return;
                        var els = [c].concat(Array.from(c.querySelectorAll('*')));
                        els.forEach(function(el) {
                            var cs = w.getComputedStyle(el);
                            ['color', 'backgroundColor', 'borderColor', 'fill', 'stroke'].forEach(function(prop) {
                                try {
                                    var val = cs[prop];
                                    if (val && val.indexOf('oklch') !== -1) el.style[prop] = '#999999';
                                } catch (e) {}
                            });
                        });
                    }
                }).then(function(canvas) {
                    var a = w.document.createElement('a');
                    a.download = 'cert-' + code + '.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                    setTimeout(function() { w.close(); }, 1500);
                }).catch(function(e) {
                    w.close();
                    alert('خطا: ' + e.message);
                });
            }, 2000);
        })
        .catch(function(e) {
            w.close();
            alert('خطا: ' + e.message);
        });
}
</script>
'''
    txt = txt + DOWNLOAD
    idx.write_text(txt, encoding='utf-8')
    print("[OK] cert index - download")


# ═══════════════════════════════════════════════════════════════
# 5. AUTO CREATE view — هم‌اندازه و مرتب
# ═══════════════════════════════════════════════════════════════

AUTO_VIEW = r'''<div>
@if($show)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:98;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:1000px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">⚡ صدور خودکار شناسنامه از SKU</h2>
            <button type="button" wire:click="close" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            {{-- ═══ کادر سرچ ═══ --}}
            <div style="margin-bottom:16px;padding:16px;background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:2px solid #16a34a;border-radius:12px">
                <label style="display:block;font-size:14px;font-weight:700;color:#15803d;margin-bottom:10px">
                    🔍 کد SKU محصول را از سایت وارد کن:
                </label>
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                    <input type="text" wire:model="sku"
                           wire:keydown.enter="searchBySku"
                           dir="ltr" autofocus
                           placeholder="مثلاً 35440"
                           style="flex:1;min-width:200px;padding:12px 16px;border:2px solid #cbd5e1;border-radius:10px;font-family:monospace;font-size:16px;background:#fff;box-sizing:border-box;outline:none">

                    <button type="button" wire:click="searchBySku"
                            wire:loading.attr="disabled"
                            style="padding:12px 28px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:14px;font-family:inherit;min-width:130px">
                        <span wire:loading.remove wire:target="searchBySku">⚡ جستجو</span>
                        <span wire:loading wire:target="searchBySku">⏳...</span>
                    </button>
                </div>

                @if($status)
                    <div style="margin-top:10px;font-size:13px;font-weight:700;color:{{ str_starts_with($status, '✅') ? '#15803d' : (str_starts_with($status, '⏳') ? '#0891b2' : '#dc2626') }}">
                        {{ $status }}
                    </div>
                @endif
            </div>

            @if(!empty($product))
                <div style="display:grid;grid-template-columns:1fr;gap:14px">

                    {{-- محصول --}}
                    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:12px;padding:14px;display:grid;grid-template-columns:120px 1fr;gap:14px">
                        @if(!empty($product['image']))
                            <img src="{{ $product['image'] }}" style="width:120px;height:120px;object-fit:cover;border-radius:10px;border:1px solid #e2e8f0">
                        @else
                            <div style="width:120px;height:120px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:48px">💎</div>
                        @endif
                        <div>
                            <div style="font-weight:700;font-size:15px;color:#1e293b;margin-bottom:8px">{{ $product['name'] }}</div>
                            <div style="font-size:12px;color:#64748b">
                                <b>SKU:</b> <span style="font-family:monospace" dir="ltr">{{ $product['sku'] }}</span>
                                &nbsp;|&nbsp; <b>قیمت:</b> {{ number_format($product['price']) }} تومان
                            </div>
                        </div>
                    </div>

                    {{-- فیلدهای قابل ویرایش --}}
                    <div style="background:#fff;border:1.5px solid #e2e8f0;border-radius:12px;padding:14px">
                        <h3 style="margin:0 0 12px;font-size:13px;font-weight:700;color:#1a5276;padding-bottom:8px;border-bottom:1px solid #e2e8f0">
                            ✏️ اطلاعات شناسنامه (قابل ویرایش)
                        </h3>
                        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px">
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">سنگ (فارسی)</label>
                                <input type="text" wire:model.live.debounce.300ms="stoneName" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">سنگ (انگلیسی)</label>
                                <input type="text" wire:model.live.debounce.300ms="stoneEn" dir="ltr" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">اصالت</label>
                                <input type="text" wire:model.live.debounce.300ms="stoneOrigin" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">فلز</label>
                                <input type="text" wire:model.live.debounce.300ms="metal" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">عیار</label>
                                <input type="text" wire:model.live.debounce.300ms="metalCarat" dir="ltr" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">طول (mm)</label>
                                <input type="number" wire:model.live.debounce.300ms="length" dir="ltr" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">عرض (mm)</label>
                                <input type="number" wire:model.live.debounce.300ms="width" dir="ltr" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">وزن (گرم)</label>
                                <input type="number" wire:model.live.debounce.300ms="weight" dir="ltr" step="0.01" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                        </div>
                    </div>

                    {{-- پیش‌نمایش --}}
                    <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border:1.5px solid #e2e8f0;border-radius:12px;padding:20px;display:flex;justify-content:center;align-items:center;min-height:350px;overflow:auto">
                        @if($previewHtml)
                            {!! $previewHtml !!}
                        @else
                            <div style="color:#94a3b8;font-size:13px">👁️ پیش‌نمایش کارت</div>
                        @endif
                    </div>
                </div>
            @endif
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px">
            <button type="button" wire:click="close"
                    style="padding:9px 20px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                انصراف
            </button>

            @if(!empty($product))
                <button type="button" wire:click="save"
                        wire:loading.attr="disabled"
                        style="padding:9px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    <span wire:loading.remove wire:target="save">✓ صدور شناسنامه</span>
                    <span wire:loading wire:target="save">⏳ در حال ذخیره...</span>
                </button>
            @endif
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/certificates/auto-create.blade.php', AUTO_VIEW)


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan route:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")