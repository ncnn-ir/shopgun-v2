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
# 1. ROUTES — ترتیب درست (مشکل دانلود از اینجا بود)
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')

    # حذف همه route های قدیمی certificates
    old_block = re.search(
        r"Route::prefix\('certificates'\)->name\('certificates\.'\)->group\(function \(\) \{.*?\n    \}\);",
        txt,
        flags=re.DOTALL
    )

    new_block = r'''Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');

        // ★ ترتیب مهم: مسیرهای خاص قبل از wildcard
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

        // ★ جدول حرفه‌ای PowerGrid
        Route::get('/table', \App\Livewire\Tables\CertificatesTable::class)->name('table');

        Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');

        // ★ wildcard آخر
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });'''

    if old_block:
        txt = txt[:old_block.start()] + new_block + txt[old_block.end():]
        routes.write_text(txt, encoding='utf-8')
        print("[OK] routes - certificates rebuilt")


# ═══════════════════════════════════════════════════════════════
# 2. POWERGRID TABLE — CertificatesTable
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
    public array $selected = [];

    public function setUp(): array
    {
        return [
            PowerGrid::header()
                ->showSearchInput()
                ->showToggleColumns()
                ->includeViewOnTop('livewire.tables.certificates-toolbar'),

            PowerGrid::footer()
                ->showPerPage(perPage: 20, perPageValues: [10, 20, 50, 100])
                ->showRecordCount(),

            PowerGrid::detail()
                ->view('livewire.tables.certificates-detail')
                ->showCollapseIcon(),
        ];
    }

    public function datasource(): Builder
    {
        return Certificate::query()->with(['customer']);
    }

    public function relationSearch(): array
    {
        return [
            'customer' => ['name', 'phone'],
        ];
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
                    . '</div>';
            });
    }

    public function columns(): array
    {
        return [
            Column::add()
                ->title('کد')
                ->field('code')
                ->searchable()
                ->sortable(),

            Column::add()
                ->title('تصویر')
                ->field('image_html'),

            Column::add()
                ->title('سنگ')
                ->field('stone_name')
                ->searchable()
                ->sortable(),

            Column::add()
                ->title('فلز')
                ->field('metal')
                ->searchable(),

            Column::add()
                ->title('ابعاد')
                ->field('dimension'),

            Column::add()
                ->title('وزن')
                ->field('weight_clean')
                ->sortable(),

            Column::add()
                ->title('سریال')
                ->field('serial')
                ->searchable()
                ->hidden(),

            Column::add()
                ->title('تاریخ و ساعت')
                ->field('issued_fmt')
                ->sortable(),

            Column::action('actions')->title('عملیات'),
        ];
    }

    public function filters(): array
    {
        return [
            Filter::inputText('code')
                ->operators(['contains', 'starts_with'])
                ->placeholder('کد...'),

            Filter::inputText('stone_name')
                ->operators(['contains', 'starts_with'])
                ->placeholder('نام سنگ...'),

            Filter::inputText('metal')
                ->operators(['contains', 'starts_with'])
                ->placeholder('فلز...'),

            Filter::inputText('serial')
                ->operators(['contains', 'starts_with'])
                ->placeholder('سریال...'),
        ];
    }

    public function header(): array
    {
        return [
            PowerGrid::actions()
                ->addButton('open-cert-form')
                ->slot('<span>➕ شناسنامه جدید</span>')
                ->class('btn btn-primary btn-sm'),

            PowerGrid::actions()
                ->addButton('open-auto-cert')
                ->slot('<span>⚡ صدور خودکار</span>')
                ->class('btn btn-success btn-sm'),
        ];
    }

    public function actionsFromView($row)
    {
        return view('livewire.tables.certificates-actions', ['row' => $row]);
    }
}
'''

write('app/Livewire/Tables/CertificatesTable.php', PG)


# ═══════════════════════════════════════════════════════════════
# 3. TOOLBAR VIEW
# ═══════════════════════════════════════════════════════════════

TOOLBAR = r'''<div style="display:flex;gap:6px;flex-wrap:wrap;padding:8px 12px;background:#f8fafc;border-bottom:1px solid #e2e8f0;align-items:center">
    <button type="button" onclick="Livewire.dispatch('open-cert-form')"
            class="btn btn-primary btn-sm">➕ شناسنامه جدید</button>

    <button type="button" onclick="Livewire.dispatch('open-auto-cert')"
            class="btn btn-success btn-sm"
            style="background:linear-gradient(135deg,#16a34a,#15803d);color:#fff">
        ⚡ صدور خودکار (از SKU سایت)
    </button>

    <div style="margin-right:auto;display:flex;gap:6px;align-items:center">
        <span style="font-size:11px;color:#64748b">🖨️ چاپ کل:</span>
        <button type="button" onclick="printAllCerts()"
                style="background:#1a5276;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-size:11px;font-weight:700;cursor:pointer">
            چاپ همه (A4)
        </button>
    </div>
