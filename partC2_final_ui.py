from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"
if not PROJECT.exists():
    raise SystemExit("❌ پروژه پیدا نشد")

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"{'🔁' if existed else '✅'} {rel}")

print("═" * 60)
print("🎨 Part C-2 — UI نهایی + اتصال Designer به Certificate")
print("═" * 60)
print()

# =========================================================
# ۱. CertSetting Service
# =========================================================

write_file("app/Support/CertConfig.php", r"""
<?php

namespace App\Support;

use App\Models\CertSetting;

class CertConfig
{
    protected static ?array $cache = null;

    protected static function load(): void
    {
        if (self::$cache !== null) return;

        self::$cache = [];
        foreach (CertSetting::all() as $s) {
            $v = $s->value;
            if (is_string($v)) {
                if (str_starts_with($v, '{') || str_starts_with($v, '[')) {
                    $v = json_decode($v, true) ?? $v;
                } elseif (is_numeric($v)) {
                    $v = $v + 0;
                } elseif ($v === 'true') {
                    $v = true;
                } elseif ($v === 'false') {
                    $v = false;
                }
            }
            self::$cache[$s->key] = $v;
        }
    }

    public static function get(string $key, $default = null)
    {
        self::load();
        return self::$cache[$key] ?? $default;
    }

    public static function set(string $key, $value): void
    {
        CertSetting::set($key, $value, 'certificate');
        self::$cache = null;
    }

    public static function all(): array
    {
        self::load();
        return self::$cache;
    }

    public static function sizes(): array
    {
        return [
            'width'            => (float) self::get('cert.width', 6.5),
            'height'           => (float) self::get('cert.height', 6.5),
            'img_w'            => (int)   self::get('cert.img_w', 120),
            'img_h'            => (int)   self::get('cert.img_h', 120),
            'qr_size'          => (int)   self::get('cert.qr_size', 40),
            'logo_w'           => (int)   self::get('cert.logo_w', 28),
            'logo_h'           => (int)   self::get('cert.logo_h', 22),
            'code_font'        => (int)   self::get('cert.code_font', 11),
            'title_font'       => (int)   self::get('cert.title_font', 20),
            'desc_font'        => (int)   self::get('cert.desc_font', 7),
            'table_label_font' => (int)   self::get('cert.table_label_font', 8),
            'table_value_font' => (int)   self::get('cert.table_value_font', 8),
        ];
    }

    public static function assets(): array
    {
        return [
            'bg_image'   => self::get('cert.bg_image', ''),
            'desc_image' => self::get('cert.desc_image', ''),
            'logo_image' => self::get('cert.logo_image', ''),
        ];
    }

    public static function hideDesc(): bool
    {
        return (bool) self::get('cert.hide_desc', false);
    }
}
""")

# =========================================================
# ۲. Certificate Model — با Design Data + QR
# =========================================================

