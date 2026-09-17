# -*- coding: utf-8 -*-
"""ShopGun V2 - Certificate Fix: Print + Sliders + Modal"""

import sys
from pathlib import Path

ROOT = Path(r'D:\prodo\shopgun-v2.2')
if not (ROOT / 'artisan').exists():
    print("ERROR: artisan not found in " + str(ROOT))
    sys.exit(1)

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak')
    p.write_text(content, encoding='utf-8')
    print("OK: " + rel)

def patch(rel, old, new, label=""):
    p = ROOT / rel
    if not p.exists():
        print("SKIP: " + rel + " not found")
        return
    txt = p.read_text(encoding='utf-8')
    if new in txt:
        print("SKIP: " + label + " already applied")
        return
    if old not in txt:
        print("WARN: " + label + " pattern not found in " + rel)
        return
    txt = txt.replace(old, new, 1)
    p.write_text(txt, encoding='utf-8')
    print("OK: " + rel + " - " + label)

# ═══════════════════════════════════════════════════════════════
# 1. PRINT ROUTE (server-side، بدون iframe)
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
txt = routes.read_text(encoding='utf-8')

if 'certificates/print' not in txt:
    marker = "Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');"
    print_route = r"""Route::get('/print', function () {
        $ids = trim((string) request('ids', ''));
        $auto = request('auto', '0') === '1';
        $ids_arr = array_values(array_filter(array_map('intval', explode(',', $ids))));
        if (empty($ids_arr)) { abort(404, 'شناسنامه‌ای انتخاب نشده'); }

        $certs = \App\Models\Certificate::whereIn('id', $ids_arr)->orderBy('id')->get()->all();
        if (empty($certs)) { abort(404); }

        $cols = count($certs) === 1 ? 1 : 3;
        $html = \App\Services\CertRenderer::renderBatchHtml($certs, $cols);

        if ($auto) {
            $script = '<script>window.addEventListener("load",function(){setTimeout(function(){window.print()},700)})</script>';
            $html = str_replace('</body></html>', $script . '</body></html>', $html);
        }

        return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
    })->name('print');"""
    txt = txt.replace(marker, print_route + "\n        " + marker)
    routes.write_text(txt, encoding='utf-8')
    print("OK: print route added")
else:
    print("SKIP: print route already exists")

# ═══════════════════════════════════════════════════════════════
# 2. UPDATE SHOW PAGE PRINT BUTTON
# ═══════════════════════════════════════════════════════════════

show_path = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'show.blade.php'
if show_path.exists():
    txt = show_path.read_text(encoding='utf-8')

    # جایگزین دکمه چاپ
    txt = txt.replace(
        'onclick="printCurrentCert()"',
        'onclick="window.open(\'{{ route("certificates.print", ["ids" => $certificate->id, "auto" => 1]) }}\', \'_blank\')"'
    )

    # حذف JS قدیمی (اگر وجود دارد)
    if '<script type="text/template" id="cert-batch-template">' in txt:
        import re
        txt = re.sub(
            r'<script type="text/template" id="cert-batch-template">.*?</script>',
            '',
            txt,
            flags=re.DOTALL
        )
    if 'window.printCurrentCert = function' in txt:
        import re
        txt = re.sub(
            r'window\.printCurrentCert = function \(\) \{.*?\};',
            '',
            txt,
            flags=re.DOTALL
        )

    show_path.write_text(txt, encoding='utf-8')
    print("OK: show.blade.php - print button updated")

# ═══════════════════════════════════════════════════════════════
# 3. SETTINGS - CERT TAB WITH SLIDERS
# ═══════════════════════════════════════════════════════════════

settings_path = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'