</div>

<script>
function printAllCerts() {
    // همه شناسنامه‌های صفحه فعلی
    var ids = Array.from(document.querySelectorAll('[data-cert-row-id]'))
        .map(el => el.dataset.certRowId).filter(Boolean);
    if (!ids.length) { alert('شناسنامه‌ای نیست'); return; }
    window.open('{{ route("certificates.print") }}?ids=' + ids.join(',') + '&auto=1', '_blank');
}
</script>
'''

write('resources/views/livewire/tables/certificates-toolbar.blade.php', TOOLBAR)


# ═══════════════════════════════════════════════════════════════
# 4. DETAIL VIEW
# ═══════════════════════════════════════════════════════════════

DETAIL = r'''<div class="p-3 bg-base-200/50 rounded-lg" dir="rtl">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div>
            <div class="text-base-content/60">سریال:</div>
            <div class="font-mono font-bold" dir="ltr">{{ $row->serial ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">اصالت:</div>
            <div>{{ $row->stone_origin ?? '—' }} ({{ $row->stone_flag ?? '—' }})</div>
        </div>
        <div>
            <div class="text-base-content/60">عیار:</div>
            <div class="font-mono">{{ $row->metal_carat ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">مشتری:</div>
            <div>{{ $row->customer?->name ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">تصویر محصول:</div>
            <div>
                @if($row->image_path)
                    <a href="{{ asset('storage/' . $row->image_path) }}" target="_blank" class="link link-primary text-xs">مشاهده</a>
                @else
                    —
                @endif
            </div>
        </div>
        <div>
            <div class="text-base-content/60">لینک عمومی:</div>
            <div>
                <a href="{{ $row->public_url }}" target="_blank" class="link link-primary text-xs">{{ $row->code }}</a>
            </div>
        </div>
    </div>
</div>
'''

write('resources/views/livewire/tables/certificates-detail.blade.php', DETAIL)

ACTIONS = r'''<div style="display:flex;gap:4px">
    <button type="button" onclick="Livewire.dispatch('open-cert-view', { certId: {{ $row->id }} })" class="sg-action-btn view">👁️</button>
    <button type="button" onclick="Livewire.dispatch('open-cert-form', { certId: {{ $row->id }} })" class="sg-action-btn edit">✏️</button>
    <button type="button" onclick="window.open('{{ route("certificates.print") }}?ids={{ $row->id }}&auto=1','_blank')" class="sg-action-btn print">🖨️</button>
</div>
'''

write('resources/views/livewire/tables/certificates-actions.blade.php', ACTIONS)


# ═══════════════════════════════════════════════════════════════
# 5. AUTO CREATE — صدور خودکار از SKU
# ═══════════════════════════════════════════════════════════════

AUTO = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\AppSetting;
use App\Models\Certificate;
use App\Models\Customer;
use Illuminate\Support\Facades\Http;
use Livewire\Attributes\On;
use Livewire\Component;

class AutoCreate extends Component
{
    public bool $show = false;
    public string $sku = '';
    public string $status = '';
    public bool $searching = false;
    public array $product = [];

    // فیلدهای قابل ویرایش
    public string $stoneName   = '';
    public string $stoneEn     = '';
    public string $stoneOrigin = '';
    public string $stoneFlag   = 'ir';
    public string $metal       = 'نقره 925';
    public string $metalEn     = 'Silver 925';
    public string $metalCarat  = '925';
    public string $length      = '';
    public string $width       = '';
    public string $weight      = '';
    public string $brilliant   = '0';
    public ?int $customerId    = null;
    public string $previewHtml = '';

    #[On('open-auto-cert')]
    public function open(): void
    {
        $this->resetForm();
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->sku = '';
        $this->status = '';
        $this->product = [];
        $this->stoneName = '';
        $this->stoneEn = '';
        $this->stoneOrigin = '';
        $this->stoneFlag = 'ir';
        $this->metal = 'نقره 925';
        $this->metalEn = 'Silver 925';
        $this->metalCarat = '925';
        $this->length = '';
        $this->width = '';
        $this->weight = '';
        $this->brilliant = '0';
        $this->customerId = null;
        $this->previewHtml = '';
        $this->status = '';
    }

    public function searchBySku(): void
    {
        $sku = trim($this->sku);
        if ($sku === '') {
            $this->status = '❌ SKU را وارد کن';
            return;
        }

        $this->searching = true;
        $this->status = '⏳ در حال جستجو در سایت...';
        $this->product = [];

        try {
            $url    = trim((string) AppSetting::get('commerce_url', ''));
            $key    = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                $this->status = '❌ تنظیمات کامرس خالی است';
                $this->searching = false;
                return;
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            // ★ جستجوی دقیق SKU
            $r = Http::withBasicAuth($key, $secret)
                ->timeout(15)
                ->get("{$base}/products", ['sku' => $sku, 'per_page' => 1]);

            if (!$r->successful()) {
                $this->status = '❌ خطای HTTP ' . $r->status();
                $this->searching = false;
                return;
            }

            $json = $r->json();
            if (empty($json) || !is_array($json)) {
                $this->status = '❌ محصولی با SKU «' . e($sku) . '» پیدا نشد';
                $this->searching = false;
                return;
            }

            $p = $json[0];
            $this->product = [
                'id' => (int) ($p['id'] ?? 0),
                'sku' => (string) ($p['sku'] ?? ''),
                'name' => (string) ($p['name'] ?? ''),
                'price' => (float) ($p['price'] ?? 0),
                'image' => $p['images'][0]['src'] ?? null,
                'images' => array_map(fn($i) => $i['src'] ?? null, $p['images'] ?? []),
                'description' => strip_tags($p['short_description'] ?? $p['description'] ?? ''),
                'weight' => (float) ($p['weight'] ?? 0),
                'categories' => array_map(fn($c) => $c['name'] ?? '', $p['categories'] ?? []),
                'attributes' => array_map(fn($a) => ['name' => $a['name'] ?? '', 'options' => $a['options'] ?? []], $p['attributes'] ?? []),
            ];

            // ★ تلاش برای استخراج اطلاعات از نام/توضیحات
            $this->autoFillFromProduct();
            $this->updatePreview();

            $this->status = '✅ محصول پیدا شد: ' . $this->product['name'];

        } catch (\Throwable $e) {
            $this->status = '❌ ' . $e->getMessage();
        }

        $this->searching = false;
    }

    protected function autoFillFromProduct(): void
    {
        $name = $this->product['name'] ?? '';

        // وزن
        if (!empty($this->product['weight'])) {
            $this->weight = (string) $this->product['weight'];
        } else {
            // از نام بگیر
            if (preg_match('/([\d.]+)\s*(گرم|گرمى|gram|g)/u', $name, $m)) {
                $this->weight = $m[1];
            }
        }

        // سنگ
        $stoneKeywords = [
            'فیروزه' => ['فیروزه', 'Turquoise', 'ir'],
            'عقیق'   => ['عقیق', 'Agate', 'ye'],
            'الماس'  => ['الماس', 'Diamond', 'za'],
            'یاقوت'  => ['یاقوت', 'Ruby', 'mm'],
            'زمرد'   => ['زمرد', 'Emerald', 'co'],
            'توپاز'  => ['توپاز', 'Topaz', 'br'],
            'در نجف' => ['در نجف', 'Najaf', 'iq'],
            'آمیتیست'=> ['آمیتیست', 'Amethyst', 'br'],
        ];

        foreach ($stoneKeywords as $fa => $meta) {
            if (mb_strpos($name, $fa) !== false) {
                $this->stoneName = $fa;
                $this->stoneEn = $meta[1];
                $this->stoneFlag = $meta[2];
                break;
            }
        }

        // فلز
        if (mb_strpos($name, 'طلا') !== false) {
            $this->metal = 'طلا 18K';
            $this->metalEn = 'Gold 18K';
            $this->metalCarat = '750';
        } elseif (mb_strpos($name, 'نقره') !== false) {
            $this->metal = 'نقره 925';
            $this->metalEn = 'Silver 925';
            $this->metalCarat = '925';
        }

        // ابعاد
        if (preg_match('/(\d+)\s*[*×x]\s*(\d+)/', $name, $m)) {
            $this->length = $m[1];
            $this->width = $m[2];
        }
    }

    public function updated(): void
    {
        $this->updatePreview();
    }

    public function updatePreview(): void
    {
        if (empty($this->stoneName) && empty($this->stoneEn)) {
            $this->previewHtml = '';
            return;
        }

        try {
            $cert = new Certificate([
                'code' => '123456',
                'serial' => 'MJ-TEMP-' . rand(1000, 9999),
                'stone_name' => $this->stoneName ?: 'سنگ',
                'stone_en' => $this->stoneEn ?: '',
                'stone_origin' => $this->stoneOrigin,
                'stone_flag' => $this->stoneFlag,
                'metal' => $this->metal,
                'metal_en' => $this->metalEn,
                'metal_carat' => $this->metalCarat,
                'length' => (float) ($this->length ?: 0),
                'width' => (float) ($this->width ?: 0),
                'weight' => (float) ($this->weight ?: 0),
                'brilliant' => (int) ($this->brilliant ?: 0),
                'image_url' => $this->product['image'] ?? null,
                'issued_at' => now(),
            ]);
            $this->previewHtml = \App\Services\CertRenderer::renderCard($cert);
        } catch (\Throwable $e) {
            $this->previewHtml = '<div style="padding:20px;color:#dc2626">خطا: ' . htmlspecialchars($e->getMessage()) . '</div>';
        }
    }

    public function save(): void
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal' => 'required|string|max:255',
        ]);

        $code = Certificate::generateCode();
        $serial = Certificate::generateSerial($code, $this->stoneEn ?: $this->stoneName);

        $cert = Certificate::create([
            'code' => $code,
            'serial' => $serial,
            'sku' => $this->product['sku'] ?? null,
            'stone_name' => $this->stoneName,
            'stone_en' => $this->stoneEn,
            'stone_origin' => $this->stoneOrigin,
            'stone_flag' => $this->stoneFlag,
            'metal' => $this->metal,
            'metal_en' => $this->metalEn,
            'metal_carat' => $this->metalCarat,
            'length' => (float) ($this->length ?: 0),
            'width' => (float) ($this->width ?: 0),
            'weight' => (float) ($this->weight ?: 0),
            'brilliant' => (int) ($this->brilliant ?: 0),
            'customer_id' => $this->customerId ?: null,
            'issued_at' => now(),
        ]);

        // تصویر محصول رو ذخیره کن
        if (!empty($this->product['image'])) {
            try {
                $img = Http::timeout(20)->get($this->product['image'])->body();
                $fname = 'certificates/' . $code . '.jpg';
                \Illuminate\Support\Facades\Storage::disk('public')->put($fname, $img);
                $cert->update(['image_path' => $fname]);
            } catch (\Throwable $e) {}
        }

        session()->flash('success', "شناسنامه #{$code} صادر شد.");
        $this->close();
        $this->dispatch('notify', type: 'success', message: "شناسنامه #{$code} صادر شد");
        $this->dispatch('cert-saved');

        return redirect()->route('certificates.index');
    }

    public function render()
    {
        return view('livewire.certificates.auto-create');
    }
}
'''

write('app/Livewire/Certificates/AutoCreate.php', AUTO)


# ═══════════════════════════════════════════════════════════════
# 6. AUTO CREATE VIEW
# ═══════════════════════════════════════════════════════════════

AUTO_VIEW = r'''<div>
@if($show)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:98;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:1100px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">⚡ صدور خودکار شناسنامه از SKU</h2>
            <button type="button" wire:click="close" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            {{-- Search --}}
            <div style="margin-bottom:16px;padding:14px;background:#f0fdf4;border:2px solid #16a34a;border-radius:12px">
                <label style="display:block;font-size:13px;font-weight:700;color:#15803d;margin-bottom:8px">
                    🔍 کد SKU محصول را از سایت وارد کن:
                </label>
                <div style="display:flex;gap:8px">
                    <input type="text" wire:model="sku"
                           wire:keydown.enter="searchBySku"
                           dir="ltr" autofocus
                           placeholder="مثلاً 35440"
                           style="flex:1;padding:12px 14px;border:2px solid #cbd5e1;border-radius:10px;font-family:monospace;font-size:16px;background:#fff;box-sizing:border-box;outline:none">

                    <button type="button" wire:click="searchBySku"
                            wire:loading.attr="disabled"
                            style="padding:12px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:14px;font-family:inherit">
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

            {{-- Product Info --}}
            @if(!empty($product))
                <div style="display:grid;grid-template-columns:1fr;gap:14px;margin-bottom:16px">

                    {{-- محصول --}}
                    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:12px;padding:14px;display:grid;grid-template-columns:140px 1fr;gap:14px">
                        @if(!empty($product['image']))
                            <img src="{{ $product['image'] }}" style="width:140px;height:140px;object-fit:cover;border-radius:10px;border:1px solid #e2e8f0">
                        @else
                            <div style="width:140px;height:140px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:48px">💎</div>
                        @endif
                        <div>
                            <div style="font-weight:700;font-size:15px;color:#1e293b;margin-bottom:8px">{{ $product['name'] }}</div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
                                <div><b>SKU:</b> <span style="font-family:monospace" dir="ltr">{{ $product['sku'] }}</span></div>
                                <div><b>قیمت:</b> {{ number_format($product['price']) }} تومان</div>
                                @if(!empty($product['categories']))
                                    <div style="grid-column:1/-1"><b>دسته:</b> {{ implode('، ', $product['categories']) }}</div>
                                @endif
                            </div>
                        </div>
                    </div>

                    {{-- فیلدهای قابل ویرایش --}}
                    <div style="background:#fff;border:1.5px solid #e2e8f0;border-radius:12px;padding:14px">
                        <h3 style="margin:0 0 12px;font-size:13px;font-weight:700;color:#1a5276;padding-bottom:8px;border-bottom:1px solid #e2e8f0">
                            ✏️ اطلاعات شناسنامه (قابل ویرایش)
                        </h3>

                        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px">
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">سنگ (فارسی)</label>
                                <input type="text" wire:model.live.debounce.300ms="stoneName"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">سنگ (انگلیسی)</label>
                                <input type="text" wire:model.live.debounce.300ms="stoneEn" dir="ltr"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">اصالت</label>
                                <input type="text" wire:model.live.debounce.300ms="stoneOrigin"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">پرچم</label>
                                <select wire:model.live="stoneFlag" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                                    <option value="ir">🇮🇷 ایران</option>
                                    <option value="ye">🇾🇪 یمن</option>
                                    <option value="iq">🇮🇶 عراق</option>
                                    <option value="af">🇦🇫 افغانستان</option>
                                    <option value="za">🇿🇦 آفریقا</option>
                                    <option value="mm">🇲🇲 میانمار</option>
                                    <option value="co">🇨🇴 کلمبیا</option>
                                    <option value="lk">🇱🇰 سری‌لانکا</option>
                                    <option value="br">🇧🇷 برزیل</option>
                                </select>
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">فلز</label>
                                <input type="text" wire:model.live.debounce.300ms="metal"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">فلز (انگلیسی)</label>
                                <input type="text" wire:model.live.debounce.300ms="metalEn" dir="ltr"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">عیار</label>
                                <input type="text" wire:model.live.debounce.300ms="metalCarat" dir="ltr"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">طول (mm)</label>
                                <input type="number" wire:model.live.debounce.300ms="length" dir="ltr"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">عرض (mm)</label>
                                <input type="number" wire:model.live.debounce.300ms="width" dir="ltr"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                            <div>
                                <label style="font-size:10px;font-weight:700;color:#64748b;display:block;margin-bottom:3px">وزن (گرم)</label>
                                <input type="number" wire:model.live.debounce.300ms="weight" dir="ltr" step="0.01"
                                       style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace;box-sizing:border-box">
                            </div>
                        </div>
                    </div>

                    {{-- پیش‌نمایش --}}
                    <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border:1.5px solid #e2e8f0;border-radius:12px;padding:20px;display:flex;justify-content:center;align-items:center;min-height:400px;overflow:auto">
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
                    style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                انصراف
            </button>

            @if(!empty($product))
                <button type="button" wire:click="save"
                        wire:loading.attr="disabled"
                        style="padding:9px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    <span wire:loading.remove wire:target="save">✓ صدور شناسنامه</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            @endif
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/certificates/auto-create.blade.php', AUTO_VIEW)


# ═══════════════════════════════════════════════════════════════
# 7. LAYOUT — اضافه کردن AutoCreate modal
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    if '<livewire:certificates.auto-create' not in txt:
        marker = '<livewire:certificates.create'
        if marker in txt:
            txt = txt.replace(marker, '<livewire:certificates.auto-create :key="\'cam\'" />\n    ' + marker, 1)
            layout.write_text(txt, encoding='utf-8')
            print("[OK] layout - auto-create modal")


# ═══════════════════════════════════════════════════════════════
# 8. SIDEBAR — حذف شناسنامه جدید
# ═══════════════════════════════════════════════════════════════

sb = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'sidebar.blade.php'
if not sb.exists():
    sb = ROOT / 'resources' / 'views' / 'livewire' / 'components' / 'sidebar.blade.php'

if sb.exists():
    txt = sb.read_text(encoding='utf-8')
    # حذف آیتم شناسنامه جدید
    txt = re.sub(r"\[\s*'route'\s*=>\s*'certificates\.create'[^\]]*\],?\s*", '', txt)
    txt = re.sub(r"<li>\s*<a[^>]*certificates\.create[^<]*</a>\s*</li>", '', txt, flags=re.DOTALL)
    sb.write_text(txt, encoding='utf-8')
    print("[OK] sidebar - حذف شناسنامه جدید")


# ═══════════════════════════════════════════════════════════════
# 9. PRINT LAYOUT — 3 کارت از راست، ادامه در ردیف بعد
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # فیکس گرید
    txt = txt.replace(
        ".cert-print-grid{display:grid;grid-template-columns:repeat(' . \$cols . ',' . \$cw . 'cm);'\n            . 'column-gap:' . \$gap . 'cm;row-gap:2mm;justify-content:start;align-content:start;padding:0;width:100%;direction:rtl}'",
        ".cert-print-grid{display:flex;flex-wrap:wrap;gap:2mm;justify-content:flex-start;align-content:flex-start;direction:rtl;padding:0}"
    )

    # جایگزینی ساده‌تر با regex
    txt = re.sub(
        r"\.cert-print-grid\{[^}]*\}",
        ".cert-print-grid{display:flex;flex-wrap:wrap;gap:2mm;justify-content:flex-start;align-items:flex-start;direction:rtl;padding:2mm 0;width:100%}",
        txt
    )
    txt = re.sub(
        r"\.batch-card \.certificate\{[^}]*\}",
        ".batch-card{flex:0 0 auto;page-break-inside:avoid;break-inside:avoid;margin:0}"
        ".batch-card .certificate{box-shadow:none!important;transform:none!important;margin:0!important}",
        txt
    )

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer - چاپ راست‌چین")


# ═══════════════════════════════════════════════════════════════
# 10. CERT INDEX — لینک به PowerGrid
# ═══════════════════════════════════════════════════════════════

idx = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if idx.exists():
    txt = idx.read_text(encoding='utf-8')

    # حذف دکمه ویرایشگر
    txt = re.sub(
        r'<a href="\{\{ route\(\'certificates\.designer\'\) \}\}"[^<]*</a>\s*',
        '',
        txt
    )
    txt = re.sub(
        r'<a[^>]*certificates\.designer[^>]*>.*?</a>\s*',
        '',
        txt,
        flags=re.DOTALL
    )

    # اضافه کردن لینک به PowerGrid
    if 'certificates.table' not in txt:
        # پیدا کردن دکمه شناسنامه جدید
        marker = '<button type="button" onclick="Livewire.dispatch(\'open-cert-form\')"'
        if marker in txt:
            pg_btn = '''<a href="{{ route('certificates.table') }}" wire:navigate class="btn btn-secondary btn-sm" style="background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;text-decoration:none;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:700">📊 جدول حرفه‌ای</a>
            '''
            txt = txt.replace(marker, pg_btn + marker, 1)

    idx.write_text(txt, encoding='utf-8')
    print("[OK] cert index - لینک PowerGrid + حذف ویرایشگر")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan route:clear")
print("  php artisan serve")