cert_model = PROJECT / "app/Models/Certificate.php"
if cert_model.exists():
    content = cert_model.read_text(encoding="utf-8")

    # افزودن متدهای کمکی در صورت نبود
    if "public function getDesignOrDefaultAttribute" not in content:
        content = content.replace(
            "    public function getQrUrlAttribute(): string\n    {\n        return 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=1&data='\n            . urlencode($this->public_url);\n    }",
            """    public function getQrUrlAttribute(): string
    {
        return 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=1&data='
            . urlencode($this->public_url);
    }

    public function getDesignOrDefaultAttribute(): array
    {
        if (! empty($this->design_data) && is_array($this->design_data)) {
            return $this->design_data;
        }

        return [
            'version' => '1.0',
            'elements' => [
                ['id' => 'title',  'type' => 'text', 'text' => 'Certificate',           'x' => 180, 'y' => 30,  'fontSize' => 28, 'fill' => '#6b4423', 'fontWeight' => 'bold'],
                ['id' => 'stone',  'type' => 'text', 'text' => '{stoneEn}',             'x' => 160, 'y' => 90,  'fontSize' => 20, 'fill' => '#0369a1', 'fontWeight' => 'bold'],
                ['id' => 'metal',  'type' => 'text', 'text' => '{metal} ({carat})',     'x' => 160, 'y' => 130, 'fontSize' => 14, 'fill' => '#334155'],
                ['id' => 'size',   'type' => 'text', 'text' => '{length}×{width} mm',   'x' => 160, 'y' => 165, 'fontSize' => 12, 'fill' => '#334155'],
                ['id' => 'weight', 'type' => 'text', 'text' => 'Weight: {weight} gr',   'x' => 160, 'y' => 195, 'fontSize' => 12, 'fill' => '#334155'],
                ['id' => 'code',   'type' => 'text', 'text' => 'Code: {code}',          'x' => 160, 'y' => 230, 'fontSize' => 14, 'fill' => '#b45309', 'fontWeight' => 'bold'],
                ['id' => 'qr',     'type' => 'qr',   'text' => '',                       'x' => 420, 'y' => 400, 'size' => 100],
            ],
        ];
    }"""
        )
        cert_model.write_text(content, encoding="utf-8")
        print("🔁 app/Models/Certificate.php (افزودن design_or_default)")
    else:
        print("✅ app/Models/Certificate.php (بدون تغییر)")

# =========================================================
# ۳. Designer — همگام با Certificate
# =========================================================