CERT_TAB = r'''
        @if($tab === 'certificate')
            <div class="sg-settings-card">
                <h3>📏 اندازه شناسنامه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>📐 عرض (cm)</label>
                        <input type="number" step="0.1" wire:model.live="cert_width" dir="ltr" />
                    </div>
                    <div class="field col-6">
                        <label>📐 ارتفاع (cm)</label>
                        <input type="number" step="0.1" wire:model.live="cert_height" dir="ltr" />
                    </div>
                </div>
                <div style="display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap">
                    <button type="button" wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-sm">۶.۵×۶.۵</button>
                    <button type="button" wire:click="setCertPreset(7,7)" class="btn btn-outline btn-sm">۷×۷</button>
                    <button type="button" wire:click="setCertPreset(8,6)" class="btn btn-outline btn-sm">۸×۶</button>
                </div>

                <h3>🖼️ ابعاد تصویر محصول</h3>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>عرض تصویر</span><span dir="ltr">{{ $cert_img_w }} px</span>
                    </label>
                    <input type="range" min="40" max="300" step="5" wire:model.live="cert_img_w" style="width:100%;accent-color:#c9a84c">
                </div>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>ارتفاع تصویر</span><span dir="ltr">{{ $cert_img_h }} px</span>
                    </label>
                    <input type="range" min="40" max="300" step="5" wire:model.live="cert_img_h" style="width:100%;accent-color:#c9a84c">
                </div>

                <h3>📱 ابعاد QR</h3>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>اندازه QR</span><span dir="ltr">{{ $cert_qr_size }} px</span>
                    </label>
                    <input type="range" min="20" max="120" step="2" wire:model.live="cert_qr_size" style="width:100%;accent-color:#c9a84c">
                </div>

                <h3>🏷️ لوگو</h3>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>عرض لوگو</span><span dir="ltr">{{ $cert_logo_w }} px</span>
                    </label>
                    <input type="range" min="10" max="100" step="2" wire:model.live="cert_logo_w" style="width:100%;accent-color:#c9a84c">
                </div>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>ارتفاع لوگو</span><span dir="ltr">{{ $cert_logo_h }} px</span>
                    </label>
                    <input type="range" min="10" max="100" step="2" wire:model.live="cert_logo_h" style="width:100%;accent-color:#c9a84c">
                </div>

                <h3>🔤 فونت‌ها</h3>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>فونت عنوان</span><span dir="ltr">{{ $cert_title_font }} px</span>
                    </label>
                    <input type="range" min="8" max="40" wire:model.live="cert_title_font" style="width:100%;accent-color:#c9a84c">
                </div>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>فونت کد</span><span dir="ltr">{{ $cert_code_font }} px</span>
                    </label>
                    <input type="range" min="6" max="30" wire:model.live="cert_code_font" style="width:100%;accent-color:#c9a84c">
                </div>
                <div style="margin-bottom:14px">
                    <label style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#1a5276;margin-bottom:6px">
                        <span>فونت توضیحات</span><span dir="ltr">{{ $cert_desc_font }} px</span>
                    </label>
                    <input type="range" min="5" max="20" wire:model.live="cert_desc_font" style="width:100%;accent-color:#c9a84c">
                </div>

                <label style="display:flex;align-items:center;gap:8px;padding:10px;background:rgba(0,0,0,.03);border-radius:8px;cursor:pointer;margin-bottom:14px">
                    <input type="checkbox" wire:model.live="cert_hide_desc" style="width:18px;height:18px;accent-color:#c9a84c">
                    <span style="font-size:13px;font-weight:700">مخفی کردن بخش توضیحات</span>
                </label>

                {{-- پیش‌نمایش زنده --}}
                <h3 style="margin-top:20px">👁️ پیش‌نمایش زنده</h3>
                <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #ffffff 0% 50%) 50% / 20px 20px;padding:20px;border-radius:12px;display:flex;justify-content:center;overflow:auto">
                    <div style="transform-origin:top center">
                        {!! $this->livePreviewHtml !!}
                    </div>
                </div>

                <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px">
                    <a href="{{ route('certificates.index') }}" wire:navigate class="btn btn-outline">🎴 مشاهده لیست</a>
                    <button type="button" wire:click="saveCertificate" class="btn btn-success">💾 ذخیره تنظیمات</button>
                </div>
            </div>
        @endif
'''

if settings_path.exists():
    txt = settings_path.read_text(encoding='utf-8')

    # پیدا کردن و جایگزینی بلوک certificate
    import re
    pattern = r"        @if\(\$tab === 'certificate'\).*?        @endif"
    match = re.search(pattern, txt, flags=re.DOTALL)
    if match:
        txt = txt[:match.start()] + CERT_TAB.strip() + '\n' + txt[match.end():]
        settings_path.write_text(txt, encoding='utf-8')
        print("OK: settings index - cert tab replaced")
    else:
        print("WARN: certificate tab pattern not found")

# ═══════════════════════════════════════════════════════════════
# 4. ADD livePreviewHtml TO Settings/Index.php
# ═══════════════════════════════════════════════════════════════