write_file("app/Livewire/Certificates/Designer.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Support\CertConfig;
use Livewire\Component;

class Designer extends Component
{
    public Certificate $certificate;
    public array $design = [];
    public array $sizes = [];
    public array $assets = [];
    public bool $hideDesc = false;

    public function mount(?int $certificate = null): void
    {
        if ($certificate) {
            $this->certificate = Certificate::findOrFail($certificate);
        } else {
            $first = Certificate::first();
            if ($first) {
                $this->certificate = $first;
            } else {
                $this->certificate = new Certificate([
                    'code' => '000000', 'serial' => 'MJ-DESIGN',
                    'stone_name' => 'فیروزه عجمی', 'stone_en' => 'Turquoise Ajami',
                    'stone_origin' => 'نیشابور', 'stone_flag' => 'ir',
                    'metal' => 'نقره 925', 'metal_en' => 'Silver 925', 'metal_carat' => '925',
                    'length' => 13, 'width' => 9, 'weight' => 1.28, 'brilliant' => 5,
                ]);
            }
        }

        $this->design  = $this->certificate->design_or_default;
        $this->sizes   = CertConfig::sizes();
        $this->assets  = CertConfig::assets();
        $this->hideDesc = CertConfig::hideDesc();
    }

    public function save(array $design): void
    {
        $this->design = $design;
        if ($this->certificate->exists) {
            $this->certificate->update(['design_data' => $design]);
        }
        CertConfig::set('cert.design_data', $design);
        session()->flash('success', 'طراحی ذخیره شد');
    }

    public function saveSizes(array $sizes): void
    {
        foreach ($sizes as $k => $v) {
            CertConfig::set('cert.' . $k, $v);
        }
        $this->sizes = CertConfig::sizes();
        session()->flash('success', 'سایزها ذخیره شد');
    }

    public function saveAssets(array $assets): void
    {
        foreach ($assets as $k => $v) {
            CertConfig::set('cert.' . $k, $v);
        }
        $this->assets = CertConfig::assets();
        session()->flash('success', 'تصاویر ذخیره شد');
    }

    public function toggleHideDesc(): void
    {
        $this->hideDesc = ! $this->hideDesc;
        CertConfig::set('cert.hide_desc', $this->hideDesc ? 'true' : 'false');
    }

    public function render()
    {
        return view('livewire.certificates.designer')
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/certificates/designer.blade.php", r"""
<div class="p-4 md:p-6 max-w-7xl mx-auto">

    @if (session('success'))
        <div class="alert alert-success mb-4 text-sm"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-3">
            <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
            <div>
                <h1 class="text-xl md:text-2xl font-bold">🎨 ویرایشگر شناسنامه</h1>
                <div class="text-xs text-base-content/60 mt-0.5">
                    {{ $certificate->code }} — {{ $certificate->stone_name }}
                </div>
            </div>
        </div>
        <div class="flex gap-2">
            <button onclick="designerExportPng()" class="btn btn-secondary btn-sm">📸 PNG</button>
            <button onclick="designerPrint()" class="btn btn-info btn-sm">🖨️ چاپ</button>
            <button onclick="designerSave()" class="btn btn-primary btn-sm">💾 ذخیره</button>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">

        {{-- ابزار چپ --}}
        <div class="card bg-base-100 shadow border lg:order-1 order-2">
            <div class="card-body p-3">

                {{-- تب‌ها --}}
                <div role="tablist" class="tabs tabs-boxed tabs-sm mb-3">
                    <a role="tab" class="tab tab-active" onclick="showTab('elements', this)">🎨 عناصر</a>
                    <a role="tab" class="tab" onclick="showTab('sizes', this)">📐 سایز</a>
                    <a role="tab" class="tab" onclick="showTab('assets', this)">🖼️ تصاویر</a>
                </div>

                {{-- تب عناصر --}}
                <div id="tab-elements">
                    <div class="space-y-2">
                        <button onclick="designerAddText('متن جدید')" class="btn btn-outline btn-sm w-full justify-start">📝 متن جدید</button>
                        <button onclick="designerAddPlaceholder('{stoneEn}')" class="btn btn-outline btn-sm w-full justify-start">💎 سنگ</button>
                        <button onclick="designerAddPlaceholder('{metal}')" class="btn btn-outline btn-sm w-full justify-start">⚙️ فلز</button>
                        <button onclick="designerAddPlaceholder('{weight} gr')" class="btn btn-outline btn-sm w-full justify-start">⚖️ وزن</button>
                        <button onclick="designerAddPlaceholder('{length}×{width}')" class="btn btn-outline btn-sm w-full justify-start">📐 ابعاد</button>
                        <button onclick="designerAddPlaceholder('#{code}')" class="btn btn-outline btn-sm w-full justify-start">🔢 کد</button>
                        <button onclick="designerAddQR()" class="btn btn-outline btn-sm w-full justify-start">📱 QR کد</button>
                    </div>

                    <div class="divider my-2 text-xs">ویرایش</div>

                    <div class="space-y-2">
                        <button onclick="designerDelete()" class="btn btn-error btn-sm w-full">🗑️ حذف</button>
                        <button onclick="designerBringForward()" class="btn btn-ghost btn-sm w-full">⬆️ بالا</button>
                        <button onclick="designerSendBackward()" class="btn btn-ghost btn-sm w-full">⬇️ پایین</button>
                    </div>

                    <div class="divider my-2 text-xs">ویژگی‌ها</div>
                    <div id="propsPanel" class="text-xs space-y-2 text-base-content/60">
                        شیئی انتخاب کن
                    </div>
                </div>

                {{-- تب سایز --}}
                <div id="tab-sizes" class="hidden">
                    <div class="space-y-2 text-xs">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="label-text font-bold">عرض (cm)</label>
                                <input type="number" id="sz-width" step="0.1" value="{{ $sizes['width'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                            <div>
                                <label class="label-text font-bold">ارتفاع (cm)</label>
                                <input type="number" id="sz-height" step="0.1" value="{{ $sizes['height'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="label-text font-bold">تصویر - عرض</label>
                                <input type="number" id="sz-img_w" value="{{ $sizes['img_w'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                            <div>
                                <label class="label-text font-bold">تصویر - ارتفاع</label>
                                <input type="number" id="sz-img_h" value="{{ $sizes['img_h'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="label-text font-bold">QR</label>
                                <input type="number" id="sz-qr_size" value="{{ $sizes['qr_size'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                            <div>
                                <label class="label-text font-bold">لوگو - عرض</label>
                                <input type="number" id="sz-logo_w" value="{{ $sizes['logo_w'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="label-text font-bold">لوگو - ارتفاع</label>
                                <input type="number" id="sz-logo_h" value="{{ $sizes['logo_h'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                            <div>
                                <label class="label-text font-bold">فونت کد</label>
                                <input type="number" id="sz-code_font" value="{{ $sizes['code_font'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="label-text font-bold">فونت عنوان</label>
                                <input type="number" id="sz-title_font" value="{{ $sizes['title_font'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                            <div>
                                <label class="label-text font-bold">فونت توضیحات</label>
                                <input type="number" id="sz-desc_font" value="{{ $sizes['desc_font'] }}" class="input input-bordered input-xs w-full" />
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="label-text font-bold">جدول - عنوان</label>
                                <input type="number" id="sz-table_label_font" value="{{ $sizes['table_label_font'] }}" step="0.5" class="input input-bordered input-xs w-full" />
                            </div>
                            <div>
                                <label class="label-text font-bold">جدول - مقدار</label>
                                <input type="number" id="sz-table_value_font" value="{{ $sizes['table_value_font'] }}" step="0.5" class="input input-bordered input-xs w-full" />
                            </div>
                        </div>
                        <button onclick="designerSaveSizes()" class="btn btn-primary btn-xs w-full mt-2">💾 ذخیره سایزها</button>
                    </div>
                </div>

                {{-- تب تصاویر --}}
                <div id="tab-assets" class="hidden">
                    <div class="space-y-3 text-xs">
                        <div>
                            <label class="label-text font-bold block mb-1">🖼️ پس‌زمینه</label>
                            <input type="file" id="asset-bg" accept="image/*" class="file-input file-input-bordered file-input-xs w-full" onchange="uploadAsset('bg_image', this)" />
                            @if($assets['bg_image'])
                                <img src="{{ $assets['bg_image'] }}" class="mt-2 w-full h-16 object-cover rounded border" />
                            @endif
                        </div>
                        <div>
                            <label class="label-text font-bold block mb-1">📝 تصویر توضیحات</label>
                            <input type="file" id="asset-desc" accept="image/*" class="file-input file-input-bordered file-input-xs w-full" onchange="uploadAsset('desc_image', this)" />
                            @if($assets['desc_image'])
                                <img src="{{ $assets['desc_image'] }}" class="mt-2 w-full h-16 object-cover rounded border" />
                            @endif
                        </div>
                        <div>
                            <label class="label-text font-bold block mb-1">🏷️ آرم/لوگو</label>
                            <input type="file" id="asset-logo" accept="image/*" class="file-input file-input-bordered file-input-xs w-full" onchange="uploadAsset('logo_image', this)" />
                            @if($assets['logo_image'])
                                <img src="{{ $assets['logo_image'] }}" class="mt-2 w-full h-16 object-contain bg-base-200 rounded border" />
                            @endif
                        </div>
                        <label class="cursor-pointer flex items-center gap-2 p-2 bg-base-200 rounded">
                            <input type="checkbox" wire:click="toggleHideDesc" {{ $hideDesc ? 'checked' : '' }} class="checkbox checkbox-xs" />
                            <span class="text-xs font-bold">مخفی کردن توضیحات</span>
                        </label>
                    </div>
                </div>

            </div>
        </div>

        {{-- بوم --}}
        <div class="card bg-base-100 shadow border lg:col-span-3 lg:order-2 order-1">
            <div class="card-body p-3">
                <div class="bg-base-200 rounded-lg p-4 flex justify-center overflow-auto min-h-[500px]">
                    <canvas id="designerCanvas" width="600" height="600"
                            class="border-4 border-white shadow-xl bg-white rounded-lg"></canvas>
                </div>
                <div class="text-xs text-base-content/60 text-center mt-2">
                    🖱 عناصر رو بکش، گوشه سبز = تغییر سایز
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
<script>
let canvas;
let certData = {
    code:      @json($certificate->code ?? ''),
    stoneEn:   @json($certificate->stone_en ?? ''),
    stoneName: @json($certificate->stone_name ?? ''),
    metal:     @json($certificate->metal ?? ''),
    metalEn:   @json($certificate->metal_en ?? ''),
    carat:     @json($certificate->metal_carat ?? ''),
    weight:    @json($certificate->weight ?? ''),
    length:    @json($certificate->length ?? ''),
    width:     @json($certificate->width ?? ''),
    brilliant: @json($certificate->brilliant ?? ''),
};
const designData = @json($design);

document.addEventListener('DOMContentLoaded', () => {
    canvas = new fabric.Canvas('designerCanvas', { backgroundColor: '#fffef9' });

    if (designData && designData.elements && designData.elements.length) {
        designData.elements.forEach(el => {
            if (el.type === 'text') addText(el.text, el.x, el.y, el);
            else if (el.type === 'qr') addQR(el.x, el.y, el.size || 100);
        });
    }

    canvas.on('selection:created', updatePropsPanel);
    canvas.on('selection:updated', updatePropsPanel);
    canvas.on('selection:cleared', () => {
        document.getElementById('propsPanel').innerHTML = 'شیئی انتخاب کن';
    });
});

function showTab(name, btn) {
    document.querySelectorAll('#tab-elements, #tab-sizes, #tab-assets').forEach(t => t.classList.add('hidden'));
    document.getElementById('tab-' + name).classList.remove('hidden');
    btn.parentNode.querySelectorAll('.tab').forEach(t => t.classList.remove('tab-active'));
    btn.classList.add('tab-active');
}

function replacePlaceholders(text) {
    return text
        .replace(/{code}/g, certData.code)
        .replace(/{stoneEn}/g, certData.stoneEn)
        .replace(/{stoneName}/g, certData.stoneName)
        .replace(/{metal}/g, certData.metal)
        .replace(/{metalEn}/g, certData.metalEn)
        .replace(/{carat}/g, certData.carat)
        .replace(/{weight}/g, certData.weight)
        .replace(/{length}/g, certData.length)
        .replace(/{width}/g, certData.width)
        .replace(/{brilliant}/g, certData.brilliant);
}

function addText(text, x, y, opts = {}) {
    const displayed = replacePlaceholders(text);
    const t = new fabric.Text(displayed, Object.assign({
        left: x, top: y, fontSize: 18, fill: '#334155',
        fontFamily: 'Tahoma, sans-serif', direction: 'rtl',
    }, opts));
    t._rawText = text;
    canvas.add(t);
    canvas.setActiveObject(t);
    canvas.renderAll();
}

function designerAddText(text) { addText(text, 100, 100, { fontSize: 16 }); }
function designerAddPlaceholder(ph) { addText(ph, 100, 150, { fontSize: 14, fill: '#0369a1' }); }

function addQR(x = 400, y = 400, size = 100) {
    const url = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + encodeURIComponent('https://mashahirid.ir/Q/' + certData.code);
    fabric.Image.fromURL(url, (img) => {
        img.scaleToWidth(size);
        img.set({ left: x, top: y });
        canvas.add(img);
        canvas.setActiveObject(img);
        canvas.renderAll();
    }, { crossOrigin: 'anonymous' });
}

function designerAddQR() { addQR(); }

function designerDelete() {
    const a = canvas.getActiveObjects();
    if (a.length) {
        a.forEach(o => canvas.remove(o));
        canvas.discardActiveObject();
        canvas.renderAll();
    }
}

function designerBringForward() { const a = canvas.getActiveObject(); if (a) canvas.bringForward(a); }
function designerSendBackward() { const a = canvas.getActiveObject(); if (a) canvas.sendBackwards(a); }

function updatePropsPanel() {
    const obj = canvas.getActiveObject();
    if (!obj) return;

    const panel = document.getElementById('propsPanel');
    panel.innerHTML = `
        <div><strong>${obj.type}</strong></div>
        <div>X: ${Math.round(obj.left)} · Y: ${Math.round(obj.top)}</div>
        ${obj.type === 'text' ? `
            <label class="block mt-2 text-base-content/80">متن</label>
            <input type="text" id="propText" value="${obj._rawText || obj.text}" class="input input-bordered input-xs w-full" />
            <label class="block mt-2 text-base-content/80">فونت</label>
            <input type="number" id="propFontSize" value="${obj.fontSize || 14}" class="input input-bordered input-xs w-full" />
            <label class="block mt-2 text-base-content/80">رنگ</label>
            <input type="color" id="propFill" value="${obj.fill || '#334155'}" class="w-full h-8 rounded" />
            <button onclick="applyTextProps()" class="btn btn-primary btn-xs w-full mt-2">اعمال</button>
        ` : ''}
    `;
}

function applyTextProps() {
    const obj = canvas.getActiveObject();
    if (!obj || obj.type !== 'text') return;
    const rawText = document.getElementById('propText').value;
    obj._rawText = rawText;
    obj.set('text', replacePlaceholders(rawText));
    obj.set('fontSize', parseInt(document.getElementById('propFontSize').value) || 14);
    obj.set('fill', document.getElementById('propFill').value);
    canvas.renderAll();
}

function designerSave() {
    const elements = [];
    canvas.getObjects().forEach(obj => {
        if (obj.type === 'text') {
            elements.push({
                id: 'txt_' + Math.random().toString(36).substr(2, 6),
                type: 'text',
                text: obj._rawText || obj.text,
                x: Math.round(obj.left), y: Math.round(obj.top),
                fontSize: obj.fontSize, fill: obj.fill,
                fontWeight: obj.fontWeight || 'normal',
            });
        } else if (obj.type === 'image') {
            elements.push({
                id: 'img_' + Math.random().toString(36).substr(2, 6),
                type: 'qr',
                x: Math.round(obj.left), y: Math.round(obj.top),
                size: Math.round(obj.width * (obj.scaleX || 1)),
            });
        }
    });

    @this.call('save', { version: '1.0', elements: elements });
}

function designerSaveSizes() {
    const sizes = {};
    ['width','height','img_w','img_h','qr_size','logo_w','logo_h','code_font','title_font','desc_font','table_label_font','table_value_font'].forEach(k => {
        const el = document.getElementById('sz-' + k);
        if (el) sizes[k] = parseFloat(el.value) || 0;
    });
    @this.call('saveSizes', sizes);
}

function uploadAsset(key, input) {
    if (!input.files || !input.files[0]) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        const dataUrl = e.target.result;
        const assets = {};
        assets[key] = dataUrl;
        @this.call('saveAssets', assets);
    };
    reader.readAsDataURL(input.files[0]);
}

function designerExportPng() {
    const dataURL = canvas.toDataURL({ format: 'png', multiplier: 3 });
    const link = document.createElement('a');
    link.download = 'certificate-' + certData.code + '.png';
    link.href = dataURL;
    link.click();
}

function designerPrint() {
    const dataURL = canvas.toDataURL({ format: 'png', multiplier: 3 });
    const w = window.open('');
    w.document.write(`
        <html dir="rtl"><head><title>چاپ</title>
        <style>@page{size:A4;margin:10mm}body{margin:0;display:flex;justify-content:center;padding:20px}img{max-width:100%}</style>
        </head><body onload="window.print();setTimeout(()=>window.close(),500)"><img src="${dataURL}"></body></html>
    `);
    w.document.close();
}
</script>
""")

print()
print("═" * 60)
print("✅ Part C-2 (بخش ۱) — Designer با تنظیمات کامل")
print("═" * 60)
print()
print("📌 برای ادامه، اسکریپت رو اجرا کن و بعد بگو 'Part C-2 ادامه'")
print()