settings_php = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if settings_php.exists():
    txt = settings_php.read_text(encoding='utf-8')

    if 'getLivePreviewHtmlProperty' not in txt:
        # اضافه کردن متد قبل از render
        method = r'''
    /**
     * ★ پیش‌نمایش زنده شناسنامه
     */
    public function getLivePreviewHtmlProperty(): string
    {
        try {
            // مقادیر رو در AppSetting ذخیره کن (بدون persist)
            $cert = \App\Models\Certificate::latest('id')->first();
            if (!$cert) {
                $cert = new \App\Models\Certificate([
                    'code' => '123456',
                    'serial' => 'MJ-000000-0000-123456-TUR-A',
                    'stone_name' => 'فیروزه عجمی',
                    'stone_en' => 'Turquoise Ajami',
                    'stone_origin' => 'نیشابور',
                    'stone_flag' => 'ir',
                    'metal' => 'نقره 925',
                    'metal_en' => 'Silver 925',
                    'metal_carat' => '925',
                    'length' => 15,
                    'width' => 12,
                    'weight' => 5.5,
                    'brilliant' => 0,
                    'issued_at' => now(),
                ]);
            }

            // ابعاد فعلی رو با مقادیر سرصفحه جایگزین کن
            $sizes = [
                'width' => $this->cert_width,
                'height' => $this->cert_height,
                'img_w' => $this->cert_img_w,
                'img_h' => $this->cert_img_h,
                'qr_size' => $this->cert_qr_size,
                'logo_w' => $this->cert_logo_w,
                'logo_h' => $this->cert_logo_h,
                'code_font' => $this->cert_code_font,
                'title_font' => $this->cert_title_font,
                'desc_font' => $this->cert_desc_font,
                'imgW' => $this->cert_img_w,
                'imgH' => $this->cert_img_h,
                'qrSize' => $this->cert_qr_size,
                'logoW' => $this->cert_logo_w,
                'logoH' => $this->cert_logo_h,
                'codeFont' => $this->cert_code_font,
                'titleFont' => $this->cert_title_font,
                'descFont' => $this->cert_desc_font,
            ];

            // CertConfig رو موقت با این مقادیر override می‌کنیم
            \App\Support\CertConfig::$overrideSizes = $sizes;

            return \App\Services\CertRenderer::renderCard($cert);
        } catch (\Throwable $e) {
            return '<div style="padding:20px;color:#dc2626">خطا: ' . htmlspecialchars($e->getMessage()) . '</div>';
        }
    }

'''
        txt = txt.replace('    public function render()', method + '    public function render()', 1)
        settings_php.write_text(txt, encoding='utf-8')
        print("OK: settings php - preview method added")

# ═══════════════════════════════════════════════════════════════
# 5. CertConfig - static override support
# ═══════════════════════════════════════════════════════════════

certconfig = ROOT / 'app' / 'Support' / 'CertConfig.php'
if certconfig.exists():
    txt = certconfig.read_text(encoding='utf-8')

    if 'public static $overrideSizes' not in txt:
        txt = txt.replace(
            'class CertConfig\n{',
            'class CertConfig\n{\n    /** @var array|null Override موقت برای پیش‌نمایش */\n    public static ?array $overrideSizes = null;\n',
            1
        )

    if 'self::$overrideSizes' not in txt:
        # در متد sizes، override رو اعمال کن
        old_return = "        return is_array($saved) ? array_merge($d, $saved) : $d;"
        new_return = "        if (self::$overrideSizes !== null) {\n            $d = array_merge($d, self::$overrideSizes);\n        }\n\n        return is_array($saved) ? array_merge($d, $saved) : $d;"
        if old_return in txt:
            txt = txt.replace(old_return, new_return, 1)

    certconfig.write_text(txt, encoding='utf-8')
    print("OK: CertConfig with override support")

# ═══════════════════════════════════════════════════════════════
# 6. MODAL - Certificate Form as Popup
# ═══════════════════════════════════════════════════════════════

# 6.1. Component تبدیل Create به Modal
create_php = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if create_php.exists():
    txt = create_php.read_text(encoding='utf-8')

    # اضافه کردن show property و listener
    if 'public bool $show = false;' not in txt:
        txt = txt.replace(
            'public int $step = 1;',
            "public int $step = 1;\n    public bool $show = false;\n    public ?int $editingId = null;",
            1
        )

    if "#[On('open-cert-form')]" not in txt:
        listener = r'''
    #[On('open-cert-form')]
    public function openModal(?int $certId = null): void
    {
        $this->resetForm();
        $this->editingId = $certId;
        if ($certId) {
            $c = Certificate::find($certId);
            if ($c) {
                $this->stoneName = $c->stone_name ?? '';
                $this->stoneEn = $c->stone_en ?? '';
                $this->stoneOrigin = $c->stone_origin ?? '';
                $this->stoneFlag = $c->stone_flag ?? 'ir';
                $this->metal = $c->metal ?? 'نقره 925';
                $this->metalEn = $c->metal_en ?? '';
                $this->metalCarat = $c->metal_carat ?? '';
                $this->length = (string) ($c->length ?? '');
                $this->width = (string) ($c->width ?? '');
                $this->weight = (string) ($c->weight ?? '');
                $this->brilliant = (string) ($c->brilliant ?? '0');
                $this->customerId = $c->customer_id;
                $this->orderId = $c->order_id;
            }
        }
        $this->show = true;
        $this->step = 1;
    }

    public function closeModal(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->step = 1;
        $this->stoneName = '';
        $this->stoneEn = '';
        $this->stoneOrigin = 'نیشابور';
        $this->stoneFlag = 'ir';
        $this->stoneIcon = '💠';
        $this->metal = 'نقره 925';
        $this->metalEn = 'Silver 925';
        $this->metalCarat = '925';
        $this->length = '';
        $this->width = '';
        $this->weight = '';
        $this->brilliant = '0';
        $this->customerId = null;
        $this->orderId = null;
        $this->image = null;
        $this->editingId = null;
    }
'''
        txt = txt.replace('    public function save()', listener + '\n    public function save()', 1)
        create_php.write_text(txt, encoding='utf-8')
        print("OK: create.php - modal methods added")

# 6.2. Update Create view - wrap in modal
create_view = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'create.blade.php'
if create_view.exists():
    txt = create_view.read_text(encoding='utf-8')

    # اگر کاربر از dispatch اومده، show=true. حالا توی modal بپیچ
    if '<div style="padding:14px;max-width:900px' in txt and 'sg-modal-overlay' not in txt:
        # محتوای فعلی داخل modal میرود
        new_view = '''<div>
@if($show)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto" @keydown.escape.window="$wire.closeModal()">
    <div style="background:#fff;width:100%;max-width:880px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.35);overflow:hidden;direction:rtl">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">{{ $editingId ? '✏️ ویرایش شناسنامه' : '💎 شناسنامه جدید' }}</h2>
            <button type="button" wire:click="closeModal" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:14px;max-height:calc(100vh - 180px);overflow-y:auto">
''' + txt.replace('<div style="padding:14px;max-width:900px;margin:0 auto" dir="rtl">', '') + '''
        </div>
    </div>
</div>
@endif
</div>'''

        # fix: بستن درست div ها
        new_view = new_view.replace('''        </div>
    </div>
</div>
@endif
</div>''', '''</div>
@endif
</div>''')

        create_view.write_text(new_view, encoding='utf-8')
        print("OK: create.blade.php - modal wrapper")

# 6.3. Index - دکمه Popup
cert_index = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if cert_index.exists():
    txt = cert_index.read_text(encoding='utf-8')

    txt = txt.replace(
        '<a href="{{ route(\'certificates.create\') }}" wire:navigate class="btn btn-primary">➕ شناسنامه جدید</a>',
        '<button onclick="Livewire.dispatch(\'open-cert-form\')" class="btn btn-primary">➕ شناسنامه جدید</button>'
    )

    cert_index.write_text(txt, encoding='utf-8')
    print("OK: certificates index - button updated")

# 6.4. Layout - اضافه کردن modal
layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    if '<livewire:certificates.create' not in txt and 'certificates.create' not in txt:
        marker = '<livewire:orders.form-modal'
        if marker in txt:
            txt = txt.replace(
                marker,
                '<livewire:certificates.create :key="\'cfm\'" />\n    ' + marker,
                1
            )
            layout.write_text(txt, encoding='utf-8')
            print("OK: layout - cert modal included")

print()
print("=" * 50)
print("DONE")
print("=" * 50)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